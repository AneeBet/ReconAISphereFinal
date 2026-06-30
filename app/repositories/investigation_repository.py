from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.attachment import Attachment
from app.models.comment import Comment
from app.models.exception import Exception
from app.models.investigation_case import InvestigationCase
from app.models.reconciliation_result import ReconciliationResult
from app.models.workflow_history import WorkflowHistory


class InvestigationRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def get_all(
        self
    ) -> list[InvestigationCase]:

        statement = (
            select(InvestigationCase)
            .options(
                selectinload(
                    InvestigationCase.owner
                )
            )
            .order_by(
                InvestigationCase.created_at.desc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )

    def get_case(
        self,
        case_id: UUID
    ) -> InvestigationCase | None:

        statement = (
            select(InvestigationCase)
            .options(

                selectinload(
                    InvestigationCase.owner
                ),

                selectinload(
                    InvestigationCase.comments
                ).selectinload(
                    Comment.user
                ),

                selectinload(
                    InvestigationCase.attachments
                ).selectinload(
                    Attachment.uploaded_by
                ),

                selectinload(
                    InvestigationCase.workflow_history
                ).selectinload(
                    WorkflowHistory.changed_by
                ),

                selectinload(
                    InvestigationCase.exception
                )
                .selectinload(
                    Exception.reconciliation_result
                )
                .selectinload(
                    ReconciliationResult.payment_transaction
                ),

                selectinload(
                    InvestigationCase.exception
                )
                .selectinload(
                    Exception.reconciliation_result
                )
                .selectinload(
                    ReconciliationResult.bank_transaction
                )

            )
            .where(
                InvestigationCase.id == case_id
            )
        )

        return self.db.scalar(statement)

    def update(
        self,
        case: InvestigationCase
    ):

        self.db.commit()
        self.db.refresh(case)

        return case

    def add_comment(
        self,
        comment
    ):

        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        return comment

    def add_attachment(
        self,
        attachment
    ):

        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)

        return attachment
