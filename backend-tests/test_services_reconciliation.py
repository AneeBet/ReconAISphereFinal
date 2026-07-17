import pytest
from datetime import datetime, timezone
from types import SimpleNamespace
from app.services.reconciliation_service import ReconciliationService


class FakeAuditService:
    def __init__(self, repository):
        self.repository = repository
        self.logged = []

    def log(self, *args, **kwargs):
        self.logged.append((args, kwargs))


class FakeRepository:
    def __init__(self):
        self.db = None
        self.updated_runs = []
        self.saved_results = []
        self.marked = False

    def create_run(self, run):
        return run

    def update_run(self, run):
        self.updated_runs.append(run)
        return run

    def get_pending_payment_transactions(self):
        return []

    def get_all_bank_transactions(self):
        return []

    def save_results(self, results):
        self.saved_results.extend(results)

    def mark_reconciled(self, payments, banks):
        self.marked = True

    def get_results(self):
        return []


@pytest.fixture(autouse=True)
def patch_audit(monkeypatch):
    monkeypatch.setattr("app.services.reconciliation_service.AuditService", lambda repository: FakeAuditService(repository))


def test_reconciliation_service_run_when_no_payments(monkeypatch):
    repo = FakeRepository()
    monkeypatch.setattr("app.services.reconciliation_service.EnterpriseReconciliationService", lambda: SimpleNamespace(reconcile=lambda payments, banks: []))
    monkeypatch.setattr("app.services.reconciliation_service.MatchingAgentFactory", SimpleNamespace(create=lambda: SimpleNamespace(validate=lambda payment, bank, score: {})))

    service = ReconciliationService(repo)
    run = service.run(initiated_by="user1")

    assert run.status.name == "COMPLETED"
    assert run.total_transactions == 0
    assert run.exceptions == 0
    assert repo.marked is False


def test_reconciliation_service_results_calls_mapper(monkeypatch):
    import uuid

    fake_reconciliation = SimpleNamespace(
        id=uuid.uuid4(),
        payment_transaction=SimpleNamespace(id=uuid.uuid4(), transaction_reference="T1", amount=100, currency="USD"),
        bank_transaction=SimpleNamespace(id=uuid.uuid4(), transaction_reference="B1", amount=100, currency="USD"),
        confidence_score=95,
        reconciliation_status=SimpleNamespace(value="MATCHED"),
    )
    repo = FakeRepository()
    repo.get_results = lambda: [fake_reconciliation]
    service = ReconciliationService(repo)

    results = service.results()

    assert results[0].status == "MATCHED"
