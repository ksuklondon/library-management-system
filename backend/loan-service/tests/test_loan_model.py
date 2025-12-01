"""
Testy dla modelu Loan.

Wymaganie: NF9 - Testy jednostkowe
Wymaganie: F11-F14, F27 - Wypożyczenia i kary
"""

import uuid
from datetime import datetime, timedelta

from app.models.loan import Loan, LoanStatus


class TestLoanModel:
    """Testy dla modelu Loan (F11-F14, F27, NF9)."""

    def test_create_loan(self, db, mock_reader):
        """
        Test: Utworzenie wypożyczenia (F11, NF9).

        Sprawdzamy:
        - poprawne utworzenie obiektu,
        - automatyczne ustawienie dat,
        - status ACTIVE,
        - brak soft delete.
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )

        db.add(loan)
        db.commit()
        db.refresh(loan)

        assert loan.id is not None
        assert loan.user_id == mock_reader["sub"]
        assert loan.status == LoanStatus.ACTIVE
        assert loan.borrowed_at is not None
        assert loan.due_date is not None  # powinno być ustawione domyślnie (+14 dni)
        assert loan.returned_at is None
        assert not loan.is_deleted

    def test_loan_auto_due_date(self, db, mock_reader):
        """
        Test: Automatyczne ustawienie due_date +14 dni (NF29).

        due_date powinno być wyliczane przez model przy braku jawnego ustawienia.
        """
        before = datetime.utcnow()

        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )

        db.add(loan)
        db.commit()
        db.refresh(loan)

        after = datetime.utcnow()

        expected_min = before + timedelta(days=14)
        expected_max = after + timedelta(days=14)

        assert expected_min <= loan.due_date <= expected_max

    def test_is_active_true(self, db, mock_reader):
        """
        Test: is_active() powinno zwracać True dla aktywnego i niezwróconego wypożyczenia (F11).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() + timedelta(days=14)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        assert loan.is_active() is True

    def test_is_active_false_returned(self, db, mock_reader):
        """
        Test: Zwrócone wypożyczenie nie jest aktywne (F12).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.RETURNED,
        )
        loan.due_date = datetime.utcnow() + timedelta(days=14)
        loan.returned_at = datetime.utcnow()

        db.add(loan)
        db.commit()
        db.refresh(loan)

        assert loan.is_active() is False

    def test_is_overdue(self, db, mock_reader):
        """
        Test: Wypożyczenie jest przetrzymane jeśli due_date < now (F27).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow() - timedelta(days=20),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() - timedelta(days=5)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        assert loan.is_overdue() is True

    def test_is_not_overdue(self, db, mock_reader):
        """
        Test: Wypożyczenie nieprzetrzymane powinno zwrócić False (NF9).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() + timedelta(days=5)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        assert loan.is_overdue() is False

    def test_can_be_returned(self, db, mock_reader):
        """
        Test: Aktywne wypożyczenie można zwrócić (F12).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )

        db.add(loan)
        db.commit()
        db.refresh(loan)

        assert loan.can_be_returned() is True

    def test_can_be_extended(self, db, mock_reader):
        """
        Test: Aktywne i nieprzetrzymane wypożyczenie można przedłużyć (F14).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() + timedelta(days=10)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        assert loan.can_be_extended() is True

    def test_cannot_extend_overdue(self, db, mock_reader):
        """
        Test: Przetrzymanego wypożyczenia nie można przedłużyć (F14).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow() - timedelta(days=20),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() - timedelta(days=5)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        assert loan.can_be_extended() is False

    def test_return_book_on_time(self, db, mock_reader):
        """
        Test: Zwrot na czas nie nalicza kary (F12).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow() - timedelta(days=10),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() + timedelta(days=4)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        loan.return_book()
        db.commit()
        db.refresh(loan)

        assert loan.status == LoanStatus.RETURNED
        assert loan.returned_at is not None
        assert loan.fine_amount == 0.0

    def test_return_book_overdue_with_fine(self, db, mock_reader):
        """
        Test: Zwrot przetrzymanego wypożyczenia nalicza karę (F27).

        Kara: 2 zł * liczba dni spóźnienia.
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow() - timedelta(days=20),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() - timedelta(days=5)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        loan.return_book()
        db.commit()
        db.refresh(loan)

        assert loan.status == LoanStatus.RETURNED
        assert loan.returned_at is not None
        assert loan.fine_amount is not None and loan.fine_amount > 0
        assert (
            loan.fine_amount is not None and loan.fine_amount >= 10.0
        )  # min. 5 dni * 2 zł

    def test_extend_loan(self, db, mock_reader):
        """
        Test: Przedłużenie wypożyczenia o zadaną liczbę dni (F14).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )
        original_due_date = datetime.utcnow() + timedelta(days=10)
        loan.due_date = original_due_date

        db.add(loan)
        db.commit()
        db.refresh(loan)

        success = loan.extend_loan(days=7)
        db.commit()
        db.refresh(loan)

        assert success is True
        assert loan.due_date == original_due_date + timedelta(days=7)

    def test_extend_loan_custom_days(self, db, mock_reader):
        """
        Test: Przedłużenie o inną liczbę dni (np. maksymalnie 14) (F14).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )
        original_due_date = datetime.utcnow() + timedelta(days=10)
        loan.due_date = original_due_date

        db.add(loan)
        db.commit()
        db.refresh(loan)

        success = loan.extend_loan(days=14)
        db.commit()
        db.refresh(loan)

        assert success is True
        assert loan.due_date == original_due_date + timedelta(days=14)

    def test_mark_as_overdue(self, db, mock_reader):
        """
        Test: Oznaczanie wypożyczenia jako OVERDUE (F27).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow() - timedelta(days=20),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() - timedelta(days=5)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        loan.mark_as_overdue()
        db.commit()
        db.refresh(loan)

        assert loan.status == LoanStatus.OVERDUE

    def test_calculate_current_fine(self, db, mock_reader):
        """
        Test: Obliczanie aktualnej kary (F27).

        Kara = dni spóźnienia * 2 zł.
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow() - timedelta(days=20),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() - timedelta(days=6)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        fine = loan.calculate_current_fine()

        assert fine == 12.0

    def test_calculate_current_fine_not_overdue(self, db, mock_reader):
        """
        Test: Nie naliczamy kary dla wypożyczeń na czas (NF9).
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )
        loan.due_date = datetime.utcnow() + timedelta(days=5)

        db.add(loan)
        db.commit()
        db.refresh(loan)

        fine = loan.calculate_current_fine()

        assert fine == 0.0

    def test_loan_timestamps(self, db, mock_reader):
        """
        Test: Automatyczne timestampy created_at i updated_at (NF9).

        Oba znaczniki czasu po zapisie muszą mieścić się między before i after.
        """
        before = datetime.utcnow()

        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )

        db.add(loan)
        db.commit()
        db.refresh(loan)

        after = datetime.utcnow()

        assert before <= loan.created_at <= after
        assert before <= loan.updated_at <= after

    def test_loan_soft_delete(self, db, mock_reader):
        """
        Test: Soft delete (NF19).

        Soft delete:
        - ustawia is_deleted=True,
        - ustawia deleted_by,
        - dezaktywuje obiekt.
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )

        db.add(loan)
        db.commit()
        db.refresh(loan)

        loan.is_deleted = True
        loan.deleted_by = "admin-id"
        db.commit()
        db.refresh(loan)

        assert loan.is_deleted is True
        assert loan.deleted_by == "admin-id"
        assert loan.is_active() is False

    def test_loan_repr(self, db, mock_reader):
        """
        Test: Czytelna reprezentacja string (NF9).

        __repr__ powinien zawierać:
        - nazwę klasy,
        - id wypożyczenia,
        - id użytkownika,
        - status.
        """
        loan = Loan(
            user_id=mock_reader["sub"],
            book_copy_id=uuid.uuid4(),
            borrowed_at=datetime.utcnow(),
            status=LoanStatus.ACTIVE,
        )

        db.add(loan)
        db.commit()
        db.refresh(loan)

        repr_str = repr(loan)

        assert "Loan" in repr_str
        assert str(loan.id) in repr_str
        assert loan.user_id in repr_str
        assert "ACTIVE" in repr_str
