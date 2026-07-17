import io
import pytest
import pandas as pd
from app.agents.common.json_parser import JsonParser
from app.parser.normalizer import Normalizer


def test_json_parser_parses_plain_json():
    text = '{"decision": "MATCH", "confidence": 95}'
    result = JsonParser.parse(text)

    assert result["decision"] == "MATCH"
    assert result["confidence"] == 95


def test_json_parser_parses_code_block_json():
    text = "```json\n{\"decision\": \"EXCEPTION\", \"confidence\": 42}\n```"
    result = JsonParser.parse(text)

    assert result["decision"] == "EXCEPTION"
    assert result["confidence"] == 42


def test_json_parser_returns_raw_response_for_invalid_json():
    text = "not json"
    result = JsonParser.parse(text)

    assert result == {"raw_response": text}


def test_normalizer_reads_csv_and_renames_columns():
    contents = b"txn_ref,end_to_end,amount,ccy\nA1,E1,100,USD\n"
    rows = Normalizer.rows(contents, "sample.csv")

    assert rows == [{
        "transaction_reference": "A1",
        "end_to_end_id": "E1",
        "amount": 100,
        "currency": "USD"
    }]


def test_normalizer_rejects_unsupported_format():
    with pytest.raises(ValueError):
        Normalizer.read(b"{}", "sample.txt")
