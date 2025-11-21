/**
 * Strona LibrarianPanel - panel główny bibliotekarza.
 *
 * Zgodność z wymaganiami:
 * - NF5: RBAC - dostęp tylko dla LIBRARIAN i ADMIN
 * - Dashboard z szybkim dostępem do funkcji bibliotekarza
 */

import {
  AlertTriangle,
  ArrowDownCircle,
  ArrowUpCircle,
  BookOpen,
  Calendar,
  Package,
  TrendingUp,
  Users,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/Button";
import Loading from "../../components/Loading";
import { useAuth } from "../../hooks/useAuth";

/**
 * Komponent LibrarianPanel - dashboard bibliotekarza.
 */
const LibrarianPanel: React.FC = () => {
  const navigate = useNavigate();
  const { user, isLibrarian, isAdmin } = useAuth();

  // Stan danych statystycznych (przykładowe - w rzeczywistości z API)
  const [stats, setStats] = useState({
    totalBooks: 0,
    totalCopies: 0,
    activeLoans: 0,
    activeReservations: 0,
    overdueLoans: 0,
    availableCopies: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Załaduj statystyki (w rzeczywistości z API).
   */
  useEffect(() => {
    const loadStats = async () => {
      setIsLoading(true);

      // Symulacja ładowania danych
      setTimeout(() => {
        setStats({
          totalBooks: 1247,
          totalCopies: 3456,
          activeLoans: 234,
          activeReservations: 67,
          overdueLoans: 15,
          availableCopies: 2189,
        });
        setIsLoading(false);
      }, 500);
    };

    loadStats();
  }, []);

  // Sprawdź uprawnienia (NF5)
  if (!isLibrarian() && !isAdmin()) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <AlertTriangle size={64} className="mx-auto text-red-500 mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Brak dostępu</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Nie masz uprawnień do tej strony. Wymagana rola: Bibliotekarz.
          </p>
          <Button onClick={() => navigate("/")}>Wróć do strony głównej</Button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return <Loading fullScreen text="Ładowanie panelu..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Panel Bibliotekarza
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Witaj, {user?.full_name || user?.email}! Zarządzaj biblioteką z jednego miejsca.
          </p>
        </div>

        {/* Statystyki */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Książki */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <BookOpen size={24} className="text-blue-600 dark:text-blue-400" />
              </div>
              <TrendingUp className="text-green-500" size={20} />
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.totalBooks}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Książek w katalogu</div>
          </div>

          {/* Egzemplarze */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <Package size={24} className="text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.totalCopies}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Egzemplarzy łącznie</div>
            <div className="text-xs text-green-600 dark:text-green-400 mt-1">
              {stats.availableCopies} dostępnych
            </div>
          </div>

          {/* Aktywne wypożyczenia */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                <ArrowDownCircle size={24} className="text-green-600 dark:text-green-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.activeLoans}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Aktywnych wypożyczeń</div>
          </div>

          {/* Rezerwacje */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                <Calendar size={24} className="text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.activeReservations}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Aktywnych rezerwacji</div>
          </div>

          {/* Przetrzymane */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-red-100 dark:bg-red-900 rounded-lg">
                <AlertTriangle size={24} className="text-red-600 dark:text-red-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">
              {stats.overdueLoans}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Przetrzymanych książek</div>
          </div>

          {/* Użytkownicy */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-indigo-100 dark:bg-indigo-900 rounded-lg">
                <Users size={24} className="text-indigo-600 dark:text-indigo-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">456</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Zarejestrowanych użytkowników
            </div>
          </div>
        </div>

        {/* Szybkie akcje */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Szybkie akcje
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button
              variant="primary"
              onClick={() => navigate("/librarian/issue")}
              className="h-24 flex flex-col items-center justify-center gap-2"
            >
              <ArrowDownCircle size={24} />
              <span>Wypożycz książkę</span>
            </Button>

            <Button
              variant="outline"
              onClick={() => navigate("/librarian/return")}
              className="h-24 flex flex-col items-center justify-center gap-2"
            >
              <ArrowUpCircle size={24} />
              <span>Przyjmij zwrot</span>
            </Button>

            <Button
              variant="outline"
              onClick={() => navigate("/librarian/books")}
              className="h-24 flex flex-col items-center justify-center gap-2"
            >
              <BookOpen size={24} />
              <span>Zarządzaj książkami</span>
            </Button>

            <Button
              variant="outline"
              onClick={() => navigate("/librarian/users")}
              className="h-24 flex flex-col items-center justify-center gap-2"
            >
              <Users size={24} />
              <span>Zarządzaj użytkownikami</span>
            </Button>
          </div>
        </div>

        {/* Ostatnie aktywności (przykładowe) */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Ostatnie aktywności
          </h2>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <ArrowDownCircle className="text-green-500" size={20} />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Jan Kowalski wypożyczył "Pan Tadeusz"
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">5 minut temu</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <ArrowUpCircle className="text-blue-500" size={20} />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Anna Nowak zwróciła "Lalka"
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">15 minut temu</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Calendar className="text-yellow-500" size={20} />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Nowa rezerwacja: "Zbrodnia i kara"
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">30 minut temu</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LibrarianPanel;
