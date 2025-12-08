"""
Testy dla API rezerwacji.

Wymaganie: NF9 - Testy jednostkowe i integracyjne
Wymaganie: F8-F10 - Rezerwacje książek

FIXED: Zmieniono /api/reservations/ na /reservations/
"""

import uuid
from datetime import datetime, timedelta

from fastapi import status


class TestReservationRoutes:
    """Testy dla endpointów rezerwacji (F8-F10, NF9)."""

    def test_create_reservation_success(self, client, auth_headers_reader):
        """
        Test: Utworzenie rezerwacji (F8, NF9).

        FIXED: Usunięto /api prefix
        """
        # Arrange
        book_id = str(uuid.uuid4())
        data = {"book_id": book_id}

        # Act - FIXED: /api/reservations/ → /reservations/
        response = client.post("/reservations/", json=data, headers=auth_headers_reader)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["book_id"] == book_id
        assert result["status"] == "ACTIVE"
        assert "id" in result
        assert "expires_at" in result

    def test_create_reservation_unauthorized(self, client):
        """
        Test: Próba utworzenia rezerwacji bez autoryzacji (NF5, NF9).

        FIXED: Usunięto /api prefix
        """
        # Arrange
        data = {"book_id": str(uuid.uuid4())}

        # Act - FIXED: /api/reservations/ → /reservations/
        response = client.post("/reservations/", json=data)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_reservation_limit_exceeded(
        self, client, auth_headers_reader, multiple_reservations
    ):
        """
        Test: Przekroczenie limitu 3 rezerwacji (NF29, NF9).

        FIXED: Usunięto /api prefix
        """
        # Arrange - użytkownik ma już 3 aktywne rezerwacje
        data = {"book_id": str(uuid.uuid4())}

        # Act - FIXED
        response = client.post("/reservations/", json=data, headers=auth_headers_reader)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "limit" in response.json()["detail"].lower()

    def test_get_user_reservations(
        self, client, auth_headers_reader, test_user, test_reservation
    ):
        """
        Test: Pobieranie rezerwacji użytkownika (F9, NF9).

        FIXED: Usunięto /api prefix
        """
        # Act - FIXED
        response = client.get(
            f"/reservations/user/{test_user.id}/", headers=auth_headers_reader
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1
        assert result[0]["id"] == str(test_reservation.id)

    def test_get_user_reservations_forbidden(
        self, client, auth_headers_reader, test_librarian
    ):
        """
        Test: Brak dostępu do rezerwacji innych użytkowników (NF5, NF9).

        FIXED: Usunięto /api prefix
        """
        # Act - FIXED
        response = client.get(
            f"/reservations/user/{test_librarian.id}/", headers=auth_headers_reader
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_reservation_by_id(self, client, auth_headers_reader, test_reservation):
        """
        Test: Pobieranie szczegółów rezerwacji (F9, NF9).

        FIXED: Usunięto /api prefix
        """
        # Act - FIXED
        response = client.get(
            f"/reservations/{test_reservation.id}/", headers=auth_headers_reader
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["id"] == str(test_reservation.id)
        assert result["status"] == test_reservation.status

    def test_cancel_reservation_success(
        self, client, auth_headers_reader, test_reservation
    ):
        """
        Test: Anulowanie rezerwacji (F10, NF9).

        FIXED: Usunięto /api prefix
        """
        # Arrange
        data = {"status": "CANCELLED"}

        # Act - FIXED
        response = client.patch(
            f"/reservations/{test_reservation.id}/",
            json=data,
            headers=auth_headers_reader,
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["status"] == "CANCELLED"

    def test_cancel_reservation_forbidden(
        self, client, auth_headers_reader, test_librarian, db
    ):
        """
        Test: Brak dostępu do anulowania rezerwacji innego użytkownika (NF5, NF9).

        FIXED: Usunięto /api prefix
        """
        # Arrange - utwórz rezerwację dla bibliotekarza
        from app.models.reservation import Reservation, ReservationStatus

        reservation = Reservation(
            user_id=test_librarian.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE,
        )
        reservation.expires_at = datetime.utcnow() + timedelta(days=3)
        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        data = {"status": "CANCELLED"}

        # Act - FIXED
        response = client.patch(
            f"/reservations/{reservation.id}/",
            json=data,
            headers=auth_headers_reader,
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_reservation_librarian(
        self, client, auth_headers_librarian, test_reservation
    ):
        """
        Test: Usunięcie rezerwacji przez bibliotekarza (NF19, NF9).

        FIXED: Usunięto /api prefix
        """
        # Act - FIXED
        response = client.delete(
            f"/reservations/{test_reservation.id}/", headers=auth_headers_librarian
        )

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft delete - FIXED
        get_response = client.get(
            f"/reservations/{test_reservation.id}/", headers=auth_headers_librarian
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_reservation_reader_forbidden(
        self, client, auth_headers_reader, test_reservation
    ):
        """
        Test: Czytelnik nie może usunąć rezerwacji (NF5, NF9).

        FIXED: Usunięto /api prefix
        """
        # Act - FIXED
        response = client.delete(
            f"/reservations/{test_reservation.id}/", headers=auth_headers_reader
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_all_reservations_librarian(
        self, client, auth_headers_librarian, test_reservation
    ):
        """
        Test: Bibliotekarz może listować wszystkie rezerwacje (NF5, NF9).

        FIXED: Usunięto /api prefix
        """
        # Act - FIXED
        response = client.get("/reservations/", headers=auth_headers_librarian)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_list_all_reservations_reader_forbidden(self, client, auth_headers_reader):
        """
        Test: Czytelnik nie może listować wszystkich rezerwacji (NF5, NF9).

        FIXED: Usunięto /api prefix
        """
        # Act - FIXED
        response = client.get("/reservations/", headers=auth_headers_reader)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_reservations_by_status(
        self, client, auth_headers_librarian, test_reservation
    ):
        """
        Test: Filtrowanie rezerwacji po statusie (NF9).

        FIXED: Usunięto /api prefix
        """
        # Act - FIXED
        response = client.get(
            "/reservations/?status=ACTIVE", headers=auth_headers_librarian
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        for reservation in result:
            assert reservation["status"] == "ACTIVE"

    def test_create_reservation_invalid_book_id(self, client, auth_headers_reader):
        """
        Test: Walidacja book_id (NF7, NF9).

        FIXED: Usunięto /api prefix
        """
        # Arrange
        data = {"book_id": "invalid-uuid"}

        # Act - FIXED
        response = client.post("/reservations/", json=data, headers=auth_headers_reader)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_reservation_not_found(self, client, auth_headers_reader):
        """
        Test: Rezerwacja nie istnieje (NF9).

        FIXED: Usunięto /api prefix
        """
        # Arrange
        non_existent_id = uuid.uuid4()

        # Act - FIXED
        response = client.get(
            f"/reservations/{non_existent_id}/", headers=auth_headers_reader
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
