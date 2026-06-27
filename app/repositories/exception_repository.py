from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.exception import Exception
from app.models.reconciliation_result import ReconciliationResult


class ExceptionRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def get_all(
        self
    ) -> list[Exception]:

        statement = (
            select(Exception)
            .options(
                selectinload(
                    Exception.reconciliation_result
                ).selectinload(
                    ReconciliationResult.payment_transaction
                )
            )
            .order_by(
                Exception.detected_at.desc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )

    def get_by_id(
        self,
        exception_id: UUID
    ) -> Exception | None:

        statement = (
            select(Exception)
            .options(
                selectinload(
                    Exception.reconciliation_result
                ).selectinload(
                    ReconciliationResult.payment_transaction
                )
            )
            .where(
                Exception.id == exception_id
            )
        )

        return self.db.scalar(
            statement
        )

    def update(
        self,
        exception: Exception
    ) -> Exception:

        self.db.commit()
        self.db.refresh(
            exception
        )

        return exception
