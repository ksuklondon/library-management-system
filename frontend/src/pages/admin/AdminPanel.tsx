/**
 * Strona AdminPanel - panel główny administratora.
 *
 * Zgodność z wymaganiami:
 * - NF5: RBAC - dostęp tylko dla ADMIN
 * - Dashboard z zaawansowanymi funkcjami administracyjnymi
 */

import {
  Activity,
  AlertTriangle,
  BookOpen,
  Database,
  FileText,
  Settings,
  Shield,
  TrendingUp,
  Users,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/Button";
import Loading from "../../components/Loading";
import { useAuth } from "../../hooks/useAuth";

/**
 * Komponent AdminPanel - dashboard administratora (NF5).
 */
const AdminPanel: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAdmin } = useAuth();

  // Stan danych statystycznych
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalBooks: 0,
    totalLoans: 0,
    totalReservations: 0,
    systemHealth: "healthy",
    databaseSize: 0,
    apiCalls: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Sprawdź uprawnienia (NF5).
   */
  if (!isAdmin()) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <AlertTriangle size={64} className="mx-auto text-red-500 mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Brak dostępu</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Nie masz uprawnień do panelu administratora. Wymagana rola: Administrator.
          </p>
          <Button onClick={() => navigate("/")}>Wróć do strony głównej</Button>
        </div>
      </div>
    );
  }

  /**
   * Załaduj statystyki systemowe.
   */
  useEffect(() => {
    const loadStats = async () => {
      setIsLoading(true);

      // Symulacja ładowania danych
      setTimeout(() => {
        setStats({
          totalUsers: 456,
          totalBooks: 1247,
          totalLoans: 234,
          totalReservations: 67,
          systemHealth: "healthy",
          databaseSize: 2.3, // GB
          apiCalls: 15234,
        });
        setIsLoading(false);
      }, 500);
    };

    loadStats();
  }, []);

  if (isLoading) {
    return <Loading fullScreen text="Ładowanie panelu..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Shield size={32} className="text-red-600 dark:text-red-400" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Panel Administratora
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Witaj, {user?.full_name || user?.email}! Zarządzaj systemem bibliotecznym.
          </p>
        </div>

        {/* Status systemu */}
        <div className="mb-8 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg shadow-md p-6 border border-green-200 dark:border-green-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity size={32} className="text-green-600 dark:text-green-400" />
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Status systemu
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Wszystkie usługi działają prawidłowo
                </p>
              </div>
            </div>
            <div className="px-4 py-2 bg-green-500 text-white rounded-full text-sm font-semibold">
              ✓ Operational
            </div>
          </div>
        </div>

        {/* Statystyki główne */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Użytkownicy */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Users size={24} className="text-blue-600 dark:text-blue-400" />
              </div>
              <TrendingUp className="text-green-500" size={20} />
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.totalUsers}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Użytkowników w systemie</div>
          </div>

          {/* Książki */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <BookOpen size={24} className="text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.totalBooks}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Książek w katalogu</div>
          </div>

          {/* Baza danych */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                <Database size={24} className="text-green-600 dark:text-green-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.databaseSize} GB
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Rozmiar bazy danych</div>
          </div>

          {/* API Calls */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-orange-100 dark:bg-orange-900 rounded-lg">
                <Activity size={24} className="text-orange-600 dark:text-orange-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.apiCalls.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Wywołań API (dziś)</div>
          </div>
        </div>

        {/* Szybkie akcje administratora */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Funkcje administratora
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Button
              variant="outline"
              onClick={() => navigate("/admin/user-roles")}
              className="h-24 flex flex-col items-center justify-center gap-2 hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20"
            >
              <Users size={24} />
              <span>Zarządzanie rolami</span>
            </Button>

            <Button
              variant="outline"
              onClick={() => navigate("/admin/audit-logs")}
              className="h-24 flex flex-col items-center justify-center gap-2 hover:border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20"
            >
              <FileText size={24} />
              <span>Logi audytu</span>
            </Button>

            <Button
              variant="outline"
              onClick={() => alert("Ustawienia systemowe będą wkrótce dostępne!")}
              className="h-24 flex flex-col items-center justify-center gap-2 hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20"
            >
              <Settings size={24} />
              <span>Ustawienia systemu</span>
            </Button>

            <Button
              variant="outline"
              onClick={() => alert("Backup bazy danych będzie wkrótce dostępny!")}
              className="h-24 flex flex-col items-center justify-center gap-2 hover:border-yellow-500 hover:bg-yellow-50 dark:hover:bg-yellow-900/20"
            >
              <Database size={24} />
              <span>Backup bazy danych</span>
            </Button>

            <Button
              variant="outline"
              onClick={() => alert("Raporty systemowe będą wkrótce dostępne!")}
              className="h-24 flex flex-col items-center justify-center gap-2 hover:border-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
            >
              <TrendingUp size={24} />
              <span>Raporty i statystyki</span>
            </Button>

            <Button
              variant="outline"
              onClick={() => alert("Monitoring systemu będzie wkrótce dostępny!")}
              className="h-24 flex flex-col items-center justify-center gap-2 hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
            >
              <Activity size={24} />
              <span>Monitoring systemu</span>
            </Button>
          </div>
        </div>

        {/* Ostatnie aktywności systemowe */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Ostatnie zdarzenia systemowe
          </h2>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Users className="text-blue-500" size={20} />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Nowy użytkownik zarejestrowany
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">2 minuty temu</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <BookOpen className="text-green-500" size={20} />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Dodano nową książkę do katalogu
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">15 minut temu</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Shield className="text-purple-500" size={20} />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Zmieniono rolę użytkownika
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">1 godzinę temu</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Database className="text-orange-500" size={20} />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Automatyczny backup bazy danych ukończony
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">3 godziny temu</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
