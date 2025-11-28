"""
Pytest configuration and fixtures for Loan Service tests.

Wymaganie: NF9 - Testy jednostkowe i integracyjne
"""

import pytest
import os
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.shared.database import Base, get_db
from backend.shared.models import User
from backend.shared.auth import create_access_token
from app.main import app
from app.models.reservation import Reservation, ReservationStatus
from app.models.loan import Loan, LoanStatus
from app.models.fine import Fine


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
def test_user(db) -> User:
    """
    Fixture tworzący testowego użytkownika o roli READER (NF9).
    """
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        role="READER",
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_librarian(db) -> User:
    """
    Fixture tworzący testowego użytkownika o roli LIBRARIAN (NF9).
    """
    user = User(
        email="librarian@example.com",
        hashed_password="hashed_password",
        role="LIBRARIAN",
        full_name="Test Librarian"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db) -> User:
    """
    Fixture tworzący testowego użytkownika o roli ADMIN (NF9).
    """
    user = User(
        email="admin@example.com",
        hashed_password="hashed_password",
        role="ADMIN",
        full_name="Test Admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------
# AUTH FIXTURES – generowanie tokenów JWT do testów (NF9)
# ---------------------------------------------------------

@pytest.fixture(scope="function")
def auth_headers_reader(test_user) -> dict:
    """
    Generuje nagłówki Authorization Bearer dla użytkownika READER (NF9).
    """
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def auth_headers_librarian(test_librarian) -> dict:
    """
    Generuje nagłówki Authorization Bearer dla LIBRARIAN (NF9).
    """
    token = create_access_token(data={"sub": test_librarian.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def auth_headers_admin(test_admin) -> dict:
    """
    Generuje nagłówki Authorization Bearer dla ADMIN (NF9).
    """
    token = create_access_token(data={"sub": test_admin.id})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------
# FIXTURES TWORZĄCE OBIEKTY DOMAIN (Reservation, Loan, Fine)
# ---------------------------------------------------------

@pytest.fixture(scope="function")
def test_reservation(db, test_user) -> Reservation:
    """
    Tworzy pojedynczą rezerwację testową (NF9).
    Ustawia datę wygaśnięcia na +3 dni.
    """
    from datetime import datetime, timedelta
    import uuid

    reservation = Reservation(
        user_id=test_user.id,
        book_id=uuid.uuid4(),
        status=ReservationStatus.ACTIVE
    )
    reservation.expires_at = datetime.utcnow() + timedelta(days=3)

    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@pytest.fixture(scope="function")
def test_loan(db, test_user) -> Loan:
    """
    Tworzy jedno aktywne wypożyczenie testowe (NF9).
    Termin zwrotu: +14 dni.
    """
    from datetime import datetime, timedelta
    import uuid

    loan = Loan(
        user_id=test_user.id,
        book_copy_id=uuid.uuid4(),
        borrowed_at=datetime.utcnow(),
        status=LoanStatus.ACTIVE
    )
    loan.due_date = datetime.utcnow() + timedelta(days=14)

    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@pytest.fixture(scope="function")
def test_overdue_loan(db, test_user) -> Loan:
    """
    Tworzy przetrzymane wypożyczenie testowe (NF9).
    - borrowed_at: 20 dni temu
    - due_date: 6 dni temu
    - fine_amount: 6 * 2 zł
    """
    from datetime import datetime, timedelta
    import uuid

    loan = Loan(
        user_id=test_user.id,
        book_copy_id=uuid.uuid4(),
        borrowed_at=datetime.utcnow() - timedelta(days=20),
        status=LoanStatus.OVERDUE
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
        loan_id=test_loan.id,
        user_id=test_loan.user_id,
        amount=10.0,
        paid=False
    )

    db.add(fine)
    db.commit()
    db.refresh(fine)
    return fine


@pytest.fixture(scope="function")
def multiple_reservations(db, test_user) -> list[Reservation]:
    """
    Tworzy 3 aktywne rezerwacje testowe (NF9).
    Przydatne do testowania limitu 3 aktywnych rezerwacji (NF29).
    """
    from datetime import datetime, timedelta
    import uuid

    reservations = []

    for i in range(3):
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )
        reservation.expires_at = datetime.utcnow() + timedelta(days=3)
        db.add(reservation)
        reservations.append(reservation)

    db.commit()

    for r in reservations:
        db.refresh(r)

    return reservations


@pytest.fixture(scope="function")
def multiple_loans(db, test_user) -> list[Loan]:
    """
    Tworzy 5 aktywnych wypożyczeń testowych (NF9).
    Przydatne do testowania limitu 5 wypożyczeń (NF29).
    """
    from datetime import datetime, timedelta
    import uuid

    loans = []

    for i in range(5):
        loan = Loan(
            user_id=test_user.id,
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE
        )
        loan.due_date = datetime.utcnow() + timedelta(days=14)
        db.add(loan)
        loans.append(loan)

    db.commit()

    for l in loans:
        db.refresh(l)

    return loans
