"""
Model BookCopy - fizyczny egzemplarz książki.

Wymagania: F16, F8, F11
Odpowiada za przechowywanie informacji o konkretnych egzemplarzach książek.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.shared.database import Base


class CopyStatus(str, enum.Enum):
    """
    Status egzemplarza książki (zgodnie z diagramem klas).

    Wymaganie F16: Zarządzanie statusem egzemplarzy
    """

    AVAILABLE = "AVAILABLE"  # Dostępny do wypożyczenia/rezerwacji
    RESERVED = "RESERVED"  # Zarezerwowany (Wymaganie F8)
    BORROWED = "BORROWED"  # Wypożyczony (Wymaganie F11)
    DAMAGED = "DAMAGED"  # Uszkodzony
    LOST = "LOST"  # Zgubiony


class BookCopy(Base):
    """
    Model fizycznego egzemplarza książki.

    Atrybuty zgodne z diagramem klas:
    - id: UUID (klucz główny)
    - book_id: UUID książki (klucz obcy)
    - inventory_no: numer inwentarzowy (unikalny)
    - status: status egzemplarza (CopyStatus enum)
    - location: lokalizacja w bibliotece (np. "Półka A-12")
    - is_deleted: soft delete
    - created_at: data dodania egzemplarza
    - updated_at: data ostatniej aktualizacji
    """

    __tablename__ = "book_copies"

    # Kolumny podstawowe
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(
        UUID(as_uuid=True), ForeignKey("books.id"), nullable=False, index=True
    )
    inventory_no = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(
        Enum(CopyStatus), default=CopyStatus.AVAILABLE, nullable=False, index=True
    )
    location = Column(String(100), nullable=True)

    # Soft delete (Wymaganie NF19)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relacje (zgodnie z diagramem klas)
    book = relationship("Book", back_populates="copies")

    def __repr__(self):
        return f"<BookCopy {self.inventory_no} - {self.status}>"

    def is_available(self) -> bool:
        """
        Sprawdza czy egzemplarz jest dostępny do wypożyczenia/rezerwacji.

        Wymaganie F8, F11: Rezerwacja i wypożyczenie tylko dla dostępnych
        """
        return self.status == CopyStatus.AVAILABLE and not self.is_deleted

    def can_be_reserved(self) -> bool:
        """
        Sprawdza czy egzemplarz może być zarezerwowany.

        Wymaganie F8: Rezerwacja możliwa tylko dla dostępnych egzemplarzy
        """
        return self.is_available()

    def can_be_borrowed(self) -> bool:
        """
        Sprawdza czy egzemplarz może być wypożyczony.

        Wymaganie F11: Wypożyczenie możliwe dla dostępnych lub zarezerwowanych
        """
        return (
            self.status in [CopyStatus.AVAILABLE, CopyStatus.RESERVED]
        ) and not self.is_deleted
