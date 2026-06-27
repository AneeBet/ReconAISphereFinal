from datetime import UTC
from datetime import datetime

from app.agents.matching.factory import (
    MatchingAgentFactory,
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

from app.reconciliation.reconciliation_service import (
    EnterpriseReconciliationService,
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

        payment_file_id,

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

        payments = self.repository.get_payment_transactions(

            payment_file_id

        )

        if not payments:

            return run

        bank_transactions = self.repository.get_bank_transactions(

            payments[0].bank_id

        )

        engine_results = self.engine.reconcile(

            payments,

            bank_transactions

        )

        reconciliation_results = []

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

                matched += 1

            else:

                exceptions += 1

            reconciliation_results.append(

                ReconciliationResult(

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

            )

        self.repository.save_results(

            reconciliation_results

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

        return self.repository.get_results()