"""
backend/shared/database.py

Konfiguracja połączenia z bazą danych PostgreSQL.
Współdzielone przez wszystkie serwisy (auth, catalog, loan).

Odpowiada za:
- Połączenie z PostgreSQL przez SQLAlchemy
- Tworzenie sesji bazodanowych
- Connection pooling
- Transakcje ACID (Wymaganie NF15)
"""

import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ==========================================
# KONFIGURACJA POŁĄCZENIA
# ==========================================

# Pobierz DATABASE_URL ze zmiennych środowiskowych
# Format: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:admin123@localhost:5432/biblioteka"  # Fallback dla development
)

# ==========================================
# SILNIK BAZY DANYCH (Engine)
# ==========================================

# Tworzymy "silnik" SQLAlchemy - zarządza połączeniami z bazą
engine = create_engine(
    DATABASE_URL,

    # Connection Pool - pula połączeń (wydajność)
    # Max 20 jednoczesnych połączeń
    pool_size=10,           # Podstawowa pula: 10 połączeń
    max_overflow=10,        # Dodatkowe połączenia w razie potrzeby: +10

    # Timeout połączenia (30 sekund)
    pool_timeout=30,

    # Recykling połączeń co 1 godzinę (bezpieczeństwo)
    pool_recycle=3600,

    # Pre-ping - sprawdź czy połączenie działa przed użyciem
    pool_pre_ping=True,

    # Echo SQL (tylko w development) - pokaż wszystkie zapytania SQL w konsoli
    echo=os.getenv("ENVIRONMENT", "development") == "development",

    # Future mode - używaj SQLAlchemy 2.0 style
    future=True
)

# ==========================================
# SESJA BAZODANOWA (Session Factory)
# ==========================================

# SessionLocal - fabryka sesji (nie sama sesja!)
# Każde żądanie HTTP dostanie swoją własną sesję
SessionLocal = sessionmaker(
    autocommit=False,      # Ręczne zarządzanie transakcjami (bezpieczniej)
    autoflush=False,       # Ręczne flush (więcej kontroli)
    bind=engine,           # Powiązanie z silnikiem
    expire_on_commit=False # Obiekty nie wygasają po commit (wygodniej)
)

# ==========================================
# BAZOWA KLASA MODELI
# ==========================================

# Wszystkie modele SQLAlchemy dziedziczą po tej klasie
# Używane w: User, Book, BookCopy, Loan, Reservation, etc.
Base = declarative_base()

# ==========================================
# DEPENDENCY INJECTION - FastAPI
# ==========================================

def get_db() -> Generator:
    """
    Dependency dla FastAPI - dostarcza sesję bazodanową.

    Użycie w endpointach:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users

    Zalety:
    - Automatyczne otwieranie sesji
    - Automatyczne zamykanie sesji (nawet przy błędzie)
    - Jedna sesja na żądanie HTTP

    Yields:
        Session: Sesja bazodanowa SQLAlchemy
    """
    # Tworzymy nową sesję
    db = SessionLocal()

    try:
        # Zwracamy sesję do użycia
        yield db

    finally:
        # ZAWSZE zamykamy sesję (nawet jeśli był błąd)
        # To zapobiega wyciekowi połączeń (connection leak)
        db.close()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def init_db() -> None:
    """
    Inicjalizacja bazy danych - tworzenie wszystkich tabel.

    UWAGA: W produkcji używamy Alembic (migracje).
    Ta funkcja przydatna tylko do testów.

    Użycie:
        from backend.shared.database import init_db, Base
        from backend.auth_service.app.models import User  # Import wszystkich modeli

        init_db()  # Tworzy tabele
    """
    # Import wszystkich modeli (żeby Base.metadata je "zobaczył")
    # W produkcji to robi Alembic
    Base.metadata.create_all(bind=engine)
    print("✅ Tabele bazy danych utworzone!")

def drop_all_tables() -> None:
    """
    Usuwa wszystkie tabele z bazy danych.

    ⚠️ NIEBEZPIECZNE! Używaj tylko w testach!

    Użycie:
        from backend.shared.database import drop_all_tables

        drop_all_tables()  # Usuwa wszystkie tabele
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Wszystkie tabele usunięte!")

def check_connection() -> bool:
    """
    Sprawdza czy połączenie z bazą danych działa.

    Użycie w health check (Wymaganie NF28):
        @app.get("/health")
        def health_check():
            db_ok = check_connection()
            return {"status": "healthy" if db_ok else "unhealthy"}

    Returns:
        bool: True jeśli połączenie działa, False w przeciwnym razie
    """
    try:
        # Próbujemy wykonać proste zapytanie
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True

    except Exception as e:
        print(f"❌ Błąd połączenia z bazą danych: {e}")
        return False

# ==========================================
# KONTEKST TRANSAKCJI (dla zaawansowanych)
# ==========================================

class TransactionContext:
    """
    Context manager dla transakcji bazodanowych.

    Automatyczne commit/rollback (Wymaganie NF15 - transakcje ACID).

    Użycie:
        from backend.shared.database import SessionLocal, TransactionContext

        with TransactionContext(SessionLocal()) as db:
            # Wszystkie operacje w jednej transakcji
            user = User(email="test@example.com")
            db.add(user)

            reservation = Reservation(user_id=user.id, ...)
            db.add(reservation)

            # Automatyczny commit na końcu
            # Jeśli błąd → automatyczny rollback
    """

    def __init__(self, session):
        """
        Args:
            session: Sesja SQLAlchemy
        """
        self.session = session

    def __enter__(self):
        """Wejście do context managera"""
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Wyjście z context managera.

        Args:
            exc_type: Typ wyjątku (jeśli był)
            exc_val: Wartość wyjątku
            exc_tb: Traceback
        """
        if exc_type is not None:
            # Był błąd → rollback
            print(f"⚠️ Transakcja anulowana (rollback): {exc_val}")
            self.session.rollback()
        else:
            # Wszystko OK → commit
            try:
                self.session.commit()
                print("✅ Transakcja zatwierdzona (commit)")
            except Exception as e:
                print(f"❌ Błąd podczas commit: {e}")
                self.session.rollback()
                raise

        finally:
            # ZAWSZE zamykamy sesję
            self.session.close()

# ==========================================
# EKSPORT
# ==========================================

__all__ = [
    "engine",              # Silnik SQLAlchemy
    "SessionLocal",        # Fabryka sesji
    "Base",               # Bazowa klasa modeli
    "get_db",             # Dependency dla FastAPI
    "init_db",            # Tworzenie tabel (testy)
    "drop_all_tables",    # Usuwanie tabel (testy)
    "check_connection",   # Health check
    "TransactionContext"  # Context manager dla transakcji
]
