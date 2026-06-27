from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ExceptionFilterRequest(BaseModel):
    status: str | None = None
    severity: str | None = None
    exception_type: str | None = None
    assigned_to: UUID | None = None
    search: str | None = None


class ExceptionSummary(BaseModel):
    id: UUID
    exception_code: str
    exception_type: str
    severity: str
    related_reference: str
    amount: float
    currency: str
    assigned_to: str | None
    status: str
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExceptionDetailResponse(BaseModel):
    id: UUID
    reconciliation_result_id: UUID
    exception_type: str
    severity: str
    status: str
    assigned_to: str | None
    detected_at: datetime
    resolved_at: datetime | None
    resolution_notes: str | None

    model_config = ConfigDict(from_attributes=True)


class AssignExceptionRequest(BaseModel):
    user_id: UUID


class ResolveExceptionRequest(BaseModel):
    resolution_notes: str


class ExceptionWorkspaceResponse(BaseModel):
    total_records: int
    exceptions: list[ExceptionSummary]
