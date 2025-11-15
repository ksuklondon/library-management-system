"""
Schemas dla modelu BookCopy - walidacja i serializacja egzemplarzy.

Wymagania: F16
Pydantic models dla operacji na egzemplarzach książek.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CopyStatusEnum(str, Enum):
    """
    Enum statusów egzemplarza (dla Pydantic).

    Wymaganie F16: Zarządzanie statusem egzemplarzy
    """

    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    BORROWED = "BORROWED"
    DAMAGED = "DAMAGED"
    LOST = "LOST"


class BookCopyBase(BaseModel):
    """
    Bazowy schemat egzemplarza książki.
    """

    inventory_no: str = Field(
        ..., min_length=1, max_length=50, description="Numer inwentarzowy (unikalny)"
    )
    location: Optional[str] = Field(
        None, max_length=100, description="Lokalizacja w bibliotece"
    )
    status: CopyStatusEnum = Field(
        CopyStatusEnum.AVAILABLE, description="Status egzemplarza"
    )


class BookCopyCreate(BaseModel):
    """
    Schemat do tworzenia nowego egzemplarza.

    Wymaganie F16: Dodawanie egzemplarzy (LIBRARIAN/ADMIN)
    """

    book_id: UUID = Field(..., description="UUID książki")
    inventory_no: str = Field(
        ..., min_length=1, max_length=50, description="Numer inwentarzowy"
    )
    location: Optional[str] = Field(None, max_length=100, description="Lokalizacja")


class BookCopyUpdate(BaseModel):
    """
    Schemat do aktualizacji egzemplarza - wszystkie pola opcjonalne.

    Wymaganie F16: Edycja egzemplarzy (LIBRARIAN/ADMIN)
    """

    inventory_no: Optional[str] = Field(None, min_length=1, max_length=50)
    location: Optional[str] = Field(None, max_length=100)
    status: Optional[CopyStatusEnum] = Field(None)


class CopyStatusUpdate(BaseModel):
    """
    Schemat do zmiany tylko statusu egzemplarza.

    Wymaganie F16: Zmiana statusu egzemplarza
    """

    status: CopyStatusEnum = Field(..., description="Nowy status egzemplarza")


class BookCopyResponse(BookCopyBase):
    """
    Schemat odpowiedzi - egzemplarz z dodatkowymi polami.

    Wymaganie F16: Wyświetlanie informacji o egzemplarzach
    """

    id: UUID
    book_id: UUID
    book_title: Optional[str] = Field(None, description="Tytuł książki (dla wygody)")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
