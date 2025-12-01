"""
Model Loan - wypożyczenia książek.

Wymaganie: F11-F14 - Wypożyczenia książek
Wymaganie: NF19 - Soft delete
Wymaganie: NF29 - Reguły biznesowe (max 5 wypożyczeń, 14 dni okres)

Model obsługuje:
- przechowywanie informacji o wypożyczeniach,
- wykrywanie przetrzymań (OVERDUE),
- wyliczanie kar (F27),
- ewentualne przedłużanie wypożyczeń.
"""

import enum
import uuid
from datetime import datetime, timedelta

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.shared.database import Base


class LoanStatus(str, enum.Enum):
    """
    Status wypożyczenia (F11-F14).

    ACTIVE   – wypożyczenie aktualnie trwa,
    RETURNED – książka zwrócona,
    OVERDUE  – wypożyczenie przetrzymane (po terminie).
    """

    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class Loan(Base):
    """
    Model Loan - reprezentuje wypożyczenie książki przez użytkownika.

    Wymagania:
    - F11: Wypożyczenie książki
    - F12: Zwrot książki
    - F13: Historia wypożyczeń
    - F14: Przedłużenie wypożyczenia (opcjonalne)
    - F27: Kary za przetrzymanie
    - NF29: Max 5 aktywnych wypożyczeń, domyślnie 14 dni okres
    """

    __tablename__ = "loans"

    # Techniczne ID wypożyczenia (UUID).
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Identyfikator użytkownika (powiązany z auth-service).
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Identyfikator konkretnego egzemplarza (BookCopy).
    book_copy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    # Data rozpoczęcia wypożyczenia.
    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Termin zwrotu (ustawiany automatycznie, np. 14 dni od borrowed_at).
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Data faktycznego zwrotu (None, jeśli jeszcze nie zwrócono).
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Status wypożyczenia (enum).
    status: Mapped[LoanStatus] = mapped_column(
        SQLEnum(LoanStatus, name="loan_status"),
        nullable=False,
        default=LoanStatus.ACTIVE,
        index=True,
    )

    # Kara naliczona za dane wypożyczenie (F27) – w momencie zwrotu.
    fine_amount: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)

    # Soft delete (NF19) – logiczne usunięcie wypożyczenia.
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Daty techniczne – utworzenie / ostatnia aktualizacja rekordu.
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, **kwargs):
        """
        Konstruktor z automatycznym ustawieniem due_date.

        Domyślnie: wypożyczenie na 14 dni (NF29).
        Jeśli due_date nie zostanie podany jawnie, przyjmuje wartość:
            now() + 14 dni.
        """
        super().__init__(**kwargs)
        if not self.due_date:
            self.due_date = datetime.utcnow() + timedelta(days=14)

    def is_active(self) -> bool:
        """
        Sprawdź czy wypożyczenie jest aktywne (F11).

        Wypożyczenie jest aktywne, jeśli:
        - ma status ACTIVE,
        - nie jest oznaczone jako usunięte,
        - nie zostało jeszcze zwrócone (returned_at == None).
        """
        return (
            self.status == LoanStatus.ACTIVE
            and not self.is_deleted
            and self.returned_at is None
        )

    def is_overdue(self) -> bool:
        """
        Sprawdź czy wypożyczenie jest przetrzymane (F27 - kary).

        Wypożyczenie jest przetrzymane, jeśli:
        - jest nadal aktywne (niezwrócone),
        - bieżący czas przekroczył termin zwrotu (due_date).
        """
        return self.is_active() and datetime.utcnow() > self.due_date

    def can_be_returned(self) -> bool:
        """
        Sprawdź czy książkę można zwrócić (F12).

        Zwrócić można tylko aktywne wypożyczenie, które nie zostało jeszcze zwrócone.
        """
        return self.is_active()

    def can_be_extended(self) -> bool:
        """
        Sprawdź czy wypożyczenie można przedłużyć (F14).

        W tej wersji:
        - można przedłużyć tylko wypożyczenie aktywne,
        - nieprzetrzymane (nie OVERDUE).
        Logikę "można przedłużyć tylko raz" można dodać w warstwie serwisu.
        """
        return self.is_active() and not self.is_overdue()

    def return_book(self) -> None:
        """
        Zwróć książkę (F12).

        - ustawia returned_at na bieżący czas,
        - zmienia status na RETURNED,
        - oblicza karę za przetrzymanie (F27 – 2 zł za każdy dzień po terminie),
        - aktualizuje znacznik updated_at.
        """
        if self.can_be_returned():
            returned_time = datetime.utcnow()
            self.returned_at = returned_time
            self.status = LoanStatus.RETURNED

            # Oblicz karę za przetrzymanie (F27 - 2 zł za dzień)
            if returned_time > self.due_date:
                days_overdue = (returned_time - self.due_date).days
                self.fine_amount = days_overdue * 2.0

            self.updated_at = datetime.utcnow()

    def extend_loan(self, days: int = 7) -> bool:
        """
        Przedłuż wypożyczenie (F14 - opcjonalne).

        Args:
            days: liczba dni do przedłużenia (domyślnie 7).

        Returns:
            True jeśli przedłużono, False jeśli nie można.
        """
        if self.can_be_extended():
            self.due_date = self.due_date + timedelta(days=days)
            self.updated_at = datetime.utcnow()
            return True
        return False

    def mark_as_overdue(self) -> None:
        """
        Oznacz wypożyczenie jako przetrzymane (F27).

        Typowy scenariusz: zadanie cykliczne (scheduler) przegląda
        aktywne wypożyczenia i dla spóźnionych wywołuje tę metodę.
        """
        if self.is_overdue():
            self.status = LoanStatus.OVERDUE
            self.updated_at = datetime.utcnow()

    def calculate_current_fine(self) -> float:
        """
        Oblicz aktualną karę za przetrzymanie (F27).

        Kara: 2 zł za każdy dzień przetrzymania.
        Funkcja przydaje się np. do wyliczania dynamicznej kary
        przed zwrotem książki.

        Returns:
            Kwota kary w złotych (float).
        """
        if not self.is_overdue():
            return 0.0

        days_overdue = (datetime.utcnow() - self.due_date).days
        return days_overdue * 2.0

    def __repr__(self) -> str:
        """
        Reprezentacja tekstowa obiektu – użyteczna przy debugowaniu/logach.
        """
        return f"<Loan(id={self.id}, user_id={self.user_id}, book_copy_id={self.book_copy_id}, status={self.status})>"
