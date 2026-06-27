from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class AuthRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:

        statement = select(User).where(User.email == email)

        return self.db.scalar(statement)

    def get_by_id(self, user_id: UUID) -> User | None:

        statement = select(User).where(User.id == user_id)

        return self.db.scalar(statement)

    def update_last_login(self, user: User) -> User:

        user.last_login = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(user)

        return user
