"""
Moduł inicjalizujący pakiet schemas.

Zawiera definicje schematów Pydantic używanych w:
- warstwie API (request/response),
- walidacji danych przychodzących od klienta,
- serializacji danych zwracanych do klienta.
"""

from .user import UserBase, UserCreate, UserUpdate, UserResponse, UserInDB
from .auth import LoginRequest, LoginResponse, TokenResponse, RefreshTokenRequest

# Dzięki __all__ można zrobić:
#     from app.schemas import UserCreate, LoginRequest
# bez konieczności odwoływania się do podmodułów.
__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    "RefreshTokenRequest",
]
