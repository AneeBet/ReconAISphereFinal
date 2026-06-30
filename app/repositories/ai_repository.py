from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.ai_chat_history import AIChatHistory
from app.models.exception import Exception
from app.models.investigation_case import InvestigationCase
from app.models.reconciliation_result import ReconciliationResult


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

        return self.db.scalar(
            statement
        )
