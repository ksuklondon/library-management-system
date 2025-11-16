"""
Testy dla book management routes - zarządzanie książkami.

Wymaganie: Punkt 5 - Opis metod i podejść do testowania
Testy dla F15 (Zarządzanie książkami - LIBRARIAN/ADMIN)
"""

from unittest.mock import Mock

import pytest
from app.models.user import User, UserRole
from fastapi import status


@pytest.fixture
def mock_librarian():
    """Mock użytkownika LIBRARIAN do testów."""
    user = Mock(spec=User)
    user.id = "librarian-uuid-1234"
    user.email = "librarian@library.com"
    user.role = UserRole.LIBRARIAN
    user.is_active = True
    user.is_blocked = False
    return user


@pytest.fixture
def mock_admin():
    """Mock użytkownika ADMIN do testów."""
    user = Mock(spec=User)
    user.id = "admin-uuid-5678"
    user.email = "admin@library.com"
    user.role = UserRole.ADMIN
    user.is_active = True
    user.is_blocked = False
    return user


class TestCreateBook:
    """
    Testy dla tworzenia książek (F15).
    """

    def test_create_book_success(self, client, db_session, mock_librarian):
        """Test pomyślnego dodania książki (F15 - LIBRARIAN)."""
        book_data = {
            "title": "New Book",
            "authors": "New Author",
            "isbn": "9781234567890",
            "publisher": "Test Publisher",
            "pages": 250,
            "language": "pl",
            "genre": "Fiction",
        }

        # Mock autoryzacji
        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.post("/api/books/", json=book_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == book_data["title"]
        assert data["authors"] == book_data["authors"]
        assert data["isbn"] == book_data["isbn"]
        assert "id" in data

        app.dependency_overrides.clear()

    def test_create_book_duplicate_isbn(
        self, client, db_session, sample_book, mock_librarian
    ):
        """Test dodania książki z duplikującym się ISBN (F15)."""
        book_data = {
            "title": "Different Title",
            "authors": "Different Author",
            "isbn": sample_book.isbn,  # Duplikat!
            "publisher": "Test Publisher",
        }

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.post("/api/books/", json=book_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "już istnieje" in response.json()["detail"].lower()

        app.dependency_overrides.clear()

    def test_create_book_invalid_isbn(self, client, mock_librarian):
        """Test walidacji ISBN (NF7 - walidacja danych)."""
        book_data = {
            "title": "Test Book",
            "authors": "Test Author",
            "isbn": "invalid-isbn",  # Za krótki
        }

        response = client.post("/api/books/", json=book_data)

        # Pydantic validation powinno odrzucić
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateBook:
    """
    Testy dla aktualizacji książek (F15).
    """

    def test_update_book_success(self, client, db_session, sample_book, mock_librarian):
        """Test pomyślnej aktualizacji książki (F15)."""
        update_data = {"title": "Updated Title", "pages": 350}

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.put(f"/api/books/{sample_book.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["pages"] == 350
        assert data["authors"] == sample_book.authors  # Nie zmienione

        app.dependency_overrides.clear()

    def test_update_book_nonexistent(self, client, mock_librarian):
        """Test aktualizacji nieistniejącej książki."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        update_data = {"title": "New Title"}

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.put(f"/api/books/{fake_uuid}", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()

    def test_update_book_isbn_conflict(
        self, client, db_session, multiple_books, mock_librarian
    ):
        """Test aktualizacji ISBN na już istniejący."""
        book1 = multiple_books[0]
        book2 = multiple_books[1]

        update_data = {"isbn": book2.isbn}  # ISBN książki 2

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.put(f"/api/books/{book1.id}", json=update_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        app.dependency_overrides.clear()


class TestDeleteBook:
    """
    Testy dla usuwania książek (F15 - tylko ADMIN).
    """

    def test_delete_book_success(self, client, db_session, sample_book, mock_admin):
        """Test pomyślnego usunięcia książki (F15 - ADMIN, NF19 - soft delete)."""
        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.delete(f"/api/books/{sample_book.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Sprawdź soft delete
        db_session.refresh(sample_book)
        assert sample_book.is_deleted == True
        assert sample_book.deleted_by == mock_admin.id

        app.dependency_overrides.clear()

    def test_delete_book_with_active_copies(
        self, client, db_session, sample_book, sample_book_copy, mock_admin
    ):
        """Test usuwania książki z wypożyczonym egzemplarzem."""
        # Ustaw status na BORROWED
        sample_book_copy.status = "BORROWED"
        db_session.commit()

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.delete(f"/api/books/{sample_book.id}")

        # Nie można usunąć
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "wypożyczonych" in response.json()["detail"].lower()

        app.dependency_overrides.clear()

    def test_delete_book_nonexistent(self, client, mock_admin):
        """Test usuwania nieistniejącej książki."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.delete(f"/api/books/{fake_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()


class TestGetAllBooks:
    """
    Testy dla pobierania wszystkich książek (zarządzanie).
    """

    def test_get_all_books_management(
        self, client, db_session, multiple_books, mock_librarian
    ):
        """Test pobierania wszystkich książek dla zarządzania (F15)."""
        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.get("/api/books/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

        app.dependency_overrides.clear()

    def test_get_all_books_include_deleted(
        self, client, db_session, sample_book, mock_admin
    ):
        """Test pobierania z usuniętymi książkami (soft delete - NF19)."""
        # Usuń książkę (soft delete)
        sample_book.is_deleted = True
        db_session.commit()

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_admin
        )

        # Bez include_deleted
        response = client.get("/api/books/")
        assert len(response.json()) == 0

        # Z include_deleted
        response = client.get("/api/books/?include_deleted=true")
        assert len(response.json()) == 1

        app.dependency_overrides.clear()
