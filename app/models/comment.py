import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class Comment(Base, BaseEntity):
    __tablename__ = "comments"

    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("investigation_cases.id"),
        nullable=False,
        index=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    comment: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    case = relationship(
        "InvestigationCase",
        back_populates="comments"
    )

    user = relationship(
        "User",
        back_populates="comments"
    )
