from app.schemas.dashboard import (
    DashboardSummaryResponse,
    ExceptionBreakdown,
    RecentRun
)


class DashboardMapper:

    @staticmethod
    def to_summary(
        total_transactions: int,
        matched_transactions: int,
        exceptions: int,
        open_cases: int,
        ai_confidence: float
    ) -> DashboardSummaryResponse:

        return DashboardSummaryResponse(
            total_transactions=total_transactions,
            matched_transactions=matched_transactions,
            exceptions=exceptions,
            open_cases=open_cases,
            ai_confidence=ai_confidence
        )

    @staticmethod
    def to_recent_run(
        run
    ) -> RecentRun:

        return RecentRun(
            id=run.id,
            run_number=f"RUN-{str(run.id)[:8].upper()}",
            initiated_by=f"{run.initiated_by.first_name} {run.initiated_by.last_name}",
            started_at=run.started_at,
            total=run.total_transactions,
            matched=run.matched,
            unmatched=run.unmatched,
            exceptions=run.exceptions,
            status=run.status.value
        )

    @staticmethod
    def to_exception_breakdown(
        row
    ) -> ExceptionBreakdown:

        return ExceptionBreakdown(
            exception_type=row[0].value,
            count=row[1]
        )

    @staticmethod
    def to_bank_summary(
        bank
    ) -> dict:

        return {
            "bank_id": bank.id,
            "bank_name": bank.bank_name,
            "country": bank.country,
            "currency": bank.currency,
            "active": bank.is_active
        }
