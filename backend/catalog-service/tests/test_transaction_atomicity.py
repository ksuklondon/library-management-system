from unittest.mock import patch

import pytest
from app.models.book_copy import BookCopy
from app.models.loan import Loan
from httpx import AsyncClient
from sqlalchemy import select

pytestmark = pytest.mark.asyncio


async def test_checkout_transaction_atomicity_success(
    async_client: AsyncClient, db_session, librarian_token, test_reservation
):
    """
    Scenariusz 2: Transakcyjność checkout - sukces

    Opis: Checkout wymaga atomowej zmiany rezerwacji, egzemplarza i utworzenia wypożyczenia.
    Wszystkie operacje muszą się udać lub wszystkie być wycofane.

    Test pozytywny: wszystkie operacje się udają
    """

    headers = {"Authorization": f"Bearer {librarian_token}"}

    checkout_data = {
        "reservation_id": str(test_reservation.id),
        "user_id": str(test_reservation.user_id),
    }

    # Stan przed checkout
    initial_reservation_status = test_reservation.status
    initial_copy_status = test_reservation.book_copy.status
    initial_loans_count = db_session.execute(select(Loan)).scalars().all()

    assert initial_reservation_status == "ACTIVE"
    assert initial_copy_status == "RESERVED"
    assert len(initial_loans_count) == 0

    # Wykonanie checkout
    response = await async_client.post(
        "/loans/checkout", json=checkout_data, headers=headers
    )

    assert response.status_code == 201

    # Weryfikacja: wszystkie zmiany zostały zapisane
    db_session.refresh(test_reservation)
    db_session.refresh(test_reservation.book_copy)

    # 1. Rezerwacja zmieniona na COMPLETED
    assert test_reservation.status == "COMPLETED"
    assert test_reservation.completed_at is not None

    # 2. Egzemplarz zmieniony na BORROWED
    assert test_reservation.book_copy.status == "BORROWED"

    # 3. Wypożyczenie utworzone
    loans = db_session.execute(select(Loan)).scalars().all()
    assert len(loans) == 1
    assert loans[0].user_id == test_reservation.user_id
    assert loans[0].book_copy_id == test_reservation.book_copy_id
    assert loans[0].reservation_id == test_reservation.id


async def test_checkout_transaction_rollback_on_error(
    async_client: AsyncClient, db_session, librarian_token, test_reservation
):
    """
    Scenariusz 2: Transakcyjność checkout - rollback przy błędzie

    Symulacja błędu w trakcie transakcji → weryfikacja że wszystkie zmiany są wycofane
    """

    headers = {"Authorization": f"Bearer {librarian_token}"}

    checkout_data = {
        "reservation_id": str(test_reservation.id),
        "user_id": str(test_reservation.user_id),
    }

    # Stan przed checkout
    initial_reservation_status = test_reservation.status
    initial_copy_status = test_reservation.book_copy.status
    initial_reservation_completed_at = test_reservation.completed_at

    # Symulacja błędu w trakcie transakcji (np. błąd przy INSERT do loans)
    with patch(
        "app.models.loan.Loan.__init__", side_effect=Exception("Database error")
    ):
        response = await async_client.post(
            "/loans/checkout", json=checkout_data, headers=headers
        )

    # Oczekiwany błąd serwera
    assert response.status_code == 500

    # Weryfikacja ROLLBACK: baza wraca do stanu sprzed transakcji
    db_session.refresh(test_reservation)
    db_session.refresh(test_reservation.book_copy)

    # 1. Rezerwacja NIE została zmieniona
    assert test_reservation.status == initial_reservation_status
    assert test_reservation.completed_at == initial_reservation_completed_at

    # 2. Egzemplarz NIE został zmieniony
    assert test_reservation.book_copy.status == initial_copy_status

    # 3. Wypożyczenie NIE zostało utworzone
    loans = db_session.execute(select(Loan)).scalars().all()
    assert len(loans) == 0


async def test_checkout_partial_failure_integrity(
    async_client: AsyncClient, db_session, librarian_token, test_reservation
):
    """
    Test integralności: sprawdzenie że częściowe wykonanie transakcji jest niemożliwe
    """

    headers = {"Authorization": f"Bearer {librarian_token}"}

    checkout_data = {
        "reservation_id": str(test_reservation.id),
        "user_id": str(test_reservation.user_id),
    }

    # Symulacja błędu po UPDATE rezerwacji, ale przed UPDATE egzemplarza
    original_update = BookCopy.__setattr__

    def failing_update(self, name, value):
        if name == "status" and value == "BORROWED":
            raise Exception("Simulated failure during copy status update")
        return original_update(self, name, value)

    with patch.object(BookCopy, "__setattr__", failing_update):
        response = await async_client.post(
            "/loans/checkout", json=checkout_data, headers=headers
        )

    assert response.status_code == 500

    # Weryfikacja: WSZYSTKIE operacje wycofane (atomicity)
    db_session.refresh(test_reservation)
    db_session.refresh(test_reservation.book_copy)

    assert test_reservation.status == "ACTIVE"  # NIE zmienione
    assert test_reservation.book_copy.status == "RESERVED"  # NIE zmienione

    loans = db_session.execute(select(Loan)).scalars().all()
    assert len(loans) == 0  # NIE utworzone
