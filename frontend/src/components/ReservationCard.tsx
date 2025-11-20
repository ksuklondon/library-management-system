/**
 * Komponent ReservationCard - karta wyświetlająca rezerwację.
 *
 * Zgodność z wymaganiami:
 * - F9: Przeglądanie własnych rezerwacji
 * - F10: Anulowanie rezerwacji
 * - NF10: Responsywny design
 */

import { formatDistanceToNow } from "date-fns";
import { pl } from "date-fns/locale";
import { AlertCircle, BookOpen, Calendar, CheckCircle, Clock, XCircle } from "lucide-react";
import React from "react";
import { useNavigate } from "react-router-dom";
import { Reservation, ReservationStatus } from "../types/loan";
import Button from "./Button";

/**
 * Props dla komponentu ReservationCard.
 */
interface ReservationCardProps {
  reservation: Reservation;
  onCancel?: (reservationId: string) => void;
  isCancelling?: boolean;
  showCancelButton?: boolean;
}

/**
 * Komponent ReservationCard - karta rezerwacji (F9).
 *
 * @param reservation - dane rezerwacji
 * @param onCancel - funkcja anulowania rezerwacji (F10)
 * @param isCancelling - czy anulowanie w trakcie
 * @param showCancelButton - czy pokazać przycisk anuluj
 */
const ReservationCard: React.FC<ReservationCardProps> = ({
  reservation,
  onCancel,
  isCancelling = false,
  showCancelButton = true,
}) => {
  const navigate = useNavigate();

  /**
   * Przejdź do szczegółów książki (F7).
   */
  const handleViewBook = () => {
    if (reservation.book?.id) {
      navigate(`/book/${reservation.book.id}`);
    } else {
      navigate(`/book/${reservation.book_id}`);
    }
  };

  /**
   * Anuluj rezerwację (F10).
   */
  const handleCancel = () => {
    if (onCancel) {
      onCancel(reservation.id);
    }
  };

  /**
   * Kolory i ikony dla statusów rezerwacji.
   */
  const statusConfig = {
    ACTIVE: {
      icon: <Clock size={16} />,
      color: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
      label: "Aktywna",
    },
    CANCELLED: {
      icon: <XCircle size={16} />,
      color: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
      label: "Anulowana",
    },
    EXPIRED: {
      icon: <AlertCircle size={16} />,
      color: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
      label: "Wygasła",
    },
    COMPLETED: {
      icon: <CheckCircle size={16} />,
      color: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
      label: "Zrealizowana",
    },
  };

  const status = statusConfig[reservation.status];

  /**
   * Oblicz czas do wygaśnięcia rezerwacji.
   */
  const expiresAt = new Date(reservation.expires_at);
  const isExpiringSoon = expiresAt.getTime() - Date.now() < 24 * 60 * 60 * 1000; // < 24h
  const timeToExpire = formatDistanceToNow(expiresAt, {
    addSuffix: true,
    locale: pl,
  });

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex flex-col md:flex-row gap-4">
        {/* Okładka książki */}
        <div className="flex-shrink-0">
          <div className="w-24 h-32 bg-gray-200 dark:bg-gray-700 rounded-md overflow-hidden">
            {reservation.book?.cover_url ? (
              <img
                src={reservation.book.cover_url}
                alt={reservation.book.title}
                className="w-full h-full object-cover cursor-pointer hover:opacity-80 transition-opacity"
                onClick={handleViewBook}
              />
            ) : (
              <div
                className="w-full h-full flex items-center justify-center cursor-pointer hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                onClick={handleViewBook}
              >
                <BookOpen size={32} className="text-gray-400 dark:text-gray-500" />
              </div>
            )}
          </div>
        </div>

        {/* Informacje o rezerwacji */}
        <div className="flex-1 min-w-0">
          {/* Tytuł książki */}
          <h3
            className="text-lg font-semibold text-gray-900 dark:text-white mb-2 cursor-pointer hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            onClick={handleViewBook}
          >
            {reservation.book?.title || "Książka"}
          </h3>

          {/* Autor */}
          {reservation.book?.authors && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {reservation.book.authors}
            </p>
          )}

          {/* Status */}
          <div className="flex items-center gap-2 mb-3">
            <span
              className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${status.color}`}
            >
              {status.icon}
              {status.label}
            </span>
          </div>

          {/* Daty */}
          <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400 mb-4">
            <div className="flex items-center gap-2">
              <Calendar size={16} />
              <span>
                Zarezerwowano: {new Date(reservation.reserved_at).toLocaleDateString("pl-PL")}
              </span>
            </div>

            {/* Czas wygaśnięcia (dla aktywnych) */}
            {reservation.status === ReservationStatus.ACTIVE && (
              <div
                className={`flex items-center gap-2 ${
                  isExpiringSoon ? "text-red-600 dark:text-red-400 font-medium" : ""
                }`}
              >
                <Clock size={16} />
                <span>
                  Wygasa: {timeToExpire}
                  {isExpiringSoon && " ⚠️"}
                </span>
              </div>
            )}

            {/* Data wygaśnięcia (dla nieaktywnych) */}
            {reservation.status !== ReservationStatus.ACTIVE && (
              <div className="flex items-center gap-2">
                <Clock size={16} />
                <span>Wygasła: {new Date(reservation.expires_at).toLocaleDateString("pl-PL")}</span>
              </div>
            )}
          </div>

          {/* Przyciski akcji */}
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="small" onClick={handleViewBook}>
              Zobacz książkę
            </Button>

            {/* Przycisk anuluj (F10 - tylko dla aktywnych) */}
            {showCancelButton && reservation.status === ReservationStatus.ACTIVE && onCancel && (
              <Button
                variant="danger"
                size="small"
                onClick={handleCancel}
                isLoading={isCancelling}
                disabled={isCancelling}
              >
                Anuluj rezerwację
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Ostrzeżenie o wygasającej rezerwacji */}
      {reservation.status === ReservationStatus.ACTIVE && isExpiringSoon && (
        <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
          <p className="text-sm text-yellow-800 dark:text-yellow-200 flex items-center gap-2">
            <AlertCircle size={16} />
            <span>Twoja rezerwacja wygasa wkrótce! Odbierz książkę lub zostanie anulowana.</span>
          </p>
        </div>
      )}
    </div>
  );
};

export default ReservationCard;
