import os
import sys
from datetime import datetime, UTC
import uuid

# Ensure required environment variables are available before importing app modules.
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://example.com")
os.environ.setdefault("AZURE_OPENAI_KEY", "test")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "test-deployment")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2026-03-17")
os.environ.setdefault("AZURE_STORAGE_CONNECTION_STRING", "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test;")
os.environ.setdefault("AZURE_STORAGE_CONTAINER", "test-container")
os.environ.setdefault("AZURE_SQL_SERVER", "localhost")
os.environ.setdefault("AZURE_SQL_DATABASE", "testdb")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "test")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "test")
os.environ.setdefault("LANGFUSE_BASE_URL", "https://api.langfuse.com")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import User, Organization

TEST_DB_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
SessionTesting = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = SessionTesting()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def test_user(db_session):
    organization = Organization(
        name=f"Test Org {uuid.uuid4().hex}",
        country="US",
        timezone="UTC",
        currency="USD",
    )
    db_session.add(organization)
    db_session.flush()
    user = User(
        organization_id=organization.id,
        first_name="Test",
        last_name="User",
        email=f"test+{uuid.uuid4().hex}@example.com",
        password_hash="hashed",
        role="ADMIN",
        is_active=True,
        last_login=datetime.now(UTC),
    )
    db_session.add(user)
    db_session.commit()
    return user
