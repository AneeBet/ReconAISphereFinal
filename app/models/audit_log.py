import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class AuditLog(Base, BaseEntity):
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    entity_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    old_value: Mapped[dict | None] = mapped_column(
        JSON
    )

    new_value: Mapped[dict | None] = mapped_column(
        JSON
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45)
    )

    user = relationship(
        "User",
        back_populates="audit_logs"
    )
