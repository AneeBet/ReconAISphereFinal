from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr


class UserSummary(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserDropdown(BaseModel):
    id: UUID
    full_name: str

    model_config = ConfigDict(from_attributes=True)
