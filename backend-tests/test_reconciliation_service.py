import pytest
from datetime import datetime, timedelta, timezone
from app.services.reconciliation_service import ReconciliationService
from app.models.exception import ExceptionType, Severity
from app.models.investigation_case import CasePriority


def make_payment(currency="USD", amount=100.0, settlement_date=None):
    return type("Payment", (), {
        "currency": currency,
        "amount": amount,
        "settlement_date": settlement_date,
        "transaction_reference": "REF1",
        "end_to_end_id": "E2E1",
    })


def make_bank(currency="USD", amount=100.0, settlement_date=None):
    return type("Bank", (), {
        "currency": currency,
        "amount": amount,
        "settlement_date": settlement_date,
    })


def test_classify_returns_missing_for_no_bank():
    payment = make_payment()
    exception_type, severity = ReconciliationService._classify(payment, None)

    assert exception_type == ExceptionType.MISSING
    assert severity == Severity.HIGH


def test_classify_returns_fx_for_currency_mismatch():
    payment = make_payment(currency="USD")
    bank = make_bank(currency="EUR")
    exception_type, severity = ReconciliationService._classify(payment, bank)

    assert exception_type == ExceptionType.FX
    assert severity == Severity.MEDIUM


def test_classify_returns_amount_for_amount_mismatch():
    payment = make_payment(amount=100.0)
    bank = make_bank(amount=105.0)
    exception_type, severity = ReconciliationService._classify(payment, bank)

    assert exception_type == ExceptionType.AMOUNT
    assert severity == Severity.HIGH


def test_classify_returns_settlement_for_mismatched_settlement_date():
    payment = make_payment(settlement_date=datetime(2026, 1, 1, tzinfo=timezone.utc))
    bank = make_bank(settlement_date=datetime(2026, 1, 2, tzinfo=timezone.utc))
    exception_type, severity = ReconciliationService._classify(payment, bank)

    assert exception_type == ExceptionType.SETTLEMENT
    assert severity == Severity.LOW


def test_priority_maps_severity_to_priority():
    assert ReconciliationService._priority(Severity.CRITICAL) == CasePriority.CRITICAL
    assert ReconciliationService._priority(Severity.LOW) == CasePriority.LOW


def test_due_date_calculates_correct_window():
    now = datetime.now(timezone.utc)
    priority = CasePriority.HIGH
    due_date = ReconciliationService._due_date(priority)

    assert due_date > now
    assert due_date <= now + timedelta(days=2)
