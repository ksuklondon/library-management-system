"""
Trasy API katalogu (Catalog Routes) – endpointy do przeglądania i wyszukiwania książek.

Realizowane wymagania funkcjonalne:
- F4: Przeglądanie katalogu
- F5: Wyszukiwanie książek
- F6: Filtrowanie katalogu
- F7: Szczegóły książki

Realizowane wymagania niefunkcjonalne:
- NF20: Paginacja wyników (limit do 50 pozycji na stronę)

Dostęp:
- otwarte dla wszystkich zalogowanych ról (READER, LIBRARIAN, ADMIN).
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.book_copy import BookCopy, CopyStatus
from app.schemas.book import BookListResponse, BookResponse
from app.schemas.catalog import SearchQuery
from shared.database import get_db

router = APIRouter()


@router.get("/browse", response_model=BookListResponse)
def browse_catalog(
    page: int = Query(1, ge=1, description="Numer strony"),
    page_size: int = Query(20, ge=1, le=50, description="Rozmiar strony (max 50)"),
    authors: Optional[str] = Query(None, description="Filtruj po autorze"),
    genre: Optional[str] = Query(None, description="Filtruj po gatunku"),
    language: Optional[str] = Query(None, description="Filtruj po języku"),
    publisher: Optional[str] = Query(None, description="Filtruj po wydawcy"),
    available_only: bool = Query(False, description="Tylko dostępne książki"),
    db: Session = Depends(get_db),
):
    """
    Przeglądanie katalogu książek z filtrowaniem i paginacją.

    Wymaganie F4: Przeglądanie katalogu.
    Wymaganie F6: Filtrowanie według autora, gatunku, języka, wydawcy.
    Wymaganie NF20: Paginacja (maks. 50 wyników na stronę).

    Parametr available_only pozwala wyświetlić tylko te pozycje,
    które mają co najmniej jeden egzemplarz o statusie AVAILABLE.
    """
    query = db.query(Book).filter(~Book.is_deleted)

    if authors:
        query = query.filter(Book.authors.ilike(f"%{authors}%"))

    if genre:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))

    if language:
        query = query.filter(Book.language == language)

    if publisher:
        query = query.filter(Book.publisher.ilike(f"%{publisher}%"))

    if available_only:
        query = (
            query.join(BookCopy)
            .filter(
                and_(
                    BookCopy.status == CopyStatus.AVAILABLE,
                    ~BookCopy.is_deleted,
                )
            )
            .distinct()
        )

    total = query.count()

    offset = (page - 1) * page_size
    books = query.offset(offset).limit(page_size).all()

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

    total_pages = (total + page_size - 1) // page_size

    return BookListResponse(
        books=books_response,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/search", response_model=BookListResponse)
def search_books(
    search: SearchQuery,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Wyszukiwanie książek według tytułu, autora lub ISBN.

    Wymaganie F5: Wyszukiwanie książek.

    Pole search.search_in określa, w którym polu szukać:
    - 'title'   – tylko tytuł,
    - 'authors' – tylko autorzy,
    - 'isbn'    – tylko ISBN,
    - inne / brak – wyszukiwanie we wszystkich trzech polach jednocześnie.
    Wyniki są paginowane (NF20) tak jak w przeglądaniu katalogu.
    """
    query = db.query(Book).filter(~Book.is_deleted)

    search_term = f"%{search.query}%"

    if search.search_in == "title":
        query = query.filter(Book.title.ilike(search_term))
    elif search.search_in == "authors":
        query = query.filter(Book.authors.ilike(search_term))
    elif search.search_in == "isbn":
        query = query.filter(Book.isbn.ilike(search_term))
    else:
        query = query.filter(
            or_(
                Book.title.ilike(search_term),
                Book.authors.ilike(search_term),
                Book.isbn.ilike(search_term),
            )
        )

    total = query.count()

    offset = (page - 1) * page_size
    books = query.offset(offset).limit(page_size).all()

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

    total_pages = (total + page_size - 1) // page_size

    return BookListResponse(
        books=books_response,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{book_id}", response_model=BookResponse)
def get_book_details(book_id: UUID, db: Session = Depends(get_db)):
    """
    Szczegóły konkretnej książki.

    Wymaganie F7: Szczegóły książki (tytuł, autor, dane wydawnicze, dostępność).
    Zwracane są m.in. liczby dostępnych egzemplarzy (available_copies)
    oraz wszystkich egzemplarzy danej książki (total_copies).
    """
    book = db.query(Book).filter(and_(Book.id == book_id, ~Book.is_deleted)).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Książka nie znaleziona"
        )

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
