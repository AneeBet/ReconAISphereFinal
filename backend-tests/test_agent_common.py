import pytest
from types import SimpleNamespace
from app.agents.common.azure_client import AzureOpenAIClient
from app.agents.common.json_parser import JsonParser


def test_json_parser_parses_plain_json():
    result = JsonParser.parse('{"decision":"MATCH","confidence":95}')
    assert result["decision"] == "MATCH"
    assert result["confidence"] == 95


def test_json_parser_parses_markdown_fence():
    payload = "```json\n{\"decision\": \"EXCEPTION\", \"confidence\": 45}\n```"
    result = JsonParser.parse(payload)
    assert result["decision"] == "EXCEPTION"
    assert result["confidence"] == 45


def test_json_parser_extracts_json_block_from_text():
    payload = "Here is the response:\n{\"decision\": \"REVIEW\", \"confidence\": 50}\nThank you."
    result = JsonParser.parse(payload)
    assert result["decision"] == "REVIEW"
    assert result["confidence"] == 50


def test_json_parser_returns_raw_response_on_invalid_json():
    text = "Not JSON at all"
    result = JsonParser.parse(text)
    assert result == {"raw_response": text}


def test_json_parser_returns_empty_dict_on_none():
    assert JsonParser.parse(None) == {}


def test_json_parser_handles_invalid_json_inside_braces():
    payload = "Here is the response: {invalid json}"
    result = JsonParser.parse(payload)

    assert result == {"raw_response": payload}


def test_azure_openai_client_complete_uses_client_response(monkeypatch):
    captured = {}

    class FakeResponse:
        output_text = "fake-output"

    class FakeClient:
        class responses:
            @staticmethod
            def create(model, input):
                captured["model"] = model
                captured["input"] = input
                return FakeResponse()

    monkeypatch.setattr(AzureOpenAIClient, "client", classmethod(lambda cls: FakeClient()))

    result = AzureOpenAIClient.complete("prompt", temperature=0.3, metadata={"foo": "bar"})

    assert result == "fake-output"
    assert captured["model"] == "test-deployment"
    assert captured["input"] == "prompt"


def test_azure_openai_client_initializes_openai_client(monkeypatch):
    created = {}

    class FakeResponse:
        output_text = "fake-output"

    class FakeOpenAI:
        def __init__(self, base_url, api_key, timeout, max_retries):
            created["base_url"] = base_url
            created["api_key"] = api_key
            created["timeout"] = timeout
            created["max_retries"] = max_retries

        class responses:
            @staticmethod
            def create(model, input):
                return FakeResponse()

    monkeypatch.setattr("app.agents.common.azure_client.OpenAI", FakeOpenAI)
    AzureOpenAIClient._client = None

    client = AzureOpenAIClient.client()

    assert created["base_url"].endswith("/openai/v1")
    assert created["api_key"] == "test"
    assert created["timeout"] == 60
    assert created["max_retries"] == 2
    assert client is AzureOpenAIClient._client
