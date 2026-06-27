from pydantic import BaseModel


class GeneralSettingsResponse(BaseModel):
    organization_name: str
    default_currency: str
    timezone: str
    date_format: str


class AISettingsResponse(BaseModel):
    matching_confidence_threshold: float
    amount_tolerance: float
    date_tolerance_days: int
    exchange_rate_source: str


class NotificationSettingsResponse(BaseModel):
    email_notifications: bool
    system_notifications: bool


class IntegrationSettingsResponse(BaseModel):
    bank_api_enabled: bool
    blob_storage_enabled: bool
    azure_openai_enabled: bool


class UpdateGeneralSettingsRequest(BaseModel):
    organization_name: str
    default_currency: str
    timezone: str
    date_format: str


class UpdateAISettingsRequest(BaseModel):
    matching_confidence_threshold: float
    amount_tolerance: float
    date_tolerance_days: int
    exchange_rate_source: str
