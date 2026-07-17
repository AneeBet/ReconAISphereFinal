import pytest
from types import SimpleNamespace
from fastapi import HTTPException
from app.core import dependencies


class DummyRepo:
    def __init__(self, user=None):
        self.user = user

    def get_by_id(self, user_id):
        return self.user


@pytest.fixture(autouse=True)
def patch_auth_repository(monkeypatch):
    monkeypatch.setattr(dependencies, "AuthRepository", DummyRepo)


def test_require_roles_allows_authorized_user(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(value="ADMIN"), is_active=True)
    dependency = dependencies.require_roles(user.role)

    def fake_get_current_user():
        return user

    monkeypatch.setattr(dependencies, "get_current_user", fake_get_current_user)

    result = dependency(current_user=user)

    assert result is user


def test_require_roles_rejects_unauthorized_user(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(value="VIEWER"), is_active=True)
    dependency = dependencies.require_roles(dependencies.UserRole.ADMIN)

    def fake_get_current_user():
        return user

    monkeypatch.setattr(dependencies, "get_current_user", fake_get_current_user)

    with pytest.raises(HTTPException):
        dependency(current_user=user)


def test_get_current_user_invalid_token(monkeypatch):
    class DummyCreds:
        credentials = "badtoken"

    class FakeJWT:
        @staticmethod
        def decode(token, secret, algorithms):
            raise Exception("invalid")

    monkeypatch.setattr(dependencies, "jwt", FakeJWT)

    with pytest.raises(HTTPException):
        dependencies.get_current_user(DummyCreds())
