"""
Schemas dla Reservation - rezerwacje książek.

Wymaganie: F8-F10 - Rezerwacje (tworzenie, przeglądanie, anulowanie)
Wymaganie: NF7 - Walidacja danych wejściowych

Schematy używane są w:
- warstwie API Loan Service (request/response),
- walidacji danych, które przychodzą z frontendu,
- serializacji danych rezerwacji zwracanych do klienta.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class ReservationStatus(str, Enum):
    """
    Status rezerwacji (F8-F10).

    ACTIVE    – rezerwacja aktywna (użytkownik czeka na książkę),
    CANCELLED – rezerwacja anulowana przez użytkownika/system,
    EXPIRED   – rezerwacja wygasła (minął termin ważności),
    COMPLETED – rezerwacja zrealizowana (książka została wypożyczona).
    """
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"


class ReservationCreate(BaseModel):
    """
    Schema do tworzenia rezerwacji (F8).

    Wymagania:
    - F8: Rezerwacja książki na podstawie jej ID,
    - NF7: Walidacja danych wejściowych (sprawdzenie, że book_id jest obecne).
    """
    book_id: uuid.UUID = Field(..., description="ID książki do zarezerwowania")

    @field_validator('book_id')
    @classmethod
    def validate_book_id(cls, v):
        """
        Walidacja book_id (NF7).

        Upewnia się, że ID książki zostało faktycznie przesłane.
        Dodatkowe walidacje (np. format UUID) realizuje Pydantic.
        """
        if v is None:
            raise ValueError("ID książki jest wymagane")
        return v

    class Config:
        # Przykład używany w dokumentacji OpenAPI (Swagger / ReDoc).
        json_schema_extra = {
            "example": {
                "book_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class ReservationUpdate(BaseModel):
    """
    Schema do aktualizacji rezerwacji (F10).

    Używana głównie do anulowania rezerwacji (zmiana statusu).
    Wymaganie: F10 - Anulowanie rezerwacji.
    """
    status: Optional[ReservationStatus] = Field(
        None,
        description="Nowy status rezerwacji (np. CANCELLED)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "CANCELLED"
            }
        }


class ReservationResponse(BaseModel):
    """
    Schema odpowiedzi z danymi rezerwacji (F9).

    Wymaganie: F9 - Przeglądanie rezerwacji użytkownika lub wszystkich
    (w zależności od roli i endpointu).
    Zawiera pełne informacje o rezerwacji, w tym daty i status.
    """
    id: uuid.UUID
    user_id: str
    book_id: uuid.UUID
    book_copy_id: Optional[uuid.UUID] = None
    status: ReservationStatus
    reserved_at: datetime
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        # Pozwala tworzyć instancje bezpośrednio z modeli ORM (SQLAlchemy).
        from_attributes = True
        # Przykładowa odpowiedź używana w dokumentacji OpenAPI.
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-uuid-123",
                "book_id": "book-uuid-456",
                "book_copy_id": None,
                "status": "ACTIVE",
                "reserved_at": "2024-11-15T10:00:00",
                "expires_at": "2024-11-18T10:00:00",
                "created_at": "2024-11-15T10:00:00",
                "updated_at": "2024-11-15T10:00:00"
            }
        }
