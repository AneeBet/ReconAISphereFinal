from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.bank_transaction import BankTransaction
from app.models.payment_transaction import PaymentTransaction
from app.models.reconciliation_result import ReconciliationResult
from app.models.reconciliation_run import ReconciliationRun


class ReconciliationRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create_run(
        self,
        run: ReconciliationRun
    ):

        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        return run

    def update_run(
        self,
        run: ReconciliationRun
    ):

        self.db.commit()
        self.db.refresh(run)

        return run

    def get_payment_transactions(
        self,
        payment_file_id: UUID
    ):

        return list(

            self.db.scalars(

                select(PaymentTransaction)

                .where(
                    PaymentTransaction.payment_file_id == payment_file_id
                )

            ).all()

        )

    def get_bank_transactions(
        self,
        bank_id: UUID
    ):

        return list(

            self.db.scalars(

                select(BankTransaction)

                .where(
                    BankTransaction.bank_id == bank_id
                )

            ).all()

        )

    def save_results(
        self,
        results: list[ReconciliationResult]
    ):

        self.db.add_all(results)
        self.db.commit()

    def get_results(
        self
    ):

        return list(

            self.db.scalars(

                select(ReconciliationResult)

                .options(
                    selectinload(
                        ReconciliationResult.payment_transaction
                    ),
                    selectinload(
                        ReconciliationResult.bank_transaction
                    )
                )

            ).all()

        )
