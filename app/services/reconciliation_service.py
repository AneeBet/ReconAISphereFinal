from datetime import UTC
from datetime import datetime

from app.agents.matching.factory import (
    MatchingAgentFactory,
)

from datetime import timedelta

from app.models.exception import (
    Exception,
    ExceptionStatus,
    ExceptionType,
    Severity,
)

from app.models.investigation_case import (
    CasePriority,
    CaseStatus,
    InvestigationCase,
)

from app.models.reconciliation_result import (
    MatchType,
    ReconciliationResult,
    ReconciliationStatus,
)

from app.models.reconciliation_run import (
    ReconciliationRun,
    ReconciliationRunStatus,
)

from app.models.payment_transaction import (
    PaymentStatus,
)

from app.reconciliation.reconciliation_service import (
    EnterpriseReconciliationService,
)

from app.mappers.reconciliation_mapper import (
    ReconciliationMapper,
)

from app.repositories.audit_repository import (
    AuditRepository,
)

from app.repositories.reconciliation_repository import (
    ReconciliationRepository,
)

from app.services.audit_service import (
    AuditService,
)


class ReconciliationService:

    def __init__(
        self,
        repository: ReconciliationRepository
    ):

        self.repository = repository

        self.engine = EnterpriseReconciliationService()

        self.agent = MatchingAgentFactory.create()

        self.audit = AuditService(

            AuditRepository(

                repository.db

            )

        )

    def run(

        self,

        initiated_by

    ):

        run = ReconciliationRun(

            initiated_by_id=initiated_by,

            started_at=datetime.now(UTC),

            status=ReconciliationRunStatus.RUNNING

        )

        run = self.repository.create_run(

            run

        )

        self.audit.log(

            user_id=initiated_by,

            entity_type="ReconciliationRun",

            entity_id=run.id,

            action="START"

        )

        payments = self.repository.get_pending_payment_transactions()

        if not payments:

            run.completed_at = datetime.now(UTC)

            run.total_transactions = 0

            run.matched = 0

            run.unmatched = 0

            run.exceptions = 0

            run.ai_processed = 0

            run.status = ReconciliationRunStatus.COMPLETED

            self.repository.update_run(run)

            self.audit.log(

                user_id=initiated_by,

                entity_type="ReconciliationRun",

                entity_id=run.id,

                action="COMPLETED",

                new_value={

                    "matched": 0,

                    "exceptions": 0,

                    "total": 0,

                    "ai_processed": 0

                }

            )

            return run

        bank_transactions = self.repository.get_all_bank_transactions()

        engine_results = self.engine.reconcile(

            payments,

            bank_transactions

        )

        reconciliation_results = []

        exception_payloads = []

        matched = 0

        exceptions = 0

        ai_processed = 0

        for result in engine_results:

            if result["status"] == "MATCHED":

                ai = {

                    "decision": "MATCH",

                    "confidence": result["score"],

                    "reason": "Exact rule engine match"

                }

                match_type = MatchType.EXACT

            elif result["status"] == "EXCEPTION":

                ai = {

                    "decision": "EXCEPTION",

                    "confidence": result["score"],

                    "reason": "Rule engine determined low confidence"

                }

                match_type = MatchType.PARTIAL

            else:

                ai_processed += 1

                ai = self.agent.validate(

                    result["payment"],

                    result["bank"],

                    result["score"]

                )

                match_type = MatchType.AI

            status = (

                ReconciliationStatus.MATCHED

                if ai["decision"] == "MATCH"

                else ReconciliationStatus.EXCEPTION

            )

            if status == ReconciliationStatus.MATCHED:

                result["payment"].status = PaymentStatus.SUCCESS

            else:

                result["payment"].status = PaymentStatus.FAILED

            if status == ReconciliationStatus.MATCHED:

                matched += 1

            else:

                exceptions += 1

            reconciliation_result = ReconciliationResult(

                run_id=run.id,

                payment_transaction_id=result["payment"].id,

                bank_transaction_id=(

                    result["bank"].id

                    if result["bank"]

                    else None

                ),

                match_type=match_type,

                confidence_score=ai["confidence"],

                matched_by="ReconAI",

                matched_at=datetime.now(UTC),

                reconciliation_status=status

            )

            reconciliation_results.append(reconciliation_result)

            if status == ReconciliationStatus.EXCEPTION:

                exception_payloads.append(
                    (
                        reconciliation_result,
                        result["payment"],
                        result["bank"]
                    )
                )

        self.repository.save_results(

            reconciliation_results

        )

        self._raise_exceptions(exception_payloads)

        self.repository.mark_reconciled(
            payments,
            [r["bank"] for r in engine_results]
        )

        run.completed_at = datetime.now(

            UTC

        )

        run.total_transactions = len(

            payments

        )

        run.matched = matched

        run.unmatched = len(payments) - matched

        run.exceptions = exceptions

        run.ai_processed = ai_processed

        run.status = ReconciliationRunStatus.COMPLETED

        self.repository.update_run(

            run

        )

        self.audit.log(

            user_id=initiated_by,

            entity_type="ReconciliationRun",

            entity_id=run.id,

            action="COMPLETED",

            new_value={

                "matched": matched,

                "exceptions": exceptions,

                "total": len(payments),

                "ai_processed": ai_processed

            }

        )

        return run

    def results(

        self

    ):

        return [
            ReconciliationMapper.to_result(result)
            for result in self.repository.get_results()
        ]

    def _raise_exceptions(
        self,
        payloads
    ):

        if not payloads:
            return

        new_exceptions = []

        new_cases = []

        for reconciliation_result, payment, bank in payloads:

            failed_leg = self.repository.get_failed_leg(
                payment.end_to_end_id
            )

            exception_type, severity = self._classify(
                payment,
                bank,
                failed_leg
            )

            existing_exception = self.repository.get_open_exception(
                payment.id
            )

            if existing_exception:

                existing_exception.reconciliation_result_id = (
                    reconciliation_result.id
                )

                existing_exception.exception_type = exception_type

                existing_exception.severity = severity

                existing_exception.detected_at = datetime.now(UTC)

                self.repository.db.commit()

                continue

            exception_record = Exception(

                reconciliation_result_id=reconciliation_result.id,

                exception_type=exception_type,

                severity=severity,

                status=ExceptionStatus.OPEN,

                detected_at=datetime.now(UTC)

            )

            self.repository.db.add(exception_record)

            self.repository.db.flush()

            new_exceptions.append(exception_record)

            stuck = (
                f" — stuck at {failed_leg.stage.value} "
                f"({failed_leg.status.value})"
                if failed_leg else ""
            )

            existing_case = self.repository.get_open_case(
                exception_record.id
            )

            if existing_case:
                continue

            new_cases.append(

                InvestigationCase(

                    exception_id=exception_record.id,

                    case_number=(
                        f"CASE-{datetime.now(UTC):%Y%m%d}-"
                        f"{exception_record.id.hex[:8].upper()}"
                    ),

                    title=(
                        f"{exception_type.value} exception "
                        f"on {payment.transaction_reference}{stuck}"
                    ),

                    description=(
                        "Auto-generated investigation case from "
                        "reconciliation run."
                    ),

                    due_date=self._due_date(
                        self._priority(severity)
                    ),

                    priority=self._priority(severity),

                    status=CaseStatus.OPEN

                )

            )

        if new_cases:

            self.repository.db.add_all(new_cases)

        self.repository.db.commit()

    @staticmethod
    def _classify(payment, bank, failed_leg=None):

        if failed_leg is not None:
            return ExceptionType.MISSING, Severity.HIGH

        if bank is None:
            return ExceptionType.MISSING, Severity.HIGH

        if str(payment.currency) != str(bank.currency):
            return ExceptionType.FX, Severity.MEDIUM

        if abs(float(payment.amount) - float(bank.amount)) > 0.01:
            return ExceptionType.AMOUNT, Severity.HIGH

        if payment.settlement_date and bank.settlement_date:
            if payment.settlement_date != bank.settlement_date:
                return ExceptionType.SETTLEMENT, Severity.LOW

        return ExceptionType.REFERENCE, Severity.LOW

    @staticmethod
    def _priority(severity):

        mapping = {
            Severity.CRITICAL: CasePriority.CRITICAL,
            Severity.HIGH: CasePriority.HIGH,
            Severity.MEDIUM: CasePriority.MEDIUM,
            Severity.LOW: CasePriority.LOW,
        }

        return mapping.get(severity, CasePriority.LOW)

    @staticmethod
    def _due_date(priority):

        now = datetime.now(UTC)

        if priority == CasePriority.CRITICAL:
            return now + timedelta(hours=4)

        if priority == CasePriority.HIGH:
            return now + timedelta(days=1)

        if priority == CasePriority.MEDIUM:
            return now + timedelta(days=3)

        return now + timedelta(days=5)