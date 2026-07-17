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


class EvidenceItem(BaseModel):
    field: str
    payment: str
    bank: str
    result: str


class AIInsightResponse(BaseModel):
    summary: str
    root_cause: str
    business_impact: str
    operational_domain: str
    confidence: float
    evidence: list[EvidenceItem]
    recommended_actions: list[str]


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
