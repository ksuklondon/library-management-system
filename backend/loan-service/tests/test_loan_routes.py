"""
Testy dla API wypożyczeń.

Wymaganie: NF9 - Testy jednostkowe i integracyjne
Wymaganie: F11-F14, F27 - Wypożyczenia i kary
"""

import uuid
from datetime import datetime, timedelta

from fastapi import status


class TestLoanRoutes:
    """Testy dla endpointów wypożyczeń (F11-F14, F27, NF9)."""

    def test_create_loan_success(self, client, auth_headers_librarian, test_user):
        """
        Test: Utworzenie wypożyczenia przez bibliotekarza (F11, NF9).

        Sprawdza scenariusz poprawnej obsługi:
        - użytkownik ma poprawne dane wejściowe
        - bibliotekarz ma uprawnienia do wypożyczenia
        - zwracany obiekt zawiera wymagane pola
        """
        data = {"user_id": test_user.id, "book_copy_id": str(uuid.uuid4())}

        response = client.post("/api/loans/", json=data, headers=auth_headers_librarian)

        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["user_id"] == test_user.id
        assert result["status"] == "ACTIVE"
        assert "id" in result
        assert "due_date" in result

    def test_create_loan_reader_forbidden(self, client, auth_headers_reader, test_user):
        """
        Test: Czytelnik nie może tworzyć wypożyczeń (NF5, NF9).

        Sprawdza poprawność RBAC:
        - READER nie ma uprawnień do wypożyczania książek
        """
        data = {"user_id": test_user.id, "book_copy_id": str(uuid.uuid4())}

        response = client.post("/api/loans/", json=data, headers=auth_headers_reader)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_loan_limit_exceeded(
        self, client, auth_headers_librarian, test_user, multiple_loans
    ):
        """
        Test: Przekroczenie limitu 5 wypożyczeń (NF29, NF9).

        Użytkownik ma już 5 aktywnych wypożyczeń → system powinien odrzucić kolejne.
        """
        data = {"user_id": test_user.id, "book_copy_id": str(uuid.uuid4())}

        response = client.post("/api/loans/", json=data, headers=auth_headers_librarian)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "limit" in response.json()["detail"].lower()

    def test_get_user_loans(self, client, auth_headers_reader, test_user, test_loan):
        """
        Test: Pobieranie wypożyczeń użytkownika (F13, NF9).

        Użytkownik powinien zobaczyć wszystkie swoje wypożyczenia.
        """
        response = client.get(
            f"/api/loans/user/{test_user.id}", headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1
        assert result[0]["id"] == str(test_loan.id)

    def test_get_user_loans_forbidden(
        self, client, auth_headers_reader, test_librarian
    ):
        """
        Test: Brak dostępu do wypożyczeń innych użytkowników (NF5, NF9).

        Czytelnik nie może przeglądać cudzych wypożyczeń.
        """
        response = client.get(
            f"/api/loans/user/{test_librarian.id}", headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_return_loan_success(self, client, auth_headers_librarian, test_loan):
        """
        Test: Zwrot książki przez bibliotekarza (F12, NF9).

        Po zwrocie:
        - status zmienia się na RETURNED
        - returned_at jest ustawione
        """
        response = client.patch(
            f"/api/loans/{test_loan.id}/return", headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["status"] == "RETURNED"
        assert result["returned_at"] is not None

    def test_return_loan_with_fine(
        self, client, auth_headers_librarian, test_overdue_loan
    ):
        """
        Test: Zwrot przetrzymanej książki z naliczeniem kary (F27, NF9).

        System powinien naliczyć karę → fine_amount > 0.
        """
        response = client.patch(
            f"/api/loans/{test_overdue_loan.id}/return", headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["status"] == "RETURNED"
        assert result["fine_amount"] > 0
        assert result["returned_at"] is not None

    def test_return_loan_reader_forbidden(self, client, auth_headers_reader, test_loan):
        """
        Test: Czytelnik nie może zwracać książek (NF5, NF9).
        """
        response = client.patch(
            f"/api/loans/{test_loan.id}/return", headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_extend_loan_success(self, client, auth_headers_reader, test_loan):
        """
        Test: Przedłużenie wypożyczenia (F14, NF9).

        Użytkownik może przedłużyć swoje aktywne wypożyczenie.
        """
        original_due_date = test_loan.due_date
        data = {"days": 7}

        response = client.patch(
            f"/api/loans/{test_loan.id}/extend", json=data, headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        new_due_date = datetime.fromisoformat(result["due_date"].replace("Z", "+00:00"))
        assert new_due_date > original_due_date

    def test_extend_overdue_loan_fail(
        self, client, auth_headers_reader, test_overdue_loan
    ):
        """
        Test: Nie można przedłużyć przetrzymanego wypożyczenia (F14, NF9).

        Przedłużenie jest możliwe tylko dla wypożyczeń terminowych.
        """
        data = {"days": 7}

        response = client.patch(
            f"/api/loans/{test_overdue_loan.id}/extend",
            json=data,
            headers=auth_headers_reader,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_extend_loan_invalid_days(self, client, auth_headers_reader, test_loan):
        """
        Test: Walidacja pól wejściowych – za duża liczba dni (NF7, NF9).

        days może mieć maksymalnie 14 – walidacja Pydantic.
        """
        data = {"days": 20}

        response = client.patch(
            f"/api/loans/{test_loan.id}/extend", json=data, headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_overdue_loans(self, client, auth_headers_librarian, test_overdue_loan):
        """
        Test: Pobieranie listy przetrzymanych wypożyczeń (F27, NF9).

        Bibliotekarz ma dostęp do listy przetrzymanych książek.
        """
        response = client.get("/api/loans/overdue/all", headers=auth_headers_librarian)

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

        overdue_ids = [loan["id"] for loan in result]
        assert str(test_overdue_loan.id) in overdue_ids

    def test_get_overdue_loans_reader_forbidden(self, client, auth_headers_reader):
        """
        Test: Czytelnik nie ma dostępu do listy przetrzymanych wypożyczeń (NF5, NF9).
        """
        response = client.get("/api/loans/overdue/all", headers=auth_headers_reader)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_all_loans_librarian(self, client, auth_headers_librarian, test_loan):
        """
        Test: Bibliotekarz może listować wszystkie wypożyczenia (NF5, NF9).
        """
        response = client.get("/api/loans/", headers=auth_headers_librarian)

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_filter_loans_by_status(self, client, auth_headers_librarian, test_loan):
        """
        Test: Filtrowanie wypożyczeń po statusie (NF9).
        """
        response = client.get(
            "/api/loans/?status=ACTIVE", headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        for loan in result:
            assert loan["status"] == "ACTIVE"

    def test_update_loan_admin(self, client, auth_headers_librarian, test_loan):
        """
        Test: Aktualizacja wypożyczenia (NF9).

        Bibliotekarz może edytować pola wypożyczenia.
        """
        new_due_date = (datetime.utcnow() + timedelta(days=21)).isoformat()
        data = {"due_date": new_due_date}

        response = client.patch(
            f"/api/loans/{test_loan.id}", json=data, headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["due_date"] == new_due_date

    def test_delete_loan_admin_only(self, client, auth_headers_admin, test_loan):
        """
        Test: Tylko admin może usuwać wypożyczenia (NF19, NF5, NF9).

        Soft delete powinien zwracać status 204.
        """
        response = client.delete(
            f"/api/loans/{test_loan.id}", headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_loan_librarian_forbidden(
        self, client, auth_headers_librarian, test_loan
    ):
        """
        Test: Bibliotekarz nie ma uprawnień do usuwania wypożyczeń (NF5, NF9).
        """
        response = client.delete(
            f"/api/loans/{test_loan.id}", headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_loan_not_found(self, client, auth_headers_librarian):
        """
        Test: Pobranie nieistniejącego wypożyczenia → 404 (NF9).
        """
        non_existent_id = uuid.uuid4()

        response = client.get(
            f"/api/loans/{non_existent_id}", headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
