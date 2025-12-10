"""
Testy endpointów autentykacji (register, login, logout, refresh token, /me).
FIXED VERSION: Dodano dependency overrides dla JWT authentication.
"""

from fastapi import status


class TestRegister:
    """
    Testy endpointu rejestracji użytkownika (/api/auth/register).
    Sprawdzają poprawne utworzenie konta oraz typowe błędy.
    """

    def test_register_success(self, client, db_session):
        """
        Scenariusz pozytywny:
        - poprawne dane rejestracyjne,
        - użytkownik zostaje utworzony z rolą READER,
        - hasło nie jest zwracane w odpowiedzi.
        """
        user_data = {
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "full_name": "New User",
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        # Domyślna rola dla nowego użytkownika
        assert data["role"] == "READER"
        # Użytkownik ma przydzielone ID
        assert "id" in data
        # Hash hasła nie powinien być zwracany do klienta
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, sample_user):
        """
        Scenariusz negatywny:
        - próba rejestracji z adresem email, który już istnieje w systemie,
        - oczekiwany błąd 400.
        """
        user_data = {
            "email": "test@example.com",  # email istnieje dzięki fixture sample_user
            "password": "Password123",
            "full_name": "Duplicate User",
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Komunikat błędu powinien informować o istniejącym emailu
        assert "już istnieje" in response.json()["detail"].lower()

    def test_register_invalid_password(self, client):
        """
        Scenariusz negatywny:
        - hasło nie spełnia wymagań walidacji (za słabe),
        - Pydantic zwróci błąd 422 (błędne dane wejściowe).
        """
        user_data = {
            "email": "test@example.com",
            "password": "weak",  # za krótkie / zbyt słabe
            "full_name": "Test User",
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_email(self, client):
        """
        Scenariusz negatywny:
        - brak wymaganego pola email w żądaniu,
        - Pydantic zwróci błąd 422 (brak wymaganych pól).
        """
        user_data = {"password": "Password123"}

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """
    Testy endpointu logowania (/api/auth/login).
    Sprawdzają różne przypadki poprawnego i błędnego logowania.
    """

    def test_login_success(self, client, sample_user):
        """
        Scenariusz pozytywny:
        - poprawne dane logowania,
        - zwracany jest access_token i refresh_token,
        - poprawne dane użytkownika w odpowiedzi.
        """
        credentials = {"email": "test@example.com", "password": "TestPassword123"}

        response = client.post("/api/auth/login", json=credentials)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == "test@example.com"
        assert data["role"] == "READER"

    def test_login_wrong_password(self, client, sample_user):
        """
        Scenariusz negatywny:
        - poprawny email, błędne hasło,
        - oczekiwany status 401 (nieautoryzowany).
        """
        credentials = {"email": "test@example.com", "password": "WrongPassword123"}

        response = client.post("/api/auth/login", json=credentials)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """
        Scenariusz negatywny:
        - próba logowania na nieistniejące konto,
        - oczekiwany status 401 (nieautoryzowany).
        """
        credentials = {"email": "nonexistent@example.com", "password": "Password123"}

        response = client.post("/api/auth/login", json=credentials)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client, sample_user, db_session):
        """
        Scenariusz negatywny:
        - konto użytkownika jest nieaktywne (is_active = False),
        - logowanie powinno być zablokowane kodem 403.
        """
        sample_user.is_active = False
        db_session.commit()

        credentials = {"email": "test@example.com", "password": "TestPassword123"}

        response = client.post("/api/auth/login", json=credentials)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "nieaktywne" in response.json()["detail"].lower()

    def test_login_blocked_user(self, client, sample_user, db_session):
        """
        Scenariusz negatywny:
        - konto użytkownika jest zablokowane (is_blocked = True),
        - logowanie powinno być zablokowane kodem 403.
        """
        sample_user.is_blocked = True
        db_session.commit()

        credentials = {"email": "test@example.com", "password": "TestPassword123"}

        response = client.post("/api/auth/login", json=credentials)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "zablokowane" in response.json()["detail"].lower()


class TestRefreshToken:
    """
    Testy endpointu odświeżania tokenu (/api/auth/refresh).
    Sprawdzają poprawne wydanie nowego access_token oraz obsługę błędnego tokenu.
    """

    def test_refresh_token_success(self, client, sample_user):
        """
        Scenariusz pozytywny:
        - użytkownik loguje się i otrzymuje refresh_token,
        - używa refresh_token do pobrania nowego access_token.
        """
        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPassword123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        response = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client):
        """
        Scenariusz negatywny:
        - przekazanie niepoprawnego / losowego refresh_token,
        - oczekiwany status 401 (nieautoryzowany).
        """
        response = client.post(
            "/api/auth/refresh", json={"refresh_token": "invalid-token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    """
    Testy endpointu wylogowania (/api/auth/logout).
    """

    def test_logout_success(self, client, sample_user, app_fixture):
        """
        Scenariusz pozytywny:
        - wylogowanie zalogowanego użytkownika,
        - endpoint zwraca komunikat o poprawnym wylogowaniu.

        FIXED: Dodano dependency override dla get_current_user_payload.
        """
        from shared.dependencies import get_current_user_payload

        # Nadpisujemy get_current_user_payload dla /logout endpoint
        mock_payload = {
            "sub": str(sample_user.id),
            "email": sample_user.email,
            "role": sample_user.role.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        # Wylogowujemy się (token w headers nie jest istotny, bo override działa)
        response = client.post("/api/auth/logout")

        assert response.status_code == status.HTTP_200_OK
        assert "wylogowano" in response.json()["message"].lower()

        # Czyścimy override
        app_fixture.dependency_overrides.clear()


class TestGetCurrentUser:
    """
    Testy endpointu pobierania aktualnego użytkownika (/api/auth/me).
    """

    def test_get_current_user_success(self, client, sample_user, app_fixture):
        """
        Scenariusz pozytywny:
        - zapytanie z poprawnym tokenem,
        - zwracane są dane zalogowanego użytkownika.

        FIXED: Dodano dependency override dla get_current_user_payload.
        """
        from shared.dependencies import get_current_user_payload

        # Nadpisujemy get_current_user_payload
        mock_payload = {
            "sub": str(sample_user.id),
            "email": sample_user.email,
            "role": sample_user.role.value,
        }
        app_fixture.dependency_overrides[get_current_user_payload] = (
            lambda: mock_payload
        )

        # Pobieramy /me
        response = client.get("/api/auth/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "READER"

        # Czyścimy override
        app_fixture.dependency_overrides.clear()

    def test_get_current_user_unauthorized(self, client):
        """
        Scenariusz negatywny:
        - brak nagłówka Authorization,
        - oczekiwany status 403 (forbidden - dependency zwraca 403).
        """
        response = client.get("/api/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN
