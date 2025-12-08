import asyncio

import pytest
from app.models.reservation import Reservation
from httpx import AsyncClient, Response

pytestmark = pytest.mark.asyncio


async def test_race_condition_reservation(
    async_client: AsyncClient, db, test_user_token, test_book_copy
):
    """
    Scenariusz 1: Race Condition przy rezerwacji

    FIXED: Usunięto async with - async_client już jest gotowy do użycia
    """

    # Przygotowanie
    headers_user1 = {"Authorization": f"Bearer {test_user_token}"}
    headers_user2 = {"Authorization": f"Bearer {test_user_token}"}

    reservation_data = {
        "book_id": str(test_book_copy.book_id),
    }

    # FIXED: Bezpośrednie użycie async_client (nie async with!)
    async def create_reservation(headers):
        return await async_client.post(
            "/reservations/", json=reservation_data, headers=headers
        )

    # Wykonanie równoczesnych requestów
    results = await asyncio.gather(
        create_reservation(headers_user1),
        create_reservation(headers_user2),
        return_exceptions=False,
    )

    response1, response2 = results

    # Weryfikacja: jeden sukces (201), jeden konflikt (400/409)
    status_codes = sorted([response1.status_code, response2.status_code])

    assert status_codes[0] == 201, f"Expected first to be 201, got {status_codes}"
    assert status_codes[1] in [400, 409], (
        f"Expected second to be 400 or 409, got {status_codes}"
    )

    # Weryfikacja w bazie: dokładnie 1 rezerwacja
    reservations = (
        db.query(Reservation)
        .filter(Reservation.book_id == test_book_copy.book_id)
        .all()
    )
    assert len(reservations) == 1, f"Expected 1 reservation, found {len(reservations)}"


async def test_race_condition_multiple_users(
    async_client: AsyncClient, db, test_user_token, test_book_copy
):
    """
    Rozszerzony test: 5 użytkowników próbuje zarezerwować ten sam egzemplarz

    FIXED: Usunięto async with
    """

    tokens = [test_user_token for _ in range(5)]

    reservation_data = {
        "book_id": str(test_book_copy.book_id),
    }

    # FIXED: Bezpośrednie użycie async_client
    async def create_reservation(token):
        headers = {"Authorization": f"Bearer {token}"}
        return await async_client.post(
            "/reservations/", json=reservation_data, headers=headers
        )

    # Równoczesne requesty
    results = await asyncio.gather(
        *[create_reservation(token) for token in tokens], return_exceptions=False
    )

    # Weryfikacja: dokładnie 1 sukces (201), reszta konflikt (400/409)
    success_count = sum(
        1 for r in results if isinstance(r, Response) and r.status_code == 201
    )
    conflict_count = sum(
        1 for r in results if isinstance(r, Response) and r.status_code in [400, 409]
    )

    assert success_count == 1, f"Expected 1 success, got {success_count}"
    assert conflict_count >= 1, f"Expected at least 1 conflict, got {conflict_count}"

    # Weryfikacja w bazie
    reservations = (
        db.query(Reservation)
        .filter(Reservation.book_id == test_book_copy.book_id)
        .all()
    )
    assert len(reservations) == 1
