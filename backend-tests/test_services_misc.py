import asyncio
import uuid
from datetime import datetime, UTC
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.audit_service import AuditService
from app.services.dashboard_service import DashboardService
from app.services.file_service import FileService
from app.services.transaction_service import TransactionService


class FakeRepo:
    def __init__(self):
        self.created = None
        self.logs = []

    def create(self, audit):
        self.created = audit
        return audit

    def get_logs(self):
        return self.logs


def test_audit_service_log_creates_audit_record():
    repository = FakeRepo()
    service = AuditService(repository)

    result = service.log(
        user_id="user-1",
        entity_type="TestEntity",
        entity_id=123,
        action="CREATE",
        old_value={"foo": "bar"},
        new_value={"foo": "baz"},
        ip_address="127.0.0.1",
    )

    assert result is repository.created
    assert result.entity_type == "TestEntity"
    assert result.entity_id == "123"
    assert result.action == "CREATE"
    assert result.ip_address == "127.0.0.1"


def test_audit_service_get_logs_formats_user_name():
    repository = FakeRepo()
    repository.logs = [
        SimpleNamespace(
            created_at=datetime.now(UTC),
            user=SimpleNamespace(first_name="John", last_name="Doe"),
            action="UPDATE",
            entity_type="Invoice",
            entity_id="1",
            ip_address="10.0.0.1",
        ),
        SimpleNamespace(
            created_at=datetime.now(UTC),
            user=None,
            action="DELETE",
            entity_type="Payment",
            entity_id="2",
            ip_address=None,
        ),
    ]

    service = AuditService(repository)
    response = service.get_logs()

    assert response.total_records == 2
    assert response.logs[0].user == "John Doe"
    assert response.logs[0].details == "Invoice UPDATE"
    assert response.logs[1].user == "System"
    assert response.logs[1].entity == "Payment"


def test_dashboard_service_forward_calls():
    repo = SimpleNamespace(
        summary=lambda: {"total": 1},
        recent_runs=lambda: ["run1"],
        banks=lambda: ["bank1"],
        exception_chart=lambda: {"critical": 0, "high": 1, "medium": 2, "low": 3},
    )

    service = DashboardService(repo)

    assert service.summary() == {"total": 1}
    assert service.recent_runs() == ["run1"]
    assert service.bank_summary() == ["bank1"]
    assert service.exception_chart() == {"critical": 0, "high": 1, "medium": 2, "low": 3}


def test_transaction_service_returns_summaries_and_detail():
    now = datetime.now(UTC)
    transaction = SimpleNamespace(
        id=uuid.uuid4(),
        transaction_reference="REF-1",
        end_to_end_id="E2E-1",
        bank=SimpleNamespace(bank_name="Test Bank"),
        payment_date=now,
        amount=100,
        currency="USD",
        status=SimpleNamespace(value="SUCCESS"),
        sender_name="Alice",
        receiver_name="Bob",
        sender_account="A1",
        receiver_account="B1",
        settlement_date=now,
        payment_type="SWIFT",
        raw_json={"foo": "bar"},
    )

    repo = SimpleNamespace(
        get_transactions=lambda: [transaction],
        get_transaction=lambda _id: transaction,
    )

    service = TransactionService(repo)
    summaries = service.get_transactions()
    assert len(summaries) == 1
    assert summaries[0].bank == "Test Bank"
    assert summaries[0].status == "SUCCESS"

    detail = service.get_transaction(transaction.id)
    assert detail.id == transaction.id
    assert detail.sender_name == "Alice"
    assert detail.raw_json == {"foo": "bar"}


def test_transaction_service_raises_for_missing_transaction():
    repo = SimpleNamespace(get_transaction=lambda _id: None)
    service = TransactionService(repo)

    with pytest.raises(HTTPException) as exc:
        service.get_transaction(uuid.uuid4())

    assert exc.value.status_code == 404
    assert "Transaction not found" in exc.value.detail


class FakeUpload:
    def __init__(self, filename, contents):
        self.filename = filename
        self._contents = contents

    async def read(self):
        return self._contents


class FakeFileRepo:
    def __init__(self):
        self.db = None
        self.saved_payment = []
        self.saved_bank = []
        self.saved_legs = []
        self.created_files = []

    def save_payment_transactions(self, items):
        self.saved_payment.extend(items)

    def save_bank_transactions(self, items):
        self.saved_bank.extend(items)

    def save_legs(self, items):
        self.saved_legs.extend(items)

    def create(self, file_obj):
        self.created_files.append(file_obj)
        return file_obj


@pytest.fixture(autouse=True)
def patch_file_service_components(monkeypatch):
    monkeypatch.setattr("app.services.file_service.AzureBlobStorage", lambda: SimpleNamespace(upload=lambda path, data: f"https://blob/{path}"))
    monkeypatch.setattr("app.services.file_service.AuditService", lambda repository: SimpleNamespace(log=lambda *args, **kwargs: None))


def test_file_service_upload_batch_stores_files(monkeypatch):
    repo = FakeFileRepo()
    service = FileService(repo)

    def fake_rows(contents, filename):
        return [
            {
                "transaction_reference": "T1",
                "end_to_end_id": "E1",
                "amount": "100",
                "currency": "USD",
                "payment_date": "2026-01-01",
                "settlement_date": "2026-01-02",
                "sender_name": "Alice",
                "receiver_name": "Bob",
                "status": "PASS",
                "detail": "note",
                "event_time": "2026-01-01T00:00:00Z",
            }
        ]

    monkeypatch.setattr("app.services.file_service.Normalizer.rows", fake_rows)

    files = {
        "payment": FakeUpload("payment.csv", b"dummy"),
        "bank": FakeUpload("bank.csv", b"dummy"),
        "aml": FakeUpload("aml.csv", b"dummy"),
        "settlement": None,
    }

    summary = asyncio.run(service.upload_batch(files, bank_id="bank-1", user_id="user-1"))

    assert summary["ingested"]["payment"] == 1
    assert summary["ingested"]["bank"] == 1
    assert summary["ingested"]["aml"] == 1
    assert len(repo.created_files) == 3
    assert len(repo.saved_payment) == 1
    assert len(repo.saved_bank) == 1
    assert len(repo.saved_legs) == 1


def test_file_service_build_helpers():
    repo = FakeFileRepo()
    service = FileService(repo)

    bad_leg = service._build_leg(
        stage=SimpleNamespace(name="AML"),
        row={
            "end_to_end_id": "E1",
            "status": "unknown",
            "detail": None,
            "event_time": None,
        },
    )
    assert bad_leg.status.name == "PASS"
    assert bad_leg.detail == "None"
    assert bad_leg.event_time is None

    assert service._optional_float(None) is None
    assert service._optional_float(123.45) == 123.45
    assert service._optional_float("123.45") == 123.45
    assert service._optional_float(float("nan")) is None

    assert service._to_date(None) is None
    dt = service._to_date("2026-01-01")
    assert dt.year == 2026


def test_file_service_history_delegates_to_repository(monkeypatch):
    repository = SimpleNamespace(get_all=lambda: ["file1", "file2"], db=None)
    monkeypatch.setattr("app.services.file_service.AzureBlobStorage", lambda: SimpleNamespace(upload=lambda path, data: "url"))
    monkeypatch.setattr("app.services.file_service.AuditService", lambda repository: SimpleNamespace(log=lambda *args, **kwargs: None))

    service = FileService(repository)
    assert service.history() == ["file1", "file2"]
