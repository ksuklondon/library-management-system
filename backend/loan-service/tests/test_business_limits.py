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

    Użytkownik próbuje utworzyć 4. rezerwację → 400 Bad Request
    """

    headers = {"Authorization": f"Bearer {test_user_token}"}

    # Zbierz UNIKALNE book_id z test_book_copies
    unique_book_ids = []
    for copy in test_book_copies:
        if copy.book_id not in unique_book_ids:
            unique_book_ids.append(copy.book_id)
        if len(unique_book_ids) == 4:
            break

    assert len(unique_book_ids) >= 4, "Test wymaga min. 4 różnych książek"

    # Krok 1: Utwórz 3 aktywne rezerwacje (różne książki)
    for i in range(3):
        reservation_data = {"book_id": str(unique_book_ids[i])}

        response = await async_client.post(
            "/reservations/", json=reservation_data, headers=headers
        )

        assert response.status_code == 201, f"Reservation {i + 1} should succeed"

    # Weryfikacja: 3 aktywne rezerwacje
    active_reservations = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == test_user.id,
            Reservation.status == "ACTIVE",
        )
        .count()
    )
    assert active_reservations == 3

    # Krok 2: Próba 4. rezerwacji → powinno się nie udać
    fourth_reservation = {"book_id": str(unique_book_ids[3])}

    response = await async_client.post(
        "/reservations/", json=fourth_reservation, headers=headers
    )

    assert response.status_code == 400
    assert "limit" in response.json()["detail"].lower()

    # Weryfikacja: nadal tylko 3 aktywne rezerwacje
    final_count = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == test_user.id,
            Reservation.status == "ACTIVE",
        )
        .count()
    )
    assert final_count == 3


async def test_max_loans_limit(
    async_client: AsyncClient,
    db,
    test_user_token,
    test_user,
    test_book_copies,
):
    """
    Scenariusz 3: Test limitu wypożyczeń (max 5 aktywnych)

    Użytkownik z 5 aktywnymi wypożyczeniami może nadal tworzyć rezerwacje
    (limit dotyczy wypożyczeń, nie rezerwacji)
    """

    for i in range(5):
        loan = Loan(
            user_id=test_user.id,
            book_copy_id=test_book_copies[i].id,
            borrowed_at=datetime.now(),
            due_date=datetime.now() + timedelta(days=14),
            returned_at=None,
        )
        db.add(loan)

    db.commit()

    active_loans = (
        db.query(Loan)
        .filter(Loan.user_id == test_user.id, Loan.returned_at.is_(None))
        .count()
    )
    assert active_loans == 5

    reservation_data = {"book_id": str(test_book_copies[5].book_id)}
    headers = {"Authorization": f"Bearer {test_user_token}"}

    response = await async_client.post(
        "/reservations/", json=reservation_data, headers=headers
    )

    assert response.status_code == 201


async def test_reservation_blocked_by_unpaid_fine(
    async_client: AsyncClient, db, test_user_token, test_user, test_book_copy
):
    """
    Rezerwacja przy nieopłaconej karze – obecnie DOZWOLONA (brak feature)
    """

    headers = {"Authorization": f"Bearer {test_user_token}"}

    loan = Loan(
        user_id=test_user.id,
        book_copy_id=test_book_copy.id,
        borrowed_at=datetime.now() - timedelta(days=20),
        due_date=datetime.now() - timedelta(days=6),
        returned_at=datetime.now(),
    )
    db.add(loan)
    db.commit()

    fine = Fine(
        loan_id=loan.id,
        user_id=test_user.id,
        amount=6.00,
        paid=False,
    )
    db.add(fine)
    db.commit()

    reservation_data = {"book_id": str(test_book_copy.book_id)}

    response = await async_client.post(
        "/reservations/", json=reservation_data, headers=headers
    )

    assert response.status_code == 201


async def test_limits_reset_after_completion(
    async_client: AsyncClient, db, test_user_token, test_user, test_book_copies
):
    """
    Limity liczą tylko AKTYWNE rezerwacje
    """

    headers = {"Authorization": f"Bearer {test_user_token}"}

    for i in range(3):
        response = await async_client.post(
            "/reservations/",
            json={"book_id": str(test_book_copies[i].book_id)},
            headers=headers,
        )
        assert response.status_code == 201

        reservation_id = response.json()["id"]

        cancel_response = await async_client.patch(
            f"/reservations/{reservation_id}",
            json={"status": "CANCELLED"},
            headers=headers,
        )
        assert cancel_response.status_code == 200

    active = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == test_user.id,
            Reservation.status == "ACTIVE",
        )
        .count()
    )
    assert active == 0

    response = await async_client.post(
        "/reservations/",
        json={"book_id": str(test_book_copies[3].book_id)},
        headers=headers,
    )
    assert response.status_code == 201
