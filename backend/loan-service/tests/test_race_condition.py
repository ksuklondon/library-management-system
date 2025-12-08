import asyncio

import pytest
from app.models.reservation import Reservation
from httpx import AsyncClient, Response
from sqlalchemy import select

pytestmark = pytest.mark.asyncio


async def test_race_condition_reservation(
    async_client: AsyncClient, db, test_user_token, test_book_copy
):
    """
    Scenariusz 1: Race Condition przy rezerwacji

    Opis: Dwóch użytkowników jednocześnie próbuje zarezerwować ten sam egzemplarz.
    Implementacja: SELECT FOR UPDATE w transakcji ACID zapobiega race condition.

    Oczekiwany rezultat:
    - Tylko jeden użytkownik otrzymuje rezerwację (201 Created)
    - Drugi otrzymuje konflikt (409 Conflict)
    - W bazie istnieje dokładnie 1 rezerwacja
    """

    # Przygotowanie: dwóch użytkowników, ten sam egzemplarz
    headers_user1 = {"Authorization": f"Bearer {test_user_token}"}
    headers_user2 = {
        "Authorization": f"Bearer {test_user_token}"
    }  # Symulacja drugiego użytkownika

    reservation_data = {
        "book_id": str(test_book_copy.book_id),
        "book_copy_id": str(test_book_copy.id),
    }

    # Symulacja równoczesnych requestów
    async def create_reservation(headers):
        return await async_client.post(
            "/reservations", json=reservation_data, headers=headers
        )

    # Wykonanie równoczesnych requestów
    results = await asyncio.gather(
        create_reservation(headers_user1),
        create_reservation(headers_user2),
        return_exceptions=False,  # Changed to False to avoid exceptions
    )

    response1, response2 = results

    # Weryfikacja: dokładnie jeden sukces (201), jeden konflikt (409)
    status_codes = sorted([response1.status_code, response2.status_code])
    assert status_codes == [201, 409], f"Expected [201, 409], got {status_codes}"

    # Weryfikacja w bazie: dokładnie 1 rezerwacja
    stmt = select(Reservation).where(Reservation.book_copy_id == test_book_copy.id)
    reservations = db.execute(stmt).scalars().all()
    assert len(reservations) == 1, f"Expected 1 reservation, found {len(reservations)}"

    # Weryfikacja statusu egzemplarza
    db.refresh(test_book_copy)
    assert test_book_copy.status == "RESERVED", (
        f"Expected RESERVED, got {test_book_copy.status}"
    )


async def test_race_condition_multiple_users(
    async_client: AsyncClient, db, test_user_token, test_book_copy
):
    """
    Rozszerzony test: 5 użytkowników próbuje zarezerwować ten sam egzemplarz
    """

    # Przygotowanie 5 tokenów (symulacja 5 użytkowników)
    tokens = [test_user_token for _ in range(5)]

    reservation_data = {
        "book_id": str(test_book_copy.book_id),
        "book_copy_id": str(test_book_copy.id),
    }

    async def create_reservation(token):
        headers = {"Authorization": f"Bearer {token}"}
        return await async_client.post(
            "/reservations", json=reservation_data, headers=headers
        )

    # Równoczesne requesty
    results = await asyncio.gather(
        *[create_reservation(token) for token in tokens], return_exceptions=False
    )

    # Weryfikacja: dokładnie 1 sukces (201), reszta konflikt (409)
    success_count = sum(
        1 for r in results if isinstance(r, Response) and r.status_code == 201
    )
    conflict_count = sum(
        1 for r in results if isinstance(r, Response) and r.status_code == 409
    )

    assert success_count == 1, f"Expected 1 success, got {success_count}"
    assert conflict_count >= 1, f"Expected at least 1 conflict, got {conflict_count}"

    # Weryfikacja w bazie
    stmt = select(Reservation).where(Reservation.book_copy_id == test_book_copy.id)
    reservations = db.execute(stmt).scalars().all()
    assert len(reservations) == 1
