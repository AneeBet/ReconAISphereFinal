from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import Numeric
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PaymentTransaction(Base, BaseEntity):
    __tablename__ = "payment_transactions"

    payment_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("payment_files.id"),
        nullable=False,
        index=True
    )

    bank_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("banks.id"),
        nullable=False,
        index=True
    )

    transaction_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    end_to_end_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    sender_account: Mapped[str] = mapped_column(
        String(100)
    )

    receiver_account: Mapped[str] = mapped_column(
        String(100)
    )

    sender_name: Mapped[str] = mapped_column(
        String(255)
    )

    receiver_name: Mapped[str] = mapped_column(
        String(255)
    )

    amount: Mapped[float] = mapped_column(
        Numeric(18,2),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    fx_rate: Mapped[float | None] = mapped_column(
        Numeric(18,6)
    )

    payment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    settlement_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    payment_type: Mapped[str] = mapped_column(
        String(50)
    )

    status: Mapped[PaymentStatus] = mapped_column(
        SqlEnum(PaymentStatus),
        default=PaymentStatus.PENDING
    )

    raw_json: Mapped[dict | None] = mapped_column(
        JSON
    )

    payment_file = relationship(
        "PaymentFile",
        back_populates="payment_transactions"
    )

    bank = relationship(
        "Bank",
        back_populates="payment_transactions"
    )

    reconciliation_results = relationship(
        "ReconciliationResult",
        back_populates="payment_transaction"
    )
