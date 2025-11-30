"""
Endpointy do zarządzania użytkownikami (moduł administracyjny):

- pobieranie listy użytkowników,
- pobieranie szczegółów użytkownika,
- tworzenie nowego użytkownika (przez ADMINA),
- aktualizacja danych użytkownika,
- usuwanie użytkownika,
- blokowanie / odblokowywanie kont.
"""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from backend.shared.database import get_db
from backend.shared.dependencies import (  # ZMIANA!
    get_current_user_payload,
    require_role,
)

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(
        require_role([UserRole.ADMIN.value, UserRole.LIBRARIAN.value])
    ),  # ZMIANA!
):
    """
    Zwraca listę użytkowników z możliwością paginacji (skip/limit).

    Dostęp: ADMIN i LIBRARIAN.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(
        require_role([UserRole.ADMIN.value, UserRole.LIBRARIAN.value])
    ),  # ZMIANA!
):
    """
    Zwraca szczegóły konkretnego użytkownika na podstawie jego UUID.

    Dostęp: ADMIN i LIBRARIAN.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Użytkownik nie znaleziony"
        )

    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(
        require_role([UserRole.ADMIN.value])
    ),  # ZMIANA!
):
    """
    Tworzenie nowego użytkownika przez administratora.

    - sprawdzenie unikalności emaila,
    - haszowanie hasła,
    - zapis do bazy danych.
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email już istnieje"
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


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user_payload: Dict[str, Any] = Depends(get_current_user_payload),  # ZMIANA!
):
    """
    Aktualizacja danych użytkownika.

    Zasady:
    - użytkownik może edytować tylko własne konto,
    - ADMIN i LIBRARIAN mogą edytować dowolne konto.
    """
    current_user_id = current_user_payload.get("sub")
    current_user_role = current_user_payload.get("role")

    if str(current_user_id) != str(user_id) and current_user_role not in [
        UserRole.ADMIN.value,
        UserRole.LIBRARIAN.value,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień do edycji tego użytkownika",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Użytkownik nie znaleziony"
        )

    # Sprawdzenie, czy nowy email nie koliduje z innym kontem.
    if user_data.email:
        existing = (
            db.query(User)
            .filter(User.email == user_data.email, User.id != user_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email już istnieje"
            )
        user.email = user_data.email

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    # Jeśli przekazano nowe hasło – ponownie je haszujemy.
    if user_data.password:
        user.hashed_password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user_payload: Dict[str, Any] = Depends(
        require_role([UserRole.ADMIN.value])
    ),  # ZMIANA!
):
    """
    Usuwanie użytkownika z systemu.

    Ograniczenia:
    - tylko ADMIN,
    - nie można usunąć własnego konta (samobójstwo konta).
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Użytkownik nie znaleziony"
        )

    current_user_id = current_user_payload.get("sub")

    if str(user.id) == str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nie możesz usunąć własnego konta",
        )

    db.delete(user)
    db.commit()

    return None


@router.post("/{user_id}/block", response_model=UserResponse)
def block_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user_payload: Dict[str, Any] = Depends(
        require_role([UserRole.ADMIN.value, UserRole.LIBRARIAN.value])
    ),  # ZMIANA!
):
    """
    Blokowanie konta użytkownika (np. za nadużycia).

    Dostęp: ADMIN i LIBRARIAN.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Użytkownik nie znaleziony"
        )

    current_user_id = current_user_payload.get("sub")

    if str(user.id) == str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nie możesz zablokować własnego konta",
        )

    user.is_blocked = True
    db.commit()
    db.refresh(user)

    return user


@router.post("/{user_id}/unblock", response_model=UserResponse)
def unblock_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user_payload: Dict[str, Any] = Depends(
        require_role([UserRole.ADMIN.value, UserRole.LIBRARIAN.value])
    ),  # ZMIANA!
):
    """
    Odblokowanie wcześniej zablokowanego konta.

    Dostęp: ADMIN i LIBRARIAN.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Użytkownik nie znaleziony"
        )

    user.is_blocked = False
    db.commit()
    db.refresh(user)

    return user
