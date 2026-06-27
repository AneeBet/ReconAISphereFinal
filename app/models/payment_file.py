from enum import Enum
import uuid

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class ProcessingStatus(str, Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PaymentFile(Base, BaseEntity):
    __tablename__ = "payment_files"

    bank_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("banks.id"),
        nullable=False,
        index=True
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    original_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    blob_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    checksum: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True
    )

    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SqlEnum(ProcessingStatus),
        default=ProcessingStatus.UPLOADED,
        nullable=False
    )

    total_records: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    valid_records: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    invalid_records: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    bank = relationship(
        "Bank",
        back_populates="payment_files"
    )

    uploaded_by = relationship(
        "User",
        back_populates="payment_files"
    )

    payment_transactions = relationship(
        "PaymentTransaction",
        back_populates="payment_file",
        cascade="all, delete-orphan"
    )
