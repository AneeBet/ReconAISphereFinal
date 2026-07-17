import struct
from types import SimpleNamespace

from app.db import database
from app.db import session as db_session


class FakeManagedIdentityCredential:
    scopes = []

    def get_token(self, scope):
        self.scopes.append(scope)
        return SimpleNamespace(token="abc")


def test_get_access_token_packs_managed_identity_token(monkeypatch):
    FakeManagedIdentityCredential.scopes = []
    monkeypatch.setattr(database, "ManagedIdentityCredential", FakeManagedIdentityCredential)

    token = database.get_access_token()
    token_bytes = "abc".encode("utf-16-le")

    assert token == struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    assert FakeManagedIdentityCredential.scopes == ["https://database.windows.net/.default"]


def test_provide_token_sets_pyodbc_attrs(monkeypatch):
    monkeypatch.setattr(database, "get_access_token", lambda: b"packed-token")
    cparams = {}

    database.provide_token(None, None, None, cparams)

    assert cparams["attrs_before"] == {
        database.SQL_COPT_SS_ACCESS_TOKEN: b"packed-token"
    }


def test_create_database_creates_all_metadata(monkeypatch):
    calls = []
    monkeypatch.setattr(
        database.Base.metadata,
        "create_all",
        lambda bind: calls.append(bind),
    )

    database.create_database()

    assert calls == [database.engine]


class FakeDb:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_get_db_yields_session_and_closes_it(monkeypatch):
    fake_db = FakeDb()
    monkeypatch.setattr(db_session, "SessionLocal", lambda: fake_db)

    generator = db_session.get_db()

    assert next(generator) is fake_db
    try:
        next(generator)
    except StopIteration:
        pass

    assert fake_db.closed is True
