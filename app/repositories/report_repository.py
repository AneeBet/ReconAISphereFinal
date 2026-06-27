from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment_transaction import PaymentTransaction
from app.models.reconciliation_result import ReconciliationResult
from app.models.exception import Exception
from app.models.bank import Bank


class ReportRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def dashboard_metrics(
        self
    ):

        return {

            "transactions":
            self.db.scalar(
                select(func.count(PaymentTransaction.id))
            ) or 0,

            "matched":
            self.db.scalar(
                select(func.count(ReconciliationResult.id))
            ) or 0,

            "exceptions":
            self.db.scalar(
                select(func.count(Exception.id))
            ) or 0

        }

    def bank_summary(
        self
    ):

        return list(

            self.db.scalars(

                select(Bank)

            ).all()

        )
