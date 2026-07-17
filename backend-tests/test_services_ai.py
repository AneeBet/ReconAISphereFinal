import pytest
from types import SimpleNamespace
from app.services.ai_service import AIService


class FakeAuditService:
    def __init__(self, repository):
        self.repository = repository

    def log(self, *args, **kwargs):
        return None


@pytest.fixture(autouse=True)
def patch_audit(monkeypatch):
    monkeypatch.setattr("app.services.ai_service.AuditService", lambda repository: FakeAuditService(repository))


class FakeRepo:
    def __init__(self):
        self.db = None
        self.history_items = []

    def get_history(self, user_id):
        return [SimpleNamespace(id=1, question="Q", answer="A", created_at="now")]

    def get_copilot_context(self):
        return {"platform": "test"}

    def get_case(self, case_id):
        payment = SimpleNamespace(
            transaction_reference="T1",
            end_to_end_id="E1",
            sender_name="Alice",
            receiver_name="Bob",
            sender_account="A1",
            receiver_account="B1",
            amount=100,
            currency="USD",
            payment_date="2026-01-01",
            settlement_date="2026-01-02",
            status=SimpleNamespace(value="PENDING"),
            fx_rate=1.0,
            raw_json={"x": 1},
        )
        bank = SimpleNamespace(
            transaction_reference="B1",
            end_to_end_id="E1",
            sender_name="Alice",
            receiver_name="Bob",
            sender_account="A1",
            receiver_account="B1",
            amount=100,
            currency="USD",
            payment_date="2026-01-01",
            settlement_date="2026-01-02",
            status="SETTLED",
            fx_rate=1.0,
            raw_json={"x": 1},
        )
        return SimpleNamespace(
            id=1,
            case_number="CASE-1",
            title="Title",
            description="Desc",
            priority=SimpleNamespace(value="HIGH"),
            status=SimpleNamespace(value="OPEN"),
            owner_id="user1",
            exception=SimpleNamespace(
                exception_type=SimpleNamespace(value="AMOUNT"),
                severity=SimpleNamespace(value="HIGH"),
                status=SimpleNamespace(value="OPEN"),
                detected_at="now",
                resolution_notes=None,
                reconciliation_result=SimpleNamespace(
                    payment_transaction=payment,
                    bank_transaction=bank,
                    reconciliation_status=SimpleNamespace(value="EXCEPTION"),
                    match_type=SimpleNamespace(value="PARTIAL"),
                    confidence_score=55,
                    matched_by="AI",
                    matched_at="now",
                )
            ),
        )

    def save_chat(self, chat):
        chat.id = 1


@pytest.fixture(autouse=True)
def patch_agents(monkeypatch):
    monkeypatch.setattr("app.services.ai_service.CopilotAgentFactory", SimpleNamespace(create=lambda: SimpleNamespace(chat=lambda question, context: "Answer")))
    monkeypatch.setattr("app.services.ai_service.ExceptionAnalysisAgentFactory", SimpleNamespace(create=lambda: SimpleNamespace(analyze=lambda context: {"business_explanation": "Exp", "root_cause": "Cause", "business_impact": "Impact", "operational_domain": "Ops", "confidence": 90, "evidence": [], "recommended_actions": []})))
    monkeypatch.setattr("app.services.ai_service.RecommendationAgentFactory", SimpleNamespace(create=lambda: SimpleNamespace(recommend=lambda case: {"assigned_team": "Team", "recommendation": "Do X"})))


def test_ai_history_returns_entries():
    service = AIService(FakeRepo())
    result = service.history("user1")

    assert result["history"][0]["question"] == "Q"


def test_ai_explain_returns_summary(monkeypatch):
    service = AIService(FakeRepo())
    result = service.explain(1)

    assert result["summary"] == "Exp"
    assert result["confidence"] == 90


def test_ai_recommend_returns_recommendation():
    service = AIService(FakeRepo())
    result = service.recommend(1)

    assert result["recommendation"] == "Do X"


def test_ai_chat_returns_assistant_message():
    service = AIService(FakeRepo())
    result = service.chat("user1", "hello")

    assert result["answer"] == "Answer"
    assert result["conversation"][-1]["role"] == "assistant"
