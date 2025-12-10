"""
Model Fine - kary za przetrzymanie książek.

Wymaganie: F27 - Płatność kar za przetrzymanie
Wymaganie: NF19 - Soft delete
Wymaganie: NF29 - Reguły biznesowe (kara 2 zł za dzień)

Model reprezentuje karę przypisaną do konkretnego wypożyczenia (Loan).
Każda kara odnosi się zawsze do:
- użytkownika (user_id),
- wypożyczenia (loan_id),
- wyliczonej kwoty (amount).

Kara może zostać:
- oznaczona jako opłacona,
- zaktualizowana (dopóki nie została opłacona),
- usunięta logicznie (soft delete).
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class Fine(Base):
    """
    Model Fine - reprezentuje karę za przetrzymanie książki.

    Wymagania:
    - F27: Płatność kar za przetrzymanie
    - NF29: Kara domyślna 2 zł za każdy dzień opóźnienia
    - NF19: Soft delete

    Kary tworzone są zwykle podczas:
    - zwrotu książki (Loan.return_book),
    - automatycznego oznaczania opóźnień (np. w batch job),
    - audytów zaległych wypożyczeń.
    """

    __tablename__ = "fines"

    # Unikalny identyfikator kary (UUID).
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Powiązanie z wypożyczeniem, którego dotyczy kara.
    loan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False, index=True
    )

    # Identyfikator użytkownika – ułatwia filtrowanie kar bez łączenia z Loan.
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Kwota kary w złotówkach (ustalana np. 2 zł * liczba dni).
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Czy kara została już opłacona.
    paid: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )

    # Data opłacenia kary – None jeśli nieopłacona.
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Soft delete (NF19) – kara usunięta logicznie, ale rekord zostaje w bazie.
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Daty techniczne – utworzenie / ostatnia aktualizacja.
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def is_paid(self) -> bool:
        """
        Sprawdź czy kara została opłacona (F27).

        True jeśli:
        - pole paid == True,
        - rekord nie jest oznaczony jako usunięty.
        """
        return self.paid and not self.is_deleted

    def can_be_paid(self) -> bool:
        """
        Sprawdź czy karę można opłacić (F27).

        Warunki:
        - nie jest opłacona,
        - nie jest usunięta,
        - kwota musi być > 0 (nie płacimy kary 0 zł).
        """
        return not self.paid and not self.is_deleted and self.amount > 0

    def mark_as_paid(self, payment_method: str | None = None) -> None:
        """
        Oznacz karę jako opłaconą (F27).

        Args:
            payment_method: np. "cash", "card", "transfer"
            (parametr opcjonalny – nie jest zapisywany, ale może być później rozwinięty).

        Ustawia:
        - paid = True,
        - paid_at = bieżący czas,
        - aktualizuje updated_at.
        """
        if self.can_be_paid():
            self.paid = True
            self.paid_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()

    def update_amount(self, new_amount: float) -> None:
        """
        Zaktualizuj kwotę kary.

        Można wykonać tylko wtedy, gdy kara nie została jeszcze opłacona.
        Przydaje się np. przy ręcznej korekcie przez bibliotekarza.

        Args:
            new_amount: nowa kwota (float)
        """
        if not self.paid:
            self.amount = new_amount
            self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """
        Reprezentacja tekstowa – pomocna w logach i debugowaniu.
        """
        return f"<Fine(id={self.id}, user_id={self.user_id}, amount={self.amount}, paid={self.paid})>"
