"""
Testy dla modelu Reservation.

Wymaganie: NF9 - Testy jednostkowe
Wymaganie: F8-F10 - Rezerwacje książek
"""

import pytest
from datetime import datetime, timedelta
import uuid

from app.models.reservation import Reservation, ReservationStatus


class TestReservationModel:
    """Testy dla modelu Reservation (F8-F10, NF9)."""

    def test_create_reservation(self, db, test_user):
        """
        Test: Utworzenie rezerwacji (F8, NF9).

        Sprawdza:
        - poprawne utworzenie obiektu,
        - automatyczne ustawienie pól timestamp,
        - brak soft delete,
        - powiązanie z użytkownikiem.
        """
        # Arrange & Act — tworzymy nową rezerwację dla testowego użytkownika
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        # Assert — weryfikujemy, że rezerwacja została poprawnie zapisana
        assert reservation.id is not None
        assert reservation.user_id == test_user.id
        assert reservation.status == ReservationStatus.ACTIVE
        assert reservation.reserved_at is not None
        assert reservation.expires_at is not None  # powinno być ustawione automatycznie
        assert not reservation.is_deleted

    def test_reservation_auto_expires_at(self, db, test_user):
        """
        Test: Automatyczne ustawienie expires_at na +3 dni (NF29, NF9).

        Expires_at zgodnie ze specyfikacją powinno zawsze być 3 dni po utworzeniu rezerwacji.
        """
        before = datetime.utcnow()

        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        after = datetime.utcnow()

        # Zakres akceptowalnego expires_at
        expected_min = before + timedelta(days=3)
        expected_max = after + timedelta(days=3)

        # Assert — sprawdzamy czy expires_at mieści się w oknie czasowym
        assert expected_min <= reservation.expires_at <= expected_max

    def test_is_active_true(self, db, test_user):
        """
        Test: Sprawdzanie czy rezerwacja jest aktywna (F8, NF9).

        is_active() powinno zwracać True dla:
        - status ACTIVE
        - niewygasłej rezerwacji
        - nieusuniętego wpisu
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )
        reservation.expires_at = datetime.utcnow() + timedelta(days=1)

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert reservation.is_active() == True

    def test_is_active_false_expired(self, db, test_user):
        """
        Test: Rezerwacja nieaktywna gdy wygasła (NF9).

        Jeśli expires_at < now, rezerwacja powinna być traktowana jako nieaktywna.
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )
        reservation.expires_at = datetime.utcnow() - timedelta(days=1)

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert reservation.is_active() == False

    def test_is_active_false_cancelled(self, db, test_user):
        """
        Test: Rezerwacja nieaktywna gdy anulowana (F10, NF9).

        Status CANCELLED powoduje, że is_active() zwraca False.
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.CANCELLED
        )
        reservation.expires_at = datetime.utcnow() + timedelta(days=1)

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert reservation.is_active() == False

    def test_is_active_false_deleted(self, db, test_user):
        """
        Test: Rezerwacja nieaktywna gdy oznaczona jako usunięta (NF19, NF9).

        Soft delete powinien dezaktywować rezerwację.
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )
        reservation.expires_at = datetime.utcnow() + timedelta(days=1)
        reservation.is_deleted = True  # soft delete

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert reservation.is_active() == False

    def test_can_be_cancelled_true(self, db, test_user):
        """
        Test: Można anulować aktywną rezerwację (F10, NF9).

        Anulowanie dozwolone tylko dla statusu ACTIVE.
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert reservation.can_be_cancelled() == True

    def test_can_be_cancelled_false(self, db, test_user):
        """
        Test: Nie można anulować rezerwacji, która już nie jest aktywna (F10, NF9).
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.CANCELLED
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert reservation.can_be_cancelled() == False

    def test_is_expired(self, db, test_user):
        """
        Test: Sprawdzanie czy rezerwacja wygasła (NF9).

        is_expired() powinno zwracać True jeśli expires_at < now.
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )
        reservation.expires_at = datetime.utcnow() - timedelta(hours=1)

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert reservation.is_expired() == True

    def test_cancel_reservation(self, db, test_user):
        """
        Test: Anulowanie rezerwacji ustawia status CANCELLED i aktualizuje timestamp (F10, NF9).
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        original_updated_at = reservation.updated_at

        # Wywołanie logiki anulowania
        reservation.cancel()
        db.commit()
        db.refresh(reservation)

        assert reservation.status == ReservationStatus.CANCELLED
        assert reservation.updated_at > original_updated_at  # timestamp powinien się zmienić

    def test_complete_reservation(self, db, test_user):
        """
        Test: Oznaczanie rezerwacji jako zrealizowanej (NF9).

        Ta operacja ustawia status COMPLETED.
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        reservation.complete()
        db.commit()
        db.refresh(reservation)

        assert reservation.status == ReservationStatus.COMPLETED

    def test_mark_as_expired(self, db, test_user):
        """
        Test: Oznaczanie rezerwacji jako wygasłej (NF9).

        Gdy expires_at minęło, rezerwacja powinna zostać oznaczona jako EXPIRED.
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )
        reservation.expires_at = datetime.utcnow() - timedelta(hours=1)

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        reservation.mark_as_expired()
        db.commit()
        db.refresh(reservation)

        assert reservation.status == ReservationStatus.EXPIRED

    def test_reservation_with_book_copy_id(self, db, test_user):
        """
        Test: Rezerwacja może opcjonalnie posiadać przypisany egzemplarz (book_copy_id) (NF9).
        """
        book_copy_id = uuid.uuid4()

        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            book_copy_id=book_copy_id,
            status=ReservationStatus.ACTIVE
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert reservation.book_copy_id == book_copy_id

    def test_reservation_timestamps(self, db, test_user):
        """
        Test: Pola created_at i updated_at ustawiane automatycznie (NF9).

        Sprawdzamy czy timestampy znajdują się w poprawnym zakresie czasowym.
        """
        before = datetime.utcnow()

        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        after = datetime.utcnow()

        assert before <= reservation.created_at <= after
        assert before <= reservation.updated_at <= after

    def test_reservation_soft_delete(self, db, test_user):
        """
        Test: Soft delete rezerwacji (NF19, NF9).

        Soft delete:
        - ustawia is_deleted=True
        - ustawia deleted_by
        - powoduje, że rezerwacja nie jest już aktywna
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        reservation.is_deleted = True
        reservation.deleted_by = "admin-id"
        db.commit()
        db.refresh(reservation)

        assert reservation.is_deleted == True
        assert reservation.deleted_by == "admin-id"
        assert reservation.is_active() == False  # usunięta rezerwacja nie może być aktywna

    def test_reservation_repr(self, db, test_user):
        """
        Test: Metoda __repr__ powinna zwracać czytelny opis obiektu (NF9).

        Sprawdzamy, czy reprezentacja zawiera:
        - nazwę modelu,
        - ID rezerwacji,
        - ID użytkownika,
        - status.
        """
        reservation = Reservation(
            user_id=test_user.id,
            book_id=uuid.uuid4(),
            status=ReservationStatus.ACTIVE
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        repr_str = repr(reservation)

        assert "Reservation" in repr_str
        assert str(reservation.id) in repr_str
        assert reservation.user_id in repr_str
        assert "ACTIVE" in repr_str
