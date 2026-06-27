from app.schemas.ai import (
    AIChatResponse,
    AIChatMessage,
    AIInsightResponse,
    ConversationHistoryItem
)


class AIMapper:

    @staticmethod
    def to_chat_response(
        answer,
        tokens
    ):

        return AIChatResponse(

            answer=answer,

            tokens_used=tokens,

            conversation=[]

        )

    @staticmethod
    def to_history_item(
        chat
    ):

        return ConversationHistoryItem(

            id=chat.id,

            question=chat.question,

            created_at=chat.created_at

        )

    @staticmethod
    def to_message(
        role,
        message,
        created_at
    ):

        return AIChatMessage(

            role=role,

            message=message,

            created_at=created_at

        )

    @staticmethod
    def to_insight(
        insight
    ):

        return AIInsightResponse(

            explanation=insight.explanation,

            recommendation=insight.recommendation,

            confidence=float(
                insight.confidence
            )

        )
