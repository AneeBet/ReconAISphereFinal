from types import SimpleNamespace

from app.api import auth as auth_api
from app.schemas.auth import LoginRequest


class FakeAuthRepository:
    def __init__(self, db):
        self.db = db


class FakeAuthService:
    calls = []

    def __init__(self, repository):
        self.repository = repository

    def login(self, request):
        self.calls.append(("login", self.repository.db, request.email, request.password))
        return {
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "Bearer",
        }

    def current_user(self, user_id):
        self.calls.append(("current_user", self.repository.db, user_id))
        return {"id": user_id}


def test_auth_api_endpoints_delegate_to_service(monkeypatch):
    monkeypatch.setattr(auth_api, "AuthRepository", FakeAuthRepository)
    monkeypatch.setattr(auth_api, "AuthService", FakeAuthService)
    FakeAuthService.calls = []

    db = object()
    user = SimpleNamespace(id="user-1")

    assert auth_api.login(LoginRequest(email="test@example.com", password="secret"), db=db) == {
        "access_token": "access",
        "refresh_token": "refresh",
        "token_type": "Bearer",
    }
    assert auth_api.current_user(current_user=user, db=db) == {"id": "user-1"}

    assert FakeAuthService.calls == [
        ("login", db, "test@example.com", "secret"),
        ("current_user", db, "user-1"),
    ]
