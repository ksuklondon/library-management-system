"""
Schemas dla Fine - kary za przetrzymanie.

Wymaganie: F27 - Płatność kar
Wymaganie: NF7 - Walidacja danych wejściowych

Schematy Pydantic wykorzystywane w Loan Service do:
- tworzenia nowych kar,
- walidacji danych wejściowych (kwoty, użytkownika, id wypożyczenia),
- rejestrowania płatności,
- zwracania danych o karach w odpowiedziach API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import uuid


class FineCreate(BaseModel):
    """
    Schema do tworzenia kary (F27).

    Używana przez endpoint odpowiedzialny za naliczanie kar.
    Zawiera:
    - ID wypożyczenia, którego dotyczy kara,
    - ID użytkownika,
    - kwotę naliczonej kary.

    Wymaganie: F27 – naliczanie kar.
    Walidacja (NF7):
    - amount nie może być ujemny,
    - amount nie może być przesadnie wysoki,
    - user_id musi być poprawny i niepusty.
    """
    loan_id: uuid.UUID = Field(..., description="ID wypożyczenia, za które naliczana jest kara")
    user_id: str = Field(..., description="ID użytkownika")
    amount: float = Field(..., ge=0.0, description="Kwota kary w złotych")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """
        Walidacja kwoty kary (NF7):
        - nie może być ujemna,
        - nie powinna przekraczać górnego limitu bezpieczeństwa,
        - zwracana kwota jest zaokrąglana do 2 miejsc.
        """
        if v < 0:
            raise ValueError("Kwota kary nie może być ujemna")
        if v > 10000:
            raise ValueError("Kwota kary jest zbyt wysoka (max 10000 zł)")
        return round(v, 2)

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        """Walidacja user_id (NF7) – nie może być puste."""
        if not v or not v.strip():
            raise ValueError("ID użytkownika jest wymagane")
        return v

    class Config:
        # Przykład używany w dokumentacji (Swagger/ReDoc)
        json_schema_extra = {
            "example": {
                "loan_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-uuid-123",
                "amount": 14.00
            }
        }


class FinePayment(BaseModel):
    """
    Schema do rejestrowania płatności kary (F27).

    Używana w endpointach opłacania kary.
    Zawiera opcjonalną metodę płatności (np. 'cash', 'card', 'transfer').
    """
    payment_method: Optional[str] = Field(
        None,
        description="Metoda płatności: cash, card, transfer"
    )

    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        """
        Walidacja metody płatności (NF7):
        - jeśli podano, musi być jedną z dopuszczalnych metod.
        """
        if v is not None:
            allowed_methods = ['cash', 'card', 'transfer']
            if v.lower() not in allowed_methods:
                raise ValueError(f"Metoda płatności musi być jedną z: {', '.join(allowed_methods)}")
            return v.lower()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "payment_method": "cash"
            }
        }


class FineResponse(BaseModel):
    """
    Schema odpowiedzi z danymi kary (F27).

    Wymagania:
    - F27 – zwracanie listy kar oraz danych szczegółowych użytkownika.

    Zawiera:
    - kwotę kary,
    - status płatności,
    - datę opłacenia,
    - metadane czasowe.

    Używana w odpowiedziach API np.:
    - GET /api/fines
    - GET /api/fines/{id}
    """
    id: uuid.UUID
    loan_id: uuid.UUID
    user_id: str
    amount: float
    paid: bool
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        # Pozwala automatycznie tworzyć schema z modeli SQLAlchemy
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "loan_id": "loan-uuid-456",
                "user_id": "user-uuid-123",
                "amount": 14.00,
                "paid": False,
                "paid_at": None,
                "created_at": "2024-11-15T10:00:00",
                "updated_at": "2024-11-15T10:00:00"
            }
        }
