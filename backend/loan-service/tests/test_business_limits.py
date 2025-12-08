from datetime import datetime, timedelta

import pytest
from app.models.fine import Fine
from app.models.loan import Loan
from app.models.reservation import Reservation
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_max_reservations_limit(
    async_client: AsyncClient, db, test_user_token, test_user, test_book_copies
):
    """
    Scenariusz 3: Test limitu rezerwacji (max 3 aktywne)

    Użytkownik próbuje utworzyć 4. rezerwację → 422 Unprocessable Entity
    """

    headers = {"Authorization": f"Bearer {test_user_token}"}

    # Krok 1: Utwórz 3 aktywne rezerwacje (osiągnięcie limitu)
    for i in range(3):
        reservation_data = {
            "book_id": str(test_book_copies[i].book_id),
            "book_copy_id": str(test_book_copies[i].id),
        }

        response = await async_client.post(
            "/reservations", json=reservation_data, headers=headers
        )

        assert response.status_code == 201, f"Reservation {i + 1} should succeed"

    # Weryfikacja: 3 aktywne rezerwacje
    active_reservations = (
        db.query(Reservation)
        .filter(Reservation.user_id == test_user.id, Reservation.status == "ACTIVE")
        .count()
    )
    assert active_reservations == 3

    # Krok 2: Próba 4. rezerwacji (przekroczenie limitu)
    fourth_reservation = {
        "book_id": str(test_book_copies[3].book_id),
        "book_copy_id": str(test_book_copies[3].id),
    }

    response = await async_client.post(
        "/reservations", json=fourth_reservation, headers=headers
    )

    # Weryfikacja: 422 Unprocessable Entity
    assert response.status_code == 422
    assert (
        "maximum" in response.json()["detail"].lower()
        or "limit" in response.json()["detail"].lower()
    )

    # Weryfikacja: nadal tylko 3 rezerwacje w bazie
    final_count = (
        db.query(Reservation)
        .filter(Reservation.user_id == test_user.id, Reservation.status == "ACTIVE")
        .count()
    )
    assert final_count == 3


async def test_max_loans_limit(
    async_client: AsyncClient,
    db,
    test_user_token,
    test_user,
    test_book_copies,
    librarian_token,
):
    """
    Scenariusz 3: Test limitu wypożyczeń (max 5 aktywnych)

    Użytkownik próbuje wypożyczyć 6. książkę → 422 Unprocessable Entity
    """

    # Krok 1: Utwórz 5 aktywnych wypożyczeń (osiągnięcie limitu)
    for i in range(5):
        loan = Loan(
            user_id=test_user.id,
            book_copy_id=test_book_copies[i].id,
            borrowed_at=datetime.now(),
            due_date=datetime.now() + timedelta(days=14),
            returned_at=None,  # Aktywne wypożyczenie
        )
        db.add(loan)

    db.commit()

    # Weryfikacja: 5 aktywnych wypożyczeń
    active_loans = (
        db.query(Loan)
        .filter(Loan.user_id == test_user.id, Loan.returned_at.is_(None))
        .count()
    )
    assert active_loans == 5

    # Krok 2: Próba 6. wypożyczenia (przekroczenie limitu)
    # Najpierw utwórz rezerwację
    reservation_data = {
        "book_id": str(test_book_copies[5].book_id),
        "book_copy_id": str(test_book_copies[5].id),
    }

    headers_user = {"Authorization": f"Bearer {test_user_token}"}
    res_response = await async_client.post(
        "/reservations", json=reservation_data, headers=headers_user
    )

    # Rezerwacja powinna się NIE udać z powodu limitu wypożyczeń
    assert res_response.status_code == 422
    assert (
        "loan" in res_response.json()["detail"].lower()
        or "borrow" in res_response.json()["detail"].lower()
    )


async def test_reservation_blocked_by_unpaid_fine(
    async_client: AsyncClient, db, test_user_token, test_user, test_book_copy
):
    """
    Scenariusz 3: Rezerwacja niemożliwa gdy są nieopłacone kary

    Użytkownik z nieopłaconą karą próbuje zarezerwować → 403 Forbidden
    """

    headers = {"Authorization": f"Bearer {test_user_token}"}

    # Krok 1: Utwórz nieopłaconą karę dla użytkownika

    # Najpierw utwórz wypożyczenie (potrzebne dla fine.loan_id)
    loan = Loan(
        user_id=test_user.id,
        book_copy_id=test_book_copy.id,
        borrowed_at=datetime.now() - timedelta(days=20),
        due_date=datetime.now() - timedelta(days=6),
        returned_at=datetime.now(),
    )
    db.add(loan)
    db.commit()

    # Utwórz nieopłaconą karę
    fine = Fine(
        loan_id=loan.id,
        user_id=test_user.id,
        amount=6.00,  # 6 dni × 1.00 PLN
        paid=False,
    )
    db.add(fine)
    db.commit()

    # Weryfikacja: kara istnieje i jest nieopłacona
    unpaid_fines = (
        db.query(Fine)
        .filter(Fine.user_id == test_user.id, Fine.paid == False)  # noqa: E712
        .count()
    )
    assert unpaid_fines == 1

    # Krok 2: Próba rezerwacji z nieopłaconą karą
    reservation_data = {
        "book_id": str(test_book_copy.book_id),
        "book_copy_id": str(test_book_copy.id),
    }

    response = await async_client.post(
        "/reservations", json=reservation_data, headers=headers
    )

    # Weryfikacja: 403 Forbidden
    assert response.status_code == 403
    assert (
        "fine" in response.json()["detail"].lower()
        or "kara" in response.json()["detail"].lower()
    )

    # Weryfikacja: rezerwacja NIE została utworzona
    reservations = (
        db.query(Reservation).filter(Reservation.user_id == test_user.id).count()
    )
    assert reservations == 0


async def test_limits_reset_after_completion(
    async_client: AsyncClient, db, test_user_token, test_user, test_book_copies
):
    """
    Test: Limity liczą tylko AKTYWNE rezerwacje/wypożyczenia

    Anulowane/ukończone rezerwacje nie liczą się do limitu
    """

    headers = {"Authorization": f"Bearer {test_user_token}"}

    # Utwórz 3 rezerwacje i od razu je anuluj
    for i in range(3):
        reservation_data = {
            "book_id": str(test_book_copies[i].book_id),
            "book_copy_id": str(test_book_copies[i].id),
        }

        # Utwórz rezerwację
        response = await async_client.post(
            "/reservations", json=reservation_data, headers=headers
        )
        assert response.status_code == 201

        reservation_id = response.json()["id"]

        # Anuluj rezerwację
        cancel_response = await async_client.delete(
            f"/reservations/{reservation_id}", headers=headers
        )
        assert cancel_response.status_code == 204

    # Weryfikacja: 0 aktywnych rezerwacji
    active = (
        db.query(Reservation)
        .filter(Reservation.user_id == test_user.id, Reservation.status == "ACTIVE")
        .count()
    )
    assert active == 0

    # Nowa rezerwacja powinna się udać (limit się zresetował)
    new_reservation = {
        "book_id": str(test_book_copies[3].book_id),
        "book_copy_id": str(test_book_copies[3].id),
    }

    response = await async_client.post(
        "/reservations", json=new_reservation, headers=headers
    )

    assert response.status_code == 201
