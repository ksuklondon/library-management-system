"""
Schematy Pydantic związane z użytkownikiem.

Używane głównie w:
- warstwie API (request/response),
- walidacji danych wejściowych,
- serializacji danych zwracanych do klienta.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class UserRoleEnum(str, Enum):
    """
    Enum z rolami użytkowników w systemie.
    Te wartości są spójne z enumem UserRole w modelu ORM.
    """
    ADMIN = "ADMIN"
    LIBRARIAN = "LIBRARIAN"
    READER = "READER"


class UserBase(BaseModel):
    """
    Podstawowy schemat użytkownika, wspólny dla wielu odpowiedzi API.
    """
    email: EmailStr = Field(..., description="Email użytkownika")
    full_name: Optional[str] = Field(None, max_length=255, description="Imię i nazwisko")
    role: UserRoleEnum = Field(UserRoleEnum.READER, description="Rola użytkownika")


class UserCreate(BaseModel):
    """
    Schemat danych wymaganych do utworzenia nowego użytkownika.
    Używany np. w endpointach rejestracji lub tworzenia użytkownika przez admina.
    """
    email: EmailStr = Field(..., description="Email użytkownika")
    password: str = Field(..., min_length=8, max_length=100, description="Hasło (min 8 znaków)")
    full_name: Optional[str] = Field(None, max_length=255, description="Imię i nazwisko")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Walidator hasła – wymusza minimalne wymagania bezpieczeństwa:
        - co najmniej 8 znaków,
        - przynajmniej jedna wielka litera,
        - przynajmniej jedna mała litera,
        - przynajmniej jedna cyfra.
        """
        if len(v) < 8:
            raise ValueError("Hasło musi mieć minimum 8 znaków")

        if not any(c.isupper() for c in v):
            raise ValueError("Hasło musi zawierać wielką literę")

        if not any(c.islower() for c in v):
            raise ValueError("Hasło musi zawierać małą literę")

        if not any(c.isdigit() for c in v):
            raise ValueError("Hasło musi zawierać cyfrę")

        return v


class UserUpdate(BaseModel):
    """
    Schemat danych do aktualizacji profilu użytkownika.
    Wszystkie pola są opcjonalne – można zmienić tylko wybrane.
    """
    email: Optional[EmailStr] = Field(None)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """
    Schemat użytkownika zwracanego w odpowiedziach API.
    Rozszerza UserBase o pola techniczne i statusowe.
    """
    id: UUID
    is_active: bool
    is_blocked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        # Pozwala tworzyć instancje na podstawie obiektów ORM (np. modeli SQLAlchemy).
        from_attributes = True


class UserInDB(UserResponse):
    """
    Schemat użytkownika używany wewnętrznie (np. w logice domenowej),
    zawiera również zahashowane hasło.
    Nie powinien być zwracany bezpośrednio do klienta.
    """
    hashed_password: str
