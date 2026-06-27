from app.schemas.exception import (
    ExceptionSummary,
    ExceptionDetailResponse
)


class ExceptionMapper:

    @staticmethod
    def to_summary(
        exception
    ):

        payment = (
            exception
            .reconciliation_result
            .payment_transaction
        )

        return ExceptionSummary(

            id=exception.id,

            exception_code=f"EX-{str(exception.id)[:8].upper()}",

            exception_type=exception.exception_type.value,

            severity=exception.severity.value,

            related_reference=
                payment.transaction_reference,

            amount=float(
                payment.amount
            ),

            currency=
                payment.currency,

            assigned_to=
                exception.assigned_to,

            status=
                exception.status.value,

            detected_at=
                exception.detected_at

        )

    @staticmethod
    def to_detail(
        exception
    ):

        return ExceptionDetailResponse(

            id=exception.id,

            reconciliation_result_id=
                exception.reconciliation_result_id,

            exception_type=
                exception.exception_type.value,

            severity=
                exception.severity.value,

            status=
                exception.status.value,

            assigned_to=
                exception.assigned_to,

            detected_at=
                exception.detected_at,

            resolved_at=
                exception.resolved_at,

            resolution_notes=
                exception.resolution_notes

        )
