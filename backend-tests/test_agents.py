import re
from types import SimpleNamespace

from app.agents.common.azure_client import AzureOpenAIClient
from app.agents.copilot.base import CopilotAgent
from app.agents.matching.base import MatchingAgent
from app.agents.exception.base import ExceptionAnalysisAgent
from app.agents.recommendation.base import RecommendationAgent
from app.agents.matching.azure_openai_agent import AzureOpenAIMatchingAgent
from app.agents.exception.azure_openai_agent import AzureOpenAIExceptionAgent
from app.agents.recommendation.azure_openai_agent import AzureOpenAIRecommendationAgent
from app.agents.copilot.azure_openai_agent import (
    AzureOpenAICopilotAgent,
    get_utc_now,
)
from app.agents.copilot.factory import CopilotAgentFactory
from app.agents.matching.factory import MatchingAgentFactory
from app.agents.exception.factory import ExceptionAnalysisAgentFactory
from app.agents.recommendation.factory import RecommendationAgentFactory


def test_azure_openai_client_complete_uses_responses_create(monkeypatch):
    class FakeResponse:
        output_text = "{\"decision\": \"MATCH\"}"

    class FakeClient:
        class responses:
            @staticmethod
            def create(model, input):
                return FakeResponse()

    monkeypatch.setattr(AzureOpenAIClient, "client", classmethod(lambda cls: FakeClient()))

    result = AzureOpenAIClient.complete("prompt", temperature=0.5, metadata={"foo": "bar"})

    assert result == FakeResponse.output_text


def test_matching_agent_validate_parses_json(monkeypatch):
    class FakeClient:
        class responses:
            @staticmethod
            def create(model, input):
                return SimpleNamespace(output_text='{"decision":"MATCH","confidence":95}')

    monkeypatch.setattr("app.agents.matching.azure_openai_agent.AzureOpenAIClient.complete", lambda prompt, **kwargs: '{"decision":"MATCH","confidence":95}')

    agent = AzureOpenAIMatchingAgent()
    payment = SimpleNamespace(
        transaction_reference="T1",
        end_to_end_id="E1",
        amount=100,
        currency="USD",
        payment_date="2026-01-01",
        sender_name="Alice",
        receiver_name="Bob",
    )
    bank = SimpleNamespace(
        transaction_reference="T1",
        end_to_end_id="E1",
        amount=100,
        currency="USD",
        payment_date="2026-01-01",
    )

    result = agent.validate(payment, bank, 60)

    assert result["decision"] == "MATCH"
    assert result["confidence"] == 95


def test_exception_agent_validate_parses_json(monkeypatch):
    monkeypatch.setattr("app.agents.exception.azure_openai_agent.AzureOpenAIClient.complete", lambda prompt, **kwargs: '{"summary":"Exp","root_cause":"Cause","confidence":45,"business_explanation":"Beef","operational_domain":"Ops","business_impact":"Impact","evidence":[],"recommended_actions":[]}')

    agent = AzureOpenAIExceptionAgent()
    result = agent.analyze({"case":"dummy"})

    assert result["confidence"] == 45
    assert result["business_explanation"] == "Beef"


def test_recommendation_agent_validate_parses_json(monkeypatch):
    monkeypatch.setattr("app.agents.recommendation.azure_openai_agent.AzureOpenAIClient.complete", lambda prompt, **kwargs: '{"recommendation":"Do X","priority":"High","assigned_team":"Team","estimated_resolution":"1 day","escalation_required":false}')

    agent = AzureOpenAIRecommendationAgent()
    result = agent.recommend({"case":"dummy"})

    assert result["recommendation"] == "Do X"
    assert result["assigned_team"] == "Team"


def test_agent_factories_create_instances():
    assert isinstance(MatchingAgentFactory.create(), AzureOpenAIMatchingAgent)
    assert isinstance(ExceptionAnalysisAgentFactory.create(), AzureOpenAIExceptionAgent)
    assert isinstance(RecommendationAgentFactory.create(), AzureOpenAIRecommendationAgent)
    assert isinstance(CopilotAgentFactory.create(), AzureOpenAICopilotAgent)


def test_copilot_agent_chat_uses_azure_client(monkeypatch):
    monkeypatch.setattr(
        "app.agents.copilot.azure_openai_agent.AzureOpenAIClient.complete",
        lambda prompt, **kwargs: "copilot-response",
    )

    agent = AzureOpenAICopilotAgent()
    result = agent.chat("What is the status?", {"foo": "bar"})

    assert result == "copilot-response"


def test_get_utc_now_format():
    now = get_utc_now()

    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\+00", now)


def test_base_classes_pass_line_executed():
    class DummyCopilotAgent(CopilotAgent):
        def chat(self, question, context):
            return super().chat(question, context)

    class DummyMatchingAgent(MatchingAgent):
        def validate(self, payment, bank, score):
            return super().validate(payment, bank, score)

    class DummyExceptionAgent(ExceptionAnalysisAgent):
        def analyze(self, reconciliation, payment_transaction, bank_transaction):
            return super().analyze(reconciliation, payment_transaction, bank_transaction)

    class DummyRecommendationAgent(RecommendationAgent):
        def recommend(self, investigation_case):
            return super().recommend(investigation_case)

    assert DummyCopilotAgent().chat("q", {}) is None
    assert DummyMatchingAgent().validate({}, {}, 0) is None
    assert DummyExceptionAgent().analyze({}, {}, {}) is None
    assert DummyRecommendationAgent().recommend({}) is None
