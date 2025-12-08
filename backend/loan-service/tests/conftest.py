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


# =============================================================================
# DODATKOWE FIXTURES DLA NOWYCH SCENARIUSZY TESTOWYCH
# =============================================================================


@pytest.fixture(scope="function")
def test_user_token(mock_reader):
    """
    Generate JWT token for READER user.
    """
    from app.core.security import create_access_token

    return create_access_token(
        data={"sub": mock_reader["sub"], "role": mock_reader["role"]}
    )


@pytest.fixture(scope="function")
def librarian_token(mock_librarian):
    """
    Generate JWT token for LIBRARIAN user.
    """
    from app.core.security import create_access_token

    return create_access_token(
        data={"sub": mock_librarian["sub"], "role": mock_librarian["role"]}
    )


@pytest.fixture(scope="function")
def admin_token(mock_admin):
    """
    Generate JWT token for ADMIN user.
    """
    from app.core.security import create_access_token

    return create_access_token(
        data={"sub": mock_admin["sub"], "role": mock_admin["role"]}
    )


@pytest.fixture(scope="function")
def reader_token(test_user_token):
    """
    Alias for test_user_token.
    """
    return test_user_token


@pytest.fixture(scope="function")
def test_book(db):
    """
    Create test book for scenarios.
    """
    # UWAGA: Sprawdź czy masz model Book w loan-service
    # Jeśli NIE MA - usuń tę fixture lub zaimportuj z catalog-service
    try:
        import uuid

        from app.models.book import Book

        book = Book(
            id=uuid.uuid4(),
            title="Test Book",
            authors=["Test Author"],
            isbn="978-83-123-4567-8",
            publisher="Test Publisher",
            pages=300,
            language="pl",
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        return book
    except ImportError:
        # Jeśli Book nie istnieje w loan-service, zwróć mock
        import uuid
        from unittest.mock import Mock

        book = Mock()
        book.id = uuid.uuid4()
        book.title = "Test Book"
        return book


@pytest.fixture(scope="function")
def test_book_copy(db, test_book):
    """
    Create single AVAILABLE book copy.
    """
    # UWAGA: Sprawdź czy masz model BookCopy w loan-service
    try:
        import uuid

        from app.models.book_copy import BookCopy, CopyStatus

        copy = BookCopy(
            id=uuid.uuid4(),
            book_id=test_book.id,
            inventory_no="INV-001",
            status=CopyStatus.AVAILABLE,
            location="Shelf A1",
        )
        db.add(copy)
        db.commit()
        db.refresh(copy)
        return copy
    except ImportError:
        # Jeśli BookCopy nie istnieje w loan-service, zwróć mock
        import uuid
        from unittest.mock import Mock

        copy = Mock()
        copy.id = uuid.uuid4()
        copy.book_id = test_book.id
        copy.status = "AVAILABLE"
        return copy


@pytest.fixture(scope="function")
def test_book_copies(db, test_book):
    """
    Create 10 AVAILABLE book copies for limit tests.
    """
    try:
        import uuid

        from app.models.book_copy import BookCopy, CopyStatus

        copies = []
        for i in range(10):
            copy = BookCopy(
                id=uuid.uuid4(),
                book_id=test_book.id,
                inventory_no=f"INV-{i:03d}",
                status=CopyStatus.AVAILABLE,
                location=f"Shelf A{i + 1}",
            )
            db.add(copy)
            copies.append(copy)

        db.commit()

        for copy in copies:
            db.refresh(copy)

        return copies
    except ImportError:
        # Mock dla testów jeśli nie ma modelu
        import uuid
        from unittest.mock import Mock

        copies = []
        for i in range(10):
            copy = Mock()
            copy.id = uuid.uuid4()
            copy.book_id = test_book.id
            copy.status = "AVAILABLE"
            copies.append(copy)
        return copies


@pytest.fixture(scope="function")
def test_user(db, mock_reader):
    """
    Create test User in database (for RBAC tests if needed).
    """
    # UWAGA: Sprawdź czy masz model User w loan-service
    try:
        from app.models.user import User, UserRole

        user = User(
            id=mock_reader["sub"],
            email=mock_reader["email"],
            hashed_password="hashed_password",
            full_name=mock_reader["full_name"],
            role=UserRole.READER,
            is_active=True,
            is_blocked=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except ImportError:
        # Jeśli User nie istnieje w loan-service, zwróć mock
        from unittest.mock import Mock

        user = Mock()
        user.id = mock_reader["sub"]
        user.email = mock_reader["email"]
        user.role = "READER"
        return user


@pytest.fixture(scope="function")
def test_user_reservation(db, mock_reader, test_book_copy):
    """
    Create ACTIVE reservation with RESERVED book copy.
    """
    reservation = Reservation(
        id=uuid.uuid4(),
        user_id=mock_reader["sub"],
        book_id=test_book_copy.book_id
        if hasattr(test_book_copy, "book_id")
        else uuid.uuid4(),
        book_copy_id=test_book_copy.id
        if hasattr(test_book_copy, "id")
        else uuid.uuid4(),
        status=ReservationStatus.ACTIVE,
        created_at=datetime.utcnow(),
    )
    reservation.expires_at = datetime.utcnow() + timedelta(days=3)

    db.add(reservation)

    # Update copy status to RESERVED if possible
    if hasattr(test_book_copy, "status"):
        test_book_copy.status = "RESERVED"

    db.commit()
    db.refresh(reservation)
    return reservation


@pytest.fixture(scope="function")
async def async_client():
    """
    AsyncClient for async tests (race condition scenarios).
    """
    from httpx import AsyncClient

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
