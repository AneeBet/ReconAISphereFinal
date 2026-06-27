import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class Attachment(Base, BaseEntity):
    __tablename__ = "attachments"

    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("investigation_cases.id"),
        nullable=False,
        index=True
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    blob_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    case = relationship(
        "InvestigationCase",
        back_populates="attachments"
    )

    uploaded_by = relationship(
        "User",
        back_populates="attachments"
    )
