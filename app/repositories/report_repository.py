from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.bank import Bank
from app.models.exception import Exception
from app.models.payment_transaction import (
    PaymentTransaction,
    PaymentStatus,
)
from app.models.reconciliation_result import ReconciliationResult


class ReportRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def dashboard_metrics(
        self
    ):

        total = self.db.scalar(
            select(func.count(PaymentTransaction.id))
        ) or 0

        matched = self.db.scalar(
            select(func.count(PaymentTransaction.id))
            .where(
                PaymentTransaction.status == PaymentStatus.SUCCESS
            )
        ) or 0

        exceptions = self.db.scalar(
            select(func.count(PaymentTransaction.id))
            .where(
                PaymentTransaction.status == PaymentStatus.FAILED
            )
        ) or 0

        pending = self.db.scalar(
            select(func.count(PaymentTransaction.id))
            .where(
                PaymentTransaction.status == PaymentStatus.PENDING
            )
        ) or 0

        return {
            "transactions": total,
            "matched": matched,
            "exceptions": exceptions,
            "pending": pending,
        }

    def bank_summary(
        self
    ):

        return list(

            self.db.scalars(

                select(Bank)

            ).all()

        )

    def reconciliation_rows(self):

        return list(

            self.db.scalars(

                select(ReconciliationResult).options(

                    selectinload(
                        ReconciliationResult.payment_transaction
                    ),

                    selectinload(
                        ReconciliationResult.bank_transaction
                    ),

                )

            ).all()

        )

    def exception_rows(self):

        return list(

            self.db.scalars(

                select(Exception).options(

                    selectinload(
                        Exception.reconciliation_result
                    ).selectinload(
                        ReconciliationResult.payment_transaction
                    )

                )

            ).all()

        )

    def transaction_rows(self):

        return list(

            self.db.scalars(

                select(PaymentTransaction)

            ).all()

        )