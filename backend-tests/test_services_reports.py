import pytest
from types import SimpleNamespace
from app.services.report_service import ReportService


def test_dashboard_report_builds_summary(monkeypatch):
    repository = SimpleNamespace(dashboard_metrics=lambda: {"transactions": 10, "matched": 7, "exceptions": 1, "pending": 2})
    service = ReportService(repository)
    service.storage = SimpleNamespace(upload=lambda path, data: f"/reports/{path}")

    report = service.dashboard_report()

    assert report.total_transactions == 10
    assert report.matched == 7
    assert report.unmatched == 2
    assert report.exceptions == 1


def test_export_builds_csv_and_uploads(monkeypatch):
    repository = SimpleNamespace(reconciliation_rows=lambda: [SimpleNamespace(payment_transaction=SimpleNamespace(transaction_reference="T1"), bank_transaction=SimpleNamespace(transaction_reference="B1"), match_type=SimpleNamespace(value="EXACT"), confidence_score=90, reconciliation_status=SimpleNamespace(value="MATCHED"))])
    service = ReportService(repository)
    uploaded = {}
    service.storage = SimpleNamespace(upload=lambda path, data: uploaded.setdefault(path, data))

    response = service.export("RECONCILIATION")

    assert response.report_url.startswith("/reports/download/")
    assert len(uploaded) == 1


def test_download_raises_not_found(monkeypatch):
    service = ReportService(SimpleNamespace())
    service.storage = SimpleNamespace(download=lambda path: (_ for _ in ()).throw(Exception("missing")))

    with pytest.raises(Exception):
        service.download("missing.csv")
