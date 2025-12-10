"""
Model Reservation - rezerwacje książek.

Wymaganie: F8-F10 - Rezerwacje książek
Wymaganie: NF19 - Soft delete
Wymaganie: NF29 - Reguły biznesowe (max 3 rezerwacje na użytkownika)
"""

import enum
import uuid
from datetime import datetime, timedelta

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class ReservationStatus(str, enum.Enum):
    """
    Status rezerwacji (F8-F10).

    ACTIVE     – rezerwacja aktywna, oczekuje na realizację,
    CANCELLED  – rezerwacja anulowana przez użytkownika/system,
    EXPIRED    – rezerwacja wygasła (minął czas ważności),
    COMPLETED  – rezerwacja zrealizowana (powiązane wypożyczenie).
    """

    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"


class Reservation(Base):
    """
    Model Reservation - reprezentuje rezerwację książki przez użytkownika.

    Wymagania:
    - F8: Rezerwacja książki
    - F9: Przeglądanie rezerwacji
    - F10: Anulowanie rezerwacji
    - NF29: Max 3 aktywne rezerwacje na użytkownika
    """

    __tablename__ = "reservations"

    # Identyfikator rezerwacji (UUID, klucz główny).
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Identyfikator użytkownika (np. UUID z auth-service trzymany jako string).
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Identyfikator książki (pozycja w katalogu, nie konkretny egzemplarz).
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    # Identyfikator konkretnego egzemplarza (opcjonalnie, gdy egzemplarz został już przydzielony).
    book_copy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Status rezerwacji – jeden z ReservationStatus.
    status: Mapped[ReservationStatus] = mapped_column(
        SQLEnum(ReservationStatus, name="reservation_status"),
        nullable=False,
        default=ReservationStatus.ACTIVE,
        index=True,
    )

    # Data utworzenia rezerwacji.
    reserved_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Data wygaśnięcia rezerwacji (np. po 3 dniach, jeśli nie została zrealizowana).
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Soft delete (NF19) – zamiast usuwać, oznaczamy rekord jako usunięty.
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Informacja kto usunął rezerwację (np. admin z panelu).
    deleted_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Znaczniki czasu utworzenia i ostatniej aktualizacji rekordu.
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, **kwargs):
        """
        Konstruktor z automatycznym ustawieniem expires_at.

        Domyślnie: rezerwacja wygasa po 3 dniach (NF29 – reguła biznesowa).
        Jeśli expires_at nie zostanie podane jawnie, ustawiamy je na "teraz + 3 dni".
        """
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=3)

    def is_active(self) -> bool:
        """
        Sprawdza, czy rezerwacja jest aktualnie aktywna (F8).

        Warunki:
        - status == ACTIVE,
        - rekord nie jest oznaczony jako usunięty (is_deleted == False),
        - obecny czas jest wcześniejszy niż expires_at.
        """
        return (
            self.status == ReservationStatus.ACTIVE
            and not self.is_deleted
            and datetime.utcnow() < self.expires_at
        )

    def can_be_cancelled(self) -> bool:
        """
        Sprawdza, czy rezerwację można anulować (F10).

        Rezerwacja może być anulowana tylko wtedy, gdy:
        - jest w statusie ACTIVE,
        - nie została oznaczona jako usunięta.
        """
        return self.status == ReservationStatus.ACTIVE and not self.is_deleted

    def is_expired(self) -> bool:
        """
        Sprawdza czy rezerwacja wygasła.

        Logika:
        - aktualny czas >= expires_at,
        - status nadal ACTIVE (czyli rezerwacja nie została jeszcze "oficjalnie" wygaszona).
        """
        return (
            datetime.utcnow() >= self.expires_at
            and self.status == ReservationStatus.ACTIVE
        )

    def cancel(self) -> None:
        """
        Anuluj rezerwację (F10).

        Ustawia status na CANCELLED, jeśli rezerwacja może być anulowana.
        Aktualizuje pole updated_at.
        """
        if self.can_be_cancelled():
            self.status = ReservationStatus.CANCELLED
            self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """
        Oznacz rezerwację jako zrealizowaną.

        Używane w momencie, gdy na podstawie tej rezerwacji
        została utworzona transakcja wypożyczenia (Loan).
        """
        if self.status == ReservationStatus.ACTIVE:
            self.status = ReservationStatus.COMPLETED
            self.updated_at = datetime.utcnow()

    def mark_as_expired(self) -> None:
        """
        Oznacz rezerwację jako wygasłą.

        Wywoływane np. przez proces cykliczny (scheduler), który
        sprawdza rezerwacje po expires_at i aktualizuje ich status.
        """
        if self.is_expired():
            self.status = ReservationStatus.EXPIRED
            self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """
        Reprezentacja tekstowa obiektu – pomocna przy logowaniu i debugowaniu.
        """
        return f"<Reservation(id={self.id}, user_id={self.user_id}, book_id={self.book_id}, status={self.status})>"
