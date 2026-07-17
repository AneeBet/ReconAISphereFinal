from datetime import UTC, datetime
from uuid import uuid4

from app.models.ai_chat_history import AIChatHistory
from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.bank import Bank
from app.models.bank_transaction import BankTransaction
from app.models.comment import Comment
from app.models.exception import Exception as ExceptionModel
from app.models.exception import ExceptionStatus, ExceptionType, Severity
from app.models.investigation_case import CasePriority, CaseStatus, InvestigationCase
from app.models.payment_file import PaymentFile, ProcessingStatus
from app.models.payment_transaction import PaymentStatus, PaymentTransaction
from app.models.reconciliation_result import MatchType, ReconciliationResult, ReconciliationStatus
from app.models.reconciliation_run import ReconciliationRun, ReconciliationRunStatus
from app.models.transaction_leg import LegStage, LegStatus, TransactionLeg
from app.repositories.ai_repository import AIRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.exception_repository import ExceptionRepository
from app.repositories.file_repository import FileRepository
from app.repositories.investigation_repository import InvestigationRepository
from app.repositories.reconciliation_repository import ReconciliationRepository
from app.repositories.report_repository import ReportRepository


def _bank(test_user):
    suffix = uuid4().hex[:8]
    return Bank(
        organization_id=test_user.organization_id,
        bank_name=f"Repo Bank {suffix}",
        bic_swift=f"RB{suffix}",
        country="US",
        currency="USD",
    )


def _payment(bank, status=PaymentStatus.PENDING, reconciled=False):
    suffix = uuid4().hex
    return PaymentTransaction(
        bank_id=bank.id,
        transaction_reference=f"PAY-{suffix}",
        end_to_end_id=f"E2E-{suffix}",
        sender_account="A1",
        receiver_account="B1",
        sender_name="Alice",
        receiver_name="Bob",
        amount=100.00,
        currency="USD",
        payment_date=datetime.now(UTC),
        settlement_date=datetime.now(UTC),
        payment_type="WIRE",
        status=status,
        reconciled=reconciled,
        raw_json={"reference": suffix},
    )


def _bank_transaction(bank, end_to_end_id=None, reconciled=False):
    suffix = uuid4().hex
    return BankTransaction(
        bank_id=bank.id,
        transaction_reference=f"BANK-{suffix}",
        end_to_end_id=end_to_end_id or f"E2E-{suffix}",
        sender_account="A1",
        receiver_account="B1",
        sender_name="Alice",
        receiver_name="Bob",
        amount=100.00,
        currency="USD",
        fx_rate=1.0,
        payment_date=datetime.now(UTC),
        settlement_date=datetime.now(UTC),
        payment_type="WIRE",
        status="POSTED",
        reconciled=reconciled,
        raw_json={"reference": suffix},
    )


def _run(test_user, status=ReconciliationRunStatus.COMPLETED):
    return ReconciliationRun(
        initiated_by_id=test_user.id,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        status=status,
        total_transactions=1,
        matched=1,
        unmatched=0,
        exceptions=1,
        ai_processed=0,
    )


def _repository_graph(db_session, test_user):
    bank = _bank(test_user)
    db_session.add(bank)
    db_session.flush()

    payment_file = PaymentFile(
        bank_id=bank.id,
        file_name=f"{uuid4().hex}.csv",
        original_name="payment.csv",
        blob_url="https://blob/payment.csv",
        file_type="payment",
        checksum=uuid4().hex,
        uploaded_by_id=test_user.id,
        processing_status=ProcessingStatus.COMPLETED,
        total_records=1,
        valid_records=1,
        invalid_records=0,
    )
    payment = _payment(bank, status=PaymentStatus.FAILED)
    bank_transaction = _bank_transaction(bank, end_to_end_id=payment.end_to_end_id)
    run = _run(test_user)
    db_session.add_all([payment_file, payment, bank_transaction, run])
    db_session.flush()

    result = ReconciliationResult(
        run_id=run.id,
        payment_transaction_id=payment.id,
        bank_transaction_id=bank_transaction.id,
        match_type=MatchType.PARTIAL,
        confidence_score=75,
        matched_by="TEST",
        matched_at=datetime.now(UTC),
        reconciliation_status=ReconciliationStatus.EXCEPTION,
    )
    db_session.add(result)
    db_session.flush()

    exception = ExceptionModel(
        reconciliation_result_id=result.id,
        exception_type=ExceptionType.AMOUNT,
        severity=Severity.HIGH,
        status=ExceptionStatus.OPEN,
        assigned_to=None,
        detected_at=datetime.now(UTC),
    )
    db_session.add(exception)
    db_session.flush()

    case = InvestigationCase(
        exception_id=exception.id,
        case_number=f"CASE-{uuid4().hex[:8]}",
        title="Repository Case",
        description="Repository test case",
        priority=CasePriority.HIGH,
        owner_id=test_user.id,
        status=CaseStatus.OPEN,
    )
    db_session.add(case)
    db_session.commit()

    return {
        "bank": bank,
        "payment_file": payment_file,
        "payment": payment,
        "bank_transaction": bank_transaction,
        "run": run,
        "result": result,
        "exception": exception,
        "case": case,
    }


def test_ai_repository_history_case_chat_and_copilot_context(db_session, test_user):
    graph = _repository_graph(db_session, test_user)
    repo = AIRepository(db_session)
    chat = AIChatHistory(
        user_id=test_user.id,
        question="What happened?",
        answer="An exception happened.",
        tokens=10,
    )

    saved = repo.save_chat(chat)
    history = repo.get_history(test_user.id)
    found_case = repo.get_case(graph["case"].id)
    context = repo.get_copilot_context()

    assert saved.id is not None
    assert any(item.id == saved.id for item in history)
    assert found_case.id == graph["case"].id
    assert context["latest_run"]["status"] == ReconciliationRunStatus.COMPLETED.value
    assert context["dashboard"]["recent_transactions"] >= 1
    assert any(item["transaction"] == graph["payment"].transaction_reference for item in context["recent_exceptions"])
    assert any(item["case_number"] == graph["case"].case_number for item in context["recent_cases"])
    assert any(item["file_name"] == graph["payment_file"].original_name for item in context["recent_uploads"])


def test_audit_repository_create_and_get_logs(db_session, test_user):
    repo = AuditRepository(db_session)
    audit_log = AuditLog(
        user_id=test_user.id,
        entity_type="Payment",
        entity_id="123",
        action="CREATE",
        old_value=None,
        new_value={"status": "NEW"},
        ip_address="127.0.0.1",
    )

    created = repo.create(audit_log)
    logs = repo.get_logs()

    assert created.id is not None
    assert any(log.id == created.id and log.user.id == test_user.id for log in logs)


def test_exception_repository_get_update_and_list(db_session, test_user):
    graph = _repository_graph(db_session, test_user)
    repo = ExceptionRepository(db_session)

    all_exceptions = repo.get_all()
    found = repo.get_by_id(graph["exception"].id)
    found.assigned_to = "ops-user"
    updated = repo.update(found)

    assert any(item.id == graph["exception"].id for item in all_exceptions)
    assert found.reconciliation_result.payment_transaction.id == graph["payment"].id
    assert updated.assigned_to == "ops-user"


def test_file_repository_create_save_get_and_update(db_session, test_user):
    bank = _bank(test_user)
    db_session.add(bank)
    db_session.commit()
    repo = FileRepository(db_session)
    payment_file = PaymentFile(
        bank_id=bank.id,
        file_name=f"{uuid4().hex}.csv",
        original_name="upload.csv",
        blob_url="https://blob/upload.csv",
        file_type="payment",
        checksum=uuid4().hex,
        uploaded_by_id=test_user.id,
        processing_status=ProcessingStatus.UPLOADED,
    )

    created_file = repo.create(payment_file)
    repo.save_payment_transactions([])
    repo.save_bank_transactions([])
    repo.save_legs([])

    payment = _payment(bank)
    bank_transaction = _bank_transaction(bank)
    leg = TransactionLeg(
        end_to_end_id=payment.end_to_end_id,
        stage=LegStage.AML,
        status=LegStatus.PASS,
        detail="ok",
        event_time=datetime.now(UTC),
    )
    repo.save_payment_transactions([payment])
    repo.save_bank_transactions([bank_transaction])
    repo.save_legs([leg])

    created_file.processing_status = ProcessingStatus.COMPLETED
    updated = repo.update(created_file)

    assert created_file.id is not None
    assert any(item.id == created_file.id for item in repo.get_all())
    assert repo.get_by_id(created_file.id).id == created_file.id
    assert updated.processing_status == ProcessingStatus.COMPLETED
    assert payment.id is not None
    assert bank_transaction.id is not None
    assert leg.id is not None


def test_investigation_repository_get_update_comment_and_attachment(db_session, test_user):
    graph = _repository_graph(db_session, test_user)
    repo = InvestigationRepository(db_session)

    cases = repo.get_all()
    found = repo.get_case(graph["case"].id)
    found.status = CaseStatus.IN_PROGRESS
    updated = repo.update(found)
    comment = repo.add_comment(
        Comment(case_id=found.id, user_id=test_user.id, comment="Working on it")
    )
    attachment = repo.add_attachment(
        Attachment(
            case_id=found.id,
            uploaded_by_id=test_user.id,
            file_name="evidence.txt",
            blob_url="https://blob/evidence.txt",
        )
    )

    assert any(item.id == graph["case"].id for item in cases)
    assert found.owner.id == test_user.id
    assert updated.status == CaseStatus.IN_PROGRESS
    assert comment.id is not None
    assert attachment.id is not None


def test_reconciliation_repository_queries_and_persistence(db_session, test_user):
    graph = _repository_graph(db_session, test_user)
    repo = ReconciliationRepository(db_session)
    new_run = repo.create_run(_run(test_user, status=ReconciliationRunStatus.RUNNING))
    new_run.status = ReconciliationRunStatus.COMPLETED
    updated_run = repo.update_run(new_run)

    pending_payments = repo.get_pending_payment_transactions()
    bank_transactions = repo.get_bank_transactions(graph["bank"].id)
    all_bank_transactions = repo.get_all_bank_transactions()
    assert repo.get_failed_leg("missing-e2e") is None

    late_leg = TransactionLeg(
        end_to_end_id="LEG-ORDER",
        stage=LegStage.SETTLEMENT,
        status=LegStatus.FAIL,
        detail="late failure",
        event_time=datetime.now(UTC),
    )
    early_leg = TransactionLeg(
        end_to_end_id="LEG-ORDER",
        stage=LegStage.AML,
        status=LegStatus.HOLD,
        detail="early hold",
        event_time=datetime.now(UTC),
    )
    db_session.add_all([late_leg, early_leg])
    db_session.commit()

    open_exception = repo.get_open_exception(graph["payment"].id)
    open_case = repo.get_open_case(graph["exception"].id)
    repo.mark_reconciled([graph["payment"]], [graph["bank_transaction"], None])
    repo.save_results([])
    repo.save_exceptions([])
    repo.save_cases([])

    extra_payment = _payment(graph["bank"])
    extra_bank = _bank_transaction(graph["bank"])
    db_session.add_all([extra_payment, extra_bank])
    db_session.flush()
    extra_result = ReconciliationResult(
        run_id=graph["run"].id,
        payment_transaction_id=extra_payment.id,
        bank_transaction_id=extra_bank.id,
        match_type=MatchType.EXACT,
        confidence_score=100,
        matched_by="TEST",
        matched_at=datetime.now(UTC),
        reconciliation_status=ReconciliationStatus.MATCHED,
    )
    repo.save_results([extra_result])
    extra_exception = ExceptionModel(
        reconciliation_result_id=extra_result.id,
        exception_type=ExceptionType.MANUAL,
        severity=Severity.LOW,
        status=ExceptionStatus.CLOSED,
        assigned_to="ops",
        detected_at=datetime.now(UTC),
    )
    repo.save_exceptions([extra_exception])
    extra_case = InvestigationCase(
        exception_id=extra_exception.id,
        case_number=f"CASE-{uuid4().hex[:8]}",
        title="Closed Case",
        description=None,
        priority=CasePriority.LOW,
        owner_id=test_user.id,
        status=CaseStatus.CLOSED,
    )
    repo.save_cases([extra_case])
    results = repo.get_results()

    assert updated_run.status == ReconciliationRunStatus.COMPLETED
    assert any(item.id == graph["payment"].id for item in pending_payments)
    assert any(item.id == graph["bank_transaction"].id for item in bank_transactions)
    assert any(item.id == graph["bank_transaction"].id for item in all_bank_transactions)
    assert repo.get_failed_leg("LEG-ORDER").id == early_leg.id
    assert open_exception.id == graph["exception"].id
    assert open_case.id == graph["case"].id
    assert graph["payment"].reconciled is True
    assert graph["bank_transaction"].reconciled is True
    assert any(item.id == extra_result.id for item in results)


def test_report_repository_metrics_and_rows(db_session, test_user):
    graph = _repository_graph(db_session, test_user)
    success_payment = _payment(graph["bank"], status=PaymentStatus.SUCCESS)
    pending_payment = _payment(graph["bank"], status=PaymentStatus.PENDING)
    db_session.add_all([success_payment, pending_payment])
    db_session.commit()

    repo = ReportRepository(db_session)
    metrics = repo.dashboard_metrics()
    banks = repo.bank_summary()
    reconciliation_rows = repo.reconciliation_rows()
    exception_rows = repo.exception_rows()
    transaction_rows = repo.transaction_rows()

    assert metrics["transactions"] >= 3
    assert metrics["matched"] >= 1
    assert metrics["exceptions"] >= 1
    assert metrics["pending"] >= 1
    assert any(bank.id == graph["bank"].id for bank in banks)
    assert any(row.id == graph["result"].id for row in reconciliation_rows)
    assert any(row.id == graph["exception"].id for row in exception_rows)
    assert any(row.id == graph["payment"].id for row in transaction_rows)
