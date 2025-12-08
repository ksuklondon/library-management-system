import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_reader_cannot_add_book(async_client: AsyncClient, reader_token):
    """
    Scenariusz 5: RBAC - Reader próbuje dodać książkę → 403 Forbidden
    """

    headers = {"Authorization": f"Bearer {reader_token}"}

    book_data = {
        "title": "Test Book",
        "authors": ["Test Author"],
        "isbn": "978-83-123-4567-8",
        "publisher": "Test Publisher",
        "pages": 300,
        "language": "pl",
    }

    response = await async_client.post(
        "http://localhost:8002/books", json=book_data, headers=headers
    )

    # Weryfikacja: 403 Forbidden
    assert response.status_code == 403
    assert (
        "permission" in response.json()["detail"].lower()
        or "forbidden" in response.json()["detail"].lower()
    )


async def test_librarian_can_add_book(async_client: AsyncClient, librarian_token):
    """
    Scenariusz 5: RBAC - Librarian dodaje książkę → 201 Created
    """

    headers = {"Authorization": f"Bearer {librarian_token}"}

    book_data = {
        "title": "Librarian Test Book",
        "authors": ["Librarian Author"],
        "isbn": "978-83-987-6543-2",
        "publisher": "Test Publisher",
        "pages": 400,
        "language": "en",
    }

    response = await async_client.post(
        "http://localhost:8002/books", json=book_data, headers=headers
    )

    # Weryfikacja: 201 Created
    assert response.status_code == 201
    assert response.json()["title"] == book_data["title"]


async def test_reader_cannot_change_user_role(
    async_client: AsyncClient, reader_token, test_user
):
    """
    Scenariusz 5: RBAC - Reader próbuje zmienić rolę użytkownika → 403 Forbidden
    """

    headers = {"Authorization": f"Bearer {reader_token}"}

    role_data = {"role": "LIBRARIAN"}

    response = await async_client.patch(
        f"http://localhost:8001/users/{test_user.id}/role",
        json=role_data,
        headers=headers,
    )

    # Weryfikacja: 403 Forbidden
    assert response.status_code == 403


async def test_admin_can_change_user_role(
    async_client: AsyncClient, admin_token, test_user, db_session
):
    """
    Scenariusz 5: RBAC - Admin zmienia rolę użytkownika → 200 OK
    """

    headers = {"Authorization": f"Bearer {admin_token}"}

    # Stan początkowy
    initial_role = test_user.role
    assert initial_role == "READER"

    # Zmiana roli na LIBRARIAN
    role_data = {"role": "LIBRARIAN"}

    response = await async_client.patch(
        f"http://localhost:8001/users/{test_user.id}/role",
        json=role_data,
        headers=headers,
    )

    # Weryfikacja: 200 OK
    assert response.status_code == 200
    assert response.json()["role"] == "LIBRARIAN"

    # Weryfikacja w bazie
    db_session.refresh(test_user)
    assert test_user.role == "LIBRARIAN"


async def test_reader_can_view_own_reservations(
    async_client: AsyncClient, reader_token, test_user_reservation
):
    """
    Test: Reader może zobaczyć swoje rezerwacje
    """

    headers = {"Authorization": f"Bearer {reader_token}"}

    response = await async_client.get("/reservations/my", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) > 0


async def test_reader_cannot_view_all_reservations(
    async_client: AsyncClient, reader_token
):
    """
    Test: Reader NIE może zobaczyć wszystkich rezerwacji → 403 Forbidden
    """

    headers = {"Authorization": f"Bearer {reader_token}"}

    response = await async_client.get(
        "/reservations",  # Endpoint dla Librarian/Admin
        headers=headers,
    )

    assert response.status_code == 403


async def test_librarian_can_view_all_reservations(
    async_client: AsyncClient, librarian_token
):
    """
    Test: Librarian może zobaczyć wszystkie rezerwacje
    """

    headers = {"Authorization": f"Bearer {librarian_token}"}

    response = await async_client.get("/reservations", headers=headers)

    assert response.status_code == 200


async def test_reader_cannot_checkout_book(
    async_client: AsyncClient, reader_token, test_reservation
):
    """
    Test: Reader NIE może wypożyczyć książki (checkout wymaga LIBRARIAN) → 403 Forbidden
    """

    headers = {"Authorization": f"Bearer {reader_token}"}

    checkout_data = {
        "reservation_id": str(test_reservation.id),
        "user_id": str(test_reservation.user_id),
    }

    response = await async_client.post(
        "/loans/checkout", json=checkout_data, headers=headers
    )

    assert response.status_code == 403


async def test_librarian_can_checkout_book(
    async_client: AsyncClient, librarian_token, test_reservation
):
    """
    Test: Librarian może wypożyczyć książkę (checkout)
    """

    headers = {"Authorization": f"Bearer {librarian_token}"}

    checkout_data = {
        "reservation_id": str(test_reservation.id),
        "user_id": str(test_reservation.user_id),
    }

    response = await async_client.post(
        "/loans/checkout", json=checkout_data, headers=headers
    )

    assert response.status_code == 201


async def test_admin_can_delete_book(async_client: AsyncClient, admin_token, test_book):
    """
    Test: Admin może usunąć książkę (soft delete)
    """

    headers = {"Authorization": f"Bearer {admin_token}"}

    response = await async_client.delete(
        f"http://localhost:8002/books/{test_book.id}", headers=headers
    )

    assert response.status_code == 204


async def test_librarian_cannot_delete_book(
    async_client: AsyncClient, librarian_token, test_book
):
    """
    Test: Librarian NIE może usunąć książki (tylko Admin) → 403 Forbidden
    """

    headers = {"Authorization": f"Bearer {librarian_token}"}

    response = await async_client.delete(
        f"http://localhost:8002/books/{test_book.id}", headers=headers
    )

    assert response.status_code == 403
