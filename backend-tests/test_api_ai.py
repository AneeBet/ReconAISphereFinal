from types import SimpleNamespace
from uuid import uuid4

from app.api import ai as ai_api
from app.schemas.ai import AIQuestionRequest


class FakeAIRepository:
    def __init__(self, db):
        self.db = db


class FakeAIService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def chat(self, user_id, question):
        self.calls.append(("chat", self.repository.db, user_id, question))
        return {"answer": "ok"}

    def history(self, user_id):
        self.calls.append(("history", self.repository.db, user_id))
        return {"history": []}

    def explain(self, case_id):
        self.calls.append(("explain", self.repository.db, case_id))
        return {"summary": "explained"}

    def recommend(self, case_id):
        self.calls.append(("recommend", self.repository.db, case_id))
        return {"recommendation": "next step"}


def test_ai_api_endpoints_delegate_to_service(monkeypatch):
    monkeypatch.setattr(ai_api, "AIRepository", FakeAIRepository)
    monkeypatch.setattr(ai_api, "AIService", FakeAIService)
    FakeAIService.calls = []

    db = object()
    user = SimpleNamespace(id="user-1")
    case_id = uuid4()

    assert ai_api.chat(AIQuestionRequest(question="hello"), current_user=user, db=db) == {"answer": "ok"}
    assert ai_api.history(current_user=user, db=db) == {"history": []}
    assert ai_api.explain(case_id, current_user=user, db=db) == {"summary": "explained"}
    assert ai_api.recommend(case_id, current_user=user, db=db) == {"recommendation": "next step"}

    assert FakeAIService.calls == [
        ("chat", db, "user-1", "hello"),
        ("history", db, "user-1"),
        ("explain", db, case_id),
        ("recommend", db, case_id),
    ]
