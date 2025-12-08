"""
Testy integracyjne dla Loan Service.

Wymaganie: NF9 - Testy integracyjne
Wymaganie: F8-F14, F27 - Pełne scenariusze użycia

FIXED: Usunięto /api prefix ze wszystkich endpointów
"""

import uuid
from datetime import datetime

from fastapi import status


class TestReservationToLoanFlow:
    """Testy integracyjne: rezerwacja -> wypożyczenie (F8-F11, NF9)."""

    def test_full_reservation_to_loan_flow(
        self, client, auth_headers_reader, auth_headers_librarian, test_user
    ):
        """Test: Pełny flow: utwórz rezerwację -> zrealizuj jako wypożyczenie (F8-F11, NF9)."""

        # KROK 1: Czytelnik tworzy rezerwację
        book_id = str(uuid.uuid4())
        reservation_data = {"book_id": book_id}

        reservation_response = client.post(
            "/reservations/", json=reservation_data, headers=auth_headers_reader
        )

        assert reservation_response.status_code == status.HTTP_201_CREATED
        reservation = reservation_response.json()  # noqa: F841

        # KROK 2: Bibliotekarz realizuje rezerwację jako wypożyczenie
        book_copy_id = str(uuid.uuid4())
        loan_data = {"user_id": test_user.id, "book_copy_id": book_copy_id}

        loan_response = client.post(
            "/loans/", json=loan_data, headers=auth_headers_librarian
        )

        assert loan_response.status_code == status.HTTP_201_CREATED
        loan = loan_response.json()
        assert loan["user_id"] == test_user.id
        assert loan["book_copy_id"] == book_copy_id
        assert loan["status"] == "ACTIVE"


class TestLoanReturnFlow:
    """Testy integracyjne: wypożyczenie -> zwrot (F11-F12, NF9)."""

    def test_issue_and_return_on_time(self, client, auth_headers_librarian, test_user):
        """Test: Wypożycz -> Zwróć na czas bez kary (F11-F12, NF9)."""

        # KROK 1: Wypożyczenie książki
        loan_data = {"user_id": test_user.id, "book_copy_id": str(uuid.uuid4())}

        loan_response = client.post(
            "/loans/", json=loan_data, headers=auth_headers_librarian
        )

        assert loan_response.status_code == status.HTTP_201_CREATED
        loan = loan_response.json()
        loan_id = loan["id"]

        # KROK 2: Zwrot książki
        return_response = client.patch(
            f"/loans/{loan_id}/return", headers=auth_headers_librarian
        )

        assert return_response.status_code == status.HTTP_200_OK
        returned_loan = return_response.json()
        assert returned_loan["status"] == "RETURNED"
        assert returned_loan["returned_at"] is not None
        assert returned_loan["fine_amount"] == 0.0

    def test_issue_and_return_with_fine(
        self, client, auth_headers_librarian, test_overdue_loan
    ):
        """Test: Zwróć przetrzymaną książkę z naliczoną karą (F12, F27, NF9)."""

        return_response = client.patch(
            f"/loans/{test_overdue_loan.id}/return", headers=auth_headers_librarian
        )

        assert return_response.status_code == status.HTTP_200_OK
        returned_loan = return_response.json()
        assert returned_loan["status"] == "RETURNED"
        assert returned_loan["fine_amount"] > 0


class TestLoanExtensionFlow:
    """Testy integracyjne: przedłużanie wypożyczeń (F14, NF9)."""

    def test_extend_loan_before_due_date(self, client, auth_headers_reader, test_loan):
        """Test: Przedłuż wypożyczenie przed terminem (F14, NF9)."""

        loan_response = client.get(
            f"/loans/{test_loan.id}/", headers=auth_headers_reader
        )
        original_loan = loan_response.json()
        original_due_date = datetime.fromisoformat(
            original_loan["due_date"].replace("Z", "+00:00")
        )

        extend_data = {"days": 7}
        extend_response = client.patch(
            f"/loans/{test_loan.id}/extend",
            json=extend_data,
            headers=auth_headers_reader,
        )

        assert extend_response.status_code == status.HTTP_200_OK
        extended_loan = extend_response.json()
        new_due_date = datetime.fromisoformat(
            extended_loan["due_date"].replace("Z", "+00:00")
        )
        assert new_due_date > original_due_date

    def test_cannot_extend_overdue_loan(
        self, client, auth_headers_reader, test_overdue_loan
    ):
        """Test: Nie można przedłużyć przetrzymanego wypożyczenia (F14, NF9)."""

        extend_data = {"days": 7}
        extend_response = client.patch(
            f"/loans/{test_overdue_loan.id}/extend",
            json=extend_data,
            headers=auth_headers_reader,
        )

        assert extend_response.status_code == status.HTTP_400_BAD_REQUEST


class TestFinePaymentFlow:
    """Testy integracyjne: kary -> płatność (F27, NF9)."""

    def test_create_fine_and_pay(
        self, client, auth_headers_librarian, auth_headers_reader, test_overdue_loan
    ):
        """Test: Utwórz karę -> Opłać (F27, NF9)."""

        # KROK 1: Bibliotekarz tworzy karę
        fine_data = {
            "loan_id": str(test_overdue_loan.id),
            "user_id": test_overdue_loan.user_id,
            "amount": 10.0,
        }

        fine_response = client.post(
            "/fines/", json=fine_data, headers=auth_headers_librarian
        )

        assert fine_response.status_code == status.HTTP_201_CREATED
        fine = fine_response.json()
        fine_id = fine["id"]
        assert fine["paid"] is False

        # KROK 2: Czytelnik płaci karę
        payment_data = {"payment_method": "card"}
        payment_response = client.patch(
            f"/fines/{fine_id}/pay", json=payment_data, headers=auth_headers_reader
        )

        assert payment_response.status_code == status.HTTP_200_OK
        paid_fine = payment_response.json()
        assert paid_fine["paid"] is True
        assert paid_fine["paid_at"] is not None

    def test_return_overdue_and_calculate_fine(
        self, client, auth_headers_librarian, test_overdue_loan
    ):
        """Test: Zwrot przetrzymanej książki -> automatyczne obliczenie kary (F12, F27, NF9)."""

        return_response = client.patch(
            f"/loans/{test_overdue_loan.id}/return", headers=auth_headers_librarian
        )

        assert return_response.status_code == status.HTTP_200_OK
        returned_loan = return_response.json()
        assert returned_loan["fine_amount"] > 0

        fines_response = client.get(
            f"/fines/user/{test_overdue_loan.user_id}/",
            headers=auth_headers_librarian,
        )

        assert fines_response.status_code == status.HTTP_200_OK
        fines = fines_response.json()
        assert len(fines) > 0


class TestUserLimitsFlow:
    """Testy integracyjne: limity użytkownika (NF29, NF9)."""

    def test_max_reservations_limit(
        self, client, auth_headers_reader, multiple_reservations
    ):
        """Test: Przekroczenie limitu 3 rezerwacji (NF29, NF9)."""

        reservation_data = {"book_id": str(uuid.uuid4())}
        response = client.post(
            "/reservations/", json=reservation_data, headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "limit" in response.json()["detail"].lower()

    def test_max_loans_limit(
        self, client, auth_headers_librarian, test_user, multiple_loans
    ):
        """Test: Przekroczenie limitu 5 wypożyczeń (NF29, NF9)."""

        loan_data = {"user_id": test_user.id, "book_copy_id": str(uuid.uuid4())}
        response = client.post(
            "/loans/", json=loan_data, headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "limit" in response.json()["detail"].lower()


class TestRBACFlow:
    """Testy integracyjne: kontrola dostępu RBAC (NF5, NF9)."""

    def test_reader_cannot_issue_loans(self, client, auth_headers_reader, test_user):
        """Test: Czytelnik nie może wypożyczać książek (NF5, NF9)."""

        loan_data = {"user_id": test_user.id, "book_copy_id": str(uuid.uuid4())}
        response = client.post("/loans/", json=loan_data, headers=auth_headers_reader)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_librarian_can_issue_loans(self, client, auth_headers_librarian, test_user):
        """Test: Bibliotekarz może wypożyczać książki (NF5, NF9)."""

        loan_data = {"user_id": test_user.id, "book_copy_id": str(uuid.uuid4())}
        response = client.post(
            "/loans/", json=loan_data, headers=auth_headers_librarian
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_reader_can_only_access_own_data(
        self, client, auth_headers_reader, test_librarian
    ):
        """Test: Czytelnik może tylko przeglądać swoje dane (NF5, NF9)."""

        response = client.get(
            f"/loans/user/{test_librarian.id}/", headers=auth_headers_reader
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSoftDeleteFlow:
    """Testy integracyjne: soft delete (NF19, NF9)."""

    def test_soft_delete_reservation(
        self, client, auth_headers_librarian, test_reservation
    ):
        """Test: Soft delete rezerwacji (NF19, NF9)."""

        delete_response = client.delete(
            f"/reservations/{test_reservation.id}/", headers=auth_headers_librarian
        )

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        get_response = client.get(
            f"/reservations/{test_reservation.id}/", headers=auth_headers_librarian
        )

        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_soft_delete_loan(self, client, auth_headers_admin, test_loan):
        """Test: Soft delete wypożyczenia (tylko admin) (NF19, NF5, NF9)."""

        delete_response = client.delete(
            f"/loans/{test_loan.id}", headers=auth_headers_admin
        )

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        get_response = client.get(f"/loans/{test_loan.id}/", headers=auth_headers_admin)

        assert get_response.status_code == status.HTTP_404_NOT_FOUND
