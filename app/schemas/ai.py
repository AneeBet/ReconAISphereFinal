from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AIQuestionRequest(BaseModel):
    question: str
    case_id: UUID | None = None


class SuggestedPrompt(BaseModel):
    title: str


class AIChatMessage(BaseModel):
    role: str
    message: str
    created_at: datetime


class AIInsightResponse(BaseModel):
    explanation: str
    recommendation: str
    confidence: float


class AIChatResponse(BaseModel):
    answer: str
    tokens_used: int
    conversation: list[AIChatMessage]


class ConversationHistoryItem(BaseModel):
    id: UUID
    question: str
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    history: list[ConversationHistoryItem]
