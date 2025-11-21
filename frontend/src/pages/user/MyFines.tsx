/**
 * Strona MyFines - kary za przetrzymanie książek.
 *
 * Zgodność z wymaganiami:
 * - F27: Płatność kar za przetrzymanie
 */

import { AlertCircle, Calendar, CheckCircle, DollarSign } from "lucide-react";
import React, { useEffect, useState } from "react";
import { getUserLoans } from "../../api/loans";
import Button from "../../components/Button";
import Loading from "../../components/Loading";
import { useAuth } from "../../hooks/useAuth";
import { Loan, LoanStatus } from "../../types/loan";
import { formatCurrency, formatDate } from "../../utils/formatters";

/**
 * Interface dla kary.
 */
interface Fine {
  loanId: string;
  bookTitle: string;
  amount: number;
  daysOverdue: number;
  dueDate: Date;
  isPaid: boolean;
}

/**
 * Komponent MyFines - lista kar użytkownika (F27).
 */
const MyFines: React.FC = () => {
  const { user } = useAuth();

  // Stan danych
  const [loans, setLoans] = useState<Loan[]>([]);
  const [fines, setFines] = useState<Fine[]>([]);

  // Stan UI
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [payingFineId, setPayingFineId] = useState<string | null>(null);

  /**
   * Załaduj wypożyczenia i oblicz kary (F27).
   */
  const loadFines = async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);

    try {
      const loansData = await getUserLoans(user.id);
      setLoans(loansData);

      // Oblicz kary dla wypożyczeń
      const calculatedFines: Fine[] = loansData
        .filter((loan) => loan.fine_amount && loan.fine_amount > 0)
        .map((loan) => {
          const dueDate = new Date(loan.due_date);
          const returnedAt = loan.returned_at ? new Date(loan.returned_at) : new Date();
          const daysOverdue = Math.max(
            0,
            Math.ceil((returnedAt.getTime() - dueDate.getTime()) / (1000 * 60 * 60 * 24))
          );

          return {
            loanId: loan.id,
            bookTitle: loan.book_copy?.book?.title || "Nieznana książka",
            amount: loan.fine_amount!,
            daysOverdue,
            dueDate,
            isPaid: loan.status === LoanStatus.RETURNED && loan.fine_amount === 0,
          };
        });

      setFines(calculatedFines);
    } catch (err: any) {
      console.error("Error loading fines:", err);
      setError(err.message || "Nie udało się załadować kar");
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Załaduj kary przy montowaniu.
   */
  useEffect(() => {
    loadFines();
  }, [user]);

  /**
   * Obsługa płatności kary (F27).
   * W prawdziwej aplikacji byłaby integracja z systemem płatności.
   */
  const handlePayFine = async (fineId: string) => {
    const confirmed = window.confirm(
      "Czy chcesz opłacić tę karę? W rzeczywistej aplikacji zostaniesz przekierowany do systemu płatności."
    );

    if (!confirmed) return;

    setPayingFineId(fineId);

    try {
      // Symulacja płatności - w rzeczywistości byłoby wywołanie API
      await new Promise((resolve) => setTimeout(resolve, 1500));

      alert("Płatność zakończona sukcesem! Dziękujemy.");

      // Odśwież listę kar
      await loadFines();
    } catch (err: any) {
      console.error("Error paying fine:", err);
      alert(err.message || "Nie udało się opłacić kary");
    } finally {
      setPayingFineId(null);
    }
  };

  // Statystyki
  const unpaidFines = fines.filter((f) => !f.isPaid);
  const totalUnpaid = unpaidFines.reduce((sum, f) => sum + f.amount, 0);
  const paidFines = fines.filter((f) => f.isPaid);
  const totalPaid = paidFines.reduce((sum, f) => sum + f.amount, 0);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
            <DollarSign size={32} />
            Moje kary
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Przeglądaj i opłacaj kary za przetrzymanie książek
          </p>
        </div>

        {/* Statystyki */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Do zapłaty
              </span>
              <AlertCircle className="text-red-500" size={20} />
            </div>
            <div className="text-3xl font-bold text-red-600 dark:text-red-400">
              {formatCurrency(totalUnpaid)}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              {unpaidFines.length} {unpaidFines.length === 1 ? "kara" : "kar"}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Opłacone</span>
              <CheckCircle className="text-green-500" size={20} />
            </div>
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">
              {formatCurrency(totalPaid)}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              {paidFines.length} {paidFines.length === 1 ? "kara" : "kar"}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Razem</span>
              <DollarSign className="text-gray-500" size={20} />
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">
              {formatCurrency(totalUnpaid + totalPaid)}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              {fines.length} {fines.length === 1 ? "kara" : "kar"} łącznie
            </div>
          </div>
        </div>

        {/* Informacja o karach */}
        <div className="mb-6 rounded-md bg-blue-50 dark:bg-blue-900/20 p-4 border border-blue-200 dark:border-blue-800">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-blue-400" />
            <div className="ml-3">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <span className="font-semibold">Zasady naliczania kar:</span> Za każdy dzień
                przetrzymania książki naliczana jest kara w wysokości 2 zł. Opłać kary jak
                najszybciej, aby móc kontynuować korzystanie z biblioteki.
              </p>
            </div>
          </div>
        </div>

        {/* Loading state */}
        {isLoading && <Loading text="Ładowanie kar..." />}

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

        {/* Brak kar */}
        {!isLoading && !error && fines.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <CheckCircle size={48} className="mx-auto text-green-500 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-2">Nie masz żadnych kar!</p>
            <p className="text-gray-500 dark:text-gray-500 text-sm">
              Świetnie! Pamiętaj o terminowym zwracaniu książek.
            </p>
          </div>
        )}

        {/* Lista kar do zapłaty (F27) */}
        {!isLoading && !error && unpaidFines.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Kary do zapłaty
            </h2>
            <div className="space-y-4">
              {unpaidFines.map((fine) => (
                <div
                  key={fine.loanId}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6"
                >
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        {fine.bookTitle}
                      </h3>
                      <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex items-center gap-2">
                          <Calendar size={16} />
                          <span>Termin zwrotu: {formatDate(fine.dueDate)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <AlertCircle size={16} />
                          <span>Przetrzymanie: {fine.daysOverdue} dni</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                          {formatCurrency(fine.amount)}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-500">
                          {fine.daysOverdue} × 2 zł
                        </div>
                      </div>

                      <Button
                        variant="success"
                        onClick={() => handlePayFine(fine.loanId)}
                        isLoading={payingFineId === fine.loanId}
                        disabled={payingFineId !== null}
                      >
                        Opłać
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Przycisk opłać wszystkie */}
            {unpaidFines.length > 1 && (
              <div className="mt-6 text-center">
                <Button
                  variant="primary"
                  size="large"
                  onClick={() => alert("Funkcja opłacenia wszystkich kar zostanie wkrótce dodana!")}
                >
                  Opłać wszystkie ({formatCurrency(totalUnpaid)})
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Historia opłaconych kar */}
        {!isLoading && !error && paidFines.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Historia opłaconych kar
            </h2>
            <div className="space-y-4">
              {paidFines.map((fine) => (
                <div
                  key={fine.loanId}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 opacity-75"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                        {fine.bookTitle}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Opłacono: {formatCurrency(fine.amount)}
                      </p>
                    </div>
                    <CheckCircle className="text-green-500" size={24} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyFines;
