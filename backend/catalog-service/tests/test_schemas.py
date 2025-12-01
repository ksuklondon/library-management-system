"""
Testy dla Pydantic schemas - walidacja danych.

Wymaganie: Punkt 5 - Opis metod i podejść do testowania
Wymaganie NF7: Walidacja danych wejściowych
Testy jednostkowe dla schematów walidacji.
"""

import pytest
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.schemas.book_copy import (
    BookCopyCreate,
    BookCopyUpdate,
    CopyStatusUpdate,
)
from app.schemas.catalog import CatalogFilter, PaginationParams, SearchQuery
from pydantic import ValidationError


class TestBookSchemas:
    """
    Testy dla schematów Book.
    """

    def test_book_create_valid(self):
        """Test tworzenia poprawnej książki (NF7)."""
        book_data = {
            "title": "Valid Book",
            "authors": "Valid Author",
            "isbn": "1234567890",
            "publisher": "Valid Publisher",
            "pages": 300,
            "language": "pl",
            "genre": "Fiction",
        }

        book = BookCreate(**book_data)

        assert book.title == "Valid Book"
        assert book.authors == "Valid Author"
        assert book.isbn == "1234567890"
        assert book.pages == 300

    def test_book_create_isbn_validation(self):
        """Test walidacji ISBN (NF7)."""
        # ISBN za krótki
        with pytest.raises(ValidationError) as exc_info:
            BookCreate(  # type: ignore
                title="Test",
                authors="Test",
                isbn="123",  # Za krótki!
            )

        assert "ISBN musi mieć 10 lub 13 cyfr" in str(exc_info.value)

        # ISBN z literami
        with pytest.raises(ValidationError) as exc_info:
            BookCreate(title="Test", authors="Test", isbn="123ABC7890")  # type: ignore

        assert "ISBN może zawierać tylko cyfry" in str(exc_info.value)

    def test_book_create_isbn_10_valid(self):
        """Test poprawnego ISBN-10."""
        book = BookCreate(title="Test", authors="Test", isbn="1234567890")  # type: ignore

        assert book.isbn == "1234567890"

    def test_book_create_isbn_13_valid(self):
        """Test poprawnego ISBN-13."""
        book = BookCreate(title="Test", authors="Test", isbn="1234567890123")  # type: ignore

        assert book.isbn == "1234567890123"

    def test_book_create_missing_required_fields(self):
        """Test brakujących wymaganych pól (NF7)."""
        # Brak title
        with pytest.raises(ValidationError):
            BookCreate(authors="Test Author")  # type: ignore

        # Brak authors
        with pytest.raises(ValidationError):
            BookCreate(title="Test Title")  # type: ignore

    def test_book_update_partial(self):
        """Test częściowej aktualizacji (wszystkie pola opcjonalne)."""
        # Tylko title
        update1 = BookUpdate(title="New Title")  # type: ignore
        assert update1.title == "New Title"
        assert update1.authors is None

        # Tylko pages
        update2 = BookUpdate(pages=500)  # type: ignore
        assert update2.pages == 500
        assert update2.title is None

    def test_book_response_from_orm(self, sample_book):
        """Test tworzenia BookResponse z modelu ORM."""
        book_response = BookResponse(
            id=sample_book.id,
            title=sample_book.title,
            authors=sample_book.authors,
            isbn=sample_book.isbn,
            publisher=sample_book.publisher,
            pages=sample_book.pages,
            language=sample_book.language,
            cover_url=sample_book.cover_url,
            description=sample_book.description,
            genre=sample_book.genre,
            available_copies=1,
            total_copies=1,
            created_at=sample_book.created_at,
            updated_at=sample_book.updated_at,
        )

        assert book_response.title == sample_book.title
        assert book_response.available_copies == 1


class TestBookCopySchemas:
    """
    Testy dla schematów BookCopy.
    """

    def test_book_copy_create_valid(self):
        """Test tworzenia poprawnego egzemplarza."""
        import uuid

        book_id = uuid.uuid4()

        copy_data = {
            "book_id": book_id,
            "inventory_no": "INV-001",
            "location": "Shelf A-1",
        }

        copy = BookCopyCreate(**copy_data)

        assert copy.book_id == book_id
        assert copy.inventory_no == "INV-001"
        assert copy.location == "Shelf A-1"

    def test_book_copy_create_missing_required(self):
        """Test brakujących wymaganych pól (NF7)."""
        import uuid

        # Brak inventory_no
        with pytest.raises(ValidationError):
            BookCopyCreate(book_id=uuid.uuid4())  # type: ignore

        # Brak book_id
        with pytest.raises(ValidationError):
            BookCopyCreate(inventory_no="INV-001")  # type: ignore

    def test_copy_status_update_valid(self):
        """Test zmiany statusu egzemplarza (F16)."""
        status_update = CopyStatusUpdate(status="DAMAGED")  # type: ignore

        assert status_update.status == "DAMAGED"

    def test_book_copy_update_partial(self):
        """Test częściowej aktualizacji egzemplarza."""
        # Tylko location
        update1 = BookCopyUpdate(location="New Location")  # type: ignore
        assert update1.location == "New Location"
        assert update1.inventory_no is None

        # Tylko status
        update2 = BookCopyUpdate(status="DAMAGED")  # type: ignore
        assert update2.status == "DAMAGED"


class TestCatalogSchemas:
    """
    Testy dla schematów wyszukiwania i filtrowania.
    """

    def test_search_query_valid(self):
        """Test poprawnego zapytania wyszukiwania (F5)."""
        query = SearchQuery(query="Python", search_in="title")  # type: ignore

        assert query.query == "Python"
        assert query.search_in == "title"

    def test_search_query_default_search_in(self):
        """Test domyślnej wartości search_in."""
        query = SearchQuery(query="Test")  # type: ignore

        assert query.search_in == "all"

    def test_search_query_min_length(self):
        """Test minimalnej długości zapytania (NF7)."""
        with pytest.raises(ValidationError):
            SearchQuery(query="")  # Puste zapytanie  # type: ignore

    def test_catalog_filter_all_fields(self):
        """Test wszystkich pól filtru (F6)."""
        filter_data = CatalogFilter(
            authors="John Doe",
            genre="Fiction",
            language="pl",
            publisher="Test Publisher",
            available_only=True,
        )  # type: ignore

        assert filter_data.authors == "John Doe"
        assert filter_data.genre == "Fiction"
        assert filter_data.language == "pl"
        assert filter_data.publisher == "Test Publisher"
        assert filter_data.available_only is True

    def test_catalog_filter_optional_fields(self):
        """Test opcjonalnych pól filtru."""
        # ⬇⬇ TUTAJ DODANY type: ignore, żeby uciszyć Pylance
        filter_data = CatalogFilter()  # type: ignore

        assert filter_data.authors is None
        assert filter_data.genre is None
        assert filter_data.available_only is False

    def test_pagination_params_default(self):
        """Test domyślnych parametrów paginacji (F4, NF20)."""
        # ⬇⬇ I TUTAJ
        pagination = PaginationParams()  # type: ignore

        assert pagination.page == 1
        assert pagination.page_size == 20

    def test_pagination_params_custom(self):
        """Test niestandardowych parametrów paginacji."""
        pagination = PaginationParams(page=3, page_size=10)  # type: ignore

        assert pagination.page == 3
        assert pagination.page_size == 10

    def test_pagination_params_max_page_size(self):
        """Test maksymalnego rozmiaru strony (NF20 - max 50)."""
        with pytest.raises(ValidationError):
            PaginationParams(page_size=100)  # type: ignore

    def test_pagination_params_min_page(self):
        """Test minimalnego numeru strony."""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)  # type: ignore

    def test_pagination_get_offset(self):
        """Test obliczania offset dla paginacji."""
        # Strona 1, rozmiar 20
        pagination1 = PaginationParams(page=1, page_size=20)  # type: ignore
        assert pagination1.get_offset() == 0

        # Strona 2, rozmiar 20
        pagination2 = PaginationParams(page=2, page_size=20)  # type: ignore
        assert pagination2.get_offset() == 20

        # Strona 3, rozmiar 10
        pagination3 = PaginationParams(page=3, page_size=10)  # type: ignore
        assert pagination3.get_offset() == 20
