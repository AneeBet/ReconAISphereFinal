from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base
from app.db.base import BaseEntity


class LegStage(str, Enum):
    SUBMITTED = "SUBMITTED"
    AML = "AML"
    FX = "FX"
    CORRESPONDENT = "CORRESPONDENT"
    SETTLEMENT = "SETTLEMENT"
    BENEFICIARY = "BENEFICIARY"


class LegStatus(str, Enum):
    PASS = "PASS"
    HOLD = "HOLD"
    FAIL = "FAIL"
    PENDING = "PENDING"


class TransactionLeg(Base, BaseEntity):
    __tablename__ = "transaction_legs"

    end_to_end_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    stage: Mapped[LegStage] = mapped_column(
        SqlEnum(LegStage),
        nullable=False
    )

    status: Mapped[LegStatus] = mapped_column(
        SqlEnum(LegStatus),
        default=LegStatus.PASS,
        nullable=False
    )

    detail: Mapped[str | None] = mapped_column(
        Text
    )

    event_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )