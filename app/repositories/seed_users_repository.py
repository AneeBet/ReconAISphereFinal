from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.user import User


class SeedUsersRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_organization(self):
        return self.db.scalar(select(Organization))

    def create_organization(self, organization):
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def get_user(self, email):
        return self.db.scalar(
            select(User).where(User.email == email)
        )

    def create_user(self, user):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
