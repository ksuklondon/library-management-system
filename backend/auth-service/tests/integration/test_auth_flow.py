import pytest
from fastapi import status


@pytest.fixture
def integration_test_init():
    """
    Fikstura przygotowana pod testy integracyjne.

    Obecnie nie wykonuje dodatkowych kroków inicjalizacyjnych (pass),
    ale pozostawia miejsce na ewentualne rozszerzenie:
    - inicjalizacja danych testowych,
    - przygotowanie środowiska, itp.
    """
    pass


class TestCompleteAuthFlow:
    """
    Testy pełnego przepływu autoryzacji i uwierzytelniania.

    Scenariusz obejmuje:
    - rejestrację użytkownika,
    - logowanie,
    - pobranie profilu /api/auth/me,
    - wylogowanie.
    """

    def test_register_login_access_profile_logout(self, client, db_session):
        # 1. Rejestracja nowego użytkownika
        user_data = {
            "email": "flowtest@example.com",
            "password": "FlowTest123",
            "full_name": "Flow Test User"
        }

        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["id"]

        # 2. Logowanie nowo zarejestrowanego użytkownika
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "flowtest@example.com",
                "password": "FlowTest123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.json()["access_token"]

        # 3. Wywołanie endpointu profilu z użyciem otrzymanego tokenu
        headers = {"Authorization": f"Bearer {access_token}"}

        profile_response = client.get("/api/auth/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.json()
        assert profile_data["email"] == "flowtest@example.com"
        assert profile_data["id"] == user_id

        # 4. Wylogowanie użytkownika
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == status.HTTP_200_OK


class TestUserManagementFlow:
    """
    Testy przepływu zarządzania użytkownikami.

    Scenariusz:
    - ADMIN tworzy nowego LIBRARIAN,
    - LIBRARIAN blokuje zwykłego czytelnika (READER).
    """

    def test_admin_creates_librarian_librarian_blocks_reader(self, client, db_session, mock_admin, sample_user):
        from backend.shared.dependencies import require_role
        from app.models.user import UserRole

        # Nadpisanie zależności require_role tak, aby "udawać" zalogowanego ADMINA
        app.dependency_overrides[require_role([UserRole.ADMIN])] = lambda: mock_admin

        # ADMIN tworzy nowego bibliotekarza
        librarian_data = {
            "email": "newlibrarian@example.com",
            "password": "LibrarianPass123",
            "full_name": "New Librarian"
        }

        create_response = client.post("/api/users/", json=librarian_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        librarian_id = create_response.json()["id"]

        # Czyścimy nadpisane zależności
        app.dependency_overrides.clear()

        # Tworzymy mocka reprezentującego nowego bibliotekarza
        from unittest.mock import Mock
        mock_librarian = Mock()
        mock_librarian.id = librarian_id
        mock_librarian.email = "newlibrarian@example.com"
        mock_librarian.role = UserRole.LIBRARIAN
        mock_librarian.is_active = True
        mock_librarian.is_blocked = False

        # Teraz wymagamy roli ADMIN lub LIBRARIAN i podstawiamy mock_librarian
        app.dependency_overrides[require_role([UserRole.ADMIN, UserRole.LIBRARIAN])] = lambda: mock_librarian

        # Bibliotekarz blokuje użytkownika-czytelnika
        block_response = client.post(f"/api/users/{sample_user.id}/block")
        assert block_response.status_code == status.HTTP_200_OK
        assert block_response.json()["is_blocked"] == True

        app.dependency_overrides.clear()


class TestTokenRefreshFlow:
    """
    Testy przepływu odświeżania tokenu.

    Scenariusz:
    - logowanie użytkownika,
    - użycie access tokenu do wywołania /me,
    - odświeżenie tokenu przez /auth/refresh,
    - użycie nowego access tokenu do ponownego wywołania /me.
    """

    def test_login_use_token_refresh_use_new_token(self, client, sample_user):
        # 1. Logowanie istniejącego użytkownika
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK

        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]

        # 2. Wywołanie /me przy pomocy pierwszego access tokenu
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/api/auth/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK

        # 3. Odświeżenie tokenu
        refresh_response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == status.HTTP_200_OK
        new_access_token = refresh_response.json()["access_token"]

        # 4. Wywołanie /me z nowym access tokenem
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        new_profile_response = client.get("/api/auth/me", headers=new_headers)
        assert new_profile_response.status_code == status.HTTP_200_OK


class TestPasswordChangeFlow:
    """
    Test przepływu zmiany hasła przez użytkownika.

    Scenariusz:
    - użytkownik zmienia własne hasło przez endpoint /api/users/{id},
    - logowanie starym hasłem nie działa,
    - logowanie nowym hasłem działa.
    """

    def test_user_changes_password_and_logs_in(self, client, db_session, sample_user):
        from backend.shared.dependencies import get_current_user
        # Udajemy, że aktualnie zalogowany użytkownik to sample_user
        app.dependency_overrides[get_current_user] = lambda: sample_user

        update_data = {
            "password": "NewPassword123"
        }

        # 1. Zmiana hasła użytkownika
        update_response = client.put(f"/api/users/{sample_user.id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK

        app.dependency_overrides.clear()

        # 2. Próba logowania starym hasłem – powinna się nie udać
        login_old_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )
        assert login_old_response.status_code == status.HTTP_401_UNAUTHORIZED

        # 3. Logowanie nowym hasłem – powinno się udać
        login_new_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "NewPassword123"
            }
        )
        assert login_new_response.status_code == status.HTTP_200_OK


class TestBlockedUserFlow:
    """
    Test przepływu blokady użytkownika.

    Scenariusz:
    - użytkownik może się zalogować,
    - LIBRARIAN/ADMIN blokuje użytkownika,
    - po blokadzie użytkownik nie może się już zalogować.
    """

    def test_user_gets_blocked_cannot_login(self, client, db_session, sample_user, mock_librarian):
        from backend.shared.dependencies import require_role
        from app.models.user import UserRole

        # 1. Upewniamy się, że przed blokadą logowanie działa
        login_before = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )
        assert login_before.status_code == status.HTTP_200_OK

        # 2. Nadpisujemy require_role, aby udawać LIBRARIAN/ADMIN podczas blokady
        app.dependency_overrides[require_role([UserRole.ADMIN, UserRole.LIBRARIAN])] = lambda: mock_librarian

        # 3. Blokujemy użytkownika
        block_response = client.post(f"/api/users/{sample_user.id}/block")
        assert block_response.status_code == status.HTTP_200_OK

        app.dependency_overrides.clear()

        # 4. Po blokadzie logowanie tym samym kontem powinno zwracać 403 FORBIDDEN
        login_after = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )
        assert login_after.status_code == status.HTTP_403_FORBIDDEN
