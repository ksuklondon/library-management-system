"""
Główny plik startowy auth-service.

Tworzy instancję aplikacji FastAPI, konfiguruje:
- logowanie,
- CORS,
- połączenie z bazą danych,
- routery z endpointami,
- endpointy techniczne (root, /health).
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.shared.config import settings, validate_config, is_development
from backend.shared.database import engine, Base, check_connection
from app.api import api_router

# Konfiguracja globalnego logowania dla serwisu.
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Funkcja lifespan służy do wykonania logiki przy starcie i zamknięciu aplikacji.

    W fazie startu:
    - waliduje konfigurację,
    - sprawdza połączenie z bazą danych,
    - w trybie development tworzy tabele w bazie.

    W fazie zamykania:
    - zapisuje informacje w logach (ewentualnie tutaj można dodać cleanup zasobów).
    """
    logger.info("Uruchamianie Auth Service...")

    try:
        # Sprawdzenie, czy wszystkie wymagane zmienne konfiguracyjne są ustawione.
        validate_config()
        logger.info("Konfiguracja poprawna")

        # Weryfikacja połączenia z bazą danych.
        if check_connection():
            logger.info("Połączenie z bazą danych OK")
        else:
            logger.error("Błąd połączenia z bazą danych!")

        # W trybie development automatycznie tworzymy struktury tabel.
        if is_development():
            logger.info("Tryb development - tworzenie tabel...")
            Base.metadata.create_all(bind=engine)
            logger.info("Tabele utworzone")

        logger.info("Auth Service uruchomiony pomyślnie")

    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania: {e}")
        # Jeśli tu rzucimy wyjątek, aplikacja nie wystartuje.
        raise

    # --- tutaj aplikacja jest już uruchomiona i może obsługiwać żądania ---
    yield
    # --- tu wykonujemy się przy zamykaniu serwisu ---

    logger.info("Zamykanie Auth Service...")
    logger.info("Auth Service zamknięty")


# Tworzymy instancję FastAPI wraz z podstawowymi metadanymi.
app = FastAPI(
    title="Library Management System - Auth Service",
    description="Serwis autentykacji i autoryzacji użytkowników",
    version="1.0.0",
    docs_url="/docs",   # Swagger UI
    redoc_url="/redoc", # ReDoc
    lifespan=lifespan   # rejestrujemy funkcję start/stop
)

# Konfiguracja CORS – pozwala na wywołania z frontendów hostowanych pod innymi domenami.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Podłączamy router z wszystkimi endpointami API (/auth, /users, itd.).
app.include_router(api_router, prefix="/api")


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    Prosty endpoint informacyjny – można użyć do sprawdzenia,
    czy serwis działa oraz gdzie znajdują się dokumentacja API.
    """
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Endpoint zdrowia (health-check) – wykorzystywany np. przez systemy
    orkiestracji (Docker, Kubernetes) do monitorowania stanu serwisu.
    """
    db_status = "healthy" if check_connection() else "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "service": "auth-service",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    # Pozwala uruchomić serwis komendą: python main.py
    import uvicorn

    logger.info(f"Uruchamianie na porcie {settings.AUTH_SERVICE_PORT}...")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.AUTH_SERVICE_PORT,
        reload=is_development(),         # autoreload w trybie dev
        log_level=settings.LOG_LEVEL.lower()
    )
