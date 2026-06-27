from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class AuditFilterRequest(BaseModel):
    user: str | None = None
    action: str | None = None
    entity: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class AuditLogItem(BaseModel):
    timestamp: datetime
    user: str
    action: str
    entity: str
    entity_id: str
    ip_address: str | None
    details: str | None

    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(BaseModel):
    total_records: int
    logs: list[AuditLogItem]
