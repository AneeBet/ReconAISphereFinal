import pytest
from types import SimpleNamespace
from app.services.seed_users_service import SeedUsersService
from app.models.bank import Bank
from app.models.user import UserRole


def test_seed_creates_organization_and_users(monkeypatch):
    created = []
    banks = []
    organization = SimpleNamespace(id=1, name="ReconSphere")

    class FakeRepo:
        def __init__(self):
            self.organization = None

        def get_organization(self):
            return self.organization

        def create_organization(self, org):
            self.organization = org
            org.id = 1
            return org

        def get_user(self, email):
            return None

        def create_user(self, user):
            created.append(user.email)
            return user

        def get_bank(self, bic):
            return None

        def create_bank(self, bank):
            banks.append(bank.bic_swift)
            bank.id = 1
            return bank

    service = SeedUsersService(FakeRepo())
    result = service.seed()

    assert result["organization"] == "ReconSphere"
    assert len(result["created"]) == 4
    assert len(result["banks"]) == 2
    assert result["password"] == "Recon@123"
