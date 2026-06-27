from uuid import UUID

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.agents.copilot.factory import (
    CopilotAgentFactory,
)

from app.agents.exception.factory import (
    ExceptionAnalysisAgentFactory,
)

from app.agents.recommendation.factory import (
    RecommendationAgentFactory,
)

from app.models.ai_chat_history import (
    AIChatHistory,
)

from app.repositories.ai_repository import (
    AIRepository,
)

from app.repositories.audit_repository import (
    AuditRepository,
)

from app.services.audit_service import (
    AuditService,
)


class AIService:

    def __init__(
        self,
        repository: AIRepository
    ):

        self.repository = repository

        self.copilot = CopilotAgentFactory.create()

        self.exception_agent = (
            ExceptionAnalysisAgentFactory.create()
        )

        self.recommendation_agent = (
            RecommendationAgentFactory.create()
        )

        self.audit = AuditService(
            AuditRepository(
                repository.db
            )
        )

    def chat(
        self,
        user_id: UUID,
        question: str
    ):

        history = self.repository.get_history(
            user_id
        )

        context = "\n".join(
            h.question
            for h in history[:5]
        )

        answer = self.copilot.chat(
            question,
            context
        )

        chat = AIChatHistory(
            user_id=user_id,
            question=question,
            answer=answer,
            tokens=0,
        )

        self.repository.save_chat(
            chat
        )

        self.audit.log(

            user_id=user_id,

            entity_type="AI",

            entity_id=chat.id,

            action="CHAT"

        )

        conversation = [

            {
                "role": "user",
                "message": h.question,
                "created_at": h.created_at,
            }

            for h in reversed(history[:10])

        ]

        conversation.append(

            {
                "role": "assistant",
                "message": answer,
                "created_at": chat.created_at,
            }

        )

        return {

            "answer": answer,

            "tokens_used": 0,

            "conversation": conversation,

        }

    def history(
        self,
        user_id: UUID
    ):

        history = self.repository.get_history(
            user_id
        )

        return {

            "history": [

                {
                    "id": item.id,
                    "question": item.question,
                    "created_at": item.created_at,
                }

                for item in history

            ]

        }

    def explain(
        self,
        case_id: UUID
    ):

        case = self.repository.get_case(
            case_id
        )

        if case is None:

            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Investigation case not found."
            )

        reconciliation = (
            case.exception
            .reconciliation_result
        )

        result = self.exception_agent.analyze(

            reconciliation,

            reconciliation.payment_transaction,

            reconciliation.bank_transaction

        )

        self.audit.log(

            user_id=case.owner_id,

            entity_type="InvestigationCase",

            entity_id=case.id,

            action="AI_EXPLAIN"

        )

        return {

            "explanation": result.get(
                "business_explanation",
                ""
            ),

            "recommendation": result.get(
                "root_cause",
                ""
            ),

            "confidence": float(
                result.get(
                    "confidence",
                    0
                )
            ),

        }

    def recommend(
        self,
        case_id: UUID
    ):

        case = self.repository.get_case(
            case_id
        )

        if case is None:

            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Investigation case not found."
            )

        result = self.recommendation_agent.recommend(
            case
        )

        self.audit.log(

            user_id=case.owner_id,

            entity_type="InvestigationCase",

            entity_id=case.id,

            action="AI_RECOMMEND"

        )

        return {

            "explanation": result.get(
                "assigned_team",
                ""
            ),

            "recommendation": result.get(
                "recommendation",
                ""
            ),

            "confidence": 100.0,

        }

