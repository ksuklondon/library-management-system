/**
 * Strona Catalog - przeglądanie, wyszukiwanie i filtrowanie książek.
 *
 * Zgodność z wymaganiami:
 * - F4: Przeglądanie katalogu książek
 * - F5: Wyszukiwanie książek
 * - F6: Filtrowanie książek
 * - NF20: Paginacja (max 50 na stronę)
 */

import { AlertCircle, BookOpen } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { browseCatalog, searchBooks } from "../../api/catalog";
import { createReservation } from "../../api/loans";
import BookCard from "../../components/BookCard";
import Button from "../../components/Button";
import FilterPanel from "../../components/FilterPanel";
import Loading from "../../components/Loading";
import SearchBar from "../../components/SearchBar";
import { useAuth } from "../../hooks/useAuth";
import { Book, CatalogFilter, CatalogResponse } from "../../types/book";

/**
 * Komponent Catalog - strona katalogu książek (F4, F5, F6).
 */
const Catalog: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  // Stan danych
  const [books, setBooks] = useState<Book[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  // Stan UI
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reservingBookId, setReservingBookId] = useState<string | null>(null);

  // Parametry wyszukiwania i filtrowania
  const [searchQuery, setSearchQuery] = useState("");
  const [searchIn, setSearchIn] = useState<"all" | "title" | "authors" | "isbn">("all");
  const [filters, setFilters] = useState<CatalogFilter>({});
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  /**
   * Załaduj książki z API (F4).
   */
  const loadBooks = async () => {
    setIsLoading(true);
    setError(null);

    try {
      let response: CatalogResponse;

      // Jeśli jest zapytanie wyszukiwania, użyj search (F5)
      if (searchQuery.trim()) {
        response = await searchBooks(
          { query: searchQuery, search_in: searchIn },
          { page, page_size: pageSize }
        );
      } else {
        // W przeciwnym razie przeglądaj z filtrami (F4, F6)
        response = await browseCatalog({ page, page_size: pageSize }, filters);
      }

      setBooks(response.books);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err: any) {
      console.error("Error loading books:", err);
      setError(err.message || "Nie udało się załadować katalogu");
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Załaduj książki przy montowaniu i zmianie parametrów.
   */
  useEffect(() => {
    loadBooks();
  }, [searchQuery, searchIn, filters, page, pageSize]);

  /**
   * Obsługa wyszukiwania (F5).
   */
  const handleSearch = (query: string, field: typeof searchIn) => {
    setSearchQuery(query);
    setSearchIn(field);
    setPage(1); // Reset do strony 1
  };

  /**
   * Obsługa zmiany filtrów (F6).
   */
  const handleFilterChange = (newFilters: CatalogFilter) => {
    setFilters(newFilters);
    setPage(1); // Reset do strony 1
  };

  /**
   * Obsługa rezerwacji książki (F8).
   */
  const handleReserve = async (bookId: string) => {
    if (!isAuthenticated) {
      alert("Musisz być zalogowany, aby zarezerwować książkę");
      return;
    }

    setReservingBookId(bookId);

    try {
      await createReservation({ book_id: bookId });
      alert("Książka została zarezerwowana!");
      // Odśwież listę książek aby zaktualizować dostępność
      loadBooks();
    } catch (err: any) {
      console.error("Error reserving book:", err);
      alert(err.message || "Nie udało się zarezerwować książki");
    } finally {
      setReservingBookId(null);
    }
  };

  /**
   * Zmiana strony paginacji (NF20).
   */
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Katalog książek</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Przeglądaj, wyszukuj i rezerwuj książki z naszej kolekcji
          </p>
        </div>

        {/* Wyszukiwarka (F5) */}
        <div className="mb-6">
          <SearchBar
            onSearch={handleSearch}
            placeholder="Szukaj po tytule, autorze lub ISBN..."
            isLoading={isLoading}
            showSearchInSelector
          />
        </div>

        {/* Layout: Filtry + Książki */}
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Panel filtrów (F6) */}
          <aside className="lg:w-64 flex-shrink-0">
            <FilterPanel
              onFilterChange={handleFilterChange}
              initialFilters={filters}
              showMobileToggle
            />
          </aside>

          {/* Lista książek */}
          <main className="flex-1">
            {/* Licznik wyników */}
            {!isLoading && (
              <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
                Znaleziono <span className="font-semibold">{total}</span>{" "}
                {total === 1 ? "książkę" : "książek"}
              </div>
            )}

            {/* Loading state */}
            {isLoading && <Loading text="Ładowanie książek..." />}

            {/* Error state */}
            {error && !isLoading && (
              <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4 border border-red-200 dark:border-red-800">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                  <div className="ml-3">
                    <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Brak wyników */}
            {!isLoading && !error && books.length === 0 && (
              <div className="text-center py-12">
                <BookOpen size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                  Nie znaleziono książek spełniających kryteria
                </p>
                <Button
                  variant="outline"
                  className="mt-4"
                  onClick={() => {
                    setSearchQuery("");
                    setFilters({});
                  }}
                >
                  Wyczyść filtry
                </Button>
              </div>
            )}

            {/* Grid książek (F4) */}
            {!isLoading && !error && books.length > 0 && (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {books.map((book) => (
                    <BookCard
                      key={book.id}
                      book={book}
                      onReserve={handleReserve}
                      showReserveButton={isAuthenticated}
                      isReserving={reservingBookId === book.id}
                    />
                  ))}
                </div>

                {/* Paginacja (NF20) */}
                {totalPages > 1 && (
                  <div className="mt-8 flex items-center justify-center gap-2">
                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(page - 1)}
                      disabled={page === 1}
                    >
                      Poprzednia
                    </Button>

                    <span className="text-sm text-gray-600 dark:text-gray-400 mx-4">
                      Strona {page} z {totalPages}
                    </span>

                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(page + 1)}
                      disabled={page === totalPages}
                    >
                      Następna
                    </Button>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default Catalog;
