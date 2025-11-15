"""
Schemas - Pydantic models dla walidacji i serializacji danych.

Eksportuje wszystkie schematy używane w Catalog Service.
"""

from .book import BookBase, BookCreate, BookListResponse, BookResponse, BookUpdate
from .book_copy import (
    BookCopyBase,
    BookCopyCreate,
    BookCopyResponse,
    BookCopyUpdate,
    CopyStatusUpdate,
)
from .catalog import CatalogFilter, PaginationParams, SearchQuery

__all__ = [
    # Book schemas
    "BookBase",
    "BookCreate",
    "BookUpdate",
    "BookResponse",
    "BookListResponse",
    # BookCopy schemas
    "BookCopyBase",
    "BookCopyCreate",
    "BookCopyUpdate",
    "BookCopyResponse",
    "CopyStatusUpdate",
    # Catalog/Search schemas
    "CatalogFilter",
    "SearchQuery",
    "PaginationParams",
]
