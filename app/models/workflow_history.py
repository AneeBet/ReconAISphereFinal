from enum import Enum
import uuid

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.base import BaseEntity


class WorkflowStatus(str, Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    AI_ANALYSIS_COMPLETED = "AI_ANALYSIS_COMPLETED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class WorkflowHistory(Base, BaseEntity):
    __tablename__ = "workflow_history"

    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("investigation_cases.id"),
        nullable=False,
        index=True
    )

    from_status: Mapped[WorkflowStatus] = mapped_column(
        SqlEnum(WorkflowStatus)
    )

    to_status: Mapped[WorkflowStatus] = mapped_column(
        SqlEnum(WorkflowStatus),
        nullable=False
    )

    changed_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    remarks: Mapped[str | None] = mapped_column(
        Text
    )

    case = relationship(
        "InvestigationCase",
        back_populates="workflow_history"
    )

    changed_by = relationship(
        "User",
        back_populates="workflow_history"
    )
