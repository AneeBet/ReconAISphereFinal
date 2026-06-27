import uuid

from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class Bank(Base, BaseEntity):
    __tablename__ = "banks"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )

    bank_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    bic_swift: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    api_endpoint: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    organization = relationship(
        "Organization",
        back_populates="banks"
    )

    payment_files = relationship(
        "PaymentFile",
        back_populates="bank",
        cascade="all, delete-orphan"
    )

    payment_transactions = relationship(
        "PaymentTransaction",
        back_populates="bank"
    )

    bank_transactions = relationship(
        "BankTransaction",
        back_populates="bank"
    )
