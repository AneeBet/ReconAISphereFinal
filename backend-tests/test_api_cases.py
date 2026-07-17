from types import SimpleNamespace
from uuid import uuid4

from app.api import cases as cases_api
from app.models.investigation_case import CaseStatus


class FakeInvestigationRepository:
    def __init__(self, db):
        self.db = db


class FakeInvestigationService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def get_all(self):
        self.calls.append(("get_all", self.repository.db))
        return ["case"]

    def get_case(self, case_id):
        self.calls.append(("get_case", self.repository.db, case_id))
        return {"id": case_id}

    def update_status(self, case_id, status):
        self.calls.append(("update_status", self.repository.db, case_id, status))
        return True

    def add_comment(self, case_id, user_id, comment):
        self.calls.append(("add_comment", self.repository.db, case_id, user_id, comment))
        return {"comment": comment}

    def add_attachment(self, case_id, user_id, file_name, blob_url):
        self.calls.append(("add_attachment", self.repository.db, case_id, user_id, file_name, blob_url))
        return {"file_name": file_name, "blob_url": blob_url}


def test_cases_api_endpoints_delegate_to_service(monkeypatch):
    monkeypatch.setattr(cases_api, "InvestigationRepository", FakeInvestigationRepository)
    monkeypatch.setattr(cases_api, "InvestigationService", FakeInvestigationService)
    FakeInvestigationService.calls = []

    db = object()
    user = SimpleNamespace(id="user-1")
    case_id = uuid4()

    assert cases_api.get_cases(current_user=user, db=db) == ["case"]
    assert cases_api.get_case(case_id, current_user=user, db=db) == {"id": case_id}
    assert cases_api.update_status(case_id, CaseStatus.CLOSED, current_user=user, db=db) is True
    assert cases_api.add_comment(case_id, "Looks fixed", current_user=user, db=db) == {
        "comment": "Looks fixed"
    }
    assert cases_api.add_attachment(
        case_id,
        "evidence.txt",
        "https://blob/evidence.txt",
        current_user=user,
        db=db,
    ) == {"file_name": "evidence.txt", "blob_url": "https://blob/evidence.txt"}

    assert FakeInvestigationService.calls == [
        ("get_all", db),
        ("get_case", db, case_id),
        ("update_status", db, case_id, CaseStatus.CLOSED),
        ("add_comment", db, case_id, "user-1", "Looks fixed"),
        ("add_attachment", db, case_id, "user-1", "evidence.txt", "https://blob/evidence.txt"),
    ]
