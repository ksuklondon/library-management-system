"""
API Routes dla Fine - kary za przetrzymanie.

Wymaganie: F27 - Płatność kar za przetrzymanie:
    - naliczanie kar
    - przeglądanie
    - opłacanie
    - statystyki

Wymaganie: NF5 - RBAC:
    - dostęp ograniczony do odpowiednich ról (USER/LIBRARIAN/ADMIN)

Wymaganie: NF19 - Audyt:
    - soft delete
    - informacje o użytkowniku, który wykonał usunięcie
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.fine import Fine
from app.models.loan import Loan
from app.schemas.fine import FineCreate, FinePayment, FineResponse
from shared.database import get_db
from shared.dependencies import get_current_user_payload, require_role

router = APIRouter()


@router.post("/", response_model=FineResponse, status_code=status.HTTP_201_CREATED)
async def create_fine(
    fine_data: FineCreate,
    current_user: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """
    Utwórz nową karę (F27).

    Wymagania:
    - F27: Naliczanie kar za przetrzymanie
    - NF5: Tylko LIBRARIAN/ADMIN może tworzyć kary
    """
    # Sprawdź, czy wypożyczenie istnieje
    loan = db.query(Loan).filter(Loan.id == fine_data.loan_id, ~Loan.is_deleted).first()

    if not loan:
        raise HTTPException(
            status_code=404, detail="Wypożyczenie nie zostało znalezione"
        )

    # Sprawdź, czy kara dla tego wypożyczenia już nie istnieje
    existing_fine = (
        db.query(Fine)
        .filter(Fine.loan_id == fine_data.loan_id, ~Fine.is_deleted)
        .first()
    )

    if existing_fine:
        raise HTTPException(
            status_code=400, detail="Kara dla tego wypożyczenia już istnieje"
        )

    # Utwórz nową karę
    fine = Fine(
        loan_id=fine_data.loan_id,
        user_id=fine_data.user_id,
        amount=fine_data.amount,
        paid=False,
    )

    db.add(fine)
    db.commit()
    db.refresh(fine)

    return fine


@router.get("/user/{user_id}", response_model=List[FineResponse])
async def get_user_fines(
    user_id: str,
    paid: bool | None = None,
    current_user: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    """
    Pobierz listę kar użytkownika (F27).

    Wymagania:
    - F27: Użytkownik może przeglądać swoje kary
    - NF5: LIBRARIAN/ADMIN widzą wszystkie
    """
    current_user_id = current_user.get("sub")
    current_user_role = current_user.get("role")

    # RBAC — READER może przeglądać tylko swoje kary
    if current_user_id != user_id and current_user_role not in ["LIBRARIAN", "ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="Nie masz uprawnień do przeglądania kar innych użytkowników",
        )

    # Pobranie kar
    query = db.query(Fine).filter(Fine.user_id == user_id, ~Fine.is_deleted)

    # Opcjonalne filtrowanie po statusie płatności
    if paid is not None:
        query = query.filter(Fine.paid == paid)

    fines = query.order_by(Fine.created_at.desc()).all()

    return fines


@router.get("/{fine_id}", response_model=FineResponse)
async def get_fine(
    fine_id: uuid.UUID,
    current_user: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    """
    Pobierz szczegóły kary (F27).

    Wymagania:
    - F27: Przeglądanie kar
    - NF5: RBAC — użytkownik widzi tylko swoje, admin/librarian wszystko
    """
    fine = db.query(Fine).filter(Fine.id == fine_id, ~Fine.is_deleted).first()

    if not fine:
        raise HTTPException(status_code=404, detail="Kara nie została znaleziona")

    current_user_id = current_user.get("sub")
    current_user_role = current_user.get("role")

    # RBAC — dostęp ograniczony
    if str(fine.user_id) != current_user_id and current_user_role not in [
        "LIBRARIAN",
        "ADMIN",
    ]:
        raise HTTPException(status_code=403, detail="Nie masz uprawnień do tej kary")

    return fine


@router.patch("/{fine_id}/pay", response_model=FineResponse)
async def pay_fine(
    fine_id: uuid.UUID,
    payment_data: FinePayment,
    current_user: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    """
    Opłać karę (F27).

    Wymagania:
    - F27: Możliwość opłacenia kary
    - NF5: READER może opłacić tylko własne kary, ADMIN/LIBRARIAN wszystkie
    """
    fine = db.query(Fine).filter(Fine.id == fine_id, ~Fine.is_deleted).first()

    if not fine:
        raise HTTPException(404, "Kara nie została znaleziona")

    current_user_id = current_user.get("sub")
    current_user_role = current_user.get("role")

    # RBAC — ograniczenie dostępu
    if str(fine.user_id) != current_user_id and current_user_role not in [
        "LIBRARIAN",
        "ADMIN",
    ]:
        raise HTTPException(403, "Nie masz uprawnień do opłacenia tej kary")

    # Sprawdź, czy kara jest możliwa do opłacenia
    if not fine.can_be_paid():
        raise HTTPException(
            400, "Kara nie może być opłacona (już opłacona lub kwota 0)"
        )

    # Oznacz jako opłaconą
    fine.mark_as_paid(payment_method=payment_data.payment_method)

    # Ustaw fine_amount w wypożyczeniu na 0 (spłacona kara)
    loan = db.query(Loan).filter(Loan.id == fine.loan_id).first()
    if loan:
        loan.fine_amount = 0.0
        loan.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(fine)

    return fine


@router.delete("/{fine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fine(
    fine_id: uuid.UUID,
    current_user: Dict[str, Any] = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db),
):
    """
    Usuń karę (soft delete) (NF19).

    Wymagania:
    - NF19: Soft delete
    - NF5: Tylko ADMIN może usuwać kary
    """
    fine = db.query(Fine).filter(Fine.id == fine_id, ~Fine.is_deleted).first()

    if not fine:
        raise HTTPException(404, "Kara nie została znaleziona")

    # Soft delete
    fine.is_deleted = True
    fine.deleted_by = current_user.get("sub")  # już jest stringiem
    fine.updated_at = datetime.utcnow()

    db.commit()

    return None


@router.get("/", response_model=List[FineResponse])
async def list_fines(
    paid: bool | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """
    Pobierz listę kar (widok administracyjny).

    Wymagania:
    - F27: Przeglądanie wszystkich kar
    - NF5: Dostęp tylko dla LIBRARIAN/ADMIN
    """
    query = db.query(Fine).filter(~Fine.is_deleted)

    if paid is not None:
        query = query.filter(Fine.paid == paid)

    fines = query.order_by(Fine.created_at.desc()).offset(skip).limit(limit).all()

    return fines


@router.get("/unpaid/total", response_model=dict)
async def get_unpaid_total(
    user_id: str | None = None,
    current_user: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """
    Pobierz statystyki nieopłaconych kar (F27).

    Wymagania:
    - F27: Raport sumy kar
    - NF5: Tylko LIBRARIAN/ADMIN
    """
    query = db.query(Fine).filter(Fine.paid.is_(False), ~Fine.is_deleted)

    # Opcjonalnie dla konkretnego użytkownika
    if user_id:
        query = query.filter(Fine.user_id == user_id)

    fines = query.all()

    total = sum(f.amount for f in fines)

    return {"total_amount": round(total, 2), "count": len(fines), "user_id": user_id}


@router.patch("/loan/{loan_id}/calculate", response_model=FineResponse)
async def calculate_and_create_fine(
    loan_id: uuid.UUID,
    current_user: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """
    Oblicz i utwórz karę dla wypożyczenia (F27).

    Wymagania:
    - F27: Automatyczne naliczanie kar (np. w CRON + API)
    - NF5: Dostęp tylko dla LIBRARIAN/ADMIN
    """
    # Pobierz wypożyczenie
    loan = db.query(Loan).filter(Loan.id == loan_id, ~Loan.is_deleted).first()

    if not loan:
        raise HTTPException(404, "Wypożyczenie nie zostało znalezione")

    # Oblicz należną karę
    fine_amount = loan.calculate_current_fine()

    if fine_amount <= 0:
        raise HTTPException(
            400, "Brak kary do naliczenia (wypożyczenie nie jest przetrzymane)"
        )

    # Sprawdź czy kara już istnieje
    existing_fine = (
        db.query(Fine).filter(Fine.loan_id == loan_id, ~Fine.is_deleted).first()
    )

    if existing_fine:
        # Zaktualizuj kwotę jeśli kara nieopłacona
        if not existing_fine.paid:
            existing_fine.update_amount(fine_amount)
            db.commit()
            db.refresh(existing_fine)
            return existing_fine
        else:
            raise HTTPException(400, "Kara już istnieje i jest opłacona")

    # Stwórz nową karę
    fine = Fine(loan_id=loan_id, user_id=loan.user_id, amount=fine_amount, paid=False)

    # Synchronizuj wartość z modelem Loan
    loan.fine_amount = fine_amount
    loan.updated_at = datetime.utcnow()

    db.add(fine)
    db.commit()
    db.refresh(fine)

    return fine
