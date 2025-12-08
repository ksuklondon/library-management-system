"""
Testy dla API kar za przetrzymanie.

Wymaganie: NF9 - Testy jednostkowe i integracyjne
Wymaganie: F27 - Płatność kar za przetrzymanie

FIXED: Usunięto /api prefix ze wszystkich endpointów
"""

import uuid
from datetime import datetime, timedelta

from fastapi import status


class TestFineRoutes:
    """Testy dla endpointów kar (F27, NF9)."""

    def test_create_fine_success(self, client, auth_headers_librarian, test_loan):
        """Test: Utworzenie kary przez bibliotekarza (F27, NF9)."""
        data = {
            "loan_id": str(test_loan.id),
            "user_id": test_loan.user_id,
            "amount": 10.0,
        }

        response = client.post("/fines/", json=data, headers=auth_headers_librarian)

        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["amount"] == 10.0
        assert result["paid"] is False
        assert "id" in result

    def test_create_fine_reader_forbidden(self, client, auth_headers_reader, test_loan):
        """Test: Czytelnik nie może tworzyć kar (NF5, NF9)."""
        data = {
            "loan_id": str(test_loan.id),
            "user_id": test_loan.user_id,
            "amount": 10.0,
        }

        response = client.post("/fines/", json=data, headers=auth_headers_reader)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_fine_duplicate(self, client, auth_headers_librarian, test_fine):
        """Test: Próba utworzenia drugiej kary dla tego samego wypożyczenia (NF9)."""
        data = {
            "loan_id": str(test_fine.loan_id),
            "user_id": test_fine.user_id,
            "amount": 10.0,
        }

        response = client.post("/fines/", json=data, headers=auth_headers_librarian)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "już istnieje" in response.json()["detail"].lower()

    def test_get_user_fines(self, client, auth_headers_reader, test_user, test_fine):
        """Test: Pobieranie listy kar użytkownika (F27, NF9)."""
        response = client.get(
            f"/fines/user/{test_user.id}/", headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_user_fines_forbidden(
        self, client, auth_headers_reader, test_librarian
    ):
        """Test: Czytelnik nie może pobierać cudzych kar (NF5, NF9)."""
        response = client.get(
            f"/fines/user/{test_librarian.id}/", headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_user_fines_by_paid_status(
        self, client, auth_headers_reader, test_user, test_fine
    ):
        """Test: Filtrowanie kar użytkownika po statusie płatności (F27, NF9)."""
        response = client.get(
            f"/fines/user/{test_user.id}/?paid=false", headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        for fine in result:
            assert fine["paid"] is False

    def test_pay_fine_success(self, client, auth_headers_reader, test_fine):
        """Test: Opłacenie kary przez użytkownika (F27, NF9)."""
        data = {"payment_method": "card"}

        response = client.patch(
            f"/fines/{test_fine.id}/pay", json=data, headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["paid"] is True
        assert result["paid_at"] is not None

    def test_pay_fine_already_paid(self, client, auth_headers_reader, test_fine, db):
        """Test: Próba ponownej płatności opłaconej kary (F27, NF9)."""
        test_fine.mark_as_paid(payment_method="cash")
        db.commit()
        db.refresh(test_fine)

        data = {"payment_method": "card"}

        response = client.patch(
            f"/fines/{test_fine.id}/pay", json=data, headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_pay_fine_forbidden(self, client, auth_headers_reader, test_librarian, db):
        """Test: Użytkownik nie może opłacić kary należącej do innej osoby (NF5, NF9)."""
        from app.models.fine import Fine
        from app.models.loan import Loan

        loan = Loan(
            user_id=test_librarian.id,
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status="ACTIVE",
        )
        loan.due_date = datetime.utcnow() + timedelta(days=14)
        db.add(loan)
        db.commit()
        db.refresh(loan)

        fine = Fine(loan_id=loan.id, user_id=test_librarian.id, amount=10.0, paid=False)
        db.add(fine)
        db.commit()
        db.refresh(fine)

        data = {"payment_method": "card"}

        response = client.patch(
            f"/fines/{fine.id}/pay", json=data, headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_all_fines_librarian(self, client, auth_headers_librarian, test_fine):
        """Test: Bibliotekarz może listować wszystkie kary (F27, NF5, NF9)."""
        response = client.get("/fines/", headers=auth_headers_librarian)

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_list_all_fines_reader_forbidden(self, client, auth_headers_reader):
        """Test: Czytelnik nie może listować wszystkich kar (NF5, NF9)."""
        response = client.get("/fines/", headers=auth_headers_reader)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_unpaid_total(self, client, auth_headers_librarian, test_fine):
        """Test: Pobieranie sumy nieopłaconych kar (F27, NF9)."""
        response = client.get("/fines/unpaid/total", headers=auth_headers_librarian)

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "total_amount" in result
        assert "count" in result
        assert result["total_amount"] >= 0

    def test_get_unpaid_total_for_user(
        self, client, auth_headers_librarian, test_user, test_fine
    ):
        """Test: Pobieranie sumy nieopłaconych kar dla konkretnego użytkownika (F27, NF9)."""
        response = client.get(
            f"/fines/unpaid/total?user_id={test_user.id}",
            headers=auth_headers_librarian,
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["user_id"] == test_user.id
        assert result["total_amount"] >= 0

    def test_calculate_and_create_fine(
        self, client, auth_headers_librarian, test_overdue_loan
    ):
        """Test: Automatyczne obliczanie i tworzenie kary (F27, NF9)."""
        response = client.patch(
            f"/fines/loan/{test_overdue_loan.id}/calculate",
            headers=auth_headers_librarian,
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["amount"] > 0
        assert result["loan_id"] == str(test_overdue_loan.id)
        assert result["paid"] is False

    def test_calculate_fine_not_overdue(
        self, client, auth_headers_librarian, test_loan
    ):
        """Test: Nie można naliczyć kary dla wypożyczenia, które nie jest przetrzymane (NF9)."""
        response = client.patch(
            f"/fines/loan/{test_loan.id}/calculate", headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_fine_admin(self, client, auth_headers_admin, test_fine):
        """Test: Usunięcie kary przez administratora (NF19, NF5, NF9)."""
        response = client.delete(f"/fines/{test_fine.id}", headers=auth_headers_admin)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_fine_librarian_forbidden(
        self, client, auth_headers_librarian, test_fine
    ):
        """Test: Bibliotekarz nie może usuwać kar (NF5, NF9)."""
        response = client.delete(
            f"/fines/{test_fine.id}", headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_fine_amount_validation(self, client, auth_headers_librarian, test_loan):
        """Test: Walidacja kwoty kary (NF7, NF9)."""
        data = {
            "loan_id": str(test_loan.id),
            "user_id": test_loan.user_id,
            "amount": -5.0,
        }

        response = client.post("/fines/", json=data, headers=auth_headers_librarian)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_fine_not_found(self, client, auth_headers_librarian):
        """Test: Pobranie nieistniejącej kary (NF9)."""
        non_existent_id = uuid.uuid4()

        response = client.get(
            f"/fines/{non_existent_id}/", headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
