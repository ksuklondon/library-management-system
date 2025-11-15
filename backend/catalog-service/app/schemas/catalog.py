"""
Schemas dla operacji katalogowych - wyszukiwanie, filtrowanie, paginacja.

Wymagania: F4, F5, F6
Pydantic models dla przeglądania i wyszukiwania książek.
"""

from typing import Optional

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """
    Schemat zapytania wyszukiwania.

    Wymaganie F5: Wyszukiwanie książek
    """

    query: str = Field(
        ..., min_length=1, max_length=200, description="Fraza do wyszukania"
    )
    search_in: Optional[str] = Field(
        "all", description="Gdzie szukać: 'title', 'authors', 'isbn', 'all'"
    )

    class Config:
        json_schema_extra = {"example": {"query": "Tolkien", "search_in": "authors"}}


class CatalogFilter(BaseModel):
    """
    Schemat filtrów dla katalogu książek.

    Wymaganie F6: Filtrowanie książek według autora, gatunku, języka
    """

    authors: Optional[str] = Field(
        None, max_length=500, description="Filtruj po autorze"
    )
    genre: Optional[str] = Field(None, max_length=100, description="Filtruj po gatunku")
    language: Optional[str] = Field(
        None, max_length=50, description="Filtruj po języku"
    )
    publisher: Optional[str] = Field(
        None, max_length=255, description="Filtruj po wydawcy"
    )
    available_only: Optional[bool] = Field(
        False, description="Tylko książki z dostępnymi egzemplarzami"
    )

    class Config:
        json_schema_extra = {
            "example": {"genre": "Fantasy", "language": "pl", "available_only": True}
        }


class PaginationParams(BaseModel):
    """
    Parametry paginacji.

    Wymaganie F4: Przeglądanie katalogu z paginacją
    Wymaganie NF20: Maksymalnie 50 wyników na stronę
    """

    page: int = Field(1, ge=1, description="Numer strony (od 1)")
    page_size: int = Field(
        20, ge=1, le=50, description="Liczba wyników na stronę (max 50)"
    )

    def get_offset(self) -> int:
        """
        Oblicza offset dla SQL query.

        Returns:
            int: Offset dla paginacji
        """
        return (self.page - 1) * self.page_size

    class Config:
        json_schema_extra = {"example": {"page": 1, "page_size": 20}}
