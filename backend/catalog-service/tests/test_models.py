"""
Testy dla modeli Book i BookCopy.

Wymaganie: Punkt 5 - Opis metod i podejść do testowania
Testy jednostkowe dla modeli danych.
"""

from uuid import UUID

from app.models.book import Book
from app.models.book_copy import BookCopy, CopyStatus


class TestBookModel:
    """
    Testy dla modelu Book.
    """

    def test_create_book(self, db_session):
        """Test tworzenia książki."""
        book = Book(
            title="Test Book",
            authors="Test Author",
            isbn="1234567890123",
            publisher="Test Publisher",
            pages=300,
            language="pl",
            genre="Fiction",
        )

        db_session.add(book)
        db_session.commit()
        db_session.refresh(book)

        assert book.id is not None
        assert book.title == "Test Book"
        assert book.authors == "Test Author"
        assert book.isbn == "1234567890123"
        assert book.is_deleted is False
        assert book.created_at is not None
        assert book.updated_at is not None

    def test_book_get_available_copies_count(self, db_session, sample_book):
        """Test metody get_available_copies_count()."""
        # Dodaj 3 egzemplarze
        copy1 = BookCopy(
            book_id=sample_book.id, inventory_no="C1", status=CopyStatus.AVAILABLE
        )
        copy2 = BookCopy(
            book_id=sample_book.id, inventory_no="C2", status=CopyStatus.AVAILABLE
        )
        copy3 = BookCopy(
            book_id=sample_book.id, inventory_no="C3", status=CopyStatus.BORROWED
        )

        db_session.add_all([copy1, copy2, copy3])
        db_session.commit()
        db_session.refresh(sample_book)

        # Powinno być 2 dostępne (C1, C2)
        assert sample_book.get_available_copies_count() == 2

    def test_book_get_total_copies_count(self, db_session, sample_book):
        """Test metody get_total_copies_count()."""
        # Dodaj 3 egzemplarze
        copy1 = BookCopy(
            book_id=sample_book.id, inventory_no="C1", status=CopyStatus.AVAILABLE
        )
        copy2 = BookCopy(
            book_id=sample_book.id, inventory_no="C2", status=CopyStatus.BORROWED
        )
        copy3 = BookCopy(
            book_id=sample_book.id, inventory_no="C3", status=CopyStatus.DAMAGED
        )

        db_session.add_all([copy1, copy2, copy3])
        db_session.commit()
        db_session.refresh(sample_book)

        assert sample_book.get_total_copies_count() == 3

    def test_book_soft_delete(self, db_session, sample_book):
        """Test soft delete książki (NF19)."""
        book_id = sample_book.id  # Zapisz ID przed modyfikacją

        sample_book.is_deleted = True
        sample_book.deleted_by = UUID("00000000-0000-0000-0000-000000000003")

        db_session.commit()

        # Nie używamy refresh() przez problem UUID w SQLite
        # Odczytaj książkę z bazy ponownie
        from app.models.book import Book

        deleted_book = db_session.query(Book).filter(Book.id == book_id).first()

        assert deleted_book.is_deleted is True
        assert deleted_book.deleted_by == UUID("00000000-0000-0000-0000-000000000003")

    def test_book_repr(self, sample_book):
        """Test reprezentacji tekstowej książki."""
        repr_str = repr(sample_book)
        assert "Test Book" in repr_str
        assert "Test Author" in repr_str


class TestBookCopyModel:
    """
    Testy dla modelu BookCopy.
    """

    def test_create_book_copy(self, db_session, sample_book):
        """Test tworzenia egzemplarza książki."""
        copy = BookCopy(
            book_id=sample_book.id,
            inventory_no="INV-001",
            status=CopyStatus.AVAILABLE,
            location="Shelf A-1",
        )

        db_session.add(copy)
        db_session.commit()
        db_session.refresh(copy)

        assert copy.id is not None
        assert copy.book_id == sample_book.id
        assert copy.inventory_no == "INV-001"
        assert copy.status == CopyStatus.AVAILABLE
        assert copy.location == "Shelf A-1"
        assert copy.is_deleted is False

    def test_copy_is_available(self, db_session, sample_book):
        """Test metody is_available() (F8, F11)."""
        # Dostępny egzemplarz
        copy1 = BookCopy(
            book_id=sample_book.id, inventory_no="C1", status=CopyStatus.AVAILABLE
        )
        db_session.add(copy1)
        db_session.commit()

        assert copy1.is_available() is True

        # Wypożyczony egzemplarz
        copy2 = BookCopy(
            book_id=sample_book.id, inventory_no="C2", status=CopyStatus.BORROWED
        )
        db_session.add(copy2)
        db_session.commit()

        assert copy2.is_available() is False

        # Usunięty egzemplarz
        copy3 = BookCopy(
            book_id=sample_book.id,
            inventory_no="C3",
            status=CopyStatus.AVAILABLE,
            is_deleted=True,
        )
        db_session.add(copy3)
        db_session.commit()

        assert copy3.is_available() is False

    def test_copy_can_be_reserved(self, db_session, sample_book):
        """Test metody can_be_reserved() (F8)."""
        copy = BookCopy(
            book_id=sample_book.id, inventory_no="C1", status=CopyStatus.AVAILABLE
        )
        db_session.add(copy)
        db_session.commit()

        assert copy.can_be_reserved() is True

        # Zmień status na BORROWED
        copy.status = CopyStatus.BORROWED
        db_session.commit()

        assert copy.can_be_reserved() is False

    def test_copy_can_be_borrowed(self, db_session, sample_book):
        """Test metody can_be_borrowed() (F11)."""
        # Dostępny
        copy1 = BookCopy(
            book_id=sample_book.id, inventory_no="C1", status=CopyStatus.AVAILABLE
        )
        db_session.add(copy1)
        db_session.commit()
        assert copy1.can_be_borrowed() is True

        # Zarezerwowany (też można wypożyczyć)
        copy2 = BookCopy(
            book_id=sample_book.id, inventory_no="C2", status=CopyStatus.RESERVED
        )
        db_session.add(copy2)
        db_session.commit()
        assert copy2.can_be_borrowed() is True

        # Wypożyczony (nie można)
        copy3 = BookCopy(
            book_id=sample_book.id, inventory_no="C3", status=CopyStatus.BORROWED
        )
        db_session.add(copy3)
        db_session.commit()
        assert copy3.can_be_borrowed() is False

        # Uszkodzony (nie można)
        copy4 = BookCopy(
            book_id=sample_book.id, inventory_no="C4", status=CopyStatus.DAMAGED
        )
        db_session.add(copy4)
        db_session.commit()
        assert copy4.can_be_borrowed() is False

    def test_copy_soft_delete(self, db_session, sample_book_copy):
        """Test soft delete egzemplarza (NF19)."""
        sample_book_copy.is_deleted = True

        db_session.commit()
        db_session.refresh(sample_book_copy)

        assert sample_book_copy.is_deleted is True

    def test_copy_repr(self, sample_book_copy):
        """Test reprezentacji tekstowej egzemplarza."""
        repr_str = repr(sample_book_copy)
        assert sample_book_copy.inventory_no in repr_str
        assert sample_book_copy.status.value in repr_str

    def test_copy_status_enum_values(self):
        """Test wartości enum CopyStatus."""
        assert CopyStatus.AVAILABLE.value == "AVAILABLE"
        assert CopyStatus.RESERVED.value == "RESERVED"
        assert CopyStatus.BORROWED.value == "BORROWED"
        assert CopyStatus.DAMAGED.value == "DAMAGED"
        assert CopyStatus.LOST.value == "LOST"
