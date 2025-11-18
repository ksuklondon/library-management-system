/**
 * API calls dla katalogu książek i egzemplarzy.
 *
 * Zgodność z wymaganiami:
 * - F4: Przeglądanie katalogu książek
 * - F5: Wyszukiwanie książek
 * - F6: Filtrowanie książek
 * - F7: Wyświetlanie szczegółów książki
 * - F15: Zarządzanie książkami (LIBRARIAN/ADMIN)
 * - F16: Zarządzanie egzemplarzami (LIBRARIAN/ADMIN)
 */

import {
  Book,
  BookCopy,
  BookCopyCreateRequest,
  BookCopyUpdateRequest,
  BookCreateRequest,
  BookUpdateRequest,
  CatalogFilter,
  CatalogResponse,
  CopyStatus,
  PaginationParams,
  SearchQuery,
} from "../types/book";
import apiClient, { getErrorMessage } from "./client";

/**
 * Bazowy URL dla catalog-service.
 */
const CATALOG_SERVICE_URL = import.meta.env.VITE_CATALOG_SERVICE_URL || "http://localhost:8002";

/**
 * Przeglądanie katalogu książek z paginacją (F4).
 * Publiczne - nie wymaga autentykacji.
 */
export const browseCatalog = async (
  pagination?: PaginationParams,
  filter?: CatalogFilter
): Promise<CatalogResponse> => {
  try {
    const response = await apiClient.get<CatalogResponse>(
      `${CATALOG_SERVICE_URL}/api/catalog/browse`,
      {
        params: {
          page: pagination?.page || 1,
          page_size: pagination?.page_size || 20,
          ...filter,
        },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Wyszukiwanie książek (F5).
 * Publiczne - nie wymaga autentykacji.
 */
export const searchBooks = async (
  query: SearchQuery,
  pagination?: PaginationParams
): Promise<CatalogResponse> => {
  try {
    const response = await apiClient.post<CatalogResponse>(
      `${CATALOG_SERVICE_URL}/api/catalog/search`,
      query,
      {
        params: {
          page: pagination?.page || 1,
          page_size: pagination?.page_size || 20,
        },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie szczegółów książki (F7).
 * Publiczne - nie wymaga autentykacji.
 */
export const getBookDetails = async (bookId: string): Promise<Book> => {
  try {
    const response = await apiClient.get<Book>(`${CATALOG_SERVICE_URL}/api/catalog/${bookId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Utworzenie nowej książki (F15 - LIBRARIAN/ADMIN).
 */
export const createBook = async (data: BookCreateRequest): Promise<Book> => {
  try {
    const response = await apiClient.post<Book>(`${CATALOG_SERVICE_URL}/api/books/`, data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Aktualizacja książki (F15 - LIBRARIAN/ADMIN).
 */
export const updateBook = async (bookId: string, data: BookUpdateRequest): Promise<Book> => {
  try {
    const response = await apiClient.put<Book>(`${CATALOG_SERVICE_URL}/api/books/${bookId}`, data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Usunięcie książki - soft delete (F15 - ADMIN only).
 */
export const deleteBook = async (bookId: string): Promise<void> => {
  try {
    await apiClient.delete(`${CATALOG_SERVICE_URL}/api/books/${bookId}`);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie wszystkich książek (F15 - LIBRARIAN/ADMIN panel).
 */
export const getAllBooks = async (skip = 0, limit = 50): Promise<Book[]> => {
  try {
    const response = await apiClient.get<Book[]>(`${CATALOG_SERVICE_URL}/api/books/`, {
      params: { skip, limit },
    });
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie egzemplarzy konkretnej książki (F16).
 */
export const getBookCopies = async (bookId: string): Promise<BookCopy[]> => {
  try {
    const response = await apiClient.get<BookCopy[]>(
      `${CATALOG_SERVICE_URL}/api/copies/book/${bookId}`
    );
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie szczegółów egzemplarza (F16).
 */
export const getCopyDetails = async (copyId: string): Promise<BookCopy> => {
  try {
    const response = await apiClient.get<BookCopy>(`${CATALOG_SERVICE_URL}/api/copies/${copyId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Utworzenie nowego egzemplarza (F16 - LIBRARIAN/ADMIN).
 */
export const createBookCopy = async (data: BookCopyCreateRequest): Promise<BookCopy> => {
  try {
    const response = await apiClient.post<BookCopy>(`${CATALOG_SERVICE_URL}/api/copies/`, data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Aktualizacja egzemplarza (F16 - LIBRARIAN/ADMIN).
 */
export const updateBookCopy = async (
  copyId: string,
  data: BookCopyUpdateRequest
): Promise<BookCopy> => {
  try {
    const response = await apiClient.put<BookCopy>(
      `${CATALOG_SERVICE_URL}/api/copies/${copyId}`,
      data
    );
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Zmiana statusu egzemplarza (F16 - LIBRARIAN/ADMIN).
 */
export const updateCopyStatus = async (copyId: string, status: CopyStatus): Promise<BookCopy> => {
  try {
    const response = await apiClient.patch<BookCopy>(
      `${CATALOG_SERVICE_URL}/api/copies/${copyId}/status`,
      { status }
    );
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Usunięcie egzemplarza - soft delete (F16 - ADMIN only).
 */
export const deleteBookCopy = async (copyId: string): Promise<void> => {
  try {
    await apiClient.delete(`${CATALOG_SERVICE_URL}/api/copies/${copyId}`);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};
