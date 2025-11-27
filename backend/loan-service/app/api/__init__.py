"""
API Routes dla Loan Service.

Wymaganie: F8-F14, F27 — Rezerwacje, wypożyczenia, kary
Wymaganie: NF5 — RBAC (Role-Based Access Control)

Plik ten pełni rolę "centralnego punktu wejścia" dla wszystkich tras API
w module Loan Service. Dzięki temu główny `main.py` może podłączyć tylko
jeden router (`api_router`), a wszystkie podmoduły (reservations, loans, fines)
są wpięte w sposób uporządkowany.

Struktura:
- /reservations → operacje związane z rezerwacjami (F8–F10)
- /loans → operacje związane z wypożyczeniami (F11–F14)
- /fines → operacje związane z karami (F27)
"""

from fastapi import APIRouter

# Importy routerów modułów domenowych:
# Każdy z nich zawiera endpointy dedykowane dla danego obszaru logiki.
from app.api.reservation_routes import router as reservation_router
from app.api.loan_routes import router as loan_router
from app.api.fine_routes import router as fine_router

# Główny router API, do którego podpinamy wszystkie pod-routery.
api_router = APIRouter()

# Rezerwacje (F8–F10):
# - tworzenie rezerwacji
# - listowanie
# - anulowanie
api_router.include_router(
    reservation_router,
    prefix="/reservations",
    tags=["Reservations"]
)

# Wypożyczenia (F11–F14):
# - wypożyczenie
# - zwrot
# - przedłużenie
api_router.include_router(
    loan_router,
    prefix="/loans",
    tags=["Loans"]
)

# Kary za przetrzymanie (F27):
# - naliczanie
# - opłacanie
# - przeglądanie
api_router.include_router(
    fine_router,
    prefix="/fines",
    tags=["Fines"]
)

# Eksport publiczny modułu.
__all__ = ['api_router']
