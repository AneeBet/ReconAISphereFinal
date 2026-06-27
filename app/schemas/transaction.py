from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class TransactionFilterRequest(BaseModel):
    bank_id: UUID | None = None
    currency: str | None = None
    status: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    search: str | None = None


class TransactionSummary(BaseModel):
    id: UUID
    transaction_reference: str
    end_to_end_id: str
    bank: str
    payment_date: datetime
    amount: float
    currency: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class TransactionDetailResponse(BaseModel):
    id: UUID
    transaction_reference: str
    end_to_end_id: str
    sender_name: str
    receiver_name: str
    sender_account: str
    receiver_account: str
    amount: float
    currency: str
    payment_date: datetime
    settlement_date: datetime | None
    payment_type: str
    status: str
    raw_json: dict | None

    model_config = ConfigDict(from_attributes=True)


class TransactionExplorerResponse(BaseModel):
    total_records: int
    transactions: list[TransactionSummary]
