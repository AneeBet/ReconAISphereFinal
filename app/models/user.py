from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPS = "OPS"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"


class User(Base, BaseEntity):
    __tablename__ = "users"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    organization = relationship(
        "Organization",
        back_populates="users"
    )

    payment_files = relationship(
        "PaymentFile",
        back_populates="uploaded_by"
    )

    investigation_cases = relationship(
        "InvestigationCase",
        back_populates="owner"
    )

    comments = relationship(
        "Comment",
        back_populates="user"
    )

    attachments = relationship(
        "Attachment",
        back_populates="uploaded_by"
    )

    notifications = relationship(
        "Notification",
        back_populates="user"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )

    ai_chat_history = relationship(
        "AIChatHistory",
        back_populates="user"
    )

    workflow_history = relationship(
        "WorkflowHistory",
        back_populates="changed_by"
    )

    system_settings = relationship(
        "SystemSetting",
        back_populates="updated_by"
    )

    reconciliation_runs = relationship(
        "ReconciliationRun",
        back_populates="initiated_by"
    )
