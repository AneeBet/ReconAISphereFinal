from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bank import Bank
from app.models.exception import Exception
from app.models.payment_transaction import PaymentTransaction
from app.models.reconciliation_run import ReconciliationRun


class DashboardRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def summary(
        self
    ):

        return {

            "total_transactions":

                self.db.scalar(

                    select(

                        func.count(
                            PaymentTransaction.id
                        )

                    )

                ) or 0,

            "exceptions":

                self.db.scalar(

                    select(

                        func.count(
                            Exception.id
                        )

                    )

                ) or 0,

            "banks":

                self.db.scalar(

                    select(

                        func.count(
                            Bank.id
                        )

                    )

                ) or 0,

            "runs":

                self.db.scalar(

                    select(

                        func.count(
                            ReconciliationRun.id
                        )

                    )

                ) or 0

        }

    def recent_runs(
        self
    ):

        return list(

            self.db.scalars(

                select(
                    ReconciliationRun
                )

                .order_by(

                    ReconciliationRun.started_at.desc()

                )

                .limit(10)

            ).all()

        )

    def banks(
        self
    ):

        return list(

            self.db.scalars(

                select(Bank)

            ).all()

        )

    def exception_chart(
        self
    ):

        return {

            "critical":

                self.db.scalar(

                    select(

                        func.count(
                            Exception.id
                        )

                    )

                    .where(

                        Exception.severity == "CRITICAL"

                    )

                ) or 0,

            "high":

                self.db.scalar(

                    select(

                        func.count(
                            Exception.id
                        )

                    )

                    .where(

                        Exception.severity == "HIGH"

                    )

                ) or 0,

            "medium":

                self.db.scalar(

                    select(

                        func.count(
                            Exception.id
                        )

                    )

                    .where(

                        Exception.severity == "MEDIUM"

                    )

                ) or 0,

            "low":

                self.db.scalar(

                    select(

                        func.count(
                            Exception.id
                        )

                    )

                    .where(

                        Exception.severity == "LOW"

                    )

                ) or 0

        }
