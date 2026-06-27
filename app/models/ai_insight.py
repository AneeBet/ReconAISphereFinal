from decimal import Decimal
from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class AIModel(str, Enum):

    GPT4 = "GPT-4.1"

    GPT41_MINI = "GPT-4.1-mini"


class AIInsight(
    Base,
    BaseEntity
):

    __tablename__ = "ai_insights"

    case_id: Mapped[str] = mapped_column(
        ForeignKey(
            "investigation_cases.id"
        ),
        nullable=False
    )

    explanation: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    recommendation: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    confidence: Mapped[Decimal] = mapped_column(
        Numeric(
            5,
            2
        ),
        nullable=False
    )

    model_name: Mapped[AIModel] = mapped_column(
        SqlEnum(AIModel),
        nullable=False
    )

    prompt_version: Mapped[str] = mapped_column(
        String(
            50
        ),
        nullable=False
    )

    case = relationship(
        "InvestigationCase",
        back_populates="ai_insights"
    )
