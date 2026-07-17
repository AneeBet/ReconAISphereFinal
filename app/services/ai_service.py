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
            case.exception.reconciliation_result
        )

        payment = reconciliation.payment_transaction

        bank = reconciliation.bank_transaction

        context = {

            "investigation_case": {

                "case_number": case.case_number,

                "title": case.title,

                "description": case.description,

                "priority": case.priority.value,

                "status": case.status.value,

                "owner": str(case.owner_id) if case.owner_id else None,

            },

            "exception": {

                "type": case.exception.exception_type.value,

                "severity": case.exception.severity.value,

                "status": case.exception.status.value,

                "detected_at": str(case.exception.detected_at),

                "resolution_notes": case.exception.resolution_notes,

            },

            "reconciliation": {

                "status": reconciliation.reconciliation_status.value,

                "match_type": reconciliation.match_type.value,

                "confidence_score": float(
                    reconciliation.confidence_score
                ),

                "matched_by": reconciliation.matched_by,

                "matched_at": str(
                    reconciliation.matched_at
                )

            },

            "payment_transaction": {

                "transaction_reference":
                    payment.transaction_reference,

                "end_to_end_id":
                    payment.end_to_end_id,

                "sender_name":
                    payment.sender_name,

                "receiver_name":
                    payment.receiver_name,

                "sender_account":
                    payment.sender_account,

                "receiver_account":
                    payment.receiver_account,

                "amount":
                    float(payment.amount),

                "currency":
                    payment.currency,

                "payment_date":
                    str(payment.payment_date),

                "settlement_date":
                    str(payment.settlement_date),

                "status":
                    payment.status.value,

                "fx_rate":
                    float(payment.fx_rate)
                    if payment.fx_rate is not None
                    else None,

                "raw":
                    payment.raw_json,

            },

            "bank_transaction":

                None if bank is None else {

                    "transaction_reference":
                        bank.transaction_reference,

                    "end_to_end_id":
                        bank.end_to_end_id,

                    "sender_name":
                        bank.sender_name,

                    "receiver_name":
                        bank.receiver_name,

                    "sender_account":
                        bank.sender_account,

                    "receiver_account":
                        bank.receiver_account,

                    "amount":
                        float(bank.amount),

                    "currency":
                        bank.currency,

                    "payment_date":
                        str(bank.payment_date),

                    "settlement_date":
                        str(bank.settlement_date),

                    "status":
                        bank.status,

                    "fx_rate":
                        float(bank.fx_rate)
                        if bank.fx_rate is not None
                        else None,

                    "raw":
                        bank.raw_json,

                },

            "comparison": {

                "payment_exists": payment is not None,

                "bank_exists": bank is not None,

                "amount_match":

                    False if bank is None else

                    float(payment.amount) == float(bank.amount),

                "currency_match":

                    False if bank is None else

                    payment.currency == bank.currency,

                "reference_match":

                    False if bank is None else

                    payment.transaction_reference ==
                    bank.transaction_reference,

                "end_to_end_match":

                    False if bank is None else

                    payment.end_to_end_id ==
                    bank.end_to_end_id,

            }

        }

        result = self.exception_agent.analyze(
            context
        )

        self.audit.log(

            user_id=case.owner_id,

            entity_type="InvestigationCase",

            entity_id=case.id,

            action="AI_EXPLAIN"

        )

        return {

            "summary": result.get(
                "business_explanation",
                ""
            ),

            "root_cause": result.get(
                "root_cause",
                ""
            ),

            "business_impact": result.get(
                "business_impact",
                ""
            ),

            "operational_domain": result.get(
                "operational_domain",
                ""
            ),

            "confidence": float(
                result.get(
                    "confidence",
                    0
                )
            ),

            "evidence": result.get(
                "evidence",
                []
            ),

            "recommended_actions": result.get(
                "recommended_actions",
                []
            )

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
    
    def chat(
        self,
        user_id: UUID,
        question: str
    ):

        history = self.repository.get_history(
            user_id
        )

        platform_context = (
            self.repository.get_copilot_context()
        )

        context = {

            "platform": platform_context,

            "recent_conversation": [

                {

                    "question": item.question,

                    "answer": item.answer

                }

                for item in history[:5]

            ]

        }

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

        self.repository.save_chat(chat)

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

