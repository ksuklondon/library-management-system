"""
Schematy Pydantic związane z procesem uwierzytelniania i autoryzacji:
- logowanie,
- odświeżanie tokenu,
- rejestracja użytkownika,
- odpowiedzi z tokenami JWT.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .user import UserRoleEnum


class LoginRequest(BaseModel):
    """
    Dane wymagane do zalogowania użytkownika.
    """
    email: EmailStr = Field(..., description="Email użytkownika")
    password: str = Field(..., description="Hasło")

    class Config:
        # Przykładowe dane wyświetlane w dokumentacji Swagger / ReDoc.
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class TokenResponse(BaseModel):
    """
    Prostsza odpowiedź zawierająca wyłącznie token dostępu.
    Używana np. w endpointzie odświeżania access tokena.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Typ tokenu")
    expires_in: int = Field(..., description="Czas wygaśnięcia w sekundach")


class LoginResponse(BaseModel):
    """
    Odpowiedź zwracana po udanym logowaniu:
    - access token i refresh token,
    - podstawowe dane zalogowanego użytkownika.
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Typ tokenu")
    user_id: str = Field(..., description="UUID użytkownika")
    email: str = Field(..., description="Email użytkownika")
    role: UserRoleEnum = Field(..., description="Rola użytkownika")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "role": "READER"
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Żądanie odświeżenia access tokena – klient przesyła refresh token.
    """
    refresh_token: str = Field(..., description="Refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class RegisterRequest(BaseModel):
    """
    Żądanie rejestracji nowego użytkownika.
    Używane w publicznym endpointzie /auth/register.
    """
    email: EmailStr = Field(..., description="Email użytkownika")
    password: str = Field(..., min_length=8, description="Hasło (min 8 znaków)")
    full_name: Optional[str] = Field(None, max_length=255, description="Imię i nazwisko")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "full_name": "Jan Kowalski"
            }
        }
