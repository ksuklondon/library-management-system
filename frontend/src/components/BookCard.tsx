/**
 * Komponent BookCard - karta wyświetlająca książkę w katalogu.
 *
 * Zgodność z wymaganiami:
 * - F4: Przeglądanie katalogu książek
 * - F7: Wyświetlanie szczegółów książki
 * - F8: Rezerwacja książki
 * - NF10: Responsywny design
 */

import { BookOpen, CheckCircle, User, XCircle } from "lucide-react";
import React from "react";
import { useNavigate } from "react-router-dom";
import { Book } from "../types/book";
import Button from "./Button";

/**
 * Props dla komponentu BookCard.
 */
interface BookCardProps {
  book: Book;
  onReserve?: (bookId: string) => void;
  showReserveButton?: boolean;
  isReserving?: boolean;
}

/**
 * Komponent BookCard - karta książki w katalogu (F4, F7).
 *
 * @param book - dane książki
 * @param onReserve - funkcja do rezerwacji (F8)
 * @param showReserveButton - czy pokazać przycisk rezerwacji
 * @param isReserving - czy rezerwacja jest w trakcie
 */
const BookCard: React.FC<BookCardProps> = ({
  book,
  onReserve,
  showReserveButton = false,
  isReserving = false,
}) => {
  const navigate = useNavigate();

  /**
   * Przejście do szczegółów książki (F7).
   */
  const handleViewDetails = () => {
    navigate(`/book/${book.id}`);
  };

  /**
   * Obsługa rezerwacji (F8).
   */
  const handleReserve = (e: React.MouseEvent) => {
    e.stopPropagation(); // Nie przejdź do szczegółów
    if (onReserve) {
      onReserve(book.id);
    }
  };

  /**
   * Czy książka jest dostępna (F7).
   */
  const isAvailable = book.available_copies > 0;

  return (
    <div
      className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden cursor-pointer"
      onClick={handleViewDetails}
    >
      {/* Okładka książki */}
      <div className="relative h-64 bg-gray-200 dark:bg-gray-700">
        {book.cover_url ? (
          <img
            src={book.cover_url}
            alt={`Okładka ${book.title}`}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <BookOpen size={64} className="text-gray-400 dark:text-gray-600" />
          </div>
        )}

        {/* Badge dostępności (F7) */}
        <div className="absolute top-2 right-2">
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
      </div>

      {/* Informacje o książce */}
      <div className="p-4">
        {/* Tytuł (F7) */}
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
          {book.title}
        </h3>

        {/* Autor (F7) */}
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
          <User size={16} />
          <span className="line-clamp-1">{book.authors}</span>
        </div>

        {/* Gatunek (F6) */}
        {book.genre && (
          <div className="mb-3">
            <span className="inline-block px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded">
              {book.genre}
            </span>
          </div>
        )}

        {/* Dostępność egzemplarzy (F7) */}
        <div className="flex items-center justify-between text-sm mb-4">
          <span className="text-gray-600 dark:text-gray-400">
            Dostępne:{" "}
            <span className="font-semibold text-gray-900 dark:text-white">
              {book.available_copies}
            </span>{" "}
            / {book.total_copies}
          </span>
        </div>

        {/* Przyciski akcji */}
        <div className="flex gap-2">
          <Button variant="outline" size="small" fullWidth onClick={handleViewDetails}>
            Zobacz szczegóły
          </Button>

          {/* Przycisk rezerwacji (F8) */}
          {showReserveButton && isAvailable && (
            <Button
              variant="primary"
              size="small"
              fullWidth
              onClick={handleReserve}
              isLoading={isReserving}
              disabled={isReserving}
            >
              Zarezerwuj
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookCard;
