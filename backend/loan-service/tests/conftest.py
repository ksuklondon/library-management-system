"""
Pytest configuration and fixtures for Loan Service tests.

Wymaganie: NF9 - Testy jednostkowe i integracyjne
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Generator

import pytest
from app.main import app
from app.models.fine import Fine
from app.models.loan import Loan, LoanStatus
from app.models.reservation import Reservation, ReservationStatus
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.shared.database import Base, get_db

# ---------------------------------------------------------
# Testowa baza danych – SQLite w pamięci (NF9)
# ---------------------------------------------------------
# Użycie "sqlite:///:memory:" pozwala na szybkie testy bez
# potrzeby stawiania zewnętrznej bazy PostgreSQL.
# StaticPool → ten sam connection pool = jedna pamięć DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


# ---------------------------------------------------------
# Silnik testowy SQLAlchemy
# ---------------------------------------------------------
# check_same_thread=False – wymagane dla FastAPI
# StaticPool – utrzymuje tę samą bazę dla wielu połączeń
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Sesja testowa SQLAlchemy
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Fixture tworzący *świeżą* bazę danych przed każdym testem (NF9).

    - Tworzy wszystkie tabele z Base.metadata
    - Dostarcza sesję DB do testu
    - Po zakończeniu testu:
        - zamyka sesję
        - usuwa wszystkie tabele (czyste środowisko)
    """
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Fixture tworzący TestClient FastAPI z podmienioną bazą danych (NF9).

    - Nadpisuje zależność get_db → kieruje zapytania do testowej sesji
    - Czyści dependency overrides po teście
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------
# USER FIXTURES – generowanie użytkowników do testów (NF9)
# ---------------------------------------------------------


@pytest.fixture(scope="function")
def mock_reader() -> Dict[str, Any]:
    """
    Fixture tworzący mock payload JWT dla READER (NF9).
    """
    return {
        "sub": str(uuid.uuid4()),
        "email": "reader@example.com",
        "role": "READER",
        "full_name": "Test Reader",
    }


@pytest.fixture(scope="function")
def mock_librarian() -> Dict[str, Any]:
    """
    Fixture tworzący mock payload JWT dla LIBRARIAN (NF9).
    """
    return {
        "sub": str(uuid.uuid4()),
        "email": "librarian@example.com",
        "role": "LIBRARIAN",
        "full_name": "Test Librarian",
    }


@pytest.fixture(scope="function")
def mock_admin() -> Dict[str, Any]:
    """
    Fixture tworzący mock payload JWT dla ADMIN (NF9).
    """
    return {
        "sub": str(uuid.uuid4()),
        "email": "admin@example.com",
        "role": "ADMIN",
        "full_name": "Test Admin",
    }


# ---------------------------------------------------------
# FIXTURES TWORZĄCE OBIEKTY DOMAIN (Reservation, Loan, Fine)
# ---------------------------------------------------------


@pytest.fixture(scope="function")
def test_reservation(db, mock_reader) -> Reservation:
    """
    Tworzy pojedynczą rezerwację testową (NF9).
    Ustawia datę wygaśnięcia na +3 dni.
    """
    reservation = Reservation(
        user_id=mock_reader["sub"],
        book_id=uuid.uuid4(),
        status=ReservationStatus.ACTIVE,
    )
    reservation.expires_at = datetime.utcnow() + timedelta(days=3)

    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@pytest.fixture(scope="function")
def test_loan(db, mock_reader) -> Loan:
    """
    Tworzy jedno aktywne wypożyczenie testowe (NF9).
    Termin zwrotu: +14 dni.
    """
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
def test_overdue_loan(db, mock_reader) -> Loan:
    """
    Tworzy przetrzymane wypożyczenie testowe (NF9).
    - borrowed_at: 20 dni temu
    - due_date: 6 dni temu
    - fine_amount: 6 * 2 zł
    """
    loan = Loan(
        user_id=mock_reader["sub"],
        book_copy_id=uuid.uuid4(),
        borrowed_at=datetime.utcnow() - timedelta(days=20),
        status=LoanStatus.OVERDUE,
    )
    loan.due_date = datetime.utcnow() - timedelta(days=6)
    loan.fine_amount = 12.0  # 6 days * 2 zł

    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@pytest.fixture(scope="function")
def test_fine(db, test_loan) -> Fine:
    """
    Tworzy testową karę przypisaną do wypożyczenia (NF9).
    """
    fine = Fine(
        loan_id=test_loan.id, user_id=test_loan.user_id, amount=10.0, paid=False
    )

    db.add(fine)
    db.commit()
    db.refresh(fine)
    return fine


@pytest.fixture(scope="function")
def multiple_reservations(db, mock_reader) -> list[Reservation]:
    """
    Tworzy 3 aktywne rezerwacje testowe (NF9).
    Przydatne do testowania limitu 3 aktywnych rezerwacji (NF29).
    """
    reservations = []

    for i in range(3):
        reservation = Reservation(
            user_id=mock_reader["sub"],
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE,
        )
        reservation.expires_at = datetime.utcnow() + timedelta(days=3)
        db.add(reservation)
        reservations.append(reservation)

    db.commit()

    for r in reservations:
        db.refresh(r)

    return reservations


@pytest.fixture(scope="function")
def multiple_loans(db, mock_reader) -> list[Loan]:
    """
    Tworzy 5 aktywnych wypożyczeń testowych (NF9).
    Przydatne do testowania limitu 5 wypożyczeń (NF29).
    """
    loans = []

    for i in range(5):
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

    for loan_obj in loans:
        db.refresh(loan_obj)

    return loans
