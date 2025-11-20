"""
Moduł odpowiedzialny za logikę bezpieczeństwa w auth-service:
- haszowanie haseł użytkowników,
- generowanie i weryfikacja tokenów JWT.
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import os

# Konfiguracja kontekstu do haszowania haseł.
# Używamy algorytmu bcrypt, a stare schematy są oznaczone jako przestarzałe.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Klucz używany do podpisywania tokenów JWT.
# W środowisku produkcyjnym powinien być ustawiony w zmiennej środowiskowej.
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")

# Algorytm podpisu JWT (domyślnie HS256).
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Czas ważności tokenu dostępowego (w minutach).
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    """
    Zwraca skrót (hash) hasła podanego w postaci jawnej.
    Hash jest jednokierunkowy – nie możemy odzyskać oryginalnego hasła.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Sprawdza, czy podane hasło (plain_password) pasuje do zapisanego hash'a (hashed_password).
    Zwraca True, jeśli hasło jest poprawne, w przeciwnym wypadku False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tworzy token JWT zawierający dane użytkownika (np. user_id, role).

    :param data: słownik z danymi, które chcemy umieścić w tokenie (tzw. "claims").
    :param expires_delta: opcjonalny czas wygaśnięcia tokenu.
    :return: zakodowany token JWT w postaci stringa.
    """
    # Kopiujemy wejściowy słownik, żeby nie modyfikować oryginału.
    to_encode = data.copy()

    # Ustalenie daty wygaśnięcia tokenu.
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Domyślnie token jest ważny ACCESS_TOKEN_EXPIRE_MINUTES minut.
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Dodajemy do payload pole "exp" wymagane przez standard JWT (czas wygaśnięcia).
    to_encode.update({"exp": expire})

    # Kodujemy token z użyciem sekretu i wybranego algorytmu.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Dekoduje i weryfikuje token JWT.
    Jeśli podpis tokenu jest niepoprawny lub token wygasł,
    biblioteka jose rzuci odpowiedni wyjątek.

    :param token: token JWT przekazany np. w nagłówku Authorization.
    :return: payload (słownik) znajdujący się w tokenie.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
