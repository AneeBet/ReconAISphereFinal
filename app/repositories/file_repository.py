from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment_file import PaymentFile


class FileRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create(
        self,
        payment_file: PaymentFile
    ):

        self.db.add(payment_file)
        self.db.commit()
        self.db.refresh(payment_file)

        return payment_file

    def get_all(
        self
    ):

        statement = (
            select(PaymentFile)
            .order_by(
                PaymentFile.created_at.desc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )

    def get_by_id(
        self,
        file_id: UUID
    ):

        return self.db.scalar(
            select(PaymentFile)
            .where(
                PaymentFile.id == file_id
            )
        )

    def update(
        self,
        payment_file: PaymentFile
    ):

        self.db.commit()
        self.db.refresh(payment_file)

        return payment_file
