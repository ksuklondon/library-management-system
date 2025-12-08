"""
Integration tests for authentication and user management flows.
FIXED VERSION: Selektywne czyszczenie dependency overrides (get_db zostaje!).
"""

from fastapi import status


class TestCompleteAuthFlow:
    """Test complete authentication flow from registration to logout."""

    def test_register_login_access_profile_logout(self, client, app_fixture):
        """Test full auth cycle - FIXED with dependency override."""
        from backend.shared.dependencies import get_current_user_payload

        # 1. Rejestracja nowego użytkownika
        user_data = {
            "email": "flowtest@example.com",
            "password": "FlowPassword123",
            "full_name": "Flow Test User",
        }
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["id"]

        # 2. Logowanie
        login_response = client.post(
            "/api/auth/login",
            json={"email": "flowtest@example.com", "password": "FlowPassword123"},
        )
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.json()["access_token"]

        # 3. Nadpisanie dependency dla /me
        mock_payload = {
            "sub": user_id,
            "email": "flowtest@example.com",
            "role": "reader",
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        # 4. Dostęp do profilu
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/api/auth/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.json()["email"] == "flowtest@example.com"

        # 5. Wylogowanie
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == status.HTTP_200_OK

        # Czyścimy TYLKO get_current_user_payload override (get_db zostaje!)
        if get_current_user_payload in app_fixture.dependency_overrides:
            del app_fixture.dependency_overrides[get_current_user_payload]


class TestUserManagementFlow:
    """Test user management flow with role-based operations."""

    def test_admin_creates_librarian_librarian_blocks_reader(
        self, client, db_session, sample_admin, sample_user, app_fixture
    ):
        """Test admin creates librarian, librarian blocks user - FIXED."""
        from app.models.user import UserRole

        from backend.shared.dependencies import get_current_user_payload

        # Nadpisanie zależności - "udajemy" zalogowanego ADMINA
        mock_payload = {
            "sub": str(sample_admin.id),
            "email": sample_admin.email,
            "role": UserRole.ADMIN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        # ADMIN tworzy nowego bibliotekarza
        librarian_data = {
            "email": "newlibrarian@example.com",
            "password": "LibrarianPass123",
            "full_name": "New Librarian",
        }

        create_response = client.post("/api/users/", json=librarian_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        new_librarian_id = create_response.json()["id"]

        # Zmieniamy nadpisanie - teraz "zalogowany" jest nowy bibliotekarz
        mock_payload_librarian = {
            "sub": new_librarian_id,
            "email": "newlibrarian@example.com",
            "role": UserRole.LIBRARIAN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload_librarian
        )

        # Bibliotekarz blokuje konto sample_user
        block_response = client.post(f"/api/users/{sample_user.id}/block")
        assert block_response.status_code == status.HTTP_200_OK
        assert block_response.json()["is_blocked"] is True

        # Odświeżamy sample_user z DB
        db_session.refresh(sample_user)

        # Weryfikujemy, że użytkownik jest zablokowany w bazie
        assert sample_user.is_blocked is True

        # Czyścimy TYLKO get_current_user_payload (get_db zostaje!)
        if get_current_user_payload in app_fixture.dependency_overrides:
            del app_fixture.dependency_overrides[get_current_user_payload]

        # Próba logowania przez zablokowanego użytkownika
        # (to już używa endpoint /login z SQLite dzięki get_db override)
        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPassword123"},
        )

        # Powinno zwrócić 403 Forbidden
        assert login_response.status_code == status.HTTP_403_FORBIDDEN
        assert "zablokowane" in login_response.json()["detail"].lower()


class TestTokenRefreshFlow:
    """Test token refresh flow."""

    def test_login_use_token_refresh_use_new_token(
        self, client, sample_user, app_fixture
    ):
        """Test login, refresh token, and use new token - FIXED."""
        from backend.shared.dependencies import get_current_user_payload

        # 1. Logowanie istniejącego użytkownika
        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPassword123"},
        )
        assert login_response.status_code == status.HTTP_200_OK

        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]

        # 2. Nadpisanie dependency dla /me
        mock_payload = {
            "sub": str(sample_user.id),
            "email": sample_user.email,
            "role": sample_user.role.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        # 3. Wywołanie /me przy pomocy pierwszego access tokenu
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/api/auth/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.json()["email"] == "test@example.com"

        # 4. Odświeżenie tokenu
        refresh_response = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == status.HTTP_200_OK
        new_access_token = refresh_response.json()["access_token"]

        # 5. Użycie nowego tokenu do /me
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        new_profile_response = client.get("/api/auth/me", headers=new_headers)
        assert new_profile_response.status_code == status.HTTP_200_OK

        # Czyścimy TYLKO get_current_user_payload override
        if get_current_user_payload in app_fixture.dependency_overrides:
            del app_fixture.dependency_overrides[get_current_user_payload]


class TestPasswordChangeFlow:
    """Test password change and login with new password."""

    def test_user_changes_password_and_logs_in(
        self, client, db_session, sample_user, app_fixture
    ):
        """Test password change flow - FIXED."""
        from backend.shared.dependencies import get_current_user_payload

        # Udajemy, że aktualnie zalogowany użytkownik to sample_user
        mock_payload = {
            "sub": str(sample_user.id),
            "email": sample_user.email,
            "role": sample_user.role.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        update_data = {"password": "NewPassword123"}

        # 1. Zmiana hasła użytkownika
        update_response = client.put(f"/api/users/{sample_user.id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK

        # Czyścimy TYLKO get_current_user_payload override (get_db zostaje!)
        if get_current_user_payload in app_fixture.dependency_overrides:
            del app_fixture.dependency_overrides[get_current_user_payload]

        # Odświeżamy sample_user z DB
        db_session.refresh(sample_user)

        # 2. Próba logowania starym hasłem – powinna się nie udać
        login_old_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPassword123"},
        )
        assert login_old_response.status_code == status.HTTP_401_UNAUTHORIZED

        # 3. Próba logowania nowym hasłem – powinna się udać
        login_new_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "NewPassword123"},
        )
        assert login_new_response.status_code == status.HTTP_200_OK
        assert "access_token" in login_new_response.json()


class TestBlockedUserFlow:
    """Test blocked user cannot login."""

    def test_user_gets_blocked_cannot_login(
        self, client, db_session, sample_user, sample_librarian, app_fixture
    ):
        """Test blocking user prevents login - FIXED."""
        from app.models.user import UserRole

        from backend.shared.dependencies import get_current_user_payload

        # 1. Upewniamy się, że przed blokadą logowanie działa
        login_before = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPassword123"},
        )
        assert login_before.status_code == status.HTTP_200_OK

        # 2. Nadpisujemy get_current_user_payload, aby udawać LIBRARIAN podczas blokady
        mock_payload = {
            "sub": str(sample_librarian.id),
            "email": sample_librarian.email,
            "role": UserRole.LIBRARIAN.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        # 3. Blokujemy użytkownika
        block_response = client.post(f"/api/users/{sample_user.id}/block")
        assert block_response.status_code == status.HTTP_200_OK

        # Czyścimy TYLKO get_current_user_payload override (get_db zostaje!)
        if get_current_user_payload in app_fixture.dependency_overrides:
            del app_fixture.dependency_overrides[get_current_user_payload]

        # Odświeżamy sample_user z DB
        db_session.refresh(sample_user)

        # Weryfikujemy, że użytkownik jest zablokowany w bazie
        assert sample_user.is_blocked is True

        # 4. Próba ponownego logowania – powinna się nie udać (403)
        login_after = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPassword123"},
        )
        assert login_after.status_code == status.HTTP_403_FORBIDDEN
        assert "zablokowane" in login_after.json()["detail"].lower()
