import pytest
from app.core.security import hash_password
from app.models.user import User, UserRole
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from shared.database import Base, get_db

# Adres testowej bazy danych — SQLite w pamięci
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Silnik bazy danych SQLite działający w pamięci RAM
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Klasa Session lokalna dla testów
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture tworzący nową instancję bazy danych i sesji dla każdego testu.
    """
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def test_app():
    """
    Fixture tworzący testową instancję FastAPI BEZ połączenia z PostgreSQL.
    """
    app = FastAPI()

    # Import routerów z prawidłowymi prefiksami
    try:
        from app.api.auth_routes import router as auth_router

        app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not load auth router: {e}")

    try:
        from app.api.user_routes import router as users_router

        app.include_router(users_router, prefix="/api/users", tags=["users"])
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not load users router: {e}")

    return app


@pytest.fixture(scope="function")
def client(db_session, test_app):
    """
    Fixture tworzący klienta testowego FastAPI (TestClient).
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Podmiana dependency injection FastAPI
    test_app.dependency_overrides[get_db] = override_get_db

    # Tworzymy testowego klienta HTTP
    with TestClient(test_app) as test_client:
        yield test_client

    # Po teście czyścimy nadpisania zależności
    test_app.dependency_overrides.clear()


@pytest.fixture
def app_fixture(test_app):
    """
    Fixture zwracający instancję aplikacji FastAPI.
    Używana w testach do nadpisywania dependencies.
    """
    return test_app


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
def mock_admin(db_session):
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
def mock_librarian(db_session):
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
    Loguje testowego użytkownika i zwraca nagłówki Authorization.
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


@pytest.fixture
def app(test_app):
    """
    Alias for test_app - integration tests expect 'app' fixture.
    """
    return test_app
