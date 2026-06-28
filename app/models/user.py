from __future__ import annotations

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

    #
    # Relationships
    #

    organization: Mapped["Organization"] = relationship(
        back_populates="users"
    )

    payment_files: Mapped[list["PaymentFile"]] = relationship(
        back_populates="uploaded_by",
        cascade="all, delete-orphan"
    )

    investigation_cases: Mapped[list["InvestigationCase"]] = relationship(
        back_populates="owner"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="user"
    )

    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="uploaded_by"
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    ai_chat_history: Mapped[list["AIChatHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    workflow_history: Mapped[list["WorkflowHistory"]] = relationship(
        back_populates="changed_by",
        cascade="all, delete-orphan"
    )

    system_settings: Mapped[list["SystemSetting"]] = relationship(
        back_populates="updated_by"
    )

    reconciliation_runs: Mapped[list["ReconciliationRun"]] = relationship(
        back_populates="initiated_by",
        cascade="all, delete-orphan"
    )