from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Numeric
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base
from app.db.base import BaseEntity


class ExchangeRate(Base, BaseEntity):
    __tablename__ = "exchange_rates"

    base_currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True
    )

    target_currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True
    )

    rate: Mapped[float] = mapped_column(
        Numeric(18, 6),
        nullable=False
    )

    effective_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
