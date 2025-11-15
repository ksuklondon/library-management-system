"""
Schemas dla modelu Book - walidacja i serializacja danych książek.

Wymagania: F4, F5, F6, F7, F15
Pydantic models dla operacji na książkach.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BookBase(BaseModel):
    """
    Bazowy schemat książki - wspólne pola dla wszystkich operacji.
    """

    title: str = Field(..., min_length=1, max_length=500, description="Tytuł książki")
    authors: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Autorzy (rozdzieleni przecinkami)",
    )
    isbn: Optional[str] = Field(
        None, min_length=10, max_length=20, description="Numer ISBN"
    )
    publisher: Optional[str] = Field(None, max_length=255, description="Wydawca")
    pages: Optional[int] = Field(None, gt=0, description="Liczba stron")
    language: Optional[str] = Field("pl", max_length=50, description="Język publikacji")
    cover_url: Optional[str] = Field(None, max_length=500, description="URL okładki")
    description: Optional[str] = Field(None, description="Opis książki")
    genre: Optional[str] = Field(None, max_length=100, description="Gatunek literacki")

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: Optional[str]) -> Optional[str]:
        """
        Walidacja numeru ISBN.

        Wymaganie NF7: Walidacja danych wejściowych
        """
        if v is None:
            return v

        cleaned = v.replace("-", "").replace(" ", "")

        if len(cleaned) not in [10, 13]:
            raise ValueError("ISBN musi mieć 10 lub 13 cyfr")

        if not cleaned.isdigit():
            raise ValueError("ISBN może zawierać tylko cyfry")

        return v


class BookCreate(BookBase):
    """
    Schemat do tworzenia nowej książki.

    Wymaganie F15: Dodawanie książek (LIBRARIAN/ADMIN)
    """

    pass


class BookUpdate(BaseModel):
    """
    Schemat do aktualizacji książki - wszystkie pola opcjonalne.

    Wymaganie F15: Edycja książek (LIBRARIAN/ADMIN)
    """

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    authors: Optional[str] = Field(None, min_length=1, max_length=500)
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    publisher: Optional[str] = Field(None, max_length=255)
    pages: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, max_length=50)
    cover_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None)
    genre: Optional[str] = Field(None, max_length=100)


class BookResponse(BookBase):
    """
    Schemat odpowiedzi - książka z dodatkowymi polami.

    Wymaganie F7: Szczegóły książki
    """

    id: UUID
    available_copies: int = Field(..., description="Liczba dostępnych egzemplarzy")
    total_copies: int = Field(..., description="Całkowita liczba egzemplarzy")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    """
    Schemat odpowiedzi dla listy książek z paginacją.

    Wymaganie F4: Przeglądanie katalogu
    Wymaganie NF20: Paginacja (max 50 wyników na stronę)
    """

    books: List[BookResponse]
    total: int = Field(..., description="Całkowita liczba książek")
    page: int = Field(..., ge=1, description="Numer strony")
    page_size: int = Field(..., ge=1, le=50, description="Rozmiar strony")
    total_pages: int = Field(..., description="Całkowita liczba stron")
