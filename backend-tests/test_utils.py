import jwt
from types import SimpleNamespace
from app.utils.password import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token
from app.core.config import settings


def test_password_hash_and_verify():
    password = "SuperSecret123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_create_access_token_contains_expected_claims():
    user = SimpleNamespace(
        id=123,
        email="tester@example.com",
        role=SimpleNamespace(value="ADMIN"),
        organization_id=456,
    )

    token = create_access_token(user)
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

    assert payload["sub"] == str(user.id)
    assert payload["email"] == user.email
    assert payload["role"] == "ADMIN"
    assert payload["org"] == str(user.organization_id)
    assert payload["jti"]


def test_create_refresh_token_contains_expected_claims():
    user = SimpleNamespace(id=123)
    token = create_refresh_token(user)
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

    assert payload["sub"] == str(user.id)
    assert payload["jti"]
