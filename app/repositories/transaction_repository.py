from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.payment_transaction import PaymentTransaction


class TransactionRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def get_transactions(
        self
    ) -> list[PaymentTransaction]:

        statement = (
            select(PaymentTransaction)
            .options(
                selectinload(
                    PaymentTransaction.bank
                )
            )
            .order_by(
                PaymentTransaction.payment_date.desc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )

    def get_transaction(
        self,
        transaction_id: UUID
    ) -> PaymentTransaction | None:

        statement = (
            select(PaymentTransaction)
            .options(
                selectinload(
                    PaymentTransaction.bank
                )
            )
            .where(
                PaymentTransaction.id == transaction_id
            )
        )

        return self.db.scalar(
            statement
        )
