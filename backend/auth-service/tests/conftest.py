import pytest
from app.core.security import hash_password
from app.main import app
from app.models.user import User, UserRole
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.shared.database import Base, get_db  # ZMIANA: dodano get_db tutaj

# Adres testowej bazy danych — tutaj używamy SQLite w pamięci (szybka, izolowana dla testów)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Tworzymy silnik bazy danych SQLite działający w pamięci RAM.
# StaticPool zapewnia, że sesje testowe korzystają z jednego połączenia (wymagane dla :memory:)
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Tworzymy klasę Session lokalną dla testów
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture tworzący nową instancję bazy danych i sesji dla każdego testu.

    - Tworzy wszystkie tabele przed testem
    - Zwraca sesję SQLAlchemy
    - Po teście usuwa wszystkie tabele (czysty stan przed kolejnym testem)
    """
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture tworzący klienta testowego FastAPI (TestClient).

    Nadpisuje zależność get_db → tak, aby aplikacja używała testowej sesji bazy danych
    zamiast prawdziwej bazy PostgreSQL.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # nie zamykamy tutaj sesji — robi to db_session fixture

    # Podmiana dependency injection FastAPI
    app.dependency_overrides[get_db] = override_get_db

    # Tworzymy testowego klienta HTTP
    with TestClient(app) as test_client:
        yield test_client

    # Po teście czyścimy nadpisania zależności
    app.dependency_overrides.clear()


@pytest.fixture
def app_fixture():  # DODANO nową fixture dla app
    """
    Fixture zwracający instancję aplikacji FastAPI.
    Używana w testach do nadpisywania dependencies.
    """
    return app


@pytest.fixture
def sample_user(db_session):
    """
    Tworzy przykładowego użytkownika typu READER w testowej bazie danych.
    """
    user = User(
        email="test@example.com",
        hashed_password=hash_password("TestPassword123"),
        full_name="Test User",
        role=UserRole.READER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_librarian(db_session):
    """
    Tworzy przykładowego użytkownika typu LIBRARIAN.
    """
    user = User(
        email="librarian@example.com",
        hashed_password=hash_password("LibPassword123"),
        full_name="Test Librarian",
        role=UserRole.LIBRARIAN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_admin(db_session):
    """
    Tworzy przykładowego użytkownika typu ADMIN.
    """
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("AdminPassword123"),
        full_name="Test Admin",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def mock_admin(db_session):  # DODANO fixture dla mock_admin
    """
    Mock użytkownika ADMIN dla testów dependency overrides.
    """
    from unittest.mock import Mock

    mock = Mock()
    mock.id = "admin-mock-id"
    mock.email = "admin@example.com"
    mock.role = UserRole.ADMIN
    mock.is_active = True
    mock.is_blocked = False
    return mock


@pytest.fixture
def mock_librarian(db_session):  # DODANO fixture dla mock_librarian
    """
    Mock użytkownika LIBRARIAN dla testów dependency overrides.
    """
    from unittest.mock import Mock

    mock = Mock()
    mock.id = "librarian-mock-id"
    mock.email = "librarian@example.com"
    mock.role = UserRole.LIBRARIAN
    mock.is_active = True
    mock.is_blocked = False
    return mock


@pytest.fixture
def auth_headers(client, sample_user):
    """
    Loguje testowego użytkownika i zwraca nagłówki Authorization,
    które można używać w testach chronionych endpointów.

    - wykonuje faktyczne żądanie POST /api/auth/login
    - pobiera access_token z odpowiedzi
    - zwraca nagłówek: {"Authorization": "Bearer <token>"}
    """
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "TestPassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# =============================================================================
# DODATKOWE FIXTURES DLA TESTÓW RBAC
# =============================================================================


@pytest.fixture
def reader_token(client, sample_user):
    """
    Generate JWT token for READER user.
    """
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "TestPassword123"},
    )
    token = response.json()["access_token"]
    return token


@pytest.fixture
def librarian_token(client, sample_librarian):
    """
    Generate JWT token for LIBRARIAN user.
    """
    response = client.post(
        "/api/auth/login",
        json={"email": "librarian@example.com", "password": "LibPassword123"},
    )
    token = response.json()["access_token"]
    return token


@pytest.fixture
def admin_token(client, sample_admin):
    """
    Generate JWT token for ADMIN user.
    """
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "AdminPassword123"},
    )
    token = response.json()["access_token"]
    return token


@pytest.fixture
def test_user(sample_user):
    """
    Alias for sample_user (for consistency with test naming).
    """
    return sample_user
