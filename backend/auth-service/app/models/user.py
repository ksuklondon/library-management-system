"""
Definicja modelu użytkownika systemu bibliotecznego.

Model jest mapowany na tabelę "users" w bazie danych i służy do:
- przechowywania danych logowania,
- przechowywania danych osobowych,
- rozróżniania ról (ADMIN, LIBRARIAN, READER),
- kontroli aktywności / blokady konta.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Adres e-mail użytkownika (unikalny, indeksowany).
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Hasło przechowujemy w postaci hasha (nigdy w postaci jawnej!).
    hashed_password = Column(String(255), nullable=False)

    # Pełne imię i nazwisko użytkownika (pole opcjonalne).
    full_name = Column(String(255), nullable=True)

    # Rola użytkownika w systemie (domyślnie READER).
    role = Column(Enum(UserRole), default=UserRole.READER, nullable=False)

    # Flaga oznaczająca, czy konto jest aktywne (np. po potwierdzeniu e-maila).
    is_active = Column(Boolean, default=True, nullable=False)

    # Flaga oznaczająca, czy konto zostało zablokowane przez administratora.
    is_blocked = Column(Boolean, default=False, nullable=False)

    # Data utworzenia rekordu (ustawiana automatycznie).
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Data ostatniej aktualizacji rekordu (aktualizowana automatycznie).
    updated_at = Column(
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
