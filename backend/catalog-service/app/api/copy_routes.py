"""
Book Copy Management Routes - zarządzanie egzemplarzami książek.

Realizowane wymagania:
- F16: Zarządzanie egzemplarzami książek (dodawanie, edycja, przeglądanie, usuwanie)
- NF19: Soft delete dla egzemplarzy (zachowanie danych do audytu)

Dostęp:
- LIBRARIAN, ADMIN – dodawanie, edycja, zmiana statusu egzemplarzy
- tylko ADMIN – usuwanie egzemplarzy
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.book_copy import BookCopy, CopyStatus
from app.models.user import User, UserRole
from app.schemas.book_copy import (
    BookCopyCreate,
    BookCopyResponse,
    BookCopyUpdate,
    CopyStatusUpdate,
)
from backend.shared.database import get_db
from backend.shared.dependencies import require_role

router = APIRouter()


@router.post("/", response_model=BookCopyResponse, status_code=status.HTTP_201_CREATED)
def create_book_copy(
    copy_data: BookCopyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.LIBRARIAN, UserRole.ADMIN])),
):
    """
    Dodawanie nowego egzemplarza książki.

    Wymaganie F16: Dodawanie egzemplarzy (LIBRARIAN/ADMIN).
    Sprawdzane jest:
    - czy książka istnieje i nie została usunięta,
    - czy numer inwentarzowy jest unikalny w systemie.
    Nowy egzemplarz domyślnie otrzymuje status AVAILABLE.
    """
    book = (
        db.query(Book)
        .filter(Book.id == copy_data.book_id, Book.is_deleted == False)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Książka nie znaleziona"
        )

    existing_copy = (
        db.query(BookCopy)
        .filter(BookCopy.inventory_no == copy_data.inventory_no)
        .first()
    )

    if existing_copy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Egzemplarz o numerze inwentarzowym {copy_data.inventory_no} już istnieje",
        )

    new_copy = BookCopy(
        book_id=copy_data.book_id,
        inventory_no=copy_data.inventory_no,
        location=copy_data.location,
        status=CopyStatus.AVAILABLE,
    )

    db.add(new_copy)
    db.commit()
    db.refresh(new_copy)

    return BookCopyResponse(
        id=new_copy.id,
        book_id=new_copy.book_id,
        inventory_no=new_copy.inventory_no,
        status=new_copy.status,
        location=new_copy.location,
        book_title=book.title,
        created_at=new_copy.created_at,
        updated_at=new_copy.updated_at,
    )


@router.get("/book/{book_id}", response_model=List[BookCopyResponse])
def get_copies_by_book(
    book_id: UUID, include_deleted: bool = False, db: Session = Depends(get_db)
):
    """
    Lista egzemplarzy konkretnej książki.

    Wymaganie F16: Wyświetlanie egzemplarzy książki.
    Parametr include_deleted pozwala zdecydować, czy zwracać również egzemplarze
    oznaczone jako usunięte (soft delete), co jest przydatne np. do audytu.
    """
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Książka nie znaleziona"
        )

    query = db.query(BookCopy).filter(BookCopy.book_id == book_id)

    if not include_deleted:
        query = query.filter(BookCopy.is_deleted == False)

    copies = query.all()

    copies_response = []
    for copy in copies:
        copy_data = BookCopyResponse(
            id=copy.id,
            book_id=copy.book_id,
            inventory_no=copy.inventory_no,
            status=copy.status,
            location=copy.location,
            book_title=book.title,
            created_at=copy.created_at,
            updated_at=copy.updated_at,
        )
        copies_response.append(copy_data)

    return copies_response


@router.get("/{copy_id}", response_model=BookCopyResponse)
def get_copy_details(copy_id: UUID, db: Session = Depends(get_db)):
    """
    Szczegóły konkretnego egzemplarza książki.

    Wymaganie F16: Wyświetlanie szczegółów egzemplarza.
    Zwraca m.in. status egzemplarza (AVAILABLE, BORROWED, DAMAGED itd.)
    oraz tytuł powiązanej książki.
    """
    copy = (
        db.query(BookCopy)
        .filter(BookCopy.id == copy_id, BookCopy.is_deleted == False)
        .first()
    )

    if not copy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Egzemplarz nie znaleziony"
        )

    book = db.query(Book).filter(Book.id == copy.book_id).first()

    return BookCopyResponse(
        id=copy.id,
        book_id=copy.book_id,
        inventory_no=copy.inventory_no,
        status=copy.status,
        location=copy.location,
        book_title=book.title if book else None,
        created_at=copy.created_at,
        updated_at=copy.updated_at,
    )


@router.put("/{copy_id}", response_model=BookCopyResponse)
def update_book_copy(
    copy_id: UUID,
    copy_data: BookCopyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.LIBRARIAN, UserRole.ADMIN])),
):
    """
    Aktualizacja informacji o egzemplarzu (np. lokalizacja, numer inwentarzowy).

    Wymaganie F16: Edycja egzemplarzy (LIBRARIAN/ADMIN).
    Przy zmianie numeru inwentarzowego sprawdzana jest jego unikalność
    wśród innych egzemplarzy.
    """
    copy = (
        db.query(BookCopy)
        .filter(BookCopy.id == copy_id, BookCopy.is_deleted == False)
        .first()
    )

    if not copy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Egzemplarz nie znaleziony"
        )

    if copy_data.inventory_no and copy_data.inventory_no != copy.inventory_no:
        existing = (
            db.query(BookCopy)
            .filter(
                BookCopy.inventory_no == copy_data.inventory_no, BookCopy.id != copy_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Numer inwentarzowy {copy_data.inventory_no} jest już używany",
            )

    update_data = copy_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(copy, field, value)

    db.commit()
    db.refresh(copy)

    book = db.query(Book).filter(Book.id == copy.book_id).first()

    return BookCopyResponse(
        id=copy.id,
        book_id=copy.book_id,
        inventory_no=copy.inventory_no,
        status=copy.status,
        location=copy.location,
        book_title=book.title if book else None,
        created_at=copy.created_at,
        updated_at=copy.updated_at,
    )


@router.patch("/{copy_id}/status", response_model=BookCopyResponse)
def update_copy_status(
    copy_id: UUID,
    status_data: CopyStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.LIBRARIAN, UserRole.ADMIN])),
):
    """
    Zmiana statusu egzemplarza (AVAILABLE, DAMAGED, LOST, BORROWED, RESERVED itd.).

    Wymaganie F16: Zmiana statusu egzemplarza.
    Logika biznesowa:
    - egzemplarz, który jest BORROWED lub RESERVED, nie może zostać
      zmieniony na status typu LOST/DAMAGED bezpośrednio, z pominięciem
      procesu obsługi wypożyczeń (loan-service).
    """
    copy = (
        db.query(BookCopy)
        .filter(BookCopy.id == copy_id, BookCopy.is_deleted == False)
        .first()
    )

    if not copy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Egzemplarz nie znaleziony"
        )

    if copy.status in [
        CopyStatus.BORROWED,
        CopyStatus.RESERVED,
    ] and status_data.status not in [
        CopyStatus.BORROWED,
        CopyStatus.RESERVED,
        CopyStatus.AVAILABLE,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nie można zmienić statusu egzemplarza który jest {copy.status}",
        )

    copy.status = status_data.status

    db.commit()
    db.refresh(copy)

    book = db.query(Book).filter(Book.id == copy.book_id).first()

    return BookCopyResponse(
        id=copy.id,
        book_id=copy.book_id,
        inventory_no=copy.inventory_no,
        status=copy.status,
        location=copy.location,
        book_title=book.title if book else None,
        created_at=copy.created_at,
        updated_at=copy.updated_at,
    )


@router.delete("/{copy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_copy(
    copy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
):
    """
    Usuwanie egzemplarza (soft delete).

    Wymaganie F16: Usuwanie egzemplarzy (tylko ADMIN).
    Wymaganie NF19: Soft delete – egzemplarz nie jest usuwany fizycznie z bazy,
    a jedynie oznaczany jako usunięty (is_deleted = True).
    Dodatkowe ograniczenie: nie można usunąć egzemplarza o statusie BORROWED
    lub RESERVED (wypożyczony / zarezerwowany).
    """
    copy = (
        db.query(BookCopy)
        .filter(BookCopy.id == copy_id, BookCopy.is_deleted == False)
        .first()
    )

    if not copy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Egzemplarz nie znaleziony"
        )

    if copy.status in [CopyStatus.BORROWED, CopyStatus.RESERVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nie można usunąć egzemplarza - status: {copy.status}",
        )

    copy.is_deleted = True

    db.commit()

    return None
