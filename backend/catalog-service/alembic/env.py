"""
Alembic environment configuration for Catalog Service.

Wymaganie NF14: PostgreSQL migrations
Odpowiada za konfigurację migracji bazy danych.
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Dodaj ścieżkę do backendu żeby móc importować modele
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Base z shared database
from backend.shared.database import Base  # noqa: E402

# Import konfiguracji Alembic
config = context.config

# Interpret the config file for Python logging (optional)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import wszystkich modeli żeby Alembic je widział

# Ustaw target_metadata na Base.metadata
target_metadata = Base.metadata

# Nadpisz database URL z zmiennej środowiskowej
database_url = os.getenv(
    "DATABASE_URL", "postgresql://admin:admin123@postgres:5432/biblioteka"
)
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
