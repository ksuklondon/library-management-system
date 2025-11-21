"""
Pakiet API dla auth-service.

Tutaj budujemy główny router FastAPI i dołączamy:
- trasy związane z uwierzytelnianiem (auth_routes),
- trasy związane z zarządzaniem użytkownikami (user_routes).
"""

from fastapi import APIRouter
from .auth_routes import router as auth_router
from .user_routes import router as user_router

# Główny router, który zostanie podłączony w main.py.
api_router = APIRouter()

# Endpointy odpowiedzialne za logowanie, rejestrację, tokeny.
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Endpointy odpowiedzialne za operacje na użytkownikach (CRUD, blokowanie).
api_router.include_router(user_router, prefix="/users", tags=["Users"])

__all__ = ["api_router"]
