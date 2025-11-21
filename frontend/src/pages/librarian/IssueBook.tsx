/**
 * Strona IssueBook - wypożyczanie książek przez bibliotekarza.
 *
 * Zgodność z wymaganiami:
 * - F11: Wypożyczenie książki (LIBRARIAN)
 * - NF5: RBAC - dostęp tylko dla LIBRARIAN i ADMIN
 * - NF7: Walidacja danych wejściowych
 */

import { AlertCircle, ArrowDownCircle, CheckCircle } from "lucide-react";
import React, { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createLoan } from "../../api/loans";
import Button from "../../components/Button";
import Input from "../../components/Input";
import { useAuth } from "../../hooks/useAuth";
import { isNotEmpty } from "../../utils/validators";

/**
 * Komponent IssueBook - wypożyczanie książek (F11).
 */
const IssueBook: React.FC = () => {
  const navigate = useNavigate();
  const { isLibrarian, isAdmin } = useAuth();

  // Stan formularza
  const [formData, setFormData] = useState({
    userId: "",
    bookCopyId: "",
    dueDate: "",
  });

  const [errors, setErrors] = useState<{
    userId?: string;
    bookCopyId?: string;
    dueDate?: string;
    general?: string;
  }>({});

  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

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
            Nie masz uprawnień do wypożyczania książek. Wymagana rola: Bibliotekarz.
          </p>
          <Button onClick={() => navigate("/")}>Wróć do strony głównej</Button>
        </div>
      </div>
    );
  }

  /**
   * Aktualizuj pole formularza.
   */
  const handleChange = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value });
    setErrors({ ...errors, [field]: undefined });
  };

  /**
   * Walidacja formularza (NF7).
   */
  const validateForm = (): boolean => {
    const newErrors: any = {};

    // User ID
    if (!isNotEmpty(formData.userId)) {
      newErrors.userId = "ID użytkownika jest wymagane";
    }

    // Book Copy ID
    if (!isNotEmpty(formData.bookCopyId)) {
      newErrors.bookCopyId = "ID egzemplarza książki jest wymagane";
    }

    // Due Date (opcjonalne, ale jeśli podane to musi być w przyszłości)
    if (formData.dueDate) {
      const dueDate = new Date(formData.dueDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (dueDate < today) {
        newErrors.dueDate = "Termin zwrotu musi być w przyszłości";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Obsługa wysłania formularza (F11).
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setSuccessMessage(null);

    // Walidacja
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Przygotuj dane
      const loanData: any = {
        user_id: formData.userId,
        book_copy_id: formData.bookCopyId,
      };

      // Dodaj due_date jeśli podane
      if (formData.dueDate) {
        loanData.due_date = new Date(formData.dueDate).toISOString();
      }

      // Wywołaj API (F11)
      await createLoan(loanData);

      // Sukces
      setSuccessMessage(
        "Książka została wypożyczona pomyślnie! Użytkownik ma 14 dni na zwrot (lub termin podany w formularzu)."
      );

      // Wyczyść formularz
      setFormData({
        userId: "",
        bookCopyId: "",
        dueDate: "",
      });

      // Przewiń do góry
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error: any) {
      console.error("Error issuing book:", error);
      setErrors({
        general:
          error.message ||
          "Nie udało się wypożyczyć książki. Sprawdź czy użytkownik i egzemplarz istnieją i są dostępne.",
      });
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
            <ArrowDownCircle size={32} className="text-blue-600 dark:text-blue-400" />
            Wypożycz książkę
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Zarejestruj nowe wypożyczenie dla użytkownika
          </p>
        </div>

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

        {/* Formularz wypożyczenia (F11) */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit}>
            <div className="space-y-6">
              {/* ID Użytkownika */}
              <div>
                <Input
                  label="ID Użytkownika"
                  type="text"
                  value={formData.userId}
                  onChange={(e) => handleChange("userId", e.target.value)}
                  error={errors.userId}
                  placeholder="np. user-uuid-123"
                  required
                  fullWidth
                  disabled={isLoading}
                  helperText="Wprowadź UUID użytkownika, który wypożycza książkę"
                />
              </div>

              {/* ID Egzemplarza książki */}
              <div>
                <Input
                  label="ID Egzemplarza książki"
                  type="text"
                  value={formData.bookCopyId}
                  onChange={(e) => handleChange("bookCopyId", e.target.value)}
                  error={errors.bookCopyId}
                  placeholder="np. copy-uuid-456"
                  required
                  fullWidth
                  disabled={isLoading}
                  helperText="Wprowadź UUID konkretnego egzemplarza książki"
                />
              </div>

              {/* Termin zwrotu (opcjonalny) */}
              <div>
                <Input
                  label="Termin zwrotu (opcjonalnie)"
                  type="date"
                  value={formData.dueDate}
                  onChange={(e) => handleChange("dueDate", e.target.value)}
                  error={errors.dueDate}
                  fullWidth
                  disabled={isLoading}
                  helperText="Jeśli nie podasz, zostanie ustawiony na 14 dni od dzisiaj"
                />
              </div>

              {/* Błąd ogólny */}
              {errors.general && (
                <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4 border border-red-200 dark:border-red-800">
                  <div className="flex">
                    <AlertCircle className="h-5 w-5 text-red-400" />
                    <div className="ml-3">
                      <p className="text-sm text-red-800 dark:text-red-200">{errors.general}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Informacje pomocnicze */}
              <div className="rounded-md bg-blue-50 dark:bg-blue-900/20 p-4 border border-blue-200 dark:border-blue-800">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-blue-400" />
                  <div className="ml-3">
                    <p className="text-sm text-blue-800 dark:text-blue-200">
                      <span className="font-semibold">Instrukcja:</span>
                    </p>
                    <ul className="text-xs text-blue-700 dark:text-blue-300 mt-2 space-y-1 list-disc list-inside">
                      <li>Sprawdź dostępność egzemplarza w katalogu</li>
                      <li>Upewnij się, że użytkownik nie ma zaległych kar</li>
                      <li>Domyślny okres wypożyczenia to 14 dni</li>
                      <li>Użytkownik może mieć maksymalnie 5 aktywnych wypożyczeń</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Przycisk wypożycz */}
              <Button
                type="submit"
                variant="primary"
                fullWidth
                isLoading={isLoading}
                disabled={isLoading}
                className="flex items-center justify-center gap-2"
              >
                <ArrowDownCircle size={20} />
                Wypożycz książkę
              </Button>
            </div>
          </form>
        </div>

        {/* Skróty klawiszowe (przyszła funkcjonalność) */}
        <div className="mt-6 bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Wskazówki</h3>
          <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <li>• Możesz skanować kod kreskowy książki i karty użytkownika (przyszła funkcja)</li>
            <li>• System automatycznie sprawdzi dostępność egzemplarza</li>
            <li>• Użytkownik otrzyma powiadomienie email o wypożyczeniu</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default IssueBook;
