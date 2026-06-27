from app.repositories.dashboard_repository import (
    DashboardRepository
)


class DashboardService:

    def __init__(
        self,
        repository: DashboardRepository
    ):

        self.repository = repository

    def summary(
        self
    ):

        return self.repository.summary()

    def recent_runs(
        self
    ):

        return self.repository.recent_runs()

    def bank_summary(
        self
    ):

        return self.repository.banks()

    def exception_chart(
        self
    ):

        return self.repository.exception_chart()
