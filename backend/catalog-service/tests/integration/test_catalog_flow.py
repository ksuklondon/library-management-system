"""
Testy integracyjne - pełny przepływ użycia katalogu.

Wymaganie: Punkt 5 - Opis metod i podejść do testowania
Testy end-to-end dla scenariuszy użytkownika.
"""

from unittest.mock import Mock

import pytest
from app.models.user import User, UserRole
from fastapi import status


@pytest.fixture
def mock_librarian():
    """Mock użytkownika LIBRARIAN."""
    user = Mock(spec=User)
    user.id = "librarian-uuid-1234"
    user.email = "librarian@library.com"
    user.role = UserRole.LIBRARIAN
    user.is_active = True
    user.is_blocked = False
    return user


@pytest.fixture
def mock_reader():
    """Mock użytkownika READER."""
    user = Mock(spec=User)
    user.id = "reader-uuid-5678"
    user.email = "reader@library.com"
    user.role = UserRole.READER
    user.is_active = True
    user.is_blocked = False
    return user


class TestLibrarianWorkflow:
    """
    Test pełnego przepływu pracy bibliotekarza (F15, F16).
    """

    def test_librarian_adds_book_and_copies(self, client, db_session, mock_librarian):
        """
        Scenariusz: Bibliotekarz dodaje nową książkę i egzemplarze.

        Kroki:
        1. Dodaj książkę
        2. Dodaj 3 egzemplarze
        3. Sprawdź czy książka widoczna w katalogu
        4. Sprawdź dostępność
        """
        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        # KROK 1: Dodaj książkę
        book_data = {
            "title": "The Great Gatsby",
            "authors": "F. Scott Fitzgerald",
            "isbn": "9780743273565",
            "publisher": "Scribner",
            "pages": 180,
            "language": "en",
            "genre": "Classic",
        }

        response = client.post("/api/books/", json=book_data)
        assert response.status_code == status.HTTP_201_CREATED
        book = response.json()
        book_id = book["id"]

        # KROK 2: Dodaj 3 egzemplarze
        for i in range(1, 4):
            copy_data = {
                "book_id": book_id,
                "inventory_no": f"GATSBY-{i:03d}",
                "location": f"Shelf A-{i}",
            }
            response = client.post("/api/copies/", json=copy_data)
            assert response.status_code == status.HTTP_201_CREATED

        # KROK 3: Sprawdź czy książka widoczna w katalogu (bez autentykacji)
        app.dependency_overrides.clear()

        response = client.get("/api/catalog/browse")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["books"][0]["title"] == "The Great Gatsby"

        # KROK 4: Sprawdź dostępność
        assert data["books"][0]["available_copies"] == 3
        assert data["books"][0]["total_copies"] == 3

        app.dependency_overrides.clear()


class TestReaderSearchWorkflow:
    """
    Test przepływu wyszukiwania dla czytelnika (F4, F5, F6, F7).
    """

    def test_reader_searches_and_views_book(self, client, db_session, multiple_books):
        """
        Scenariusz: Czytelnik wyszukuje książkę i ogląda szczegóły.

        Kroki:
        1. Przeglądaj katalog
        2. Filtruj po gatunku
        3. Wyszukaj konkretną książkę
        4. Zobacz szczegóły
        """
        # KROK 1: Przeglądaj katalog (F4)
        response = client.get("/api/catalog/browse")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3

        # KROK 2: Filtruj po gatunku Programming (F6)
        response = client.get("/api/catalog/browse?genre=Programming")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2

        # KROK 3: Wyszukaj "Python" (F5)
        search_data = {"query": "Python", "search_in": "title"}
        response = client.post("/api/catalog/search", json=search_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1

        book_id = data["books"][0]["id"]

        # KROK 4: Zobacz szczegóły książki (F7)
        response = client.get(f"/api/catalog/{book_id}")
        assert response.status_code == status.HTTP_200_OK
        book = response.json()
        assert "Python" in book["title"]
        assert "available_copies" in book
        assert "total_copies" in book


class TestBookLifecycle:
    """
    Test pełnego cyklu życia książki i egzemplarza.
    """

    def test_complete_book_lifecycle(
        self, client, db_session, mock_librarian, mock_admin
    ):
        """
        Scenariusz: Cykl życia książki od dodania do usunięcia.

        Kroki:
        1. Bibliotekarz dodaje książkę
        2. Dodaje egzemplarze
        3. Edytuje informacje o książce
        4. Zmienia status egzemplarza (uszkodzony)
        5. Admin usuwa książkę (soft delete)
        6. Sprawdź czy nie widoczna w katalogu
        """
        from backend.shared.dependencies import require_role

        # KROK 1: Dodaj książkę
        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        book_data = {
            "title": "Test Lifecycle Book",
            "authors": "Test Author",
            "isbn": "1111111111111",
        }

        response = client.post("/api/books/", json=book_data)
        assert response.status_code == status.HTTP_201_CREATED
        book_id = response.json()["id"]

        # KROK 2: Dodaj egzemplarz
        copy_data = {"book_id": book_id, "inventory_no": "LIFE-001"}
        response = client.post("/api/copies/", json=copy_data)
        assert response.status_code == status.HTTP_201_CREATED
        copy_id = response.json()["id"]

        # KROK 3: Edytuj książkę
        update_data = {"pages": 500}
        response = client.put(f"/api/books/{book_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pages"] == 500

        # KROK 4: Zmień status egzemplarza na DAMAGED
        status_data = {"status": "DAMAGED"}
        response = client.patch(f"/api/copies/{copy_id}/status", json=status_data)
        assert response.status_code == status.HTTP_200_OK

        # KROK 5: Admin usuwa książkę
        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.delete(f"/api/books/{book_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # KROK 6: Sprawdź czy nie widoczna w katalogu
        app.dependency_overrides.clear()

        response = client.get("/api/catalog/browse")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Książka nie powinna być widoczna (soft delete)
        book_titles = [book["title"] for book in data["books"]]
        assert "Test Lifecycle Book" not in book_titles

        app.dependency_overrides.clear()


class TestPaginationFlow:
    """
    Test przepływu z paginacją (NF20).
    """

    def test_pagination_through_catalog(self, client, db_session, mock_librarian):
        """
        Scenariusz: Przeglądanie dużego katalogu z paginacją.

        Kroki:
        1. Dodaj 25 książek
        2. Przeglądaj stronami (10 na stronę)
        3. Sprawdź wszystkie strony
        """
        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        # KROK 1: Dodaj 25 książek
        for i in range(1, 26):
            book_data = {
                "title": f"Book {i:02d}",
                "authors": f"Author {i}",
                "isbn": f"{i:013d}",
            }
            response = client.post("/api/books/", json=book_data)
            assert response.status_code == status.HTTP_201_CREATED

        app.dependency_overrides.clear()

        # KROK 2 & 3: Przeglądaj stronami
        # Strona 1
        response = client.get("/api/catalog/browse?page=1&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 25
        assert len(data["books"]) == 10
        assert data["page"] == 1
        assert data["total_pages"] == 3

        # Strona 2
        response = client.get("/api/catalog/browse?page=2&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["books"]) == 10
        assert data["page"] == 2

        # Strona 3 (ostatnia)
        response = client.get("/api/catalog/browse?page=3&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["books"]) == 5  # Pozostałe 5 książek
        assert data["page"] == 3
