from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bank import Bank
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

    def get_bank(self, bic_swift):
        return self.db.scalar(
            select(Bank).where(Bank.bic_swift == bic_swift)
        )

    def create_bank(self, bank):
        self.db.add(bank)
        self.db.commit()
        self.db.refresh(bank)
        return bank

    def get_user(self, email):
        return self.db.scalar(
            select(User).where(User.email == email)
        )

    def create_user(self, user):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
