import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class SystemSetting(Base, BaseEntity):
    __tablename__ = "system_settings"

    setting_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    setting_value: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    updated_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    updated_by = relationship(
        "User",
        back_populates="system_settings"
    )
