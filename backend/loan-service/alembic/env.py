"""
Alembic environment configuration for Loan Service.

Wymaganie: NF8 - Migracje bazy danych
Konfiguracja środowiska Alembic odpowiedzialna za:
- połączenie z bazą danych,
- integrację z modelami SQLAlchemy,
- tryb offline/online dla migracji,
- automatyczne generowanie zmian schematu.
"""

from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Dodaj katalog główny projektu do sys.path, aby importy backend.shared działały poprawnie.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import bazowej klasy modeli oraz konfiguracji aplikacji
# Base – metadane SQLAlchemy (tabele, kolumny)
# settings – odczyty ze zmiennych środowiskowych, w tym adres bazy
from backend.shared.database import Base
from backend.shared.config import settings

# Import modeli Loan Service — konieczne, aby Alembic wiedział,
# jakie tabele istnieją i mógł generować migracje (autogenerate=True).
from app.models.reservation import Reservation
from app.models.loan import Loan
from app.models.fine import Fine

# Obiekt konfiguracji Alembic — czyta ustawienia z alembic.ini
config = context.config

# Nadpisanie URL połączenia do bazy danymi z env
# (NF8 – konfiguracja migracji z użyciem zmiennych środowiskowych).
config.set_main_option(
    "sqlalchemy.url",
    settings.LOAN_DATABASE_URL
)

# Konfiguracja loggerów Alembic — wczytywana z alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Przypisanie metadanych modeli — kluczowe dla autogenerowania migracji
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Uruchamia migracje w trybie *offline* (NF8).

    Tryb offline:
    - nie tworzy połączenia z bazą,
    - generuje SQL jako tekst,
    - przydatny w CI/CD lub gdy brak dostępu do DB.

    context.configure(...) ustawia parametry generowania migracji.
    """
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,            # wartości bindowane literalnie w SQL
        dialect_opts={"paramstyle": "named"},
        compare_type=True,             # porównywanie typów kolumn
        compare_server_default=True,   # porównywanie domyślnych wartości
    )

    # Rozpoczęcie „wirtualnej” transakcji migracji
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Uruchamia migracje w trybie *online* (NF8).

    Tryb online:
    - otwiera prawdziwe połączenie z bazą danych,
    - wykonuje migracje bezpośrednio na DB.
    """
    # Tworzenie silnika SQLAlchemy na podstawie ustawień Alembic
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # brak puli połączeń (bezpieczniejsze w migracjach)
    )

    # Otwórz połączenie i powiąż je z kontekstem migracyjnym
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        # Wykonaj migracje w transakcji
        with context.begin_transaction():
            context.run_migrations()


# Wybierz odpowiedni tryb
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
