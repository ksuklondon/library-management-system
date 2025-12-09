"""
Pytest configuration and fixtures for Loan Service tests.

Wymaganie: NF9 - Testy jednostkowe i integracyjne
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Generator
from unittest.mock import Mock

import pytest
from app.models.fine import Fine
from app.models.loan import Loan, LoanStatus
from app.models.reservation import Reservation, ReservationStatus
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.shared.database import Base, get_db

# =============================================================================
# TEST DATABASE (SQLite in-memory)
# =============================================================================

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db):
    return db


# =============================================================================
# FASTAPI APP & CLIENT
# =============================================================================


@pytest.fixture(scope="function")
def test_app():
    app = FastAPI()

    from app.api.fine_routes import router as fines_router
    from app.api.loan_routes import router as loans_router
    from app.api.reservation_routes import router as reservations_router

    app.include_router(reservations_router, prefix="/reservations")
    app.include_router(loans_router, prefix="/loans")
    app.include_router(fines_router, prefix="/fines")

    return app


@pytest.fixture(scope="function")
def app_fixture(test_app):
    return test_app


@pytest.fixture(scope="function")
def client(db, test_app):
    def override_get_db():
        yield db

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as c:
        yield c

    test_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def async_client(test_app, db, mock_reader):
    from httpx import AsyncClient

    from backend.shared.dependencies import get_current_user_payload

    def override_get_db():
        yield db

    def override_user():
        return mock_reader

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user_payload] = override_user

    return AsyncClient(app=test_app, base_url="http://test")


# =============================================================================
# USER / AUTH FIXTURES
# =============================================================================


@pytest.fixture(scope="function")
def mock_reader() -> Dict[str, Any]:
    return {
        "sub": str(uuid.uuid4()),
        "email": "reader@test.com",
        "role": "READER",
    }


@pytest.fixture(scope="function")
def mock_librarian() -> Dict[str, Any]:
    return {
        "sub": str(uuid.uuid4()),
        "email": "librarian@test.com",
        "role": "LIBRARIAN",
    }


@pytest.fixture(scope="function")
def mock_admin() -> Dict[str, Any]:
    return {
        "sub": str(uuid.uuid4()),
        "email": "admin@test.com",
        "role": "ADMIN",
    }


@pytest.fixture(scope="function")
def test_user(mock_reader):
    user = Mock()
    user.id = mock_reader["sub"]
    return user


@pytest.fixture(scope="function")
def test_user_token():
    return "mock-reader-token"


# =============================================================================
# DOMAIN OBJECTS
# =============================================================================


@pytest.fixture(scope="function")
def test_book():
    book = Mock()
    book.id = uuid.uuid4()
    return book


@pytest.fixture(scope="function")
def test_book_copy():
    """
    ✅ FIX: pojedynczy egzemplarz książki (wymagany przez test_reservation_blocked_by_unpaid_fine)
    """
    copy = Mock()
    copy.id = uuid.uuid4()
    copy.book_id = uuid.uuid4()
    copy.status = "AVAILABLE"
    return copy


@pytest.fixture(scope="function")
def test_book_copies():
    """
    ✅ FIX: kopie z RÓŻNYMI book_id (krytyczne dla limitu rezerwacji)
    """
    copies = []
    for _ in range(10):
        copy = Mock()
        copy.id = uuid.uuid4()
        copy.book_id = uuid.uuid4()
        copy.status = "AVAILABLE"
        copies.append(copy)
    return copies


@pytest.fixture(scope="function")
def test_reservation(db, mock_reader):
    r = Reservation(
        user_id=mock_reader["sub"],
        book_id=uuid.uuid4(),
        book_copy_id=uuid.uuid4(),
        status=ReservationStatus.ACTIVE,
    )
    r.expires_at = datetime.utcnow() + timedelta(days=3)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@pytest.fixture(scope="function")
def test_loan(db, mock_reader):
    loan = Loan(
        user_id=mock_reader["sub"],
        book_copy_id=uuid.uuid4(),
        borrowed_at=datetime.utcnow(),
        status=LoanStatus.ACTIVE,
    )
    loan.due_date = datetime.utcnow() + timedelta(days=14)
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@pytest.fixture(scope="function")
def test_fine(db, test_loan):
    fine = Fine(
        loan_id=test_loan.id,
        user_id=test_loan.user_id,
        amount=10.0,
        paid=False,
    )
    db.add(fine)
    db.commit()
    db.refresh(fine)
    return fine


@pytest.fixture(scope="function")
def multiple_reservations(db, mock_reader):
    reservations = []
    for _ in range(3):
        r = Reservation(
            user_id=mock_reader["sub"],
            book_id=uuid.uuid4(),
            book_copy_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE,
        )
        r.expires_at = datetime.utcnow() + timedelta(days=3)
        db.add(r)
        reservations.append(r)

    db.commit()
    return reservations


@pytest.fixture(scope="function")
def multiple_loans(db, mock_reader):
    loans = []
    for _ in range(5):
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() + timedelta(days=14)
        db.add(loan)
        loans.append(loan)

    db.commit()
    return loans
