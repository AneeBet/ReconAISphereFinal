from datetime import UTC, datetime

from app.repositories.report_repository import (
    ReportRepository,
)

from app.schemas.report import (
    DashboardReport,
    ReportResponse,
)


class ReportService:

    def __init__(
        self,
        repository: ReportRepository
    ):
        self.repository = repository

    def dashboard_report(
        self
    ):

        metrics = self.repository.dashboard_metrics()

        matched = metrics["matched"]

        total = metrics["transactions"]

        exceptions = metrics["exceptions"]

        unmatched = max(
            total - matched,
            0
        )

        return DashboardReport(

            total_transactions=total,

            matched=matched,

            unmatched=unmatched,

            exceptions=exceptions

        )

    def export(
        self,
        report_type: str
    ):

        report_name = f"{report_type.lower()}.pdf"

        return ReportResponse(

            report_name=report_name,

            report_url=f"/reports/download/{report_name}",

            generated_at=datetime.now(UTC)

        )
