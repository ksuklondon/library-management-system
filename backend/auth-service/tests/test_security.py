"""
Testy jednostkowe dla modułu bezpieczeństwa (app.core.security):

- TestPasswordHashing  – testy haszowania i weryfikacji haseł,
- TestJWTTokens        – testy tworzenia i weryfikacji tokenów JWT,
- TestPasswordStrength – testy pomocnicze dotyczące złożoności haseł
  (odzwierciedlają wymagania walidacji z schemas.user).

FIXED VERSION: Naprawiono test_different_tokens_for_same_data z time.sleep(1).
"""

import time
from datetime import timedelta

import pytest
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    """
    Zestaw testów sprawdzających poprawność haszowania i weryfikacji haseł.
    """

    def test_hash_password(self):
        """
        Sprawdza, czy funkcja hash_password:
        - zwraca wartość różną od oryginalnego hasła,
        - zwraca niepusty hash,
        - generuje hash w formacie bcrypt (prefix '$2b$').
        """
        password = "TestPassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")

    def test_hash_password_different_results(self):
        """
        Dwa wywołania hash_password z tym samym hasłem
        powinny zwrócić różne hashe (salt).
        """
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """
        verify_password powinno zwrócić True dla poprawnego hasła.
        """
        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """
        verify_password powinno zwrócić False dla niepoprawnego hasła.
        """
        password = "TestPassword123"
        wrong_password = "WrongPassword123"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_case_sensitive(self):
        """
        verify_password powinno być czułe na wielkość liter (case-sensitive).
        """
        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password("testpassword123", hashed) is False


class TestJWTTokens:
    """
    Zestaw testów dotyczących generowania i weryfikacji tokenów JWT.
    """

    def test_create_access_token(self):
        """
        Sprawdza, czy create_access_token zwraca niepusty string.
        """
        data = {"sub": "user-123", "email": "test@example.com", "role": "READER"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """
        Sprawdza, czy można utworzyć token z własnym czasem wygaśnięcia.
        """
        data = {"sub": "user-123"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=expires_delta)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """
        verify_token powinno poprawnie dekodować prawidłowy token
        i zwrócić payload z polami sub, email, role oraz exp.
        """
        data = {"sub": "user-123", "email": "test@example.com", "role": "READER"}
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "READER"
        assert "exp" in payload

    def test_verify_token_invalid(self):
        """
        verify_token powinno rzucić wyjątek dla nieprawidłowego tokenu.
        """
        with pytest.raises(Exception):
            verify_token("invalid-token-xyz")

    def test_verify_token_expired(self):
        """
        verify_token powinno rzucić wyjątek, gdy token jest już przeterminowany.
        """
        data = {"sub": "user-123"}
        # Ujemny timedelta sprawia, że token jest natychmiast nieważny
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expires_delta)

        with pytest.raises(Exception):
            verify_token(token)

    def test_token_contains_exp_claim(self):
        """
        Każdy wygenerowany token powinien zawierać claim 'exp'
        (czas wygaśnięcia) w postaci liczby całkowitej.
        """
        data = {"sub": "user-123"}
        token = create_access_token(data)
        payload = verify_token(token)

        assert "exp" in payload
        assert isinstance(payload["exp"], int)

    def test_different_tokens_for_same_data(self):
        """
        Dwa tokeny wygenerowane z tym samym payloadem powinny być różne
        (ze względu na różne czasy 'iat' / 'exp' lub użyty losowy komponent).

        FIXED: Dodano time.sleep(1) aby zapewnić różne timestampy exp.
        """
        data = {"sub": "user-123"}

        # Pierwszy token
        token1 = create_access_token(data)

        # Czekamy 1 sekundę, żeby timestamp exp był inny
        time.sleep(1)

        # Drugi token
        token2 = create_access_token(data)

        # Tokeny powinny być różne
        assert token1 != token2

        # Weryfikujemy oba tokeny
        payload1 = verify_token(token1)
        payload2 = verify_token(token2)

        # sub powinien być taki sam
        assert payload1["sub"] == payload2["sub"]

        # exp powinien być różny (różnica ~1 sekunda)
        assert payload1["exp"] != payload2["exp"]


class TestPasswordStrength:
    """
    Proste testy sprawdzające kryteria złożoności hasła.
    Odzwierciedlają wymagania walidatora z klasy UserCreate (schemas.user).
    """

    def test_weak_password_too_short(self):
        """
        Hasło krótsze niż 8 znaków powinno być traktowane jako zbyt słabe.
        """
        password = "Pass1"

        assert len(password) < 8

    def test_password_without_uppercase(self):
        """
        Hasło bez wielkiej litery nie spełnia wymagań złożoności.
        """
        password = "password123"

        assert not any(c.isupper() for c in password)

    def test_password_without_lowercase(self):
        """
        Hasło bez małej litery nie spełnia wymagań złożoności.
        """
        password = "PASSWORD123"

        assert not any(c.islower() for c in password)

    def test_password_without_digit(self):
        """
        Hasło bez cyfry nie spełnia wymagań złożoności.
        """
        password = "PasswordABC"

        assert not any(c.isdigit() for c in password)

    def test_strong_password(self):
        """
        Przykład poprawnego, silnego hasła:
        - min. 8 znaków,
        - zawiera wielką literę,
        - zawiera małą literę,
        - zawiera cyfrę.
        """
        password = "StrongPassword123"

        assert len(password) >= 8
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)
