"""
API Routes dla Loan - wypożyczenia książek.

Wymaganie: F11-F14 - Wypożyczenia książek:
    - F11: Utworzenie wypożyczenia
    - F12: Zwrot książki
    - F13: Przeglądanie historii wypożyczeń
    - F14: Przedłużenie wypożyczenia

Wymaganie: NF5 - RBAC (Role-Based Access Control):
    - dostęp do operacji zależny od roli (READER/LIBRARIAN/ADMIN)

Wymaganie: NF19 - Audyt:
    - soft delete zamiast trwałego usuwania
    - przechowywanie informacji kto usunął rekord
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import uuid

from backend.shared.database import get_db
from backend.shared.auth import get_current_user, require_roles
from backend.shared.models import User
from app.models.loan import Loan, LoanStatus
from app.schemas.loan import (
    LoanCreate,
    LoanResponse,
    LoanUpdate,
    LoanExtend
)

router = APIRouter()


@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    loan_data: LoanCreate,
    current_user: User = Depends(require_roles(['LIBRARIAN', 'ADMIN'])),
    db: Session = Depends(get_db)
):
    """
    Utwórz nowe wypożyczenie (F11).

    Wymagania:
    - F11: Możliwość wypożyczenia książki
    - NF29: Limit 5 aktywnych wypożyczeń na użytkownika
    - NF5: Tylko LIBRARIAN/ADMIN może tworzyć wypożyczenia
    """
    # Sprawdź limit wypożyczeń użytkownika (NF29)
    active_loans = db.query(Loan).filter(
        Loan.user_id == loan_data.user_id,
        Loan.status == LoanStatus.ACTIVE,
        Loan.is_deleted == False
    ).count()

    if active_loans >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Użytkownik osiągnął limit 5 aktywnych wypożyczeń"
        )

    # Sprawdź, czy użytkownik nie ma już wypożyczonego tego egzemplarza
    existing_loan = db.query(Loan).filter(
        Loan.user_id == loan_data.user_id,
        Loan.book_copy_id == loan_data.book_copy_id,
        Loan.status == LoanStatus.ACTIVE,
        Loan.is_deleted == False
    ).first()

    if existing_loan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Użytkownik ma już wypożyczony ten egzemplarz"
        )

    # Utwórz wypożyczenie
    loan = Loan(
        user_id=loan_data.user_id,
        book_copy_id=loan_data.book_copy_id,
        borrowed_at=datetime.utcnow(),
        status=LoanStatus.ACTIVE
    )

    # Jeśli podano due_date – użyj go, w przeciwnym razie +14 dni (NF29)
    loan.due_date = loan_data.due_date or (datetime.utcnow() + timedelta(days=14))

    db.add(loan)
    db.commit()
    db.refresh(loan)

    return loan


@router.get("/user/{user_id}", response_model=List[LoanResponse])
async def get_user_loans(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pobierz wszystkie wypożyczenia użytkownika (F13).

    Wymagania:
    - F13: Historia wypożyczeń użytkownika
    - NF5: READER widzi tylko swoje wypożyczenia, LIBRARIAN/ADMIN mogą przeglądać wszystkie
    """
    # Sprawdzenie uprawnień (RBAC)
    if current_user.id != user_id and current_user.role not in ['LIBRARIAN', 'ADMIN']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nie masz uprawnień do przeglądania wypożyczeń innych użytkowników"
        )

    # Pobranie wypożyczeń
    loans = db.query(Loan).filter(
        Loan.user_id == user_id,
        Loan.is_deleted == False
    ).order_by(Loan.borrowed_at.desc()).all()

    return loans


@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(
    loan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pobierz szczegóły wypożyczenia (F13).

    Wymagania:
    - F13: Wgląd w szczegóły wypożyczenia
    - NF5: READER widzi swoje, LIBRARIAN/ADMIN widzą wszystkie
    """
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.is_deleted == False
    ).first()

    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wypożyczenie nie zostało znalezione"
        )

    # RBAC – dostęp tylko dla właściciela lub LIBRARIAN/ADMIN
    if loan.user_id != current_user.id and current_user.role not in ['LIBRARIAN', 'ADMIN']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nie masz uprawnień do tego wypożyczenia"
        )

    return loan


@router.patch("/{loan_id}/return", response_model=LoanResponse)
async def return_loan(
    loan_id: uuid.UUID,
    current_user: User = Depends(require_roles(['LIBRARIAN', 'ADMIN'])),
    db: Session = Depends(get_db)
):
    """
    Zwróć książkę (F12).

    Wymagania:
    - F12: Zwrot wypożyczonej książki
    - F27: Automatyczne naliczanie kary za przetrzymanie
    - NF5: Tylko LIBRARIAN/ADMIN mogą rejestrować zwroty
    """
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.is_deleted == False
    ).first()

    if not loan:
        raise HTTPException(status_code=404, detail="Wypożyczenie nie zostało znalezione")

    if not loan.can_be_returned():
        raise HTTPException(
            status_code=400,
            detail="Nie można zwrócić tej książki (nieprawidłowy status)"
        )

    # Wykonanie zwrotu i obliczenie ewentualnej kary (F27)
    loan.return_book()

    db.commit()
    db.refresh(loan)

    return loan


@router.patch("/{loan_id}/extend", response_model=LoanResponse)
async def extend_loan(
    loan_id: uuid.UUID,
    extend_data: LoanExtend,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Przedłuż wypożyczenie (F14).

    Wymagania:
    - F14: Przedłużenie o 1–14 dni
    - NF5: READER może przedłużyć swoje wypożyczenia, LIBRARIAN/ADMIN dowolne
    """
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.is_deleted == False
    ).first()

    if not loan:
        raise HTTPException(404, "Wypożyczenie nie zostało znalezione")

    # RBAC
    if loan.user_id != current_user.id and current_user.role not in ['LIBRARIAN', 'ADMIN']:
        raise HTTPException(403, "Nie masz uprawnień do tego wypożyczenia")

    # Sprawdź, czy można przedłużyć (F14)
    if not loan.can_be_extended():
        raise HTTPException(
            400, "Nie można przedłużyć tego wypożyczenia (przetrzymane lub już przedłużone)"
        )

    # Próba przedłużenia
    success = loan.extend_loan(days=extend_data.days)

    if not success:
        raise HTTPException(400, "Nie udało się przedłużyć wypożyczenia")

    db.commit()
    db.refresh(loan)

    return loan


@router.patch("/{loan_id}", response_model=LoanResponse)
async def update_loan(
    loan_id: uuid.UUID,
    update_data: LoanUpdate,
    current_user: User = Depends(require_roles(['LIBRARIAN', 'ADMIN'])),
    db: Session = Depends(get_db)
):
    """
    Aktualizacja wypożyczenia (ADMIN/LIBRARIAN).

    Wymagania:
    - NF5: Operacja tylko dla LIBRARIAN/ADMIN
    """
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.is_deleted == False
    ).first()

    if not loan:
        raise HTTPException(404, "Wypożyczenie nie zostało znalezione")

    # Zaktualizuj pola zależnie od przekazanych danych
    if update_data.returned_at is not None:
        loan.returned_at = update_data.returned_at
        if loan.returned_at and loan.status == LoanStatus.ACTIVE:
            loan.status = LoanStatus.RETURNED

    if update_data.due_date is not None:
        loan.due_date = update_data.due_date

    if update_data.status is not None:
        loan.status = update_data.status

    loan.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(loan)

    return loan


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(
    loan_id: uuid.UUID,
    current_user: User = Depends(require_roles(['ADMIN'])),
    db: Session = Depends(get_db)
):
    """
    Usuń wypożyczenie (soft delete) (NF19).

    Wymagania:
    - NF19: Soft delete – ukrywanie rekordów zamiast fizycznego kasowania
    - NF5: Tylko ADMIN może usuwać wypożyczenia
    """
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.is_deleted == False
    ).first()

    if not loan:
        raise HTTPException(404, "Wypożyczenie nie zostało znalezione")

    loan.is_deleted = True
    loan.deleted_by = current_user.id
    loan.updated_at = datetime.utcnow()

    db.commit()

    return None


@router.get("/", response_model=List[LoanResponse])
async def list_loans(
    status: LoanStatus = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_roles(['LIBRARIAN', 'ADMIN'])),
    db: Session = Depends(get_db)
):
    """
    Pobierz listę wypożyczeń (widok administracyjny).

    Wymagania:
    - NF5: Dostęp tylko dla LIBRARIAN/ADMIN
    - NF20: Paginacja
    """
    query = db.query(Loan).filter(Loan.is_deleted == False)

    # Filtr statusu
    if status:
        query = query.filter(Loan.status == status)

    loans = query.order_by(
        Loan.borrowed_at.desc()
    ).offset(skip).limit(limit).all()

    return loans


@router.get("/overdue/all", response_model=List[LoanResponse])
async def get_overdue_loans(
    current_user: User = Depends(require_roles(['LIBRARIAN', 'ADMIN'])),
    db: Session = Depends(get_db)
):
    """
    Pobierz wszystkie przetrzymane wypożyczenia (F27).

    Wymagania:
    - F27: Identyfikacja przeterminowanych wypożyczeń
    - NF5: Dostęp tylko dla LIBRARIAN/ADMIN
    """
    overdue_loans = db.query(Loan).filter(
        Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]),
        Loan.due_date < datetime.utcnow(),
        Loan.returned_at.is_(None),
        Loan.is_deleted == False
    ).order_by(Loan.due_date.asc()).all()

    # Aktualizacja statusu w bazie
    for loan in overdue_loans:
        if loan.status == LoanStatus.ACTIVE:
            loan.mark_as_overdue()

    db.commit()

    return overdue_loans
