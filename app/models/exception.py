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


class ExceptionType(str, Enum):
    DUPLICATE = "DUPLICATE"
    FX = "FX"
    MISSING = "MISSING"
    AMOUNT = "AMOUNT"
    DATE = "DATE"
    SETTLEMENT = "SETTLEMENT"
    REFERENCE = "REFERENCE"
    MANUAL = "MANUAL"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExceptionStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Exception(Base, BaseEntity):
    __tablename__ = "exceptions"

    reconciliation_result_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reconciliation_results.id"),
        nullable=False,
        unique=True,
        index=True
    )

    exception_type: Mapped[ExceptionType] = mapped_column(
        SqlEnum(ExceptionType),
        nullable=False
    )

    severity: Mapped[Severity] = mapped_column(
        SqlEnum(Severity),
        nullable=False
    )

    status: Mapped[ExceptionStatus] = mapped_column(
        SqlEnum(ExceptionStatus),
        default=ExceptionStatus.OPEN,
        nullable=False
    )

    assigned_to: Mapped[str | None] = mapped_column(
        String(255)
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    resolution_notes: Mapped[str | None] = mapped_column(
        Text
    )

    reconciliation_result = relationship(
        "ReconciliationResult",
        back_populates="exception"
    )

    investigation_case = relationship(
        "InvestigationCase",
        back_populates="exception",
        uselist=False,
        cascade="all, delete-orphan"
    )
