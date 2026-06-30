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

    def get_pending_payment_transactions(
        self
    ):

        return list(
            self.db.scalars(
                select(PaymentTransaction)
                .where(PaymentTransaction.reconciled == False)  # noqa: E712
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

    def get_all_bank_transactions(
        self
    ):

        return list(

            self.db.scalars(

                select(BankTransaction)

            ).all()

        )

    def get_failed_leg(self, end_to_end_id):
        from app.models.transaction_leg import TransactionLeg, LegStatus
        stage_order = ["SUBMITTED", "AML", "FX", "CORRESPONDENT",
                       "SETTLEMENT", "BENEFICIARY"]
        legs = list(self.db.scalars(
            select(TransactionLeg)
            .where(TransactionLeg.end_to_end_id == end_to_end_id)
        ).all())
        failed = [
            l for l in legs
            if l.status in (LegStatus.FAIL, LegStatus.HOLD)
        ]
        if not failed:
            return None
        return sorted(
            failed,
            key=lambda l: stage_order.index(l.stage.value)
            if l.stage.value in stage_order else 99
        )[0]

    def mark_reconciled(self, payments, banks):
        for p in payments:
            p.reconciled = True
        for b in banks:
            if b is not None:
                b.reconciled = True
        self.db.commit()

    def save_results(
        self,
        results: list[ReconciliationResult]
    ):

        self.db.add_all(results)
        self.db.commit()

    def save_exceptions(
        self,
        exceptions: list
    ):

        if not exceptions:
            return

        self.db.add_all(exceptions)
        self.db.commit()

    def save_cases(
        self,
        cases: list
    ):

        if not cases:
            return

        self.db.add_all(cases)
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