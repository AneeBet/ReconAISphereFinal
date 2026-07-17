from datetime import UTC, datetime
from uuid import uuid4

from app.models.bank import Bank
from app.models.exception import Exception as ExceptionModel
from app.models.exception import ExceptionStatus, ExceptionType, Severity
from app.models.organization import Organization
from app.models.payment_transaction import PaymentTransaction, PaymentStatus
from app.models.reconciliation_result import ReconciliationResult, ReconciliationStatus, MatchType
from app.models.reconciliation_run import ReconciliationRun, ReconciliationRunStatus
from app.models.user import User, UserRole
from app.repositories.auth_repository import AuthRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.seed_users_repository import SeedUsersRepository
from app.repositories.transaction_repository import TransactionRepository


def test_auth_repository_get_by_email_and_id(db_session, test_user):
    repo = AuthRepository(db_session)

    found_by_email = repo.get_by_email(test_user.email)
    found_by_id = repo.get_by_id(test_user.id)

    assert found_by_email is test_user
    assert found_by_id is test_user


def test_auth_repository_update_last_login(db_session, test_user):
    repo = AuthRepository(db_session)

    previous_login = test_user.last_login
    updated = repo.update_last_login(test_user)

    assert updated is test_user
    assert updated.last_login is not None
    assert updated.last_login != previous_login


def test_seed_users_repository_create_and_get_entities(db_session):
    repo = SeedUsersRepository(db_session)

    organization = Organization(
        name=f"Repo Test Org {uuid4().hex}",
        country="US",
        timezone="UTC",
        currency="USD",
    )
    created_org = repo.create_organization(organization)

    assert created_org.id is not None
    assert db_session.get(Organization, created_org.id) is created_org

    bank = Bank(
        organization_id=created_org.id,
        bank_name="Test Bank",
        bic_swift=f"TESTBIC{uuid4().hex[:8]}",
        country="US",
        currency="USD",
    )
    created_bank = repo.create_bank(bank)

    assert created_bank.id is not None
    assert repo.get_bank(created_bank.bic_swift).id == created_bank.id
    assert repo.get_bank(created_bank.bic_swift).bank_name == created_bank.bank_name

    user = User(
        organization_id=created_org.id,
        first_name="Jane",
        last_name="Doe",
        email=f"jane.doe+{uuid4().hex}@example.com",
        password_hash="hashed",
        role=UserRole.ADMIN,
        is_active=True,
        last_login=datetime.now(UTC),
    )
    created_user = repo.create_user(user)

    assert created_user.id is not None
    found_user = repo.get_user(created_user.email)
    assert found_user.id == created_user.id
    assert found_user.email == created_user.email


def test_transaction_repository_gets_transactions_and_transaction_by_id(db_session):
    bank = Bank(
        organization_id=uuid4(),
        bank_name="Test Bank 2",
        bic_swift=f"TESTBIC{uuid4().hex[:8]}",
        country="US",
        currency="USD",
    )
    db_session.add(bank)
    db_session.flush()

    payment = PaymentTransaction(
        bank_id=bank.id,
        transaction_reference="REF-123",
        end_to_end_id="E2E-123",
        sender_account="A1",
        receiver_account="B1",
        sender_name="Alice",
        receiver_name="Bob",
        amount=100.00,
        currency="USD",
        payment_date=datetime.now(UTC),
        settlement_date=datetime.now(UTC),
        payment_type="SWIFT",
        status=PaymentStatus.SUCCESS,
        reconciled=False,
        raw_json={"foo": "bar"},
    )
    db_session.add(payment)
    db_session.commit()

    repo = TransactionRepository(db_session)
    transactions = repo.get_transactions()
    assert len(transactions) >= 1
    assert transactions[0].id == payment.id

    found = repo.get_transaction(payment.id)
    assert found is not None
    assert found.id == payment.id
    assert found.transaction_reference == "REF-123"


def test_dashboard_repository_summary_and_banks(db_session, test_user):
    bank = Bank(
        organization_id=test_user.organization_id,
        bank_name="Summary Bank",
        bic_swift=f"SUMMARY{uuid4().hex[:8]}",
        country="US",
        currency="USD",
    )
    db_session.add(bank)
    db_session.flush()

    payment = PaymentTransaction(
        bank_id=bank.id,
        transaction_reference="REF-456",
        end_to_end_id="E2E-456",
        sender_account="C1",
        receiver_account="D1",
        sender_name="Carol",
        receiver_name="Dave",
        amount=200.00,
        currency="USD",
        payment_date=datetime.now(UTC),
        settlement_date=datetime.now(UTC),
        payment_type="ACH",
        status=PaymentStatus.PENDING,
        reconciled=False,
        raw_json={"baz": "qux"},
    )
    db_session.add(payment)
    db_session.flush()

    run = ReconciliationRun(
        initiated_by_id=test_user.id,
        started_at=datetime.now(UTC),
        status=ReconciliationRunStatus.COMPLETED,
        total_transactions=1,
        matched=1,
        unmatched=0,
        exceptions=0,
        ai_processed=0,
    )
    db_session.add(run)
    db_session.commit()

    repo = DashboardRepository(db_session)
    summary = repo.summary()

    assert summary["total_transactions"] >= 1
    assert summary["banks"] >= 1
    assert summary["runs"] >= 1

    banks = repo.banks()
    assert any(b.id == bank.id for b in banks)

    recent = repo.recent_runs()
    assert any(r.id == run.id for r in recent)

    chart = repo.exception_chart()
    assert chart["critical"] == 0
    assert chart["high"] == 0
    assert chart["medium"] == 0
    assert chart["low"] == 0
