from types import SimpleNamespace
from app.mappers.transaction_mapper import TransactionMapper
from app.schemas.transaction import TransactionSummary, TransactionDetailResponse


import uuid


def test_transaction_mapper_to_summary():
    transaction = SimpleNamespace(
        id=uuid.uuid4(),
        transaction_reference="T1",
        end_to_end_id="E1",
        bank=SimpleNamespace(bank_name="Test Bank"),
        payment_date="2026-01-01",
        amount=100.12,
        currency="USD",
        status=SimpleNamespace(value="SUCCESS"),
    )

    summary = TransactionMapper.to_summary(transaction)

    assert isinstance(summary, TransactionSummary)
    assert summary.bank == "Test Bank"
    assert summary.amount == 100.12


def test_transaction_mapper_to_detail():
    transaction = SimpleNamespace(
        id=uuid.uuid4(),
        transaction_reference="T2",
        end_to_end_id="E2",
        sender_name="Alice",
        receiver_name="Bob",
        sender_account="A1",
        receiver_account="B1",
        amount=50.0,
        currency="EUR",
        payment_date="2026-02-01",
        settlement_date="2026-02-02",
        payment_type="WIRE",
        status=SimpleNamespace(value="PENDING"),
        raw_json={"foo": "bar"},
    )

    detail = TransactionMapper.to_detail(transaction)

    assert isinstance(detail, TransactionDetailResponse)
    assert detail.sender_name == "Alice"
    assert detail.receiver_name == "Bob"
    assert detail.amount == 50.0
    assert detail.status == "PENDING"
    assert detail.raw_json == {"foo": "bar"}
