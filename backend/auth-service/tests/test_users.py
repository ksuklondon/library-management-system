import pytest
from fastapi import status
from unittest.mock import Mock
from app.models.user import User, UserRole


@pytest.fixture
def mock_librarian():
    """
    Fixture tworząca mockowanego użytkownika z rolą LIBRARIAN.
    Używane do testowania endpointów wymagających uprawnień bibliotekarza.
    """
    user = Mock(spec=User)
    user.id = "librarian-uuid-1234"
    user.email = "librarian@library.com"
    user.role = UserRole.LIBRARIAN
    user.is_active = True
    user.is_blocked = False
    return user


@pytest.fixture
def mock_admin():
    """
    Fixture tworząca mockowanego użytkownika z rolą ADMIN.
    Używane do testowania endpointów wymagających uprawnień administratora.
    """
    user = Mock(spec=User)
    user.id = "admin-uuid-5678"
    user.email = "admin@library.com"
    user.role = UserRole.ADMIN
    user.is_active = True
    user.is_blocked = False
    return user


class TestGetAllUsers:
    """
    Testy endpointu pobierającego listę użytkowników (/api/users/).
    """

    def test_get_all_users_as_librarian(self, client, db_session, sample_librarian, sample_user, mock_librarian):
        """
        Bibliotekarz (LIBRARIAN) powinien móc pobrać listę wszystkich użytkowników.

        Sprawdzamy:
        - nadpisanie zależności require_role, aby zwrócić mock_librarian,
        - że endpoint zwraca HTTP 200,
        - że w odpowiedzi jest co najmniej 2 użytkowników (sample_librarian + sample_user).
        """
        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN, UserRole.LIBRARIAN])] = lambda: mock_librarian

        response = client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2

        app.dependency_overrides.clear()

    def test_get_all_users_pagination(self, client, mock_librarian):
        """
        Sprawdzamy, czy endpoint poprawnie obsługuje parametry paginacji (skip, limit).
        """
        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN, UserRole.LIBRARIAN])] = lambda: mock_librarian

        response = client.get("/api/users/?skip=0&limit=10")

        assert response.status_code == status.HTTP_200_OK

        app.dependency_overrides.clear()


class TestGetUserById:
    """
    Testy endpointu pobierającego użytkownika po ID (/api/users/{user_id}).
    """

    def test_get_user_by_id_success(self, client, db_session, sample_user, mock_librarian):
        """
        Powinno się udać pobranie istniejącego użytkownika po ID,
        jeśli dzwoni LIBRARIAN (ma odpowiednie uprawnienia).
        """
        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN, UserRole.LIBRARIAN])] = lambda: mock_librarian

        response = client.get(f"/api/users/{sample_user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_user.id)
        assert data["email"] == sample_user.email

        app.dependency_overrides.clear()

    def test_get_user_by_id_not_found(self, client, mock_librarian):
        """
        Dla nieistniejącego ID powinniśmy dostać 404 NOT FOUND.
        """
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN, UserRole.LIBRARIAN])] = lambda: mock_librarian

        response = client.get(f"/api/users/{fake_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()


class TestCreateUser:
    """
    Testy tworzenia użytkowników (/api/users/ - POST).
    """

    def test_create_user_as_admin(self, client, mock_admin):
        """
        ADMIN powinien móc utworzyć nowego użytkownika.
        Sprawdzamy, że:
        - status to 201 CREATED,
        - email w odpowiedzi zgadza się z wysłanymi danymi.
        """
        user_data = {
            "email": "created@example.com",
            "password": "CreatedPass123",
            "full_name": "Created User"
        }

        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.post("/api/users/", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]

        app.dependency_overrides.clear()

    def test_create_user_duplicate_email(self, client, sample_user, mock_admin):
        """
        Próba utworzenia użytkownika z istniejącym adresem email
        powinna zakończyć się błędem 400 BAD REQUEST.
        """
        user_data = {
            "email": "test@example.com",
            "password": "Password123"
        }

        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.post("/api/users/", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        app.dependency_overrides.clear()


class TestUpdateUser:
    """
    Testy aktualizacji użytkowników (/api/users/{user_id} - PUT).
    """

    def test_update_own_profile(self, client, db_session, sample_user):
        """
        Użytkownik powinien móc zaktualizować własny profil (np. full_name).
        """
        update_data = {
            "full_name": "Updated Name"
        }

        from backend.shared.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: sample_user

        response = client.put(f"/api/users/{sample_user.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated Name"

        app.dependency_overrides.clear()

    def test_update_other_user_forbidden(self, client, sample_user, sample_librarian):
        """
        Zwykły użytkownik nie powinien móc edytować profilu innej osoby.
        Oczekujemy 403 FORBIDDEN.
        """
        update_data = {
            "full_name": "Hacked Name"
        }

        from backend.shared.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: sample_user

        response = client.put(f"/api/users/{sample_librarian.id}", json=update_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

        app.dependency_overrides.clear()

    def test_update_user_email_conflict(self, client, db_session, sample_user, sample_librarian):
        """
        Próba zmiany emaila na adres już zajęty przez innego użytkownika
        powinna zakończyć się błędem 400 BAD REQUEST.
        """
        update_data = {
            "email": "librarian@example.com"
        }

        from backend.shared.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: sample_user

        response = client.put(f"/api/users/{sample_user.id}", json=update_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        app.dependency_overrides.clear()


class TestDeleteUser:
    """
    Testy usuwania użytkowników (/api/users/{user_id} - DELETE).
    """

    def test_delete_user_as_admin(self, client, db_session, sample_user, mock_admin):
        """
        ADMIN powinien móc usunąć (soft-delete) innego użytkownika.
        """
        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.delete(f"/api/users/{sample_user.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        app.dependency_overrides.clear()

    def test_delete_own_account_forbidden(self, client, mock_admin):
        """
        ADMIN nie może usunąć własnego konta – zabezpieczenie przed
        przypadkowym usunięciem ostatniego administratora.
        """
        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        response = client.delete(f"/api/users/{mock_admin.id}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "własnego konta" in response.json()["detail"].lower()

        app.dependency_overrides.clear()


class TestBlockUser:
    """
    Testy blokowania użytkowników (/api/users/{user_id}/block - POST).
    """

    def test_block_user_success(self, client, db_session, sample_user, mock_librarian):
        """
        LIBRARIAN (lub ADMIN) powinien móc zablokować użytkownika.
        Po operacji pole is_blocked w odpowiedzi powinno być True.
        """
        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN, UserRole.LIBRARIAN])] = lambda: mock_librarian

        response = client.post(f"/api/users/{sample_user.id}/block")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_blocked"] is True

        app.dependency_overrides.clear()

    def test_block_own_account_forbidden(self, client, mock_librarian):
        """
        Użytkownik z rolą LIBRARIAN nie może zablokować własnego konta.
        Oczekiwany wynik: 400 BAD REQUEST.
        """
        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN, UserRole.LIBRARIAN])] = lambda: mock_librarian

        response = client.post(f"/api/users/{mock_librarian.id}/block")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        app.dependency_overrides.clear()


class TestUnblockUser:
    """
    Testy odblokowywania użytkowników (/api/users/{user_id}/unblock - POST).
    """

    def test_unblock_user_success(self, client, db_session, sample_user, mock_librarian):
        """
        LIBRARIAN powinien móc odblokować wcześniej zablokowanego użytkownika.
        Sprawdzamy, że po wywołaniu endpointu is_blocked == False.
        """
        sample_user.is_blocked = True
        db_session.commit()

        from backend.shared.dependencies import require_role
        app.dependency_overrides[require_role([UserRole.ADMIN, UserRole.LIBRARIAN])] = lambda: mock_librarian

        response = client.post(f"/api/users/{sample_user.id}/unblock")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_blocked"] is False

        app.dependency_overrides.clear()
