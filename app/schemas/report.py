from datetime import datetime

from pydantic import BaseModel


class ReportRequest(BaseModel):
    report_type: str
    start_date: datetime
    end_date: datetime
    format: str = "PDF"


class ReportResponse(BaseModel):
    report_name: str
    report_url: str
    generated_at: datetime


class DashboardReport(BaseModel):
    total_transactions: int
    matched: int
    unmatched: int
    exceptions: int


class ExceptionReport(BaseModel):
    total_exceptions: int
    resolved: int
    open: int


class BankPerformanceReport(BaseModel):
    bank: str
    match_rate: float
    avg_processing_time: float


class AgingReport(BaseModel):
    age_bucket: str
    total_cases: int
