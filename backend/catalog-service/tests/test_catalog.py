"""
Testy dla catalog routes - przeglądanie i wyszukiwanie książek.

Wymaganie: Punkt 5 - Opis metod i podejść do testowania
Testy dla F4 (Browse), F5 (Search), F6 (Filter), F7 (Details)
"""

from fastapi import status


class TestBrowseCatalog:
    """
    Testy dla przeglądania katalogu (F4).
    """

    def test_browse_empty_catalog(self, client):
        """Test przeglądania pustego katalogu."""
        response = client.get("/api/catalog/browse")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["books"]) == 0
        assert data["page"] == 1

    def test_browse_catalog_with_books(self, client, multiple_books):
        """Test przeglądania katalogu z książkami."""
        response = client.get("/api/catalog/browse")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["books"]) == 3

    def test_browse_catalog_pagination(self, client, multiple_books):
        """Test paginacji katalogu (F4, NF20)."""
        # Strona 1, 2 książki
        response = client.get("/api/catalog/browse?page=1&page_size=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["books"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 2

        # Strona 2, 1 książka
        response = client.get("/api/catalog/browse?page=2&page_size=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["books"]) == 1
        assert data["page"] == 2

    def test_browse_catalog_max_page_size(self, client, multiple_books):
        """Test maksymalnego rozmiaru strony (NF20 - max 50)."""
        response = client.get("/api/catalog/browse?page_size=100")

        # FastAPI validation powinno odrzucić > 50
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestFilterCatalog:
    """
    Testy dla filtrowania katalogu (F6).
    """

    def test_filter_by_genre(self, client, multiple_books):
        """Test filtrowania po gatunku (F6)."""
        response = client.get("/api/catalog/browse?genre=Programming")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert all(book["genre"] == "Programming" for book in data["books"])

    def test_filter_by_language(self, client, multiple_books):
        """Test filtrowania po języku (F6)."""
        response = client.get("/api/catalog/browse?language=pl")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["books"][0]["language"] == "pl"

    def test_filter_by_authors(self, client, multiple_books):
        """Test filtrowania po autorze (F6)."""
        response = client.get("/api/catalog/browse?authors=John")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert "John" in data["books"][0]["authors"]

    def test_filter_available_only(self, client, sample_book, sample_book_copy):
        """Test filtrowania - tylko dostępne książki (F6)."""
        response = client.get("/api/catalog/browse?available_only=true")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["books"][0]["available_copies"] > 0


class TestSearchCatalog:
    """
    Testy dla wyszukiwania książek (F5).
    """

    def test_search_by_title(self, client, multiple_books):
        """Test wyszukiwania po tytule (F5)."""
        response = client.post(
            "/api/catalog/search", json={"query": "Python", "search_in": "title"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert any("Python" in book["title"] for book in data["books"])

    def test_search_by_authors(self, client, multiple_books):
        """Test wyszukiwania po autorze (F5)."""
        response = client.post(
            "/api/catalog/search", json={"query": "Kowalski", "search_in": "authors"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert "Kowalski" in data["books"][0]["authors"]

    def test_search_by_isbn(self, client, multiple_books):
        """Test wyszukiwania po ISBN (F5)."""
        response = client.post(
            "/api/catalog/search", json={"query": "1111111111111", "search_in": "isbn"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["books"][0]["isbn"] == "1111111111111"

    def test_search_all_fields(self, client, multiple_books):
        """Test wyszukiwania we wszystkich polach (F5)."""
        response = client.post(
            "/api/catalog/search", json={"query": "Python", "search_in": "all"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 2  # W title i authors

    def test_search_case_insensitive(self, client, sample_book):
        """Test wyszukiwania case-insensitive."""
        response = client.post(
            "/api/catalog/search", json={"query": "test book", "search_in": "title"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1


class TestBookDetails:
    """
    Testy dla szczegółów książki (F7).
    """

    def test_get_book_details(self, client, sample_book, sample_book_copy):
        """Test pobierania szczegółów książki (F7)."""
        response = client.get(f"/api/catalog/{sample_book.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_book.id)
        assert data["title"] == sample_book.title
        assert data["authors"] == sample_book.authors
        assert data["available_copies"] == 1
        assert data["total_copies"] == 1

    def test_get_nonexistent_book(self, client):
        """Test pobierania nieistniejącej książki."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/catalog/{fake_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_book_details_show_availability(
        self, client, sample_book, sample_book_copy
    ):
        """Test czy szczegóły pokazują dostępność (F7)."""
        response = client.get(f"/api/catalog/{sample_book.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "available_copies" in data
        assert "total_copies" in data
        assert data["available_copies"] <= data["total_copies"]
