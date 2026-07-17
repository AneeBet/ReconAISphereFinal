from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MatchInformation(BaseModel):
    match_type: str
    confidence: float
    matched_by: str
    matched_at: datetime
    status: str


class ReconciliationItem(BaseModel):
    reconciliation_id: UUID
    payment_transaction_id: UUID
    bank_transaction_id: UUID | None

    payment_reference: str
    bank_reference: str | None

    payment_amount: float
    bank_amount: float | None

    payment_currency: str
    bank_currency: str | None

    ai_confidence: float
    status: str


class ReconciliationWorkspaceResponse(BaseModel):
    total: int
    matched: int
    unmatched: int
    exceptions: int
    results: list[ReconciliationItem]