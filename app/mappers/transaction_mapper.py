from app.schemas.transaction import (
    TransactionSummary,
    TransactionDetailResponse
)


class TransactionMapper:

    @staticmethod
    def to_summary(
        transaction
    ) -> TransactionSummary:

        return TransactionSummary(

            id=transaction.id,

            transaction_reference=transaction.transaction_reference,

            end_to_end_id=transaction.end_to_end_id,

            bank=transaction.bank.bank_name,

            payment_date=transaction.payment_date,

            amount=float(
                transaction.amount
            ),

            currency=transaction.currency,

            status=transaction.status.value

        )

    @staticmethod
    def to_detail(
        transaction
    ) -> TransactionDetailResponse:

        return TransactionDetailResponse(

            id=transaction.id,

            transaction_reference=transaction.transaction_reference,

            end_to_end_id=transaction.end_to_end_id,

            sender_name=transaction.sender_name,

            receiver_name=transaction.receiver_name,

            sender_account=transaction.sender_account,

            receiver_account=transaction.receiver_account,

            amount=float(
                transaction.amount
            ),

            currency=transaction.currency,

            payment_date=transaction.payment_date,

            settlement_date=transaction.settlement_date,

            payment_type=transaction.payment_type,

            status=transaction.status.value,

            raw_json=transaction.raw_json

        )
