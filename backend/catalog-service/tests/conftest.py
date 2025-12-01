"""
Pytest configuration and fixtures for Catalog Service tests.

Wymaganie: Punkt 5 - Opis metod i podejść do testowania
Konfiguracja testów jednostkowych i integracyjnych.
"""

from unittest.mock import Mock

import pytest
from app.main import app
from app.models.book import Book
from app.models.book_copy import BookCopy, CopyStatus
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.shared.database import Base, get_db

# Database URL dla testów (in-memory SQLite)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Tworzenie test engine
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture dla sesji bazodanowej.
    Tworzy czystą bazę danych dla każdego testu.
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
    Fixture dla test clienta FastAPI.
    Używa testowej bazy danych.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def app_fixture():
    """
    Fixture zwracający instancję aplikacji FastAPI.
    Używana w testach do nadpisywania dependencies.
    """
    return app


@pytest.fixture
def mock_librarian():
    """
    Mock użytkownika LIBRARIAN dla testów dependency overrides.
    """
    mock = Mock()
    mock.id = "librarian-uuid-1234"
    mock.email = "librarian@library.com"
    mock.role = "LIBRARIAN"
    mock.is_active = True
    mock.is_blocked = False
    return mock


@pytest.fixture
def mock_admin():
    """
    Mock użytkownika ADMIN dla testów dependency overrides.
    """
    mock = Mock()
    mock.id = "admin-uuid-5678"
    mock.email = "admin@library.com"
    mock.role = "ADMIN"
    mock.is_active = True
    mock.is_blocked = False
    return mock


@pytest.fixture
def mock_reader():
    """
    Mock użytkownika READER dla testów dependency overrides.
    """
    mock = Mock()
    mock.id = "reader-uuid-9012"
    mock.email = "reader@library.com"
    mock.role = "READER"
    mock.is_active = True
    mock.is_blocked = False
    return mock


@pytest.fixture
def sample_book(db_session):
    """
    Fixture tworzący przykładową książkę do testów.
    """
    book = Book(
        title="Test Book Title",
        authors="Test Author",
        isbn="1234567890123",
        publisher="Test Publisher",
        pages=300,
        language="pl",
        description="Test description",
        genre="Fiction",
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book


@pytest.fixture
def sample_book_copy(db_session, sample_book):
    """
    Fixture tworzący przykładowy egzemplarz książki do testów.
    """
    copy = BookCopy(
        book_id=sample_book.id,
        inventory_no="TEST-001",
        status=CopyStatus.AVAILABLE,
        location="Shelf A-1",
    )
    db_session.add(copy)
    db_session.commit()
    db_session.refresh(copy)
    return copy


@pytest.fixture
def multiple_books(db_session):
    """
    Fixture tworzący wiele książek do testów wyszukiwania i filtrowania.
    """
    books = [
        Book(
            title="Python Programming",
            authors="John Doe",
            isbn="1111111111111",
            genre="Programming",
            language="en",
        ),
        Book(
            title="Programowanie w Pythonie",
            authors="Jan Kowalski",
            isbn="2222222222222",
            genre="Programming",
            language="pl",
        ),
        Book(
            title="Fantasy Adventure",
            authors="Jane Smith",
            isbn="3333333333333",
            genre="Fantasy",
            language="en",
        ),
    ]

    for book in books:
        db_session.add(book)

    db_session.commit()

    for book in books:
        db_session.refresh(book)

    return books
