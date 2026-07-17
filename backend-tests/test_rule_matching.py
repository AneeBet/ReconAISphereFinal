from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from app.reconciliation.rule_engine import RuleEngine
from app.reconciliation.matching_engine import MatchingEngine
from app.reconciliation.reconciliation_service import EnterpriseReconciliationService


def make_payment():
    return SimpleNamespace(
        transaction_reference="TXN1",
        end_to_end_id="E2E1",
        amount="100.00",
        currency="USD",
        payment_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def make_bank():
    return SimpleNamespace(
        transaction_reference="TXN1",
        end_to_end_id="E2E1",
        amount="100.00",
        currency="USD",
        payment_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def test_rule_engine_exact_match():
    payment = make_payment()
    bank = make_bank()

    rules = RuleEngine()
    assert rules.exact_match(payment, bank)
    assert rules.end_to_end_match(payment, bank)
    assert rules.amount_match(payment, bank)
    assert rules.currency_match(payment, bank)
    assert rules.date_match(payment, bank)


def test_rule_engine_amount_tolerance():
    payment = make_payment()
    bank = make_bank()
    bank.amount = "100.009"

    rules = RuleEngine()
    assert rules.amount_match(payment, bank)


def test_matching_engine_score():
    payment = make_payment()
    bank = make_bank()

    engine = MatchingEngine()
    score = engine.match(payment, bank)

    assert score == 100


def test_enterprise_reconciliation_service_statuses():
    payment = make_payment()
    bank = make_bank()
    bank.amount = "100.00"

    service = EnterpriseReconciliationService()
    results = service.reconcile([payment], [bank])

    assert len(results) == 1
    assert results[0]["status"] == "MATCHED"
    assert results[0]["ai_required"] is False

    payment2 = make_payment()
    payment2.transaction_reference = "OTHER"
    payment2.end_to_end_id = "OTHER"
    payment2.amount = "100.00"
    bank2 = make_bank()
    bank2.amount = "101.00"

    results2 = service.reconcile([payment2], [bank2])
    assert results2[0]["status"] == "EXCEPTION"
