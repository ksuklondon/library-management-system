/**
 * Strona MyLoans - wypożyczenia użytkownika.
 *
 * Zgodność z wymaganiami:
 * - F13: Historia wypożyczeń
 * - F14: Przedłużenie wypożyczenia (opcjonalne)
 */

import { AlertCircle, BookOpen } from "lucide-react";
import React, { useCallback, useEffect, useState } from "react";
import Button from "../../components/Button";
import Loading from "../../components/Loading";
import LoanCard from "../../components/LoanCard";
import { useAuth } from "../../hooks/useAuth";
import type { Loan } from "../../types/loan";
import { LoanStatus } from "../../types/loan";

/**
 * Komponent MyLoans - lista wypożyczeń użytkownika (F13, F14).
 */
const MyLoans: React.FC = () => {
  const { user } = useAuth();

  // Stan danych
  const [loans, setLoans] = useState<Loan[]>([]);

  // Stan UI
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [extendingId, setExtendingId] = useState<string | null>(null);

  // Filtr statusu
  const [statusFilter, setStatusFilter] = useState<"all" | LoanStatus>("all");

  /**
   * Załaduj wypożyczenia użytkownika (F13).
   */
  const loadLoans = useCallback(async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);

    try {
      // Symulacja danych - w przyszłości użyj getUserLoans(user.id)
      const mockLoans: Loan[] = [
        {
          id: "loan-1",
          user_id: user.id,
          book_copy_id: "copy-1",
          borrowed_at: "2024-11-20T10:00:00Z",
          due_date: "2024-12-04T23:59:59Z",
          status: LoanStatus.ACTIVE,
          fine_amount: 0,
          created_at: "2024-11-20T10:00:00Z",
          updated_at: "2024-11-20T10:00:00Z",
        },
        {
          id: "loan-2",
          user_id: user.id,
          book_copy_id: "copy-2",
          borrowed_at: "2024-10-15T10:00:00Z",
          due_date: "2024-10-29T23:59:59Z",
          returned_at: "2024-10-28T14:30:00Z",
          status: LoanStatus.RETURNED,
          fine_amount: 0,
          created_at: "2024-10-15T10:00:00Z",
          updated_at: "2024-10-28T14:30:00Z",
        },
      ];

      setLoans(mockLoans);
    } catch (err: unknown) {
      console.error("Error loading loans:", err);
      setError(err instanceof Error ? err.message : "Nie udało się załadować wypożyczeń");
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  /**
   * Załaduj wypożyczenia przy montowaniu.
   */
  useEffect(() => {
    loadLoans();
  }, [loadLoans]);

  /**
   * Obsługa przedłużenia wypożyczenia (F14).
   */
  const handleExtend = async (loanId: string) => {
    const confirmed = window.confirm("Czy chcesz przedłużyć to wypożyczenie o 7 dni?");

    if (!confirmed) return;

    setExtendingId(loanId);

    try {
      // Symulacja przedłużenia - w przyszłości użyj extendLoan(loanId, { days: 7 })
      await new Promise((resolve) => setTimeout(resolve, 1000));
      alert("Wypożyczenie zostało przedłużone o 7 dni!");
      // Odśwież listę wypożyczeń
      await loadLoans();
    } catch (err: unknown) {
      console.error("Error extending loan:", err);
      alert(err instanceof Error ? err.message : "Nie udało się przedłużyć wypożyczenia");
    } finally {
      setExtendingId(null);
    }
  };

  /**
   * Filtruj wypożyczenia według statusu.
   */
  const filteredLoans =
    statusFilter === "all" ? loans : loans.filter((l) => l.status === statusFilter);

  // Statystyki
  const activeCount = loans.filter((l) => l.status === LoanStatus.ACTIVE).length;
  const returnedCount = loans.filter((l) => l.status === LoanStatus.RETURNED).length;
  const overdueCount = loans.filter((l) => l.status === LoanStatus.OVERDUE).length;

  // Suma kar do zapłacenia
  const totalFines = loans
    .filter((l) => l.fine_amount && l.fine_amount > 0)
    .reduce((sum, l) => sum + (l.fine_amount || 0), 0);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
            <BookOpen size={32} />
            Moje wypożyczenia
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Zarządzaj swoimi wypożyczeniami i przeglądaj historię
          </p>
        </div>

        {/* Statystyki */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{activeCount}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Aktywne</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {returnedCount}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Zwrócone</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">{overdueCount}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Przetrzymane</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
              {totalFines.toFixed(2)} zł
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Kary</div>
          </div>
        </div>

        {/* Ostrzeżenie o karach */}
        {totalFines > 0 && (
          <div className="mb-6 rounded-md bg-yellow-50 dark:bg-yellow-900/20 p-4 border border-yellow-200 dark:border-yellow-800">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-yellow-400" />
              <div className="ml-3">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  Masz nieopłacone kary za przetrzymanie w wysokości{" "}
                  <span className="font-bold">{totalFines.toFixed(2)} zł</span>. Opłać je w zakładce{" "}
                  <a href="/my-fines" className="underline font-medium">
                    Moje kary
                  </a>
                  .
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Filtry statusu */}
        <div className="mb-6 flex flex-wrap gap-2">
          <Button
            variant={statusFilter === "all" ? "primary" : "outline"}
            size="small"
            onClick={() => setStatusFilter("all")}
          >
            Wszystkie ({loans.length})
          </Button>
          <Button
            variant={statusFilter === LoanStatus.ACTIVE ? "primary" : "outline"}
            size="small"
            onClick={() => setStatusFilter(LoanStatus.ACTIVE)}
          >
            Aktywne ({activeCount})
          </Button>
          <Button
            variant={statusFilter === LoanStatus.RETURNED ? "primary" : "outline"}
            size="small"
            onClick={() => setStatusFilter(LoanStatus.RETURNED)}
          >
            Zwrócone ({returnedCount})
          </Button>
          <Button
            variant={statusFilter === LoanStatus.OVERDUE ? "primary" : "outline"}
            size="small"
            onClick={() => setStatusFilter(LoanStatus.OVERDUE)}
          >
            Przetrzymane ({overdueCount})
          </Button>
        </div>

        {/* Loading state */}
        {isLoading && <Loading text="Ładowanie wypożyczeń..." />}

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

        {/* Brak wypożyczeń */}
        {!isLoading && !error && filteredLoans.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <BookOpen size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-2">
              {statusFilter === "all"
                ? "Nie masz jeszcze żadnych wypożyczeń"
                : `Brak wypożyczeń o statusie: ${statusFilter}`}
            </p>
            <p className="text-gray-500 dark:text-gray-500 text-sm mb-4">
              Zarezerwuj książkę i odbierz ją w bibliotece!
            </p>
            <Button variant="primary" onClick={() => (window.location.href = "/catalog")}>
              Przeglądaj katalog
            </Button>
          </div>
        )}

        {/* Lista wypożyczeń (F13) */}
        {!isLoading && !error && filteredLoans.length > 0 && (
          <div className="space-y-4">
            {filteredLoans.map((loan) => (
              <LoanCard
                key={loan.id}
                loan={loan}
                onExtend={handleExtend}
                isExtending={extendingId === loan.id}
                showExtendButton={loan.status === LoanStatus.ACTIVE}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyLoans;
