import pytest
from fastapi import HTTPException
from types import SimpleNamespace
from app.services.auth_service import AuthService


class DummyRepository:
    def __init__(self, user=None):
        self.user = user
        self.updated = False
        self.db = None

    def get_by_email(self, email):
        return self.user if self.user and self.user.email == email else None

    def update_last_login(self, user):
        self.updated = True
        return user

    def get_by_id(self, user_id):
        return self.user if self.user and str(self.user.id) == str(user_id) else None


class DummyAuditService:
    def __init__(self, repository=None):
        self.repository = repository
        self.logged = []

    def log(self, *args, **kwargs):
        self.logged.append((args, kwargs))


@pytest.fixture(autouse=True)
def patch_audit(monkeypatch):
    monkeypatch.setattr("app.services.auth_service.AuditService", lambda repository: DummyAuditService(repository))


def test_login_success(monkeypatch):
    user = SimpleNamespace(
        id=1,
        email="test@example.com",
        password_hash="$2b$12$abcdefghijklmnopqrstuv",
        role=SimpleNamespace(value="ADMIN"),
        organization_id=123,
    )
    repository = DummyRepository(user)
    service = AuthService(repository)
    service.audit = DummyAuditService(None)

    monkeypatch.setattr("app.services.auth_service.verify_password", lambda password, hashed: True)
    request = SimpleNamespace(email="test@example.com", password="secret")

    result = service.login(request)

    assert result["token_type"] == "Bearer"
    assert "access_token" in result
    assert "refresh_token" in result
    assert repository.updated


def test_login_failure_invalid_credentials(monkeypatch):
    repository = DummyRepository()
    service = AuthService(repository)
    service.audit = DummyAuditService(None)

    monkeypatch.setattr("app.services.auth_service.verify_password", lambda password, hashed: False)
    request = SimpleNamespace(email="missing@example.com", password="secret")

    with pytest.raises(HTTPException) as exc:
        service.login(request)

    assert exc.value.status_code == 401


def test_current_user_found():
    user = SimpleNamespace(id=1, email="test@example.com")
    repository = DummyRepository(user)
    service = AuthService(repository)

    current = service.current_user(1)

    assert current is user


def test_current_user_not_found():
    repository = DummyRepository()
    service = AuthService(repository)

    with pytest.raises(HTTPException) as exc:
        service.current_user(1)

    assert exc.value.status_code == 401
