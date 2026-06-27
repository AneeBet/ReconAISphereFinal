import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class AIChatHistory(Base, BaseEntity):
    __tablename__ = "ai_chat_history"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="ai_chat_history"
    )
