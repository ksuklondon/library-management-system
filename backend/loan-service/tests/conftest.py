"""
Pytest configuration and fixtures for Loan Service tests.

Wymaganie: NF9 - Testy jednostkowe i integracyjne

ULTIMATE FIX:
- Dodano auth_headers_reader, auth_headers_librarian, auth_headers_admin fixtures
- Dodano async_auth_reader, async_auth_librarian, async_auth_admin fixtures
- Poprawione importy routerów (reservation_routes, loan_routes, fine_routes)
- Naprawiony async_client fixture
- Usunięto prefix /api z routerów
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Generator

import pytest
import pytest_asyncio  # CRITICAL: Import for async fixtures!
from app.models.fine import Fine
from app.models.loan import Loan, LoanStatus
from app.models.reservation import Reservation, ReservationStatus
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.shared.database import Base, get_db

# ---------------------------------------------------------
# Testowa baza danych – SQLite w pamięci (NF9)
# ---------------------------------------------------------
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Fixture tworzący *świeżą* bazę danych przed każdym testem (NF9).
    """
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db):
    """Alias dla db fixture (niektóre testy używają db_session)."""
    return db


@pytest.fixture(scope="function")
def test_app():
    """
    Fixture tworzący testową instancję FastAPI BEZ połączenia z PostgreSQL.

    FIXED: Poprawione nazwy importów routerów i usunięty prefix /api.
    """
    app = FastAPI()

    # FIXED: Poprawione nazwy plików routerów
    try:
        from app.api.reservation_routes import router as reservations_router

        app.include_router(
            reservations_router, prefix="/reservations", tags=["reservations"]
        )
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not load reservation router: {e}")

    try:
        from app.api.loan_routes import router as loans_router

        app.include_router(loans_router, prefix="/loans", tags=["loans"])
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not load loan router: {e}")

    try:
        from app.api.fine_routes import router as fines_router

        app.include_router(fines_router, prefix="/fines", tags=["fines"])
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not load fine router: {e}")

    return app


@pytest.fixture(scope="function")
def app_fixture(test_app):
    """Alias dla test_app - niektóre testy używają app_fixture."""
    return test_app


@pytest.fixture(scope="function")
def client(db, test_app) -> Generator:
    """
    Fixture tworzący TestClient FastAPI z podmienioną bazą danych (NF9).
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()


# ---------------------------------------------------------
# USER FIXTURES – generowanie użytkowników do testów (NF9)
# ---------------------------------------------------------


@pytest.fixture(scope="function")
def mock_reader() -> Dict[str, Any]:
    """Fixture tworzący mock payload JWT dla READER (NF9)."""
    return {
        "sub": str(uuid.uuid4()),
        "email": "reader@example.com",
        "role": "READER",
        "full_name": "Test Reader",
    }


@pytest.fixture(scope="function")
def mock_librarian() -> Dict[str, Any]:
    """Fixture tworzący mock payload JWT dla LIBRARIAN (NF9)."""
    return {
        "sub": str(uuid.uuid4()),
        "email": "librarian@example.com",
        "role": "LIBRARIAN",
        "full_name": "Test Librarian",
    }


@pytest.fixture(scope="function")
def mock_admin() -> Dict[str, Any]:
    """Fixture tworzący mock payload JWT dla ADMIN (NF9)."""
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
    """Tworzy pojedynczą rezerwację testową (NF9)."""
    reservation = Reservation(
        user_id=mock_reader["sub"],
        book_id=uuid.uuid4(),
        book_copy_id=uuid.uuid4(),
        status=ReservationStatus.ACTIVE,
    )
    reservation.expires_at = datetime.utcnow() + timedelta(days=3)

    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@pytest.fixture(scope="function")
def test_loan(db, mock_reader) -> Loan:
    """Tworzy jedno aktywne wypożyczenie testowe (NF9)."""
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
    """Tworzy przetrzymane wypożyczenie testowe (NF9)."""
    loan = Loan(
        user_id=mock_reader["sub"],
        book_copy_id=uuid.uuid4(),
        borrowed_at=datetime.utcnow() - timedelta(days=20),
        status=LoanStatus.OVERDUE,
    )
    loan.due_date = datetime.utcnow() - timedelta(days=6)
    loan.fine_amount = 12.0

    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@pytest.fixture(scope="function")
def test_fine(db, test_loan) -> Fine:
    """Tworzy testową karę przypisaną do wypożyczenia (NF9)."""
    fine = Fine(
        loan_id=test_loan.id, user_id=test_loan.user_id, amount=10.0, paid=False
    )

    db.add(fine)
    db.commit()
    db.refresh(fine)
    return fine


@pytest.fixture(scope="function")
def multiple_reservations(db, mock_reader) -> list[Reservation]:
    """Tworzy 3 aktywne rezerwacje testowe (NF9)."""
    reservations = []

    for i in range(3):
        reservation = Reservation(
            user_id=mock_reader["sub"],
            book_id=uuid.uuid4(),
            book_copy_id=uuid.uuid4(),
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
    """Tworzy 5 aktywnych wypożyczeń testowych (NF9)."""
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
# TOKEN FIXTURES
# =============================================================================


@pytest.fixture(scope="function")
def test_user_token(mock_reader):
    """Generate JWT token for READER user."""
    try:
        from backend.auth_service.app.core.security import create_access_token

        return create_access_token(
            data={"sub": mock_reader["sub"], "role": mock_reader["role"]}
        )
    except ImportError:
        return "mock-reader-token"


@pytest.fixture(scope="function")
def librarian_token(mock_librarian):
    """Generate JWT token for LIBRARIAN user."""
    try:
        from backend.auth_service.app.core.security import create_access_token

        return create_access_token(
            data={"sub": mock_librarian["sub"], "role": mock_librarian["role"]}
        )
    except ImportError:
        return "mock-librarian-token"


@pytest.fixture(scope="function")
def admin_token(mock_admin):
    """Generate JWT token for ADMIN user."""
    try:
        from backend.auth_service.app.core.security import create_access_token

        return create_access_token(
            data={"sub": mock_admin["sub"], "role": mock_admin["role"]}
        )
    except ImportError:
        return "mock-admin-token"


@pytest.fixture(scope="function")
def reader_token(test_user_token):
    """Alias for test_user_token."""
    return test_user_token


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================


@pytest.fixture(scope="function")
def test_book(db):
    """Create test book for scenarios."""
    from unittest.mock import Mock

    book = Mock()
    book.id = uuid.uuid4()
    book.title = "Test Book"
    return book


@pytest.fixture(scope="function")
def test_book_copy(db, test_book):
    """Create single AVAILABLE book copy."""
    from unittest.mock import Mock

    copy = Mock()
    copy.id = uuid.uuid4()
    copy.book_id = test_book.id if hasattr(test_book, "id") else uuid.uuid4()
    copy.status = "AVAILABLE"
    return copy


@pytest.fixture(scope="function")
def test_book_copies(db, test_book):
    """Create 10 AVAILABLE book copies for limit tests."""
    from unittest.mock import Mock

    copies = []
    for i in range(10):
        copy = Mock()
        copy.id = uuid.uuid4()
        copy.book_id = test_book.id if hasattr(test_book, "id") else uuid.uuid4()
        copy.status = "AVAILABLE"
        copies.append(copy)
    return copies


@pytest.fixture(scope="function")
def test_user(db, mock_reader):
    """Create test User mock (for integration tests)."""
    from unittest.mock import Mock

    user = Mock()
    user.id = mock_reader["sub"]
    user.email = mock_reader["email"]
    user.role = "READER"
    return user


@pytest.fixture(scope="function")
def test_librarian(db, mock_librarian):
    """Create test Librarian mock."""
    from unittest.mock import Mock

    user = Mock()
    user.id = mock_librarian["sub"]
    user.email = mock_librarian["email"]
    user.role = "LIBRARIAN"
    return user


@pytest.fixture(scope="function")
def test_user_reservation(db, mock_reader, test_book_copy):
    """Create ACTIVE reservation with RESERVED book copy."""
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
def async_client(test_app, db, mock_reader):
    """
    AsyncClient for async tests with DEFAULT mock_reader auth.

    HYBRID APPROACH:
    - Has default mock_reader auth for backward compatibility
    - Can be overridden by async_auth_* fixtures for specific roles

    This allows both:
    1. Old tests using test_user_token to work (gets mock_reader by default)
    2. New tests using async_auth_librarian/admin for specific roles
    """
    from httpx import AsyncClient

    # Override get_db
    def override_get_db():
        try:
            yield db
        finally:
            pass

    # DEFAULT: Override get_current_user_payload with mock_reader
    # This can be overridden later by async_auth_* fixtures
    def override_get_current_user_payload():
        return mock_reader

    test_app.dependency_overrides[get_db] = override_get_db

    # Import and override dependency with DEFAULT mock_reader
    try:
        from backend.shared.dependencies import get_current_user_payload

        test_app.dependency_overrides[get_current_user_payload] = (
            override_get_current_user_payload
        )
    except ImportError:
        pass

    # Return AsyncClient instance
    return AsyncClient(app=test_app, base_url="http://test")


# =============================================================================
# AUTH HEADERS FIXTURES - CRITICAL FOR ROUTE TESTS!
# =============================================================================


@pytest.fixture(scope="function")
def auth_headers_reader(test_app, mock_reader, reader_token):
    """
    Authorization headers for READER role.

    Returns: dict with Authorization header
    Usage: client.post("/endpoint/", headers=auth_headers_reader)

    CRITICAL: Override get_current_user_payload dla TestClient (sync)
    """
    # Import dependency
    try:
        from backend.shared.dependencies import get_current_user_payload
    except ImportError:
        try:
            from shared.auth import get_current_user_payload
        except ImportError:
            # Fallback - just return headers without override
            return {"Authorization": f"Bearer {reader_token}"}

    # Override dependency to return mock_reader
    def override_get_current_user():
        return mock_reader

    test_app.dependency_overrides[get_current_user_payload] = override_get_current_user

    # Return headers
    return {"Authorization": f"Bearer {reader_token}"}


@pytest.fixture(scope="function")
def auth_headers_librarian(test_app, mock_librarian, librarian_token):
    """
    Authorization headers for LIBRARIAN role.

    Returns: dict with Authorization header
    Usage: client.post("/endpoint/", headers=auth_headers_librarian)

    CRITICAL: Override get_current_user_payload dla TestClient (sync)
    """
    # Import dependency
    try:
        from backend.shared.dependencies import get_current_user_payload
    except ImportError:
        try:
            from shared.auth import get_current_user_payload
        except ImportError:
            # Fallback - just return headers without override
            return {"Authorization": f"Bearer {librarian_token}"}

    # Override dependency to return mock_librarian
    def override_get_current_user():
        return mock_librarian

    test_app.dependency_overrides[get_current_user_payload] = override_get_current_user

    # Return headers
    return {"Authorization": f"Bearer {librarian_token}"}


@pytest.fixture(scope="function")
def auth_headers_admin(test_app, mock_admin, admin_token):
    """
    Authorization headers for ADMIN role.

    Returns: dict with Authorization header
    Usage: client.post("/endpoint/", headers=auth_headers_admin)

    CRITICAL: Override get_current_user_payload dla TestClient (sync)
    """
    # Import dependency
    try:
        from backend.shared.dependencies import get_current_user_payload
    except ImportError:
        try:
            from shared.auth import get_current_user_payload
        except ImportError:
            # Fallback - just return headers without override
            return {"Authorization": f"Bearer {admin_token}"}

    # Override dependency to return mock_admin
    def override_get_current_user():
        return mock_admin

    test_app.dependency_overrides[get_current_user_payload] = override_get_current_user

    # Return headers
    return {"Authorization": f"Bearer {admin_token}"}


# =============================================================================
# ASYNC-COMPATIBLE AUTH FIXTURES (for async_client with manual override)
# =============================================================================


@pytest_asyncio.fixture
async def async_auth_reader(test_app, mock_reader, reader_token):
    """
    Async auth fixture for READER role with async_client.

    Usage:
        async def test_something(async_client, async_auth_reader):
            headers = async_auth_reader
            response = await async_client.post("/endpoint/", headers=headers)
    """
    # Import dependency
    try:
        from backend.shared.dependencies import get_current_user_payload
    except ImportError:
        try:
            from shared.auth import get_current_user_payload
        except ImportError:
            # Fallback - FIXED: use yield not return!
            yield {"Authorization": f"Bearer {reader_token}"}
            return

    # Override dependency
    def override_get_current_user():
        return mock_reader

    test_app.dependency_overrides[get_current_user_payload] = override_get_current_user

    yield {"Authorization": f"Bearer {reader_token}"}

    # Cleanup
    if get_current_user_payload in test_app.dependency_overrides:
        del test_app.dependency_overrides[get_current_user_payload]


@pytest_asyncio.fixture
async def async_auth_librarian(test_app, mock_librarian, librarian_token):
    """
    Async auth fixture for LIBRARIAN role with async_client.

    Usage:
        async def test_something(async_client, async_auth_librarian):
            headers = async_auth_librarian
            response = await async_client.post("/endpoint/", headers=headers)
    """
    # Import dependency
    try:
        from backend.shared.dependencies import get_current_user_payload
    except ImportError:
        try:
            from shared.auth import get_current_user_payload
        except ImportError:
            # Fallback - FIXED: use yield not return!
            yield {"Authorization": f"Bearer {librarian_token}"}
            return

    # Override dependency
    def override_get_current_user():
        return mock_librarian

    test_app.dependency_overrides[get_current_user_payload] = override_get_current_user

    yield {"Authorization": f"Bearer {librarian_token}"}

    # Cleanup
    if get_current_user_payload in test_app.dependency_overrides:
        del test_app.dependency_overrides[get_current_user_payload]


@pytest_asyncio.fixture
async def async_auth_admin(test_app, mock_admin, admin_token):
    """
    Async auth fixture for ADMIN role with async_client.

    Usage:
        async def test_something(async_client, async_auth_admin):
            headers = async_auth_admin
            response = await async_client.post("/endpoint/", headers=headers)
    """
    # Import dependency
    try:
        from backend.shared.dependencies import get_current_user_payload
    except ImportError:
        try:
            from shared.auth import get_current_user_payload
        except ImportError:
            # Fallback - FIXED: use yield not return!
            yield {"Authorization": f"Bearer {admin_token}"}
            return

    # Override dependency
    def override_get_current_user():
        return mock_admin

    test_app.dependency_overrides[get_current_user_payload] = override_get_current_user

    yield {"Authorization": f"Bearer {admin_token}"}

    # Cleanup
    if get_current_user_payload in test_app.dependency_overrides:
        del test_app.dependency_overrides[get_current_user_payload]
