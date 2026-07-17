from datetime import UTC, datetime
import importlib
from types import SimpleNamespace
from uuid import uuid4

from app.mappers.ai_mapper import AIMapper
from app.mappers.exception_mapper import ExceptionMapper
from app.schemas.ai import AIChatMessage, AIChatResponse, ConversationHistoryItem
from app.schemas.exception import ExceptionDetailResponse, ExceptionSummary


class FakeAIInsightResponse:
    def __init__(self, explanation, recommendation, confidence):
        self.explanation = explanation
        self.recommendation = recommendation
        self.confidence = confidence


def test_ai_mapper_builds_chat_history_message_and_insight_responses(monkeypatch):
    monkeypatch.setattr("app.mappers.ai_mapper.AIInsightResponse", FakeAIInsightResponse)
    now = datetime.now(UTC)
    chat_id = uuid4()

    chat_response = AIMapper.to_chat_response("Answer", 12)
    history_item = AIMapper.to_history_item(
        SimpleNamespace(id=chat_id, question="Question?", created_at=now)
    )
    message = AIMapper.to_message("assistant", "Hello", now)
    insight = AIMapper.to_insight(
        SimpleNamespace(
            explanation="Explanation",
            recommendation="Review",
            confidence="98.5",
        )
    )

    assert isinstance(chat_response, AIChatResponse)
    assert chat_response.answer == "Answer"
    assert chat_response.tokens_used == 12
    assert chat_response.conversation == []
    assert isinstance(history_item, ConversationHistoryItem)
    assert history_item.id == chat_id
    assert history_item.question == "Question?"
    assert isinstance(message, AIChatMessage)
    assert message.role == "assistant"
    assert message.created_at == now
    assert isinstance(insight, FakeAIInsightResponse)
    assert insight.explanation == "Explanation"
    assert insight.recommendation == "Review"
    assert insight.confidence == 98.5


class FakeDashboardSummaryResponse:
    def __init__(
        self,
        total_transactions,
        matched_transactions,
        exceptions,
        open_cases,
        ai_confidence,
    ):
        self.total_transactions = total_transactions
        self.matched_transactions = matched_transactions
        self.exceptions = exceptions
        self.open_cases = open_cases
        self.ai_confidence = ai_confidence


class FakeRecentRun:
    def __init__(
        self,
        id,
        run_number,
        initiated_by,
        started_at,
        total,
        matched,
        unmatched,
        exceptions,
        status,
    ):
        self.id = id
        self.run_number = run_number
        self.initiated_by = initiated_by
        self.started_at = started_at
        self.total = total
        self.matched = matched
        self.unmatched = unmatched
        self.exceptions = exceptions
        self.status = status


class FakeExceptionBreakdown:
    def __init__(self, exception_type, count):
        self.exception_type = exception_type
        self.count = count


def test_dashboard_mapper_builds_summary_run_breakdown_and_bank_responses(monkeypatch):
    import app.schemas.dashboard as dashboard_schema

    monkeypatch.setattr(
        dashboard_schema,
        "DashboardSummaryResponse",
        FakeDashboardSummaryResponse,
    )
    monkeypatch.setattr(dashboard_schema, "RecentRun", FakeRecentRun, raising=False)
    monkeypatch.setattr(
        dashboard_schema,
        "ExceptionBreakdown",
        FakeExceptionBreakdown,
        raising=False,
    )
    dashboard_mapper = importlib.import_module("app.mappers.dashboard_mapper")
    dashboard_mapper = importlib.reload(dashboard_mapper)
    DashboardMapper = dashboard_mapper.DashboardMapper

    now = datetime.now(UTC)
    run_id = uuid4()
    bank_id = uuid4()

    summary = DashboardMapper.to_summary(
        total_transactions=10,
        matched_transactions=8,
        exceptions=2,
        open_cases=1,
        ai_confidence=95.5,
    )
    recent_run = DashboardMapper.to_recent_run(
        SimpleNamespace(
            id=run_id,
            initiated_by=SimpleNamespace(first_name="Test", last_name="User"),
            started_at=now,
            total_transactions=10,
            matched=8,
            unmatched=1,
            exceptions=1,
            status=SimpleNamespace(value="COMPLETED"),
        )
    )
    breakdown = DashboardMapper.to_exception_breakdown(
        (SimpleNamespace(value="AMOUNT"), 3)
    )
    bank = DashboardMapper.to_bank_summary(
        SimpleNamespace(
            id=bank_id,
            bank_name="Test Bank",
            country="US",
            currency="USD",
            is_active=True,
        )
    )

    assert isinstance(summary, FakeDashboardSummaryResponse)
    assert summary.total_transactions == 10
    assert summary.matched_transactions == 8
    assert summary.exceptions == 2
    assert summary.open_cases == 1
    assert summary.ai_confidence == 95.5
    assert isinstance(recent_run, FakeRecentRun)
    assert recent_run.id == run_id
    assert recent_run.run_number == f"RUN-{str(run_id)[:8].upper()}"
    assert recent_run.initiated_by == "Test User"
    assert recent_run.status == "COMPLETED"
    assert isinstance(breakdown, FakeExceptionBreakdown)
    assert breakdown.exception_type == "AMOUNT"
    assert breakdown.count == 3
    assert bank == {
        "bank_id": bank_id,
        "bank_name": "Test Bank",
        "country": "US",
        "currency": "USD",
        "active": True,
    }


def test_exception_mapper_builds_summary_and_detail_responses():
    now = datetime.now(UTC)
    exception_id = uuid4()
    reconciliation_result_id = uuid4()
    exception = SimpleNamespace(
        id=exception_id,
        reconciliation_result_id=reconciliation_result_id,
        exception_type=SimpleNamespace(value="AMOUNT"),
        severity=SimpleNamespace(value="HIGH"),
        status=SimpleNamespace(value="OPEN"),
        assigned_to="user-1",
        detected_at=now,
        resolved_at=None,
        resolution_notes=None,
        reconciliation_result=SimpleNamespace(
            payment_transaction=SimpleNamespace(
                transaction_reference="PAY-1",
                amount="125.50",
                currency="USD",
            )
        ),
    )

    summary = ExceptionMapper.to_summary(exception)
    detail = ExceptionMapper.to_detail(exception)

    assert isinstance(summary, ExceptionSummary)
    assert summary.id == exception_id
    assert summary.exception_code == f"EX-{str(exception_id)[:8].upper()}"
    assert summary.related_reference == "PAY-1"
    assert summary.amount == 125.50
    assert summary.currency == "USD"
    assert isinstance(detail, ExceptionDetailResponse)
    assert detail.reconciliation_result_id == reconciliation_result_id
    assert detail.exception_type == "AMOUNT"
    assert detail.resolution_notes is None
