from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CaseStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class InvestigationCase(Base, BaseEntity):
    __tablename__ = "investigation_cases"

    exception_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exceptions.id"),
        nullable=False,
        unique=True,
        index=True
    )

    case_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    priority: Mapped[CasePriority] = mapped_column(
        SqlEnum(CasePriority),
        nullable=False
    )

    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id")
    )

    status: Mapped[CaseStatus] = mapped_column(
        SqlEnum(CaseStatus),
        default=CaseStatus.OPEN,
        nullable=False
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    exception = relationship(
        "Exception",
        back_populates="investigation_case"
    )

    owner = relationship(
        "User",
        back_populates="investigation_cases"
    )

    ai_insights = relationship(
        "AIInsight",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    comments = relationship(
        "Comment",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    attachments = relationship(
        "Attachment",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    workflow_history = relationship(
        "WorkflowHistory",
        back_populates="case",
        cascade="all, delete-orphan"
    )
