/**
 * Strona MyReservations - rezerwacje użytkownika.
 *
 * Zgodność z wymaganiami:
 * - F9: Przeglądanie własnych rezerwacji
 * - F10: Anulowanie rezerwacji
 */

import { AlertCircle, Calendar } from "lucide-react";
import React, { useEffect, useState } from "react";
import { cancelReservation, getUserReservations } from "../../api/loans";
import Button from "../../components/Button";
import Loading from "../../components/Loading";
import ReservationCard from "../../components/ReservationCard";
import { useAuth } from "../../hooks/useAuth";
import { Reservation, ReservationStatus } from "../../types/loan";

/**
 * Komponent MyReservations - lista rezerwacji użytkownika (F9, F10).
 */
const MyReservations: React.FC = () => {
  const { user } = useAuth();

  // Stan danych
  const [reservations, setReservations] = useState<Reservation[]>([]);

  // Stan UI
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancellingId, setCancellingId] = useState<string | null>(null);

  // Filtr statusu
  const [statusFilter, setStatusFilter] = useState<"all" | ReservationStatus>("all");

  /**
   * Załaduj rezerwacje użytkownika (F9).
   */
  const loadReservations = async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await getUserReservations(user.id);
      setReservations(data);
    } catch (err: any) {
      console.error("Error loading reservations:", err);
      setError(err.message || "Nie udało się załadować rezerwacji");
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Załaduj rezerwacje przy montowaniu.
   */
  useEffect(() => {
    loadReservations();
  }, [user]);

  /**
   * Obsługa anulowania rezerwacji (F10).
   */
  const handleCancel = async (reservationId: string) => {
    const confirmed = window.confirm("Czy na pewno chcesz anulować tę rezerwację?");

    if (!confirmed) return;

    setCancellingId(reservationId);

    try {
      await cancelReservation(reservationId);
      // Odśwież listę rezerwacji
      await loadReservations();
    } catch (err: any) {
      console.error("Error cancelling reservation:", err);
      alert(err.message || "Nie udało się anulować rezerwacji");
    } finally {
      setCancellingId(null);
    }
  };

  /**
   * Filtruj rezerwacje według statusu.
   */
  const filteredReservations =
    statusFilter === "all" ? reservations : reservations.filter((r) => r.status === statusFilter);

  // Statystyki
  const activeCount = reservations.filter((r) => r.status === ReservationStatus.ACTIVE).length;
  const completedCount = reservations.filter(
    (r) => r.status === ReservationStatus.COMPLETED
  ).length;
  const cancelledCount = reservations.filter(
    (r) => r.status === ReservationStatus.CANCELLED
  ).length;
  const expiredCount = reservations.filter((r) => r.status === ReservationStatus.EXPIRED).length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
            <Calendar size={32} />
            Moje rezerwacje
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Zarządzaj swoimi rezerwacjami książek</p>
        </div>

        {/* Statystyki */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{activeCount}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Aktywne</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {completedCount}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Zrealizowane</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-gray-600 dark:text-gray-400">
              {cancelledCount}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Anulowane</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">{expiredCount}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Wygasłe</div>
          </div>
        </div>

        {/* Filtry statusu */}
        <div className="mb-6 flex flex-wrap gap-2">
          <Button
            variant={statusFilter === "all" ? "primary" : "outline"}
            size="small"
            onClick={() => setStatusFilter("all")}
          >
            Wszystkie ({reservations.length})
          </Button>
          <Button
            variant={statusFilter === ReservationStatus.ACTIVE ? "primary" : "outline"}
            size="small"
            onClick={() => setStatusFilter(ReservationStatus.ACTIVE)}
          >
            Aktywne ({activeCount})
          </Button>
          <Button
            variant={statusFilter === ReservationStatus.COMPLETED ? "primary" : "outline"}
            size="small"
            onClick={() => setStatusFilter(ReservationStatus.COMPLETED)}
          >
            Zrealizowane ({completedCount})
          </Button>
          <Button
            variant={statusFilter === ReservationStatus.CANCELLED ? "primary" : "outline"}
            size="small"
            onClick={() => setStatusFilter(ReservationStatus.CANCELLED)}
          >
            Anulowane ({cancelledCount})
          </Button>
          <Button
            variant={statusFilter === ReservationStatus.EXPIRED ? "primary" : "outline"}
            size="small"
            onClick={() => setStatusFilter(ReservationStatus.EXPIRED)}
          >
            Wygasłe ({expiredCount})
          </Button>
        </div>

        {/* Loading state */}
        {isLoading && <Loading text="Ładowanie rezerwacji..." />}

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

        {/* Brak rezerwacji */}
        {!isLoading && !error && filteredReservations.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <Calendar size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-2">
              {statusFilter === "all"
                ? "Nie masz jeszcze żadnych rezerwacji"
                : `Brak rezerwacji o statusie: ${statusFilter}`}
            </p>
            <p className="text-gray-500 dark:text-gray-500 text-sm mb-4">
              Odwiedź katalog i zarezerwuj swoją pierwszą książkę!
            </p>
            <Button variant="primary" onClick={() => (window.location.href = "/catalog")}>
              Przeglądaj katalog
            </Button>
          </div>
        )}

        {/* Lista rezerwacji (F9) */}
        {!isLoading && !error && filteredReservations.length > 0 && (
          <div className="space-y-4">
            {filteredReservations.map((reservation) => (
              <ReservationCard
                key={reservation.id}
                reservation={reservation}
                onCancel={handleCancel}
                isCancelling={cancellingId === reservation.id}
                showCancelButton={reservation.status === ReservationStatus.ACTIVE}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyReservations;
