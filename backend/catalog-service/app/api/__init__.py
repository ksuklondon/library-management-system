"""
API Routes - główny router dla Catalog Service.

Łączy wszystkie endpointy serwisu katalogowego.
"""

from fastapi import APIRouter

from .book_routes import router as book_router
from .catalog_routes import router as catalog_router
from .copy_routes import router as copy_router

api_router = APIRouter()

# Wymaganie F4-F7: Katalog - przeglądanie, wyszukiwanie, filtrowanie
api_router.include_router(catalog_router, prefix="/catalog", tags=["Catalog"])

# Wymaganie F15: Zarządzanie książkami (LIBRARIAN/ADMIN)
api_router.include_router(book_router, prefix="/books", tags=["Books Management"])

# Wymaganie F16: Zarządzanie egzemplarzami (LIBRARIAN/ADMIN)
api_router.include_router(
    copy_router, prefix="/copies", tags=["Book Copies Management"]
)

__all__ = ["api_router"]
