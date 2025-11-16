"""
Testy dla book copy management routes - zarządzanie egzemplarzami.

Wymaganie: Punkt 5 - Opis metod i podejść do testowania
Testy dla F16 (Zarządzanie egzemplarzami - LIBRARIAN/ADMIN)
"""

from unittest.mock import Mock

import pytest
from app.models.book_copy import CopyStatus
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


class TestCreateBookCopy:
    """
    Testy dla tworzenia egzemplarzy (F16).
    """

    def test_create_copy_success(self, client, db_session, sample_book, mock_librarian):
        """Test pomyślnego dodania egzemplarza (F16 - LIBRARIAN)."""
        copy_data = {
            "book_id": str(sample_book.id),
            "inventory_no": "INV-2024-001",
            "location": "Shelf A-2",
        }

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.post("/api/copies/", json=copy_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["inventory_no"] == copy_data["inventory_no"]
        assert data["book_id"] == copy_data["book_id"]
        assert data["status"] == "AVAILABLE"
        assert "id" in data

        app.dependency_overrides.clear()

    def test_create_copy_nonexistent_book(self, client, mock_librarian):
        """Test dodania egzemplarza do nieistniejącej książki."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        copy_data = {"book_id": fake_uuid, "inventory_no": "INV-2024-999"}

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.post("/api/copies/", json=copy_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()

    def test_create_copy_duplicate_inventory_no(
        self, client, db_session, sample_book, sample_book_copy, mock_librarian
    ):
        """Test dodania egzemplarza z duplikującym się numerem inwentarzowym."""
        copy_data = {
            "book_id": str(sample_book.id),
            "inventory_no": sample_book_copy.inventory_no,  # Duplikat!
        }

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.post("/api/copies/", json=copy_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "już istnieje" in response.json()["detail"].lower()

        app.dependency_overrides.clear()


class TestGetCopiesByBook:
    """
    Testy dla pobierania egzemplarzy książki (F16).
    """

    def test_get_copies_by_book(
        self, client, db_session, sample_book, sample_book_copy
    ):
        """Test pobierania egzemplarzy konkretnej książki (F16)."""
        response = client.get(f"/api/copies/book/{sample_book.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["book_id"] == str(sample_book.id)
        assert data[0]["inventory_no"] == sample_book_copy.inventory_no

    def test_get_copies_nonexistent_book(self, client):
        """Test pobierania egzemplarzy nieistniejącej książki."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/copies/book/{fake_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetCopyDetails:
    """
    Testy dla szczegółów egzemplarza (F16).
    """

    def test_get_copy_details(self, client, sample_book_copy):
        """Test pobierania szczegółów egzemplarza (F16)."""
        response = client.get(f"/api/copies/{sample_book_copy.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_book_copy.id)
        assert data["inventory_no"] == sample_book_copy.inventory_no
        assert data["status"] == sample_book_copy.status.value

    def test_get_copy_details_nonexistent(self, client):
        """Test pobierania nieistniejącego egzemplarza."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/copies/{fake_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateBookCopy:
    """
    Testy dla aktualizacji egzemplarzy (F16).
    """

    def test_update_copy_success(
        self, client, db_session, sample_book_copy, mock_librarian
    ):
        """Test pomyślnej aktualizacji egzemplarza (F16)."""
        update_data = {"location": "Shelf B-5"}

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.put(f"/api/copies/{sample_book_copy.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["location"] == "Shelf B-5"

        app.dependency_overrides.clear()

    def test_update_copy_inventory_no_conflict(
        self, client, db_session, sample_book, mock_librarian
    ):
        """Test aktualizacji numeru inwentarzowego na już istniejący."""
        # Stwórz drugi egzemplarz
        from app.models.book_copy import BookCopy

        copy2 = BookCopy(
            book_id=sample_book.id,
            inventory_no="INV-SECOND",
            status=CopyStatus.AVAILABLE,
        )
        db_session.add(copy2)
        db_session.commit()

        # Próba zmiany na istniejący numer
        update_data = {"inventory_no": "INV-SECOND"}

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.put(f"/api/copies/{sample_book_copy.id}", json=update_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        app.dependency_overrides.clear()


class TestUpdateCopyStatus:
    """
    Testy dla zmiany statusu egzemplarza (F16).
    """

    def test_update_copy_status_success(
        self, client, db_session, sample_book_copy, mock_librarian
    ):
        """Test pomyślnej zmiany statusu egzemplarza (F16)."""
        status_data = {"status": "DAMAGED"}

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.patch(
            f"/api/copies/{sample_book_copy.id}/status", json=status_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "DAMAGED"

        app.dependency_overrides.clear()

    def test_update_borrowed_copy_to_damaged(
        self, client, db_session, sample_book_copy, mock_librarian
    ):
        """Test zmiany statusu wypożyczonego egzemplarza."""
        # Ustaw status na BORROWED
        sample_book_copy.status = CopyStatus.BORROWED
        db_session.commit()

        status_data = {"status": "DAMAGED"}

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.LIBRARIAN, UserRole.ADMIN])] = (
            lambda: mock_librarian
        )

        response = client.patch(
            f"/api/copies/{sample_book_copy.id}/status", json=status_data
        )

        # Nie można zmienić statusu wypożyczonego egzemplarza na DAMAGED
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        app.dependency_overrides.clear()


class TestDeleteBookCopy:
    """
    Testy dla usuwania egzemplarzy (F16 - tylko ADMIN).
    """

    def test_delete_copy_success(
        self, client, db_session, sample_book_copy, mock_admin
    ):
        """Test pomyślnego usunięcia egzemplarza (F16 - ADMIN, NF19 - soft delete)."""
        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.delete(f"/api/copies/{sample_book_copy.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Sprawdź soft delete
        db_session.refresh(sample_book_copy)
        assert sample_book_copy.is_deleted == True

        app.dependency_overrides.clear()

    def test_delete_borrowed_copy(
        self, client, db_session, sample_book_copy, mock_admin
    ):
        """Test usuwania wypożyczonego egzemplarza."""
        # Ustaw status na BORROWED
        sample_book_copy.status = CopyStatus.BORROWED
        db_session.commit()

        from backend.shared.dependencies import require_role

        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.delete(f"/api/copies/{sample_book_copy.id}")

        # Nie można usunąć wypożyczonego
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "borrowed" in response.json()["detail"].lower()
            or "wypożyczon" in response.json()["detail"].lower()
        )

        app.dependency_overrides.clear()
