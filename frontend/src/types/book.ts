/**
 * Typy danych dla książek i egzemplarzy.
 *
 * Zgodność z wymaganiami:
 * - F4: Przeglądanie katalogu książek
 * - F5: Wyszukiwanie książek
 * - F6: Filtrowanie książek
 * - F7: Wyświetlanie szczegółów książki
 * - F15: Zarządzanie książkami (CRUD)
 * - F16: Zarządzanie egzemplarzami
 */

/**
 * Interface reprezentujący książkę w katalogu.
 * Zgodny z modelem Book z backend/catalog-service.
 */
export interface Book {
  id: string;
  title: string;
  authors: string;
  isbn?: string;
  publisher?: string;
  pages?: number;
  language?: string;
  cover_url?: string;
  description?: string;
  genre?: string;
  available_copies: number; // Liczba dostępnych egzemplarzy (F7)
  total_copies: number; // Łączna liczba egzemplarzy (F7)
  created_at: string;
  updated_at: string;
}

/**
 * Enum ze statusami egzemplarza książki (F16).
 */
export enum CopyStatus {
  AVAILABLE = "AVAILABLE",
  RESERVED = "RESERVED",
  BORROWED = "BORROWED",
  DAMAGED = "DAMAGED",
  LOST = "LOST",
}

/**
 * Interface reprezentujący pojedynczy egzemplarz książki.
 * Zgodny z modelem BookCopy z backend/catalog-service.
 */
export interface BookCopy {
  id: string;
  book_id: string;
  inventory_no: string;
  status: CopyStatus;
  location?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Request do tworzenia nowej książki (F15 - LIBRARIAN/ADMIN).
 */
export interface BookCreateRequest {
  title: string;
  authors: string;
  isbn?: string;
  publisher?: string;
  pages?: number;
  language?: string;
  cover_url?: string;
  description?: string;
  genre?: string;
}

/**
 * Request do aktualizacji książki (F15 - LIBRARIAN/ADMIN).
 */
export interface BookUpdateRequest {
  title?: string;
  authors?: string;
  isbn?: string;
  publisher?: string;
  pages?: number;
  language?: string;
  cover_url?: string;
  description?: string;
  genre?: string;
}

/**
 * Request do tworzenia egzemplarza (F16 - LIBRARIAN/ADMIN).
 */
export interface BookCopyCreateRequest {
  book_id: string;
  inventory_no: string;
  location?: string;
}

/**
 * Request do aktualizacji egzemplarza (F16 - LIBRARIAN/ADMIN).
 */
export interface BookCopyUpdateRequest {
  inventory_no?: string;
  status?: CopyStatus;
  location?: string;
}

/**
 * Parametry wyszukiwania książek (F5).
 */
export interface SearchQuery {
  query: string;
  search_in?: "all" | "title" | "authors" | "isbn";
}

/**
 * Parametry filtrowania katalogu (F6).
 */
export interface CatalogFilter {
  authors?: string;
  genre?: string;
  language?: string;
  publisher?: string;
  available_only?: boolean;
}

/**
 * Parametry paginacji (F4, NF20 - max 50 na stronę).
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

/**
 * Response z wynikami przeglądania katalogu (F4).
 */
export interface CatalogResponse {
  books: Book[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
