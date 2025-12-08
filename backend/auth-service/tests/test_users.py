"""
Testy jednostkowe dla modułu zarządzania użytkownikami (user_routes.py).

Wymaganie: Punkt 5 - Opis metod i podejść do testowania
Scenariusze testowe:
- pobieranie listy użytkowników (GET /users),
- pobieranie użytkownika po ID (GET /users/{id}),
- tworzenie użytkownika przez ADMINA (POST /users),
- aktualizacja danych użytkownika (PUT /users/{id}),
- usuwanie użytkownika (DELETE /users/{id}),
- blokowanie / odblokowywanie użytkownika (POST /users/{id}/block, POST /users/{id}/unblock).
"""

from app.models.user import UserRole
from fastapi import status


class TestGetAllUsers:
    """Testy dla endpointu GET /users/ (pobieranie listy użytkowników)."""

    def test_get_all_users_as_librarian(
        self,
        client,
        db_session,
        sample_librarian,
        sample_user,
        mock_librarian,
        app_fixture,
    ):
        """
        Bibliotekarz (LIBRARIAN) powinien móc pobrać listę wszystkich użytkowników.
        """
        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_librarian.id),
            "email": sample_librarian.email,
            "role": UserRole.LIBRARIAN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 2

    def test_get_all_users_pagination(self, client, sample_librarian, app_fixture):
        """
        Sprawdzamy, czy endpoint poprawnie obsługuje parametry paginacji (skip, limit).
        """
        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_librarian.id),
            "email": sample_librarian.email,
            "role": UserRole.LIBRARIAN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.get("/api/users/?skip=0&limit=10")

        assert response.status_code == status.HTTP_200_OK


class TestGetUserById:
    """Testy dla endpointu GET /users/{user_id}."""

    def test_get_user_by_id_success(
        self, client, db_session, sample_user, sample_librarian, app_fixture
    ):
        """
        Powinno się udać pobranie istniejącego użytkownika po ID,
        jeśli dzwoni LIBRARIAN (ma odpowiednie uprawnienia).
        """
        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_librarian.id),
            "email": sample_librarian.email,
            "role": UserRole.LIBRARIAN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.get(f"/api/users/{sample_user.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == sample_user.email

    def test_get_user_by_id_not_found(self, client, sample_librarian, app_fixture):
        """
        Dla nieistniejącego ID powinniśmy dostać 404 NOT FOUND.
        """
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_librarian.id),
            "email": sample_librarian.email,
            "role": UserRole.LIBRARIAN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.get(f"/api/users/{fake_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCreateUser:
    """Testy dla endpointu POST /users/ (tworzenie użytkownika przez ADMINA)."""

    def test_create_user_as_admin(self, client, sample_admin, app_fixture):
        """
        ADMIN powinien móc utworzyć nowego użytkownika.
        """
        user_data = {
            "email": "created@example.com",
            "password": "CreatedPass123",
            "full_name": "Created User",
        }

        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_admin.id),
            "email": sample_admin.email,
            "role": UserRole.ADMIN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.post("/api/users/", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == user_data["email"]

    def test_create_user_duplicate_email(
        self, client, sample_user, sample_admin, app_fixture
    ):
        """
        Próba utworzenia użytkownika z istniejącym adresem email
        powinna zakończyć się błędem 400 BAD REQUEST.
        """
        user_data = {"email": "test@example.com", "password": "Password123"}

        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_admin.id),
            "email": sample_admin.email,
            "role": UserRole.ADMIN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.post("/api/users/", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUpdateUser:
    """Testy dla endpointu PUT /users/{user_id} (aktualizacja danych użytkownika)."""

    def test_update_own_profile(self, client, db_session, sample_user, app_fixture):
        """
        Użytkownik powinien móc zaktualizować własny profil (np. full_name).
        """
        update_data = {"full_name": "Updated Name"}

        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_user.id),
            "email": sample_user.email,
            "role": sample_user.role.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.put(f"/api/users/{sample_user.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["full_name"] == "Updated Name"

        # Weryfikacja w bazie danych
        db_session.refresh(sample_user)
        assert sample_user.full_name == "Updated Name"

    def test_update_other_user_forbidden(
        self, client, sample_user, sample_librarian, app_fixture
    ):
        """
        Użytkownik READER nie powinien móc edytować profilu innego użytkownika
        (w tym przypadku próbuje edytować sample_librarian, a sam jest sample_user).
        Oczekiwany status: 403 FORBIDDEN.
        """
        update_data = {"full_name": "Hacker Name"}

        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_user.id),
            "email": sample_user.email,
            "role": sample_user.role.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        # Próba edycji profilu innego użytkownika (sample_librarian)
        response = client.put(f"/api/users/{sample_librarian.id}", json=update_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_user_email_conflict(
        self, client, db_session, sample_user, sample_librarian, app_fixture
    ):
        """
        Próba zmiany emaila na adres już zajęty przez innego użytkownika
        powinna zakończyć się błędem 400 BAD REQUEST.
        """
        update_data = {"email": "librarian@example.com"}

        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_user.id),
            "email": sample_user.email,
            "role": sample_user.role.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.put(f"/api/users/{sample_user.id}", json=update_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteUser:
    """Testy dla endpointu DELETE /users/{user_id}."""

    def test_delete_user_as_admin(
        self, client, db_session, sample_user, sample_admin, app_fixture
    ):
        """
        ADMIN powinien móc usunąć (soft-delete) innego użytkownika.
        """
        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_admin.id),
            "email": sample_admin.email,
            "role": UserRole.ADMIN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.delete(f"/api/users/{sample_user.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_own_account_forbidden(self, client, sample_admin, app_fixture):
        """
        ADMIN nie może usunąć własnego konta – zabezpieczenie przed
        przypadkowym usunięciem ostatniego administratora.
        """
        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_admin.id),
            "email": sample_admin.email,
            "role": UserRole.ADMIN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.delete(f"/api/users/{sample_admin.id}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestBlockUser:
    """Testy dla endpointu POST /users/{user_id}/block."""

    def test_block_user_success(
        self, client, db_session, sample_user, sample_librarian, app_fixture
    ):
        """
        LIBRARIAN (lub ADMIN) powinien móc zablokować użytkownika.
        Po operacji pole is_blocked w odpowiedzi powinno być True.
        """
        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_librarian.id),
            "email": sample_librarian.email,
            "role": UserRole.LIBRARIAN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.post(f"/api/users/{sample_user.id}/block")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_blocked"] is True

    def test_block_own_account_forbidden(self, client, sample_librarian, app_fixture):
        """
        Użytkownik z rolą LIBRARIAN nie może zablokować własnego konta.
        Oczekiwany wynik: 400 BAD REQUEST.
        """
        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_librarian.id),
            "email": sample_librarian.email,
            "role": UserRole.LIBRARIAN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.post(f"/api/users/{sample_librarian.id}/block")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUnblockUser:
    """Testy dla endpointu POST /users/{user_id}/unblock."""

    def test_unblock_user_success(
        self, client, db_session, sample_user, sample_librarian, app_fixture
    ):
        """
        LIBRARIAN powinien móc odblokować wcześniej zablokowanego użytkownika.
        Sprawdzamy, że po wywołaniu endpointu is_blocked == False.
        """
        sample_user.is_blocked = True
        db_session.commit()

        from backend.shared.dependencies import get_current_user_payload

        mock_payload = {
            "sub": str(sample_librarian.id),
            "email": sample_librarian.email,
            "role": UserRole.LIBRARIAN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        response = client.post(f"/api/users/{sample_user.id}/unblock")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_blocked"] is False
