"""
Testy dla modelu Fine.

Wymaganie: NF9 - Testy jednostkowe
Wymaganie: F27 - Płatność kar za przetrzymanie
"""

import pytest
from datetime import datetime
import uuid

from app.models.fine import Fine
from app.models.loan import Loan, LoanStatus


class TestFineModel:
    """Testy dla modelu Fine (F27, NF9)."""

    def test_create_fine(self, db, test_loan):
        """
        Test: Utworzenie kary (F27, NF9).

        Weryfikujemy:
        - prawidłowe powstanie obiektu,
        - poprawne ustawienie pól,
        - brak soft-delete,
        - brak daty opłacenia.
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.id is not None
        assert fine.loan_id == test_loan.id
        assert fine.user_id == test_loan.user_id
        assert fine.amount == 10.0
        assert fine.paid == False
        assert fine.paid_at is None
        assert not fine.is_deleted

    def test_is_paid_true(self, db, test_loan):
        """
        Test: is_paid() powinno zwracać True,
        gdy kara ma paid=True i paid_at ustawione (F27).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=True
        )
        fine.paid_at = datetime.utcnow()

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.is_paid() == True

    def test_is_paid_false(self, db, test_loan):
        """
        Test: is_paid() == False gdy kara nieopłacona (F27).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.is_paid() == False

    def test_is_paid_false_deleted(self, db, test_loan):
        """
        Test: Soft-deleted kara nie jest traktowana jako opłacona (NF19).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=True
        )
        fine.paid_at = datetime.utcnow()
        fine.is_deleted = True

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.is_paid() == False

    def test_can_be_paid_true(self, db, test_loan):
        """
        Test: Kara może zostać opłacona, jeśli jest:
        - nieopłacona,
        - nieusunięta,
        - ma kwotę > 0
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.can_be_paid() == True

    def test_can_be_paid_false_already_paid(self, db, test_loan):
        """
        Test: Nie można ponownie opłacić opłaconej kary (F27).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=True
        )
        fine.paid_at = datetime.utcnow()

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.can_be_paid() == False

    def test_can_be_paid_false_deleted(self, db, test_loan):
        """
        Test: Soft-deleted kara nie może być opłacona (NF19).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )
        fine.is_deleted = True

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.can_be_paid() == False

    def test_can_be_paid_false_zero_amount(self, db, test_loan):
        """
        Test: Kara z kwotą 0 zł nie powinna być płatna (NF7 / logika F27).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=0.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.can_be_paid() == False

    def test_mark_as_paid(self, db, test_loan):
        """
        Test: Oznaczanie kary jako opłaconej (F27).

        mark_as_paid():
        - ustawia paid=True,
        - ustawia paid_at na teraz,
        - wymaga podania payment_method.
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        before = datetime.utcnow()

        fine.mark_as_paid(payment_method="card")
        db.commit()
        db.refresh(fine)

        after = datetime.utcnow()

        assert fine.paid == True
        assert fine.paid_at is not None
        assert before <= fine.paid_at <= after

    def test_mark_as_paid_with_payment_method(self, db, test_loan):
        """
        Test: mark_as_paid() obsługuje podanie payment_method.

        Model nie zapisuje payment_method, jednak metoda ma działać.
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        fine.mark_as_paid(payment_method="cash")
        db.commit()
        db.refresh(fine)

        assert fine.paid == True

    def test_update_amount(self, db, test_loan):
        """
        Test: Aktualizacja kwoty kary (F27).

        Możliwa jeśli kara nie została jeszcze opłacona.
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        fine.update_amount(15.0)
        db.commit()
        db.refresh(fine)

        assert fine.amount == 15.0

    def test_update_amount_when_paid(self, db, test_loan):
        """
        Test: Nie wolno zmieniać kwoty opłaconej kary (F27).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=True
        )
        fine.paid_at = datetime.utcnow()

        db.add(fine)
        db.commit()
        db.refresh(fine)

        original_amount = fine.amount

        fine.update_amount(20.0)
        db.commit()
        db.refresh(fine)

        assert fine.amount == original_amount  # wartość nie może się zmienić

    def test_fine_with_loan_relationship(self, db, test_user):
        """
        Test: Sprawdzenie relacji FK fine -> loan (NF9).
        """
        loan = Loan(
            user_id=test_user.id,
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE
        )

        db.add(loan)
        db.commit()
        db.refresh(loan)

        fine = Fine(
            loan_id=loan.id,
            user_id=test_user.id,
            amount=12.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.loan_id == loan.id

    def test_fine_timestamps(self, db, test_loan):
        """
        Test: created_at i updated_at generują się automatycznie (NF9).
        """
        before = datetime.utcnow()

        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        after = datetime.utcnow()

        assert before <= fine.created_at <= after
        assert before <= fine.updated_at <= after

    def test_fine_updated_at_changes(self, db, test_loan):
        """
        Test: updated_at powinno się zmienić przy aktualizacji danych (NF9).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        original_updated_at = fine.updated_at

        # krótka pauza, aby timestamp się zmienił
        import time
        time.sleep(0.1)

        fine.update_amount(15.0)
        db.commit()
        db.refresh(fine)

        assert fine.updated_at > original_updated_at

    def test_fine_soft_delete(self, db, test_loan):
        """
        Test: Soft delete (NF19).

        Soft delete skutkuje:
        - ustawieniem is_deleted=True,
        - ustawieniem deleted_by,
        - zablokowaniem opłacenia kary.
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        fine.is_deleted = True
        fine.deleted_by = "admin-id"
        db.commit()
        db.refresh(fine)

        assert fine.is_deleted == True
        assert fine.deleted_by == "admin-id"
        assert fine.is_paid() == False
        assert fine.can_be_paid() == False

    def test_fine_repr(self, db, test_loan):
        """
        Test: __repr__ musi zawierać kluczowe dane obiektu (NF9).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=10.0,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        repr_str = repr(fine)

        assert "Fine" in repr_str
        assert str(fine.id) in repr_str
        assert fine.user_id in repr_str
        assert "10.0" in repr_str
        assert "False" in repr_str or "paid=False" in repr_str.lower()

    def test_fine_amount_precision(self, db, test_loan):
        """
        Test: Precyzja wartości amount — powinna zachować 2 miejsca po przecinku (F27).
        """
        fine = Fine(
            loan_id=test_loan.id,
            user_id=test_loan.user_id,
            amount=12.56,
            paid=False
        )

        db.add(fine)
        db.commit()
        db.refresh(fine)

        assert fine.amount == 12.56
