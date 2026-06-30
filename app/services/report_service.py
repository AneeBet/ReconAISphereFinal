import csv
import io
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.repositories.report_repository import (
    ReportRepository,
)

from app.schemas.report import (
    DashboardReport,
    ReportResponse,
)

from app.storage.azure_blob_storage import (
    AzureBlobStorage,
)


class ReportService:

    def __init__(
        self,
        repository: ReportRepository
    ):
        self.repository = repository
        self.storage = AzureBlobStorage()

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

        report_type = (report_type or "RECONCILIATION").upper()

        headers, rows = self._build_dataset(report_type)

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(headers)
        writer.writerows(rows)

        report_name = (
            f"{report_type.lower()}_"
            f"{datetime.now(UTC):%Y%m%d}_{uuid.uuid4().hex[:8]}.csv"
        )

        self.storage.upload(
            f"reports/{report_name}",
            buffer.getvalue().encode("utf-8")
        )

        return ReportResponse(
            report_name=report_name,
            report_url=f"/reports/download/{report_name}",
            generated_at=datetime.now(UTC)
        )

    def download(
        self,
        report_name: str
    ):

        try:
            return self.storage.download(f"reports/{report_name}")
        except Exception:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Report not found."
            )

    def _build_dataset(self, report_type):

        if report_type == "EXCEPTIONS":
            headers = ["exception_type", "severity", "status", "reference"]
            rows = [
                [
                    e.exception_type.value,
                    e.severity.value,
                    e.status.value,
                    e.reconciliation_result.payment_transaction
                    .transaction_reference,
                ]
                for e in self.repository.exception_rows()
            ]
            return headers, rows

        if report_type == "TRANSACTIONS":
            headers = ["reference", "amount", "currency", "status"]
            rows = [
                [t.transaction_reference, float(t.amount), t.currency,
                 t.status.value]
                for t in self.repository.transaction_rows()
            ]
            return headers, rows

        headers = ["payment_ref", "bank_ref", "match_type", "confidence",
                   "status"]
        rows = [
            [
                r.payment_transaction.transaction_reference,
                r.bank_transaction.transaction_reference
                if r.bank_transaction else "",
                r.match_type.value,
                float(r.confidence_score),
                r.reconciliation_status.value,
            ]
            for r in self.repository.reconciliation_rows()
        ]
        return headers, rows