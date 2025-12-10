"""
Trasy API do zarządzania książkami (Book Management Routes).

Realizowane wymagania:
- F15: Zarządzanie książkami (dodawanie, edycja, usuwanie, lista)
- NF19: Soft delete dla książek (wsparcie dla audytu)

Dostęp:
- LIBRARIAN, ADMIN – tworzenie i edycja książek
- tylko ADMIN – usuwanie książek
"""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from shared.database import get_db
from shared.dependencies import require_role

router = APIRouter()


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
):
    """
    Dodawanie nowej książki do katalogu.

    Wymaganie F15: Dodawanie książek (LIBRARIAN/ADMIN).
    Jeśli podano ISBN, endpoint sprawdza, czy książka z takim ISBN nie istnieje już w systemie.
    """
    if book_data.isbn:
        existing_book = db.query(Book).filter(Book.isbn == book_data.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Książka z ISBN {book_data.isbn} już istnieje",
            )

    new_book = Book(
        title=book_data.title,
        authors=book_data.authors,
        isbn=book_data.isbn,
        publisher=book_data.publisher,
        pages=book_data.pages,
        language=book_data.language,
        cover_url=book_data.cover_url,
        description=book_data.description,
        genre=book_data.genre,
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return BookResponse(
        id=new_book.id,
        title=new_book.title,
        authors=new_book.authors,
        isbn=new_book.isbn,
        publisher=new_book.publisher,
        pages=new_book.pages,
        language=new_book.language,
        cover_url=new_book.cover_url,
        description=new_book.description,
        genre=new_book.genre,
        available_copies=0,
        total_copies=0,
        created_at=new_book.created_at,
        updated_at=new_book.updated_at,
    )


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
):
    """
    Aktualizacja informacji o książce.

    Wymaganie F15: Edycja książek (LIBRARIAN/ADMIN).
    Dodatkowo pilnowana jest unikalność ISBN – nie można przypisać ISBN
    już używanego przez inną książkę.
    """
    book = db.query(Book).filter(Book.id == book_id, Book.is_deleted.is_(False)).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Książka nie znaleziona"
        )

    if book_data.isbn and book_data.isbn != book.isbn:
        existing = (
            db.query(Book)
            .filter(Book.isbn == book_data.isbn, Book.id != book_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ISBN {book_data.isbn} jest już używany przez inną książkę",
            )

    update_data = book_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)

    return BookResponse(
        id=book.id,
        title=book.title,
        authors=book.authors,
        isbn=book.isbn,
        publisher=book.publisher,
        pages=book.pages,
        language=book.language,
        cover_url=book.cover_url,
        description=book.description,
        genre=book.genre,
        available_copies=book.get_available_copies_count(),
        total_copies=book.get_total_copies_count(),
        created_at=book.created_at,
        updated_at=book.updated_at,
    )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_role(["ADMIN"])),
):
    """
    Usuwanie książki (soft delete).

    Wymaganie F15: Usuwanie książek (tylko ADMIN)
    Wymaganie NF19: Soft delete (audyt) – rekord książki i jej egzemplarzy
    jest oznaczany jako usunięty, ale pozostaje w bazie.
    Dodatkowo książka nie może zostać usunięta, jeśli istnieją wypożyczone
    lub zarezerwowane egzemplarze.
    """
    book = db.query(Book).filter(Book.id == book_id, Book.is_deleted.is_(False)).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Książka nie znaleziona"
        )

    active_copies = sum(
        1
        for copy in book.copies
        if copy.status in ["BORROWED", "RESERVED"] and not copy.is_deleted
    )

    if active_copies > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nie można usunąć książki - {active_copies} egzemplarzy jest wypożyczonych lub zarezerwowanych",
        )

    book.is_deleted = True
    book.deleted_by = UUID(current_user.get("sub"))

    for copy in book.copies:
        if not copy.is_deleted:
            copy.is_deleted = True

    db.commit()

    return None


@router.get("/", response_model=List[BookResponse])
def get_all_books_management(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
):
    """
    Lista wszystkich książek (dla panelu zarządzania).

    Wymaganie F15: Zarządzanie książkami.
    Parametr include_deleted pozwala opcjonalnie uwzględnić książki
    oznaczone jako usunięte (soft delete), co ułatwia przegląd historii.
    """
    query = db.query(Book)

    if not include_deleted:
        query = query.filter(Book.is_deleted.is_(False))

    books = query.offset(skip).limit(limit).all()

    books_response = []
    for book in books:
        book_data = BookResponse(
            id=book.id,
            title=book.title,
            authors=book.authors,
            isbn=book.isbn,
            publisher=book.publisher,
            pages=book.pages,
            language=book.language,
            cover_url=book.cover_url,
            description=book.description,
            genre=book.genre,
            available_copies=book.get_available_copies_count(),
            total_copies=book.get_total_copies_count(),
            created_at=book.created_at,
            updated_at=book.updated_at,
        )
        books_response.append(book_data)

    return books_response
