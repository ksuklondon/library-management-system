import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Dodajemy katalog nadrzędny do sys.path, żeby można było poprawnie importować
# moduły z projektu (backend.shared, app.models, itp.) w czasie migracji.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importujemy bazową klasę modeli (Base) oraz modele, które mają być śledzone
# przez Alembica przy generowaniu migracji (autogenerate).
from app.models.user import User  # noqa: E402, F401

from shared.database import Base  # noqa: E402

# Obiekt konfiguracji Alembica – wczytywany z pliku alembic.ini.
config = context.config

# Jeśli zdefiniowano plik konfiguracyjny, ładujemy z niego konfigurację logowania.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadane wszystkich modeli – Alembic używa ich do porównywania schematu bazy
# z aktualnymi modelami ORM (autogenerate).
target_metadata = Base.metadata

# Odczytujemy URL bazy danych z zmiennej środowiskowej DATABASE_URL.
# Jeśli nie jest ustawiona, używamy wartości domyślnej (np. dla lokalnego Dockera).
database_url = os.getenv(
    "DATABASE_URL", "postgresql://admin:admin123@postgres:5432/biblioteka"
)
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """
    Uruchamianie migracji w trybie offline.

    W tym trybie Alembic nie łączy się faktycznie z bazą danych –
    zamiast tego generuje skrypt SQL na podstawie metadanych.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # wartości parametrów są wstawiane bezpośrednio w SQL
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # porównywanie typów kolumn
        compare_server_default=True,  # porównywanie domyślnych wartości po stronie serwera
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Uruchamianie migracji w trybie online.

    W tym trybie Alembic tworzy połączenie z bazą danych i wykonuje
    skrypty migracji bezpośrednio na docelowej bazie.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # brak współdzielonej puli połączeń dla migracji
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # porównywanie typów kolumn
            compare_server_default=True,  # porównywanie domyślnych wartości
        )

        with context.begin_transaction():
            context.run_migrations()


# W zależności od trybu (offline/online) uruchamiamy odpowiednią ścieżkę.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
