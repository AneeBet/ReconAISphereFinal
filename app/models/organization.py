from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class Organization(Base, BaseEntity):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    users = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan"
    )

    banks = relationship(
        "Bank",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
