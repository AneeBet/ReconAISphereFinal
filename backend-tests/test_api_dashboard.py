from app.api import dashboard as dashboard_api


class FakeDashboardRepository:
    def __init__(self, db):
        self.db = db


class FakeDashboardService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def summary(self):
        self.calls.append(("summary", self.repository.db))
        return {"total_transactions": 1}

    def recent_runs(self):
        self.calls.append(("recent_runs", self.repository.db))
        return ["run"]

    def bank_summary(self):
        self.calls.append(("bank_summary", self.repository.db))
        return ["bank"]

    def exception_chart(self):
        self.calls.append(("exception_chart", self.repository.db))
        return {"high": 1}


def test_dashboard_api_endpoints_delegate_to_service(monkeypatch):
    monkeypatch.setattr(dashboard_api, "DashboardRepository", FakeDashboardRepository)
    monkeypatch.setattr(dashboard_api, "DashboardService", FakeDashboardService)
    FakeDashboardService.calls = []

    db = object()
    user = object()

    assert dashboard_api.summary(current_user=user, db=db) == {"total_transactions": 1}
    assert dashboard_api.reconciliation_runs(current_user=user, db=db) == ["run"]
    assert dashboard_api.bank_summary(current_user=user, db=db) == ["bank"]
    assert dashboard_api.exception_chart(current_user=user, db=db) == {"high": 1}

    assert FakeDashboardService.calls == [
        ("summary", db),
        ("recent_runs", db),
        ("bank_summary", db),
        ("exception_chart", db),
    ]
