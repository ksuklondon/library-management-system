/**
 * Strona ReturnBook - przyjmowanie zwrotów książek przez bibliotekarza.
 *
 * Zgodność z wymaganiami:
 * - F12: Zwrot książki (LIBRARIAN)
 * - F27: Automatyczne naliczanie kar za przetrzymanie
 * - NF5: RBAC - dostęp tylko dla LIBRARIAN i ADMIN
 */

import { AlertCircle, ArrowUpCircle, CheckCircle, DollarSign } from "lucide-react";
import React, { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { returnLoan } from "../../api/loans";
import Button from "../../components/Button";
import Input from "../../components/Input";
import { useAuth } from "../../hooks/useAuth";
import { formatCurrency } from "../../utils/formatters";
import { isNotEmpty } from "../../utils/validators";

/**
 * Komponent ReturnBook - zwrot książek (F12, F27).
 */
const ReturnBook: React.FC = () => {
  const navigate = useNavigate();
  const { isLibrarian, isAdmin } = useAuth();

  // Stan formularza
  const [loanId, setLoanId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Stan sukcesu z informacją o karze
  const [successData, setSuccessData] = useState<{
    message: string;
    fine?: number;
  } | null>(null);

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
            Nie masz uprawnień do przyjmowania zwrotów. Wymagana rola: Bibliotekarz.
          </p>
          <Button onClick={() => navigate("/")}>Wróć do strony głównej</Button>
        </div>
      </div>
    );
  }

  /**
   * Walidacja formularza.
   */
  const validateForm = (): boolean => {
    if (!isNotEmpty(loanId)) {
      setError("ID wypożyczenia jest wymagane");
      return false;
    }
    return true;
  };

  /**
   * Obsługa wysłania formularza (F12).
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessData(null);

    // Walidacja
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Wywołaj API zwrotu (F12, F27 - automatyczne naliczanie kary)
      const returnedLoan = await returnLoan(loanId);

      // Sprawdź czy jest kara (F27)
      const hasFine = returnedLoan.fine_amount && returnedLoan.fine_amount > 0;

      // Sukces
      setSuccessData({
        message: hasFine
          ? "Książka została zwrócona. Naliczono karę za przetrzymanie."
          : "Książka została zwrócona pomyślnie bez kar!",
        fine: hasFine ? returnedLoan.fine_amount : undefined,
      });

      // Wyczyść formularz
      setLoanId("");

      // Przewiń do góry
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err: any) {
      console.error("Error returning book:", err);
      setError(
        err.message ||
          "Nie udało się zwrócić książki. Sprawdź czy wypożyczenie istnieje i jest aktywne."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <Button variant="outline" onClick={() => navigate("/librarian")} className="mb-4">
            ← Wróć do panelu
          </Button>

          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
            <ArrowUpCircle size={32} className="text-green-600 dark:text-green-400" />
            Przyjmij zwrot książki
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Zarejestruj zwrot wypożyczonej książki</p>
        </div>

        {/* Komunikat sukcesu */}
        {successData && (
          <div
            className={`mb-6 rounded-md p-4 border ${
              successData.fine
                ? "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800"
                : "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800"
            }`}
          >
            <div className="flex">
              {successData.fine ? (
                <AlertCircle className="h-5 w-5 text-yellow-400" />
              ) : (
                <CheckCircle className="h-5 w-5 text-green-400" />
              )}
              <div className="ml-3 flex-1">
                <p
                  className={`text-sm ${
                    successData.fine
                      ? "text-yellow-800 dark:text-yellow-200"
                      : "text-green-800 dark:text-green-200"
                  }`}
                >
                  {successData.message}
                </p>
                {successData.fine && (
                  <div className="mt-2 p-3 bg-white dark:bg-yellow-900/30 rounded-md">
                    <div className="flex items-center gap-2">
                      <DollarSign size={20} className="text-yellow-600 dark:text-yellow-400" />
                      <span className="font-semibold text-yellow-900 dark:text-yellow-100">
                        Kara: {formatCurrency(successData.fine)}
                      </span>
                    </div>
                    <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                      Użytkownik musi opłacić karę za przetrzymanie (2 zł/dzień)
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Formularz zwrotu (F12) */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit}>
            <div className="space-y-6">
              {/* ID Wypożyczenia */}
              <div>
                <Input
                  label="ID Wypożyczenia"
                  type="text"
                  value={loanId}
                  onChange={(e) => setLoanId(e.target.value)}
                  error={error}
                  placeholder="np. loan-uuid-123"
                  required
                  fullWidth
                  disabled={isLoading}
                  helperText="Wprowadź UUID wypożyczenia, które chcesz zwrócić"
                />
              </div>

              {/* Informacje pomocnicze */}
              <div className="rounded-md bg-blue-50 dark:bg-blue-900/20 p-4 border border-blue-200 dark:border-blue-800">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-blue-400" />
                  <div className="ml-3">
                    <p className="text-sm text-blue-800 dark:text-blue-200">
                      <span className="font-semibold">Instrukcja:</span>
                    </p>
                    <ul className="text-xs text-blue-700 dark:text-blue-300 mt-2 space-y-1 list-disc list-inside">
                      <li>Sprawdź stan książki przed przyjęciem zwrotu</li>
                      <li>System automatycznie naliczy karę za przetrzymanie (2 zł/dzień)</li>
                      <li>Kara pojawi się w systemie i będzie widoczna dla użytkownika</li>
                      <li>Egzemplarz zostanie automatycznie oznaczony jako dostępny</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Przycisk zwróć */}
              <Button
                type="submit"
                variant="primary"
                fullWidth
                isLoading={isLoading}
                disabled={isLoading}
                className="flex items-center justify-center gap-2"
              >
                <ArrowUpCircle size={20} />
                Przyjmij zwrot
              </Button>
            </div>
          </form>
        </div>

        {/* Informacje o karach (F27) */}
        <div className="mt-6 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
          <h3 className="text-sm font-semibold text-yellow-900 dark:text-yellow-100 mb-2 flex items-center gap-2">
            <DollarSign size={18} />
            Informacje o karach
          </h3>
          <div className="text-xs text-yellow-800 dark:text-yellow-200 space-y-1">
            <p>
              • Kara za przetrzymanie: <strong>2 zł za każdy dzień</strong>
            </p>
            <p>• System automatycznie oblicza karę przy zwrocie</p>
            <p>• Użytkownik musi opłacić karę przed następnym wypożyczeniem</p>
            <p>• Kary można przeglądać i zarządzać nimi w panelu kar</p>
          </div>
        </div>

        {/* Skróty klawiszowe (przyszła funkcjonalność) */}
        <div className="mt-6 bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Wskazówki</h3>
          <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <li>• Możesz skanować kod kreskowy książki (przyszła funkcja)</li>
            <li>• System automatycznie zaktualizuje dostępność egzemplarza</li>
            <li>• Użytkownik otrzyma powiadomienie email o zwrocie</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ReturnBook;
