import asyncio
from types import SimpleNamespace
from uuid import uuid4

from app.api import audit as audit_api
from app.api import exceptions as exceptions_api
from app.api import files as files_api
from app.api import reconciliation as reconciliation_api
from app.api import reports as reports_api
from app.api import seed_users as seed_users_api
from app.api import transactions as transactions_api
from app.schemas.exception import AssignExceptionRequest, ResolveExceptionRequest
from app.schemas.report import ReportRequest


class FakeRepository:
    def __init__(self, db):
        self.db = db


class FakeExceptionService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def get_all(self):
        self.calls.append(("get_all", self.repository.db))
        return ["exception"]

    def assign(self, exception_id, user_id):
        self.calls.append(("assign", self.repository.db, exception_id, user_id))
        return True

    def update_status(self, exception_id, resolution_notes):
        self.calls.append(("update_status", self.repository.db, exception_id, resolution_notes))
        return True


def test_exceptions_api_endpoints_delegate_to_service(monkeypatch):
    monkeypatch.setattr(exceptions_api, "ExceptionRepository", FakeRepository)
    monkeypatch.setattr(exceptions_api, "ExceptionService", FakeExceptionService)
    FakeExceptionService.calls = []

    db = object()
    user = object()
    exception_id = uuid4()
    assigned_user_id = uuid4()

    assert exceptions_api.get_exceptions(current_user=user, db=db) == ["exception"]
    assert exceptions_api.assign_exception(
        exception_id,
        AssignExceptionRequest(user_id=assigned_user_id),
        current_user=user,
        db=db,
    ) is True
    assert exceptions_api.update_status(
        exception_id,
        ResolveExceptionRequest(resolution_notes="Resolved"),
        current_user=user,
        db=db,
    ) is True

    assert FakeExceptionService.calls == [
        ("get_all", db),
        ("assign", db, exception_id, assigned_user_id),
        ("update_status", db, exception_id, "Resolved"),
    ]


class FakeFileService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    async def upload_batch(self, files, bank_id, user_id):
        self.calls.append(("upload_batch", self.repository.db, files, bank_id, user_id))
        return {"ingested": len([file for file in files.values() if file is not None])}

    def history(self):
        self.calls.append(("history", self.repository.db))
        return ["file"]


def test_files_api_endpoints_delegate_to_service(monkeypatch):
    monkeypatch.setattr(files_api, "FileRepository", FakeRepository)
    monkeypatch.setattr(files_api, "FileService", FakeFileService)
    FakeFileService.calls = []

    db = object()
    user = SimpleNamespace(id="user-1")
    bank_id = uuid4()
    payment_file = object()
    bank_file = object()

    result = asyncio.run(
        files_api.upload_batch(
            bank_id=bank_id,
            payment=payment_file,
            bank=bank_file,
            aml=None,
            fx=None,
            correspondent=None,
            settlement=None,
            current_user=user,
            db=db,
        )
    )
    assert result == {"ingested": 2}
    assert files_api.history(current_user=user, db=db) == ["file"]

    method, called_db, files, called_bank_id, called_user_id = FakeFileService.calls[0]
    assert (method, called_db, called_bank_id, called_user_id) == (
        "upload_batch",
        db,
        bank_id,
        "user-1",
    )
    assert files["payment"] is payment_file
    assert files["bank"] is bank_file
    assert files["aml"] is None
    assert FakeFileService.calls[1] == ("history", db)


class FakeReconciliationService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def run(self, user_id):
        self.calls.append(("run", self.repository.db, user_id))
        return {"status": "started"}

    def results(self):
        self.calls.append(("results", self.repository.db))
        return ["result"]


def test_reconciliation_api_endpoints_delegate_to_service(monkeypatch):
    monkeypatch.setattr(reconciliation_api, "ReconciliationRepository", FakeRepository)
    monkeypatch.setattr(reconciliation_api, "ReconciliationService", FakeReconciliationService)
    FakeReconciliationService.calls = []

    db = object()
    user = SimpleNamespace(id="user-1")

    assert reconciliation_api.run_reconciliation(current_user=user, db=db) == {"status": "started"}
    assert reconciliation_api.get_results(current_user=user, db=db) == ["result"]
    assert FakeReconciliationService.calls == [
        ("run", db, "user-1"),
        ("results", db),
    ]


class FakeReportService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def dashboard_report(self):
        self.calls.append(("dashboard_report", self.repository.db))
        return {"total_transactions": 1}

    def export(self, report_type):
        self.calls.append(("export", self.repository.db, report_type))
        return {"report_name": "summary.csv"}

    def download(self, report_name):
        self.calls.append(("download", self.repository.db, report_name))
        return b"id,name\n1,test\n"


def test_reports_api_endpoints_delegate_to_service(monkeypatch):
    monkeypatch.setattr(reports_api, "ReportRepository", FakeRepository)
    monkeypatch.setattr(reports_api, "ReportService", FakeReportService)
    FakeReportService.calls = []

    db = object()
    user = object()

    assert reports_api.dashboard_report(current_user=user, db=db) == {"total_transactions": 1}
    assert reports_api.export(ReportRequest(report_type="dashboard"), current_user=user, db=db) == {
        "report_name": "summary.csv"
    }
    response = reports_api.download("summary.csv", current_user=user, db=db)

    assert response.body == b"id,name\n1,test\n"
    assert response.media_type == "text/csv"
    assert response.headers["content-disposition"] == 'attachment; filename="summary.csv"'
    assert FakeReportService.calls == [
        ("dashboard_report", db),
        ("export", db, "dashboard"),
        ("download", db, "summary.csv"),
    ]


class FakeSeedUsersService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def seed(self):
        self.calls.append(("seed", self.repository.db))
        return {"created": 3}


def test_seed_users_api_delegates_to_service(monkeypatch):
    monkeypatch.setattr(seed_users_api, "SeedUsersRepository", FakeRepository)
    monkeypatch.setattr(seed_users_api, "SeedUsersService", FakeSeedUsersService)
    FakeSeedUsersService.calls = []

    db = object()

    assert seed_users_api.seed_users(db=db) == {"created": 3}
    assert FakeSeedUsersService.calls == [("seed", db)]


class FakeTransactionService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def get_transactions(self):
        self.calls.append(("get_transactions", self.repository.db))
        return ["transaction"]

    def get_transaction(self, transaction_id):
        self.calls.append(("get_transaction", self.repository.db, transaction_id))
        return {"id": transaction_id}


def test_transactions_api_endpoints_delegate_to_service(monkeypatch):
    monkeypatch.setattr(transactions_api, "TransactionRepository", FakeRepository)
    monkeypatch.setattr(transactions_api, "TransactionService", FakeTransactionService)
    FakeTransactionService.calls = []

    db = object()
    user = object()
    transaction_id = uuid4()

    assert transactions_api.get_transactions(current_user=user, db=db) == ["transaction"]
    assert transactions_api.get_transaction(transaction_id, current_user=user, db=db) == {
        "id": transaction_id
    }
    assert FakeTransactionService.calls == [
        ("get_transactions", db),
        ("get_transaction", db, transaction_id),
    ]


class FakeAuditService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def get_logs(self):
        self.calls.append(("get_logs", self.repository.db))
        return {"logs": []}


def test_audit_api_delegates_to_service(monkeypatch):
    monkeypatch.setattr(audit_api, "AuditRepository", FakeRepository)
    monkeypatch.setattr(audit_api, "AuditService", FakeAuditService)
    FakeAuditService.calls = []

    db = object()
    user = object()

    assert audit_api.audit_logs(current_user=user, db=db) == {"logs": []}
    assert FakeAuditService.calls == [("get_logs", db)]
