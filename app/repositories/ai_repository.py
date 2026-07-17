from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.ai_chat_history import AIChatHistory
from app.models.bank import Bank
from app.models.exception import Exception
from app.models.investigation_case import InvestigationCase
from app.models.payment_file import PaymentFile
from app.models.payment_transaction import PaymentTransaction
from app.models.reconciliation_result import ReconciliationResult
from app.models.reconciliation_run import ReconciliationRun


class AIRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def get_history(
        self,
        user_id: UUID
    ) -> list[AIChatHistory]:

        statement = (
            select(AIChatHistory)
            .where(
                AIChatHistory.user_id == user_id
            )
            .order_by(
                AIChatHistory.created_at.desc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )

    def save_chat(
        self,
        chat: AIChatHistory
    ) -> AIChatHistory:

        self.db.add(chat)

        self.db.commit()

        self.db.refresh(chat)

        return chat

    def get_case(
        self,
        case_id: UUID
    ) -> InvestigationCase | None:

        statement = (
            select(InvestigationCase)
            .options(
                selectinload(
                    InvestigationCase.exception
                )
                .selectinload(
                    Exception.reconciliation_result
                )
                .selectinload(
                    ReconciliationResult.payment_transaction
                ),
                selectinload(
                    InvestigationCase.exception
                )
                .selectinload(
                    Exception.reconciliation_result
                )
                .selectinload(
                    ReconciliationResult.bank_transaction
                ),
            )
            .where(
                InvestigationCase.id == case_id
            )
        )

        return self.db.scalar(statement)

    def get_copilot_context(
        self
    ):

        latest_run = self.db.scalar(
            select(
                ReconciliationRun
            )
            .order_by(
                ReconciliationRun.started_at.desc()
            )
            .limit(1)
        )

        exceptions = list(
            self.db.scalars(
                select(
                    Exception
                )
                .options(
                    selectinload(
                        Exception.reconciliation_result
                    ).selectinload(
                        ReconciliationResult.payment_transaction
                    )
                )
                .order_by(
                    Exception.detected_at.desc()
                )
                .limit(10)
            ).all()
        )

        cases = list(
            self.db.scalars(
                select(
                    InvestigationCase
                )
                .options(
                    selectinload(
                        InvestigationCase.exception
                    )
                    .selectinload(
                        Exception.reconciliation_result
                    )
                    .selectinload(
                        ReconciliationResult.payment_transaction
                    ),
                    selectinload(
                        InvestigationCase.owner
                    )
                )
                .order_by(
                    InvestigationCase.created_at.desc()
                )
                .limit(10)
            ).all()
        )

        transactions = list(
            self.db.scalars(
                select(
                    PaymentTransaction
                )
                .order_by(
                    PaymentTransaction.created_at.desc()
                )
                .limit(10)
            ).all()
        )

        uploads = list(
            self.db.scalars(
                select(
                    PaymentFile
                )
                .options(
                    selectinload(
                        PaymentFile.bank
                    )
                )
                .order_by(
                    PaymentFile.created_at.desc()
                )
                .limit(10)
            ).all()
        )

        return {

            "dashboard": {

                "recent_transactions": len(transactions),

                "recent_exceptions": len(exceptions),

                "recent_cases": len(cases)

            },

            "latest_run":

                None if latest_run is None else {

                    "status": latest_run.status.value,

                    "started_at": str(latest_run.started_at),

                    "completed_at": str(latest_run.completed_at),

                    "matched": latest_run.matched,

                    "exceptions": latest_run.exceptions,

                    "total_transactions": latest_run.total_transactions

                },

            "recent_exceptions": [

                {

                    "transaction":

                        item.reconciliation_result
                        .payment_transaction
                        .transaction_reference,

                    "end_to_end_id":

                        item.reconciliation_result
                        .payment_transaction
                        .end_to_end_id,

                    "type":

                        item.exception_type.value,

                    "severity":

                        item.severity.value,

                    "status":

                        item.status.value,

                    "detected_at":

                        str(item.detected_at)

                }

                for item in exceptions

            ],

            "recent_cases": [

                {

                    "case_number":

                        item.case_number,

                    "transaction":

                        item.exception
                        .reconciliation_result
                        .payment_transaction
                        .transaction_reference,

                    "title":

                        item.title,

                    "priority":

                        item.priority.value,

                    "status":

                        item.status.value,

                    "owner":

                        None if item.owner is None else

                        f"{item.owner.first_name} {item.owner.last_name}"

                }

                for item in cases

            ],

            "recent_transactions": [

                {

                    "transaction_reference":

                        item.transaction_reference,

                    "end_to_end_id":

                        item.end_to_end_id,

                    "amount":

                        float(item.amount),

                    "currency":

                        item.currency,

                    "status":

                        item.status.value

                }

                for item in transactions

            ],

            "recent_uploads": [

                {

                    "file_name":

                        item.original_name,

                    "file_type":

                        item.file_type,

                    "bank":

                        item.bank.bank_name,

                    "status":

                        item.processing_status.value,

                    "uploaded_at":

                        str(item.created_at),

                    "records": {

                        "total":

                            item.total_records,

                        "valid":

                            item.valid_records,

                        "invalid":

                            item.invalid_records

                    }

                }

                for item in uploads

            ]

        }