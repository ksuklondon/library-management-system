"""
API Routes dla Reservation - rezerwacje książek.

Wymaganie: F8-F10 - Rezerwacje książek:
    - F8: Rezerwacja książki
    - F9: Przeglądanie rezerwacji
    - F10: Anulowanie rezerwacji

Wymaganie: NF5 - RBAC (Role-Based Access Control)
    - kontrola dostępu na podstawie roli użytkownika (READER, LIBRARIAN, ADMIN)

Wymaganie: NF19 - Audyt
    - zamiast twardego usuwania stosujemy soft delete (flaga is_deleted, pole deleted_by)
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.reservation import Reservation, ReservationStatus
from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
)
from shared.database import get_db
from shared.dependencies import get_current_user_payload, require_role

router = APIRouter()


@router.post(
    "/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED
)
async def create_reservation(
    reservation_data: ReservationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    """
    Utwórz nową rezerwację książki (F8).

    Wymagania:
    - F8: Rezerwacja książki (użytkownik zgłasza chęć zarezerwowania wybranej pozycji)
    - NF29: Max 3 aktywne rezerwacje na użytkownika
    - NF5: Dostęp dla READER, LIBRARIAN, ADMIN (kontrola przez get_current_user + reguły)
    """
    current_user_id = current_user.get("sub")

    # Sprawdź limit rezerwacji (NF29 - max 3 aktywne na użytkownika)
    active_reservations = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == current_user_id,
            Reservation.status == ReservationStatus.ACTIVE,
            ~Reservation.is_deleted,
        )
        .count()
    )

    if active_reservations >= 3:
        # Użytkownik przekroczył limit aktywnych rezerwacji
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Osiągnięto limit 3 aktywnych rezerwacji",
        )

    # Sprawdź czy użytkownik nie ma już aktywnej rezerwacji tej konkretnej książki
    existing_reservation = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == current_user_id,
            Reservation.book_id == reservation_data.book_id,
            Reservation.status == ReservationStatus.ACTIVE,
            ~Reservation.is_deleted,
        )
        .first()
    )

    if existing_reservation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Masz już aktywną rezerwację tej książki",
        )

    # Utwórz rezerwację (F8) – domyślne daty i status ustawia model Reservation
    reservation = Reservation(
        user_id=current_user_id,
        book_id=reservation_data.book_id,
        status=ReservationStatus.ACTIVE,
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation


@router.get("/user/{user_id}", response_model=List[ReservationResponse])
async def get_user_reservations(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    """
    Pobierz rezerwacje użytkownika (F9).

    Wymagania:
    - F9: Przeglądanie własnych rezerwacji
    - NF5: RBAC – użytkownik widzi tylko swoje rezerwacje,
      LIBRARIAN/ADMIN może przeglądać rezerwacje dowolnego użytkownika.
    """
    current_user_id = current_user.get("sub")
    current_user_role = current_user.get("role")

    # Sprawdź uprawnienia (NF5 – ograniczenie dostępu do cudzych rezerwacji)
    if current_user_id != user_id and current_user_role not in ["LIBRARIAN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nie masz uprawnień do przeglądania rezerwacji innych użytkowników",
        )

    # Pobierz rezerwacje (F9) – tylko te, które nie zostały soft-usunięte
    reservations = (
        db.query(Reservation)
        .filter(Reservation.user_id == user_id, ~Reservation.is_deleted)
        .order_by(Reservation.created_at.desc())
        .all()
    )

    return reservations


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: uuid.UUID,
    current_user: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    """
    Pobierz szczegóły pojedynczej rezerwacji (F9).

    Wymagania:
    - F9: Przeglądanie rezerwacji
    - NF5: RBAC – dostęp do rezerwacji mają:
        * właściciel rezerwacji,
        * LIBRARIAN,
        * ADMIN.
    """
    # Pobierz rezerwację z bazy (z pominięciem soft-usuniętych)
    reservation = (
        db.query(Reservation)
        .filter(Reservation.id == reservation_id, ~Reservation.is_deleted)
        .first()
    )

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rezerwacja nie została znaleziona",
        )

    current_user_id = current_user.get("sub")
    current_user_role = current_user.get("role")

    # Sprawdź uprawnienia (NF5)
    if str(reservation.user_id) != current_user_id and current_user_role not in [
        "LIBRARIAN",
        "ADMIN",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nie masz uprawnień do tej rezerwacji",
        )

    return reservation


@router.patch("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: uuid.UUID,
    update_data: ReservationUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    """
    Aktualizuj rezerwację (F10 - głównie anulowanie).

    Wymagania:
    - F10: Anulowanie rezerwacji przez użytkownika
    - NF5: RBAC – właściciel, LIBRARIAN, ADMIN
    """
    # Pobierz rezerwację, jeżeli nie została soft-usunięta
    reservation = (
        db.query(Reservation)
        .filter(Reservation.id == reservation_id, ~Reservation.is_deleted)
        .first()
    )

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rezerwacja nie została znaleziona",
        )

    current_user_id = current_user.get("sub")
    current_user_role = current_user.get("role")

    # Sprawdź uprawnienia (NF5)
    if str(reservation.user_id) != current_user_id and current_user_role not in [
        "LIBRARIAN",
        "ADMIN",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nie masz uprawnień do tej rezerwacji",
        )

    # Sprawdź czy można anulować (logika biznesowa w modelu Reservation)
    if not reservation.can_be_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nie można anulować tej rezerwacji (nieprawidłowy status)",
        )

    # Aktualizuj status (F10) – typowo na CANCELLED
    if update_data.status:
        reservation.status = ReservationStatus(update_data.status)
        reservation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(reservation)

    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    reservation_id: uuid.UUID,
    current_user: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """
    Usuń rezerwację (soft delete) (NF19).

    Wymagania:
    - NF19: Soft delete zamiast fizycznego usuwania z bazy
    - NF5: RBAC – tylko LIBRARIAN/ADMIN mogą fizycznie "usuwać" rezerwacje (logicznie)
    """
    # Pobierz rezerwację, jeśli jeszcze istnieje logicznie
    reservation = (
        db.query(Reservation)
        .filter(Reservation.id == reservation_id, ~Reservation.is_deleted)
        .first()
    )

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rezerwacja nie została znaleziona",
        )

    # Soft delete (NF19) – oznaczamy jako usuniętą i zapisujemy, kto usunął
    reservation.is_deleted = True
    reservation.deleted_by = current_user.get("sub")
    reservation.updated_at = datetime.utcnow()

    db.commit()

    return None


@router.get("/", response_model=List[ReservationResponse])
async def list_reservations(
    status_filter: ReservationStatus | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """
    Pobierz listę wszystkich rezerwacji (widok administracyjny).

    Wymagania:
    - F9: Przeglądanie rezerwacji (w ujęciu globalnym – dla bibliotekarza/admina)
    - NF5: Dostęp tylko dla LIBRARIAN/ADMIN
    - NF20 (pośrednio): paginacja przy użyciu skip/limit
    """
    # Bazowe zapytanie – tylko nieusunięte rezerwacje
    query = db.query(Reservation).filter(~Reservation.is_deleted)

    # Filtruj po statusie jeśli podany (np. tylko ACTIVE, tylko EXPIRED)
    if status_filter:
        query = query.filter(Reservation.status == status_filter)

    # Paginacja i sortowanie malejąco po dacie utworzenia
    reservations = (
        query.order_by(Reservation.created_at.desc()).offset(skip).limit(limit).all()
    )

    return reservations
