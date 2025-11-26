"""
Schemas dla Loan - wypożyczenia książek.

Wymaganie: F11-F14 - Wypożyczenia
Wymaganie: NF7 - Walidacja danych wejściowych

Schematy Pydantic używane do:
- przyjmowania żądań tworzenia / aktualizacji wypożyczeń,
- walidacji danych wejściowych z API,
- zwracania ustrukturyzowanych odpowiedzi z danymi wypożyczeń.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class LoanStatus(str, Enum):
    """Status wypożyczenia (F11-F14)."""
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class LoanCreate(BaseModel):
    """
    Schema do tworzenia wypożyczenia (F11).

    Wymaganie: F11 - Wypożyczenie książki (LIBRARIAN)
    Wymaganie: NF7 - Walidacja danych

    Używana w endpointach tworzących nowe wypożyczenie:
    - sprawdzamy, czy przekazano user_id i book_copy_id,
    - opcjonalnie można podać własny due_date (termin zwrotu),
      w przeciwnym wypadku model domenowy ustawi domyślnie +14 dni.
    """
    user_id: str = Field(..., description="ID użytkownika wypożyczającego")
    book_copy_id: uuid.UUID = Field(..., description="ID egzemplarza książki")
    due_date: Optional[datetime] = Field(
        None,
        description="Termin zwrotu (domyślnie +14 dni, jeśli nie podano)"
    )

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        """Walidacja user_id (NF7) – nie może być puste."""
        if not v or not v.strip():
            raise ValueError("ID użytkownika jest wymagane")
        return v

    @field_validator('book_copy_id')
    @classmethod
    def validate_book_copy_id(cls, v):
        """Walidacja book_copy_id (NF7) – musi zostać przekazane poprawne UUID."""
        if v is None:
            raise ValueError("ID egzemplarza książki jest wymagane")
        return v

    class Config:
        # Przykład ułatwia testowanie i dokumentację w Swagger / ReDoc.
        json_schema_extra = {
            "example": {
                "user_id": "user-uuid-123",
                "book_copy_id": "123e4567-e89b-12d3-a456-426614174000",
                "due_date": "2024-11-29T23:59:59"
            }
        }


class LoanUpdate(BaseModel):
    """
    Schema do aktualizacji wypożyczenia (F12, F14).

    Wymaganie: F12 - Zwrot książki
    Wymaganie: F14 - Przedłużenie wypożyczenia (opcjonalne)

    Wszystkie pola są opcjonalne – można zaktualizować tylko wybrane:
    - returned_at – data faktycznego zwrotu,
    - due_date – nowy termin zwrotu (np. ręczne przedłużenie),
    - status – zmiana statusu (np. na RETURNED).
    """
    returned_at: Optional[datetime] = Field(None, description="Data zwrotu książki")
    due_date: Optional[datetime] = Field(None, description="Nowy termin zwrotu (przedłużenie)")
    status: Optional[LoanStatus] = Field(None, description="Nowy status wypożyczenia")

    class Config:
        json_schema_extra = {
            "example": {
                "returned_at": "2024-11-20T15:30:00",
                "status": "RETURNED"
            }
        }


class LoanExtend(BaseModel):
    """
    Schema do przedłużenia wypożyczenia (F14).

    Wymaganie: F14 - Przedłużenie wypożyczenia

    Używana np. w dedykowanym endpointzie:
    - użytkownik/bibliotekarz podaje liczbę dni przedłużenia,
    - serwis sprawdza reguły biznesowe i wywołuje metodę extend_loan w modelu Loan.
    """
    days: int = Field(
        default=7,
        ge=1,
        le=14,
        description="Liczba dni przedłużenia (1-14)"
    )

    @field_validator('days')
    @classmethod
    def validate_days(cls, v):
        """Walidacja liczby dni (NF7) – tylko wartości z zakresu 1–14 są akceptowane."""
        if v < 1 or v > 14:
            raise ValueError("Można przedłużyć od 1 do 14 dni")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "days": 7
            }
        }


class LoanResponse(BaseModel):
    """
    Schema odpowiedzi z danymi wypożyczenia (F13).

    Wymaganie: F13 - Historia wypożyczeń

    Zawiera pełne informacje potrzebne do wyświetlenia historii:
    - daty wypożyczenia, terminu zwrotu, ewentualnego zwrotu,
    - status wypożyczenia,
    - aktualną kwotę kary (jeśli istnieje),
    - znaczniki czasowe utworzenia i aktualizacji rekordu.
    """
    id: uuid.UUID
    user_id: str
    book_copy_id: uuid.UUID
    borrowed_at: datetime
    due_date: datetime
    returned_at: Optional[datetime] = None
    status: LoanStatus
    fine_amount: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        # Pozwala tworzyć obiekty bezpośrednio z modeli ORM (np. SQLAlchemy).
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-uuid-123",
                "book_copy_id": "copy-uuid-456",
                "borrowed_at": "2024-11-15T10:00:00",
                "due_date": "2024-11-29T23:59:59",
                "returned_at": None,
                "status": "ACTIVE",
                "fine_amount": 0.0,
                "created_at": "2024-11-15T10:00:00",
                "updated_at": "2024-11-15T10:00:00"
            }
        }
