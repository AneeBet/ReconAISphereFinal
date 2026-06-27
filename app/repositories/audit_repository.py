from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.audit_log import AuditLog


class AuditRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create(
        self,
        audit_log: AuditLog
    ) -> AuditLog:

        self.db.add(
            audit_log
        )

        self.db.commit()

        self.db.refresh(
            audit_log
        )

        return audit_log

    def get_logs(
        self
    ):

        statement = (

            select(AuditLog)

            .options(

                selectinload(
                    AuditLog.user
                )

            )

            .order_by(

                AuditLog.created_at.desc()

            )

        )

        return list(

            self.db.scalars(

                statement

            ).all()

        )

