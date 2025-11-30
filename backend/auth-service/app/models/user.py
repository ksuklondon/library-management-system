"""
Definicja modelu użytkownika systemu bibliotecznego.

Model jest mapowany na tabelę "users" w bazie danych i służy do:
- przechowywania danych logowania,
- przechowywania danych osobowych,
- rozróżniania ról (ADMIN, LIBRARIAN, READER),
- kontroli aktywności / blokady konta.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.shared.database import Base


class UserRole(str, enum.Enum):
    """
    Enum określający rolę użytkownika w systemie.

    ADMIN     – administrator systemu (pełne uprawnienia),
    LIBRARIAN – bibliotekarz (operacje na książkach i wypożyczeniach),
    READER    – zwykły czytelnik (przeglądanie katalogu, wypożyczenia).
    """

    ADMIN = "ADMIN"
    LIBRARIAN = "LIBRARIAN"
    READER = "READER"


class User(Base):
    """
    Model ORM reprezentujący rekord w tabeli "users".
    """

    __tablename__ = "users"

    # Identyfikator użytkownika typu UUID – generowany automatycznie.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Adres e-mail użytkownika (unikalny, indeksowany).
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    # Hasło przechowujemy w postaci hasha (nigdy w postaci jawnej!).
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Pełne imię i nazwisko użytkownika (pole opcjonalne).
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Rola użytkownika w systemie (domyślnie READER).
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.READER, nullable=False
    )

    # Flaga oznaczająca, czy konto jest aktywne (np. po potwierdzeniu e-maila).
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Flaga oznaczająca, czy konto zostało zablokowane przez administratora.
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Data utworzenia rekordu (ustawiana automatycznie).
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Data ostatniej aktualizacji rekordu (aktualizowana automatycznie).
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        """
        Reprezentacja tekstowa obiektu – pomocna np. przy debugowaniu i logowaniu.
        """
        return f"<User {self.email}>"
