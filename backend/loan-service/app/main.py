"""
Main FastAPI application dla Loan Service.

Wymagania:
- F8–F14, F27 — Wypożyczenia, rezerwacje, kary
- NF1–NF6 — Bezpieczeństwo, CORS, JWT, komunikacja między serwisami
- NF16 — Logowanie i monitoring działania serwisu
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.shared.database import engine, Base
from app.api import reservation_routes, loan_routes, fine_routes

# Konfiguracja logowania — zapisuje kluczowe informacje o starcie/wyłączeniu serwisu i błędach
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager uruchamiany przy starcie i zamykaniu serwisu.

    - Tworzy tabele w bazie danych (jeśli nie istnieją)
    - Loguje status przy starcie i przy zamknięciu
    """
    logger.info("Starting Loan Service...")

    # Utworzenie wszystkich tabel zgodnie z modelami SQLAlchemy
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Przekazanie kontroli do właściwej aplikacji
    yield

    # Kod wykonywany podczas zamykania serwisu
    logger.info("Shutting down Loan Service...")


# Konfiguracja głównej aplikacji FastAPI
app = FastAPI(
    title="Library Loan Service",
    description="Serwis zarządzania wypożyczeniami, rezerwacjami i karami",
    version="1.0.0",
    lifespan=lifespan  # rejestracja lifecycle managera
)

# Dozwolone źródła CORS – aplikacja frontendowa
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
]

# Konfiguracja middleware CORS (Wymaganie NF1–NF6)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # zezwolone domeny
    allow_credentials=True,        # pozwala na ciasteczka/autoryzację
    allow_methods=["*"],           # zezwala na wszystkie metody HTTP
    allow_headers=["*"],           # zezwala na wszystkie nagłówki
)

# Rejestracja routerów odpowiedzialnych za funkcje biznesowe serwisu
app.include_router(reservation_routes.router, prefix="/api/reservations", tags=["reservations"])
app.include_router(loan_routes.router, prefix="/api/loans", tags=["loans"])
app.include_router(fine_routes.router, prefix="/api/fines", tags=["fines"])


@app.get("/health")
async def health_check():
    """
    Endpoint zdrowotny serwisu.

    Używany przez load balancer / Docker HEALTHCHECK.
    """
    return {
        "status": "healthy",
        "service": "loan-service",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """
    Główny endpoint serwisu – zwraca podstawowe informacje i odnośnik do dokumentacji.
    """
    return {
        "message": "Library Loan Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }
