from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class DashboardSummaryResponse(BaseModel):
    total_transactions: int
    exceptions: int
    banks: int
    runs: int


class RecentRunResponse(BaseModel):
    id: UUID
    started_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class BankSummaryResponse(BaseModel):
    id: UUID
    bank_name: str

    model_config = ConfigDict(from_attributes=True)


class ExceptionChartResponse(BaseModel):
    critical: int
    high: int
    medium: int
    low: int
