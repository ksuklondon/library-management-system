/**
 * Strona ManageBooks - zarządzanie książkami w katalogu.
 *
 * Zgodność z wymaganiami:
 * - F15: Dodawanie książek do katalogu (LIBRARIAN)
 * - NF5: RBAC - dostęp tylko dla LIBRARIAN i ADMIN
 */

import { AlertCircle, BookOpen, Edit, Plus, Search, Trash2 } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { browseCatalog } from "../../api/catalog";
import BookCard from "../../components/BookCard";
import Button from "../../components/Button";
import Input from "../../components/Input";
import Loading from "../../components/Loading";
import { useAuth } from "../../hooks/useAuth";
import { Book } from "../../types/book";

/**
 * Komponent ManageBooks - zarządzanie katalogiem książek (F15).
 */
const ManageBooks: React.FC = () => {
  const navigate = useNavigate();
  const { isLibrarian, isAdmin } = useAuth();

  // Stan danych
  const [books, setBooks] = useState<Book[]>([]);
  const [total, setTotal] = useState(0);

  // Stan UI
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Paginacja
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  /**
   * Sprawdź uprawnienia (NF5).
   */
  if (!isLibrarian() && !isAdmin()) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <AlertCircle size={64} className="mx-auto text-red-500 mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Brak dostępu</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Nie masz uprawnień do zarządzania książkami. Wymagana rola: Bibliotekarz.
          </p>
          <Button onClick={() => navigate("/")}>Wróć do strony głównej</Button>
        </div>
      </div>
    );
  }

  /**
   * Załaduj książki z API.
   */
  const loadBooks = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await browseCatalog(
        { page, page_size: pageSize },
        searchQuery ? { search: searchQuery } : {}
      );

      setBooks(response.books);
      setTotal(response.total);
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
  }, [page, searchQuery]);

  /**
   * Obsługa wyszukiwania.
   */
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadBooks();
  };

  /**
   * Przejdź do dodawania nowej książki (F15).
   */
  const handleAddBook = () => {
    // W przyszłości: modal lub nowa strona do dodawania książki
    alert(
      "Funkcja dodawania książek będzie wkrótce dostępna! (wymaga integracji z Catalog Service)"
    );
  };

  /**
   * Przejdź do edycji książki.
   */
  const handleEditBook = (bookId: string) => {
    // W przyszłości: modal lub strona edycji
    alert(`Edycja książki ${bookId} będzie wkrótce dostępna!`);
  };

  /**
   * Usuń książkę.
   */
  const handleDeleteBook = async (bookId: string) => {
    const confirmed = window.confirm(
      "Czy na pewno chcesz usunąć tę książkę? Wszystkie jej egzemplarze również zostaną usunięte."
    );

    if (!confirmed) return;

    // W przyszłości: wywołanie API delete
    alert(`Usuwanie książki ${bookId} będzie wkrótce dostępne!`);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <Button variant="outline" onClick={() => navigate("/librarian")} className="mb-4">
            ← Wróć do panelu
          </Button>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
                <BookOpen size={32} />
                Zarządzanie książkami
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Dodawaj, edytuj i usuwaj książki z katalogu
              </p>
            </div>

            {/* Przycisk dodaj książkę (F15) */}
            <Button variant="primary" onClick={handleAddBook} className="flex items-center gap-2">
              <Plus size={20} />
              Dodaj książkę
            </Button>
          </div>
        </div>

        {/* Wyszukiwarka */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
          <form onSubmit={handleSearch} className="flex gap-2">
            <Input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Szukaj po tytule, autorze lub ISBN..."
              fullWidth
            />
            <Button type="submit" variant="primary" className="flex items-center gap-2">
              <Search size={18} />
              Szukaj
            </Button>
          </form>
        </div>

        {/* Statystyki */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Znaleziono <span className="font-semibold">{total}</span> książek
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-500">Strona {page}</span>
          </div>
        </div>

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
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <BookOpen size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-2">Nie znaleziono książek</p>
            <Button variant="primary" onClick={handleAddBook} className="mt-4">
              Dodaj pierwszą książkę
            </Button>
          </div>
        )}

        {/* Lista książek */}
        {!isLoading && !error && books.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {books.map((book) => (
                <div key={book.id} className="relative">
                  <BookCard book={book} showReserveButton={false} />

                  {/* Przyciski akcji */}
                  <div className="absolute top-2 right-2 flex gap-2">
                    <button
                      onClick={() => handleEditBook(book.id)}
                      className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors shadow-md"
                      title="Edytuj książkę"
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      onClick={() => handleDeleteBook(book.id)}
                      className="p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors shadow-md"
                      title="Usuń książkę"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Paginacja */}
            <div className="mt-8 flex items-center justify-center gap-2">
              <Button variant="outline" onClick={() => setPage(page - 1)} disabled={page === 1}>
                Poprzednia
              </Button>

              <span className="text-sm text-gray-600 dark:text-gray-400 mx-4">Strona {page}</span>

              <Button
                variant="outline"
                onClick={() => setPage(page + 1)}
                disabled={books.length < pageSize}
              >
                Następna
              </Button>
            </div>
          </>
        )}

        {/* Informacja o przyszłych funkcjach */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-blue-400" />
            <div className="ml-3">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <span className="font-semibold">W przygotowaniu:</span>
              </p>
              <ul className="text-xs text-blue-700 dark:text-blue-300 mt-2 space-y-1 list-disc list-inside">
                <li>Formularz dodawania nowych książek (F15)</li>
                <li>Edycja istniejących książek</li>
                <li>Usuwanie książek z systemu</li>
                <li>Import książek z CSV/Excel</li>
                <li>Zaawansowane filtrowanie i sortowanie</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManageBooks;
