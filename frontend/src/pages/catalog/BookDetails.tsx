/**
 * Strona BookDetails - szczegóły książki z możliwością rezerwacji.
 *
 * Zgodność z wymaganiami:
 * - F7: Wyświetlanie szczegółów książki
 * - F8: Rezerwacja książki
 */

import {
  AlertCircle,
  ArrowLeft,
  BookOpen,
  CheckCircle,
  MapPin,
  Package,
  User,
  XCircle,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getBookCopies, getBookDetails } from "../../api/catalog";
import { createReservation } from "../../api/loans";
import Button from "../../components/Button";
import Loading from "../../components/Loading";
import { useAuth } from "../../hooks/useAuth";
import { Book, BookCopy } from "../../types/book";
import { formatISBN } from "../../utils/formatters";

/**
 * Komponent BookDetails - szczegóły książki (F7, F8).
 */
const BookDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Stan danych
  const [book, setBook] = useState<Book | null>(null);
  const [copies, setCopies] = useState<BookCopy[]>([]);

  // Stan UI
  const [isLoading, setIsLoading] = useState(true);
  const [isReserving, setIsReserving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  /**
   * Załaduj szczegóły książki i egzemplarze (F7).
   */
  useEffect(() => {
    const loadBookDetails = async () => {
      if (!id) return;

      setIsLoading(true);
      setError(null);

      try {
        // Pobierz szczegóły książki (F7)
        const bookData = await getBookDetails(id);
        setBook(bookData);

        // Pobierz listę egzemplarzy (F7)
        const copiesData = await getBookCopies(id);
        setCopies(copiesData);
      } catch (err: any) {
        console.error("Error loading book details:", err);
        setError(err.message || "Nie udało się załadować szczegółów książki");
      } finally {
        setIsLoading(false);
      }
    };

    loadBookDetails();
  }, [id]);

  /**
   * Obsługa rezerwacji książki (F8).
   */
  const handleReserve = async () => {
    if (!isAuthenticated) {
      alert("Musisz być zalogowany, aby zarezerwować książkę");
      navigate("/login");
      return;
    }

    if (!book || !id) return;

    setIsReserving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await createReservation({ book_id: id });
      setSuccessMessage("Książka została zarezerwowana! Odbierz ją w bibliotece w ciągu 3 dni.");

      // Odśwież dane książki
      const updatedBook = await getBookDetails(id);
      setBook(updatedBook);
    } catch (err: any) {
      console.error("Error reserving book:", err);
      setError(err.message || "Nie udało się zarezerwować książki");
    } finally {
      setIsReserving(false);
    }
  };

  // Loading state
  if (isLoading) {
    return <Loading fullScreen text="Ładowanie szczegółów książki..." />;
  }

  // Error state
  if (error && !book) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <AlertCircle size={64} className="mx-auto text-red-500 mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Błąd</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
          <Button onClick={() => navigate("/catalog")}>Wróć do katalogu</Button>
        </div>
      </div>
    );
  }

  if (!book) return null;

  const isAvailable = book.available_copies > 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Przycisk powrotu */}
        <Button
          variant="outline"
          onClick={() => navigate("/catalog")}
          className="mb-6 flex items-center gap-2"
        >
          <ArrowLeft size={18} />
          Wróć do katalogu
        </Button>

        {/* Komunikat sukcesu */}
        {successMessage && (
          <div className="mb-6 rounded-md bg-green-50 dark:bg-green-900/20 p-4 border border-green-200 dark:border-green-800">
            <div className="flex">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <div className="ml-3">
                <p className="text-sm text-green-800 dark:text-green-200">{successMessage}</p>
              </div>
            </div>
          </div>
        )}

        {/* Komunikat błędu */}
        {error && (
          <div className="mb-6 rounded-md bg-red-50 dark:bg-red-900/20 p-4 border border-red-200 dark:border-red-800">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Główna zawartość */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
          <div className="md:flex">
            {/* Okładka książki */}
            <div className="md:w-1/3 bg-gray-200 dark:bg-gray-700">
              {book.cover_url ? (
                <img
                  src={book.cover_url}
                  alt={`Okładka ${book.title}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-96 flex items-center justify-center">
                  <BookOpen size={96} className="text-gray-400 dark:text-gray-600" />
                </div>
              )}
            </div>

            {/* Informacje o książce (F7) */}
            <div className="md:w-2/3 p-8">
              {/* Tytuł */}
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                {book.title}
              </h1>

              {/* Autor */}
              <div className="flex items-center gap-2 text-lg text-gray-600 dark:text-gray-400 mb-2">
                <User size={20} />
                <span>{book.authors}</span>
              </div>

              {/* Gatunek */}
              {book.genre && (
                <div className="mb-4">
                  <span className="inline-block px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm">
                    {book.genre}
                  </span>
                </div>
              )}

              {/* Dostępność (F7) */}
              <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Dostępność
                  </span>
                  {isAvailable ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-500 text-white text-xs font-semibold rounded-full">
                      <CheckCircle size={14} />
                      Dostępna
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-500 text-white text-xs font-semibold rounded-full">
                      <XCircle size={14} />
                      Niedostępna
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Dostępne: <span className="font-semibold">{book.available_copies}</span> /{" "}
                  {book.total_copies} egzemplarzy
                </p>
              </div>

              {/* Szczegóły dodatkowe (F7) */}
              <div className="space-y-3 mb-6">
                {book.isbn && (
                  <div className="flex items-start gap-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300 w-24">
                      ISBN:
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {formatISBN(book.isbn)}
                    </span>
                  </div>
                )}

                {book.publisher && (
                  <div className="flex items-start gap-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300 w-24">
                      Wydawca:
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {book.publisher}
                    </span>
                  </div>
                )}

                {book.pages && (
                  <div className="flex items-start gap-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300 w-24">
                      Strony:
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">{book.pages}</span>
                  </div>
                )}

                {book.language && (
                  <div className="flex items-start gap-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300 w-24">
                      Język:
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {book.language}
                    </span>
                  </div>
                )}
              </div>

              {/* Opis (F7) */}
              {book.description && (
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Opis</h2>
                  <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                    {book.description}
                  </p>
                </div>
              )}

              {/* Przycisk rezerwacji (F8) */}
              {isAuthenticated && isAvailable && (
                <Button
                  variant="primary"
                  size="large"
                  onClick={handleReserve}
                  isLoading={isReserving}
                  disabled={isReserving}
                  fullWidth
                >
                  Zarezerwuj książkę
                </Button>
              )}

              {!isAuthenticated && isAvailable && (
                <Button variant="primary" size="large" onClick={() => navigate("/login")} fullWidth>
                  Zaloguj się, aby zarezerwować
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Lista egzemplarzy (F7) */}
        {copies.length > 0 && (
          <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Package size={24} />
              Dostępne egzemplarze ({copies.length})
            </h2>
            <div className="space-y-3">
              {copies.map((copy) => (
                <div
                  key={copy.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {copy.inventory_no}
                    </span>
                    {copy.location && (
                      <span className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
                        <MapPin size={14} />
                        {copy.location}
                      </span>
                    )}
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      copy.status === "AVAILABLE"
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                        : copy.status === "BORROWED"
                        ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                        : "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
                    }`}
                  >
                    {copy.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BookDetails;
