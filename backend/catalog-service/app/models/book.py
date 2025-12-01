"""
Model Book - książka w katalogu biblioteki.

Wymagania: F4, F5, F6, F7, F15
Odpowiada za przechowywanie informacji o książkach.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.database import Base

if TYPE_CHECKING:
    from app.models.book_copy import BookCopy


class Book(Base):
    """
    Model książki w systemie bibliotecznym.

    Atrybuty zgodne z diagramem klas:
    - id: UUID (klucz główny)
    - title: tytuł książki
    - authors: autorzy (string, może być wielu - rozdzieleni przecinkami)
    - isbn: numer ISBN
    - publisher: wydawca
    - pages: liczba stron
    - language: język publikacji
    - cover_url: URL do okładki
    - description: opis książki
    - genre: gatunek literacki
    - is_deleted: soft delete (nie usuwamy fizycznie)
    - deleted_by: UUID użytkownika który usunął
    - created_at: data utworzenia
    - updated_at: data ostatniej aktualizacji
    """

    __tablename__ = "books"

    # Kolumny podstawowe
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    authors: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    isbn: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True, index=True
    )
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default="pl"
    )
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Soft delete (Wymaganie NF19 - audyt)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Timestamps (Wymaganie NF16 - logowanie zmian)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relacje (zgodnie z diagramem klas)
    copies: Mapped[list["BookCopy"]] = relationship(
        "BookCopy", back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Book {self.title} by {self.authors}>"

    def get_available_copies_count(self) -> int:
        """
        Zwraca liczbę dostępnych egzemplarzy (status AVAILABLE).

        Wymaganie F7: Szczegóły książki - pokazuje dostępność
        """
        return sum(
            1
            for copy in self.copies
            if copy.status == "AVAILABLE" and not copy.is_deleted
        )

    def get_total_copies_count(self) -> int:
        """
        Zwraca całkowitą liczbę egzemplarzy (nie usuniętych).
        """
        return sum(1 for copy in self.copies if not copy.is_deleted)
