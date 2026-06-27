from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class PaymentFileResponse(BaseModel):
    id: UUID
    bank_id: UUID
    file_name: str
    original_name: str
    blob_url: str
    file_type: str
    processing_status: str
    total_records: int
    valid_records: int
    invalid_records: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
