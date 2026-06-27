from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class ReconciliationRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReconciliationRun(Base, BaseEntity):
    __tablename__ = "reconciliation_runs"

    initiated_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    status: Mapped[ReconciliationRunStatus] = mapped_column(
        SqlEnum(ReconciliationRunStatus),
        default=ReconciliationRunStatus.PENDING,
        nullable=False
    )

    total_transactions: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    matched: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    unmatched: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    exceptions: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    ai_processed: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    initiated_by = relationship(
        "User",
        back_populates="reconciliation_runs"
    )

    reconciliation_results = relationship(
        "ReconciliationResult",
        back_populates="run",
        cascade="all, delete-orphan"
    )
