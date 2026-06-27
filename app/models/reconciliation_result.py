from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class MatchType(str, Enum):
    EXACT = "EXACT"
    PARTIAL = "PARTIAL"
    AI = "AI"
    MANUAL = "MANUAL"


class ReconciliationStatus(str, Enum):
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"
    EXCEPTION = "EXCEPTION"


class ReconciliationResult(Base, BaseEntity):
    __tablename__ = "reconciliation_results"

    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reconciliation_runs.id"),
        nullable=False,
        index=True
    )

    payment_transaction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("payment_transactions.id"),
        nullable=False,
        index=True
    )

    bank_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("bank_transactions.id")
    )

    match_type: Mapped[MatchType] = mapped_column(
        SqlEnum(MatchType),
        nullable=False
    )

    confidence_score: Mapped[float] = mapped_column(
        Numeric(5,2),
        default=0
    )

    matched_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    matched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    reconciliation_status: Mapped[ReconciliationStatus] = mapped_column(
        SqlEnum(ReconciliationStatus),
        nullable=False
    )

    run = relationship(
        "ReconciliationRun",
        back_populates="reconciliation_results"
    )

    payment_transaction = relationship(
        "PaymentTransaction",
        back_populates="reconciliation_results"
    )

    bank_transaction = relationship(
        "BankTransaction",
        back_populates="reconciliation_results"
    )

    exception = relationship(
        "Exception",
        back_populates="reconciliation_result",
        uselist=False,
        cascade="all, delete-orphan"
    )
