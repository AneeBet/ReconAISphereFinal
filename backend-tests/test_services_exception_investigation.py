import pytest
import uuid
from datetime import datetime, UTC
from types import SimpleNamespace
from app.models.investigation_case import CaseStatus
from app.services.exception_service import ExceptionService
from app.services.investigation_service import InvestigationService


class FakeAuditService:
    def __init__(self, repository):
        self.repository = repository

    def log(self, *args, **kwargs):
        return None


@pytest.fixture(autouse=True)
def patch_audit(monkeypatch):
    monkeypatch.setattr("app.services.exception_service.AuditService", lambda repository: FakeAuditService(repository))
    monkeypatch.setattr("app.services.investigation_service.AuditService", lambda repository: FakeAuditService(repository))


class FakeExceptionRepo:
    def __init__(self):
        self.db = None
        self.saved = []

    def get_all(self):
        return [
            SimpleNamespace(
                id=uuid.uuid4(),
                exception_type=SimpleNamespace(value="AMOUNT"),
                severity=SimpleNamespace(value="HIGH"),
                status=SimpleNamespace(value="OPEN"),
                assigned_to=str(uuid.uuid4()),
                detected_at=datetime.now(UTC),
                reconciliation_result=SimpleNamespace(
                    payment_transaction=SimpleNamespace(
                        transaction_reference="T1",
                        amount=100,
                        currency="USD"
                    )
                )
            )
        ]

    def get_by_id(self, exception_id):
        return SimpleNamespace(
            id=exception_id,
            assigned_to=str(uuid.uuid4()),
            exception_type=SimpleNamespace(value="AMOUNT"),
            severity=SimpleNamespace(value="HIGH"),
            status=SimpleNamespace(value="OPEN"),
            investigation_case=SimpleNamespace(
                owner_id=str(uuid.uuid4()),
                status=SimpleNamespace(value="OPEN")
            ),
            resolution_notes=None,
            reconciliation_result=SimpleNamespace(
                payment_transaction=SimpleNamespace(transaction_reference="T1"),
                bank_transaction=SimpleNamespace(transaction_reference="B1"),
                reconciliation_status=SimpleNamespace(value="EXCEPTION"),
                match_type=SimpleNamespace(value="PARTIAL"),
                confidence_score=45,
            ),
        )

    def update(self, exception):
        self.saved.append(exception)
        return True


class FakeInvestigationRepo:
    def __init__(self):
        self.db = None
        self.updated = []

    def get_all(self):
        return [
            SimpleNamespace(
                id=uuid.uuid4(),
                case_number="CASE-1",
                title="Title",
                description="Desc",
                priority=SimpleNamespace(value="LOW"),
                owner=SimpleNamespace(first_name="Test", last_name="User"),
                status=CaseStatus.OPEN,
                due_date=None,
                created_at=datetime.now(UTC),
                exception=SimpleNamespace(
                    reconciliation_result=SimpleNamespace(
                        payment_transaction=SimpleNamespace(transaction_reference="T1", amount=100),
                        bank_transaction=SimpleNamespace(transaction_reference="B1", amount=90),
                    )
                ),
                workflow_history=[],
                comments=[],
                attachments=[]
            )
        ]

    def get_case(self, case_id):
        return SimpleNamespace(
            id=uuid.uuid4(),
            case_number="CASE-1",
            title="Title",
            description="Desc",
            priority=SimpleNamespace(value="LOW"),
            owner=SimpleNamespace(first_name="Test", last_name="User"),
            owner_id=str(uuid.uuid4()),
            status=CaseStatus.OPEN,
            due_date=None,
            created_at=datetime.now(UTC),
            exception=SimpleNamespace(
                reconciliation_result=SimpleNamespace(
                    payment_transaction=SimpleNamespace(transaction_reference="T1", amount=100),
                    bank_transaction=SimpleNamespace(transaction_reference="B1", amount=90),
                )
            ),
            workflow_history=[],
            comments=[],
            attachments=[]
        )

    def update(self, case):
        self.updated.append(case)
        return True

    def add_comment(self, comment):
        self.updated.append(comment)
        return comment

    def add_attachment(self, attachment):
        self.updated.append(attachment)
        return attachment


def test_exception_service_get_all_and_assign_and_resolve():
    repo = FakeExceptionRepo()
    service = ExceptionService(repo)

    exceptions = service.get_all()
    assert len(exceptions) == 1
    assert exceptions[0].exception_type == "AMOUNT"

    assigned = service.assign(1, "user2")
    assert assigned is True
    assert repo.saved[-1].assigned_to == "user2"

    resolved = service.update_status(1, "Fixed")
    assert resolved is True
    assert repo.saved[-1].resolution_notes == "Fixed"


def test_investigation_service_get_case_update_and_comments():
    repo = FakeInvestigationRepo()
    service = InvestigationService(repo)

    case = service.get_case(1)
    assert case.overview.case_number == "CASE-1"

    updated = service.update_status(1, CaseStatus.CLOSED)
    assert updated is True
    assert repo.updated[-1].status == CaseStatus.CLOSED

    comment = service.add_comment(1, "user1", "note")
    assert comment.comment == "note"

    attachment = service.add_attachment(1, "user1", "file.txt", "https://example.com/file.txt")
    assert attachment.file_name == "file.txt"
