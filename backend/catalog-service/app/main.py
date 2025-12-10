"""
backend/catalog-service/app/main.py

Główna aplikacja FastAPI dla serwisu katalogu książek.

Odpowiada za:
- Przeglądanie katalogu książek (F4)
- Wyszukiwanie książek (F5)
- Filtrowanie książek (F6)
- Szczegóły książki (F7)
- Zarządzanie książkami (F15 - LIBRARIAN/ADMIN)
- Zarządzanie egzemplarzami (F16 - LIBRARIAN/ADMIN)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

# DODANE: Import routera
from app.api import api_router
from shared.config import is_development, settings, validate_config
from shared.database import Base, check_connection, engine

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Uruchamianie Catalog Service...")

    try:
        validate_config()
        logger.info("Konfiguracja poprawna")

        if check_connection():
            logger.info("Połączenie z bazą danych OK")
        else:
            logger.error("Błąd połączenia z bazą danych!")

        if is_development():
            logger.info("Tryb development - tworzenie tabel...")
            Base.metadata.create_all(bind=engine)
            logger.info("Tabele utworzone")

        logger.info("Catalog Service uruchomiony pomyślnie")

    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania: {e}")
        raise

    yield

    logger.info("Zamykanie Catalog Service...")
    logger.info("Catalog Service zamknięty")


app = FastAPI(
    title="Library Management System - Catalog Service",
    description="Serwis katalogu - przeglądanie, wyszukiwanie, zarządzanie książkami",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DODANE: Rejestracja routerów API
app.include_router(api_router, prefix="/api")


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {
        "service": "Catalog Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    db_status = "healthy" if check_connection() else "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "service": "catalog-service",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Uruchamianie na porcie {settings.CATALOG_SERVICE_PORT}...")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.CATALOG_SERVICE_PORT,
        reload=is_development(),
        log_level=settings.LOG_LEVEL.lower(),
    )
