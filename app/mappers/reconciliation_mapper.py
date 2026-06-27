from app.schemas.reconciliation import (
    ReconciliationItem
)


class ReconciliationMapper:

    @staticmethod
    def to_result(
        reconciliation
    ):

        payment = reconciliation.payment_transaction
        bank = reconciliation.bank_transaction

        return ReconciliationItem(

            reconciliation_id=reconciliation.id,

            payment_transaction_id=payment.id,

            bank_transaction_id=(
                bank.id
                if bank
                else None
            ),

            payment_reference=
                payment.transaction_reference,

            bank_reference=
                bank.transaction_reference
                if bank
                else None,

            payment_amount=float(
                payment.amount
            ),

            bank_amount=(
                float(bank.amount)
                if bank
                else None
            ),

            payment_currency=
                payment.currency,

            bank_currency=(
                bank.currency
                if bank
                else None
            ),

            ai_confidence=float(
                reconciliation.confidence_score
            ),

            status=
                reconciliation.reconciliation_status.value

        )
