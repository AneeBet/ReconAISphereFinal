from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class InvestigationCaseSummary(BaseModel):
    id: UUID
    case_number: str

    transaction_reference: str   # <-- ADD THIS

    title: str
    priority: str
    owner: str | None
    status: str
    due_date: datetime | None

    model_config = ConfigDict(from_attributes=True)


class InvestigationOverview(BaseModel):
    id: UUID
    case_number: str
    transaction_reference: str
    title: str
    description: str | None
    priority: str
    owner: str | None
    status: str
    due_date: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimelineItem(BaseModel):
    changed_at: datetime
    changed_by: str
    from_status: str | None
    to_status: str
    remarks: str | None


class RelatedTransaction(BaseModel):
    payment_reference: str
    bank_reference: str | None
    payment_amount: float
    bank_amount: float | None
    difference: float | None


class CaseComment(BaseModel):
    id: UUID
    user: str
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddCommentRequest(BaseModel):
    comment: str


class CaseAttachment(BaseModel):
    id: UUID
    file_name: str
    blob_url: str
    uploaded_by: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddAttachmentRequest(BaseModel):
    file_name: str
    blob_url: str


class UpdateCaseStatusRequest(BaseModel):
    status: str


class InvestigationCaseResponse(BaseModel):
    overview: InvestigationOverview
    ai_explanation: str | None
    ai_recommendation: str | None
    confidence_score: float | None
    related_transactions: list[RelatedTransaction]
    timeline: list[TimelineItem]
    comments: list[CaseComment]
    attachments: list[CaseAttachment]


class InvestigationWorkspaceResponse(BaseModel):
    total_records: int
    cases: list[InvestigationCaseSummary]
