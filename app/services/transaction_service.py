from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.mappers.transaction_mapper import (
    TransactionMapper
)

from app.repositories.transaction_repository import (
    TransactionRepository
)


class TransactionService:

    def __init__(
        self,
        repository: TransactionRepository
    ):
        self.repository = repository

    def get_transactions(
        self
    ):

        transactions = self.repository.get_transactions()

        return [

            TransactionMapper.to_summary(
                transaction
            )

            for transaction in transactions

        ]

    def get_transaction(
        self,
        transaction_id
    ):

        transaction = self.repository.get_transaction(
            transaction_id
        )

        if transaction is None:

            raise HTTPException(

                status_code=HTTP_404_NOT_FOUND,

                detail="Transaction not found."

            )

        return TransactionMapper.to_detail(
            transaction
        )
