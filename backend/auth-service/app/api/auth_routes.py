"""
Endpointy związane z uwierzytelnianiem użytkowników:

- /register – rejestracja nowego użytkownika,
- /login    – logowanie i wydanie access/refresh tokenów,
- /refresh  – wygenerowanie nowego access tokenu na podstawie refresh tokenu,
- /logout   – wylogowanie (logiczne; w tej wersji bez blacklisty),
- /me       – pobranie informacji o aktualnie zalogowanym użytkowniku.

FIXED VERSION: Dodano konwersję str -> UUID w endpoint /me.
"""

from datetime import timedelta
from typing import Any, Dict
from uuid import UUID

from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.dependencies import get_current_user_payload

router = APIRouter()

# Czas ważności refresh tokenu – tutaj 7 dni.
REFRESH_TOKEN_EXPIRE_DAYS = 7


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Rejestracja nowego użytkownika w systemie.

    - sprawdza, czy email nie jest już zajęty,
    - haszuje hasło,
    - tworzy rekord w bazie danych.
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email już istnieje w systemie",
        )

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Logowanie użytkownika.

    Krok po kroku:
    - wyszukujemy użytkownika po emailu,
    - weryfikujemy hasło,
    - sprawdzamy, czy konto jest aktywne i niezablokowane,
    - generujemy access token i refresh token.
    """
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło",
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Konto nieaktywne"
        )

    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Konto zablokowane"
        )

    # Tworzymy access token zawierający podstawowe dane użytkownika.
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value}
    )

    # Refresh token służy tylko do odświeżania access tokenu.
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=str(user.id),
        email=user.email,
        role=user.role.value,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest):
    """
    Endpoint do odświeżenia access tokenu na podstawie refresh tokenu.

    - weryfikuje podpis tokenu,
    - sprawdza, czy token ma typ "refresh",
    - generuje nowy access token.
    """
    try:
        payload = verify_token(request.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nieprawidłowy refresh token",
            )

        user_id = payload.get("sub")

        access_token = create_access_token(data={"sub": user_id})

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except Exception:
        # W przypadku dowolnego błędu traktujemy token jako nieważny.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy lub wygasły refresh token",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(user_payload: Dict[str, Any] = Depends(get_current_user_payload)):
    """
    "Wylogowanie" użytkownika.

    W tej prostej wersji aplikacji nie przechowujemy stanu sesji ani blacklisty tokenów,
    więc endpoint pełni głównie funkcję informacyjną / pod przyszłą rozbudowę.
    """
    return {"message": "Wylogowano pomyślnie"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    user_payload: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    """
    Zwraca dane aktualnie zalogowanego użytkownika na podstawie tokenu JWT.

    FIXED: Konwersja str -> UUID dla user_id.
    """
    user_id_str = user_payload.get("sub")

    # Konwersja string -> UUID (JWT zawsze zwraca stringi)
    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy format ID użytkownika w tokenie",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Użytkownik nie istnieje"
        )

    return user
