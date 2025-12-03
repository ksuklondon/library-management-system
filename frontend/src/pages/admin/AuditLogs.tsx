/**
 * Strona AuditLogs - przeglądanie logów audytu systemu.
 *
 * Zgodność z wymaganiami:
 * - NF19: Audyt działań (logi systemowe)
 * - NF5: RBAC - dostęp tylko dla ADMIN
 */

import { AlertCircle, Calendar, Download, FileText, Filter, User } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/Button";
import Input from "../../components/Input";
import Loading from "../../components/Loading";
import { useAuth } from "../../hooks/useAuth";
import { formatDateTime } from "../../utils/formatters";

/**
 * Interface dla logu audytu.
 */
interface AuditLog {
  id: string;
  timestamp: string;
  user_id: string;
  user_email: string;
  action: string;
  resource: string;
  resource_id?: string;
  details?: string;
  ip_address?: string;
  status: "SUCCESS" | "FAILURE";
}

/**
 * Komponent AuditLogs - przegląd logów audytu (NF19).
 */
const AuditLogs: React.FC = () => {
  const navigate = useNavigate();
  const { isAdmin } = useAuth();

  // Stan danych
  const [logs, setLogs] = useState<AuditLog[]>([]);

  // Stan UI
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filtry
  const [searchQuery, setSearchQuery] = useState("");
  const [actionFilter, setActionFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  /**
   * Załaduj logi przy montowaniu.
   */
  useEffect(() => {
    const initLoadLogs = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // W przyszłości: wywołanie API getAuditLogs()
        // Teraz: symulacja danych
        setTimeout(() => {
          setLogs([
            {
              id: "1",
              timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
              user_id: "user-123",
              user_email: "admin@example.com",
              action: "USER_ROLE_CHANGED",
              resource: "User",
              resource_id: "user-456",
              details: "Changed role from READER to LIBRARIAN",
              ip_address: "192.168.1.100",
              status: "SUCCESS",
            },
            {
              id: "2",
              timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
              user_id: "user-789",
              user_email: "librarian@example.com",
              action: "BOOK_ISSUED",
              resource: "Loan",
              resource_id: "loan-101",
              details: "Book issued to user-456",
              ip_address: "192.168.1.101",
              status: "SUCCESS",
            },
            {
              id: "3",
              timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
              user_id: "user-456",
              user_email: "reader@example.com",
              action: "LOGIN_FAILED",
              resource: "Auth",
              details: "Invalid password",
              ip_address: "192.168.1.102",
              status: "FAILURE",
            },
            {
              id: "4",
              timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
              user_id: "user-789",
              user_email: "librarian@example.com",
              action: "BOOK_ADDED",
              resource: "Book",
              resource_id: "book-999",
              details: 'Added new book: "The Great Gatsby"',
              ip_address: "192.168.1.101",
              status: "SUCCESS",
            },
            {
              id: "5",
              timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
              user_id: "user-123",
              user_email: "admin@example.com",
              action: "USER_BLOCKED",
              resource: "User",
              resource_id: "user-999",
              details: "Blocked user due to policy violation",
              ip_address: "192.168.1.100",
              status: "SUCCESS",
            },
          ]);
          setIsLoading(false);
        }, 500);
      } catch (err: unknown) {
        console.error("Error loading audit logs:", err);
        setError(err instanceof Error ? err.message : "Nie udało się załadować logów audytu");
        setIsLoading(false);
      }
    };

    initLoadLogs();
  }, []);

  /**
   * Sprawdź uprawnienia (NF5).
   */
  if (!isAdmin()) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <AlertCircle size={64} className="mx-auto text-red-500 mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Brak dostępu</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Nie masz uprawnień do przeglądania logów audytu. Wymagana rola: Administrator.
          </p>
          <Button onClick={() => navigate("/")}>Wróć do strony głównej</Button>
        </div>
      </div>
    );
  }

  /**
   * Zastosuj filtry.
   */
  const handleApplyFilters = () => {
    // W przyszłości: wywołaj API z parametrami filtrów
    console.log("Applying filters:", { searchQuery, actionFilter, statusFilter });
  };

  /**
   * Eksportuj logi do CSV.
   */
  const handleExport = () => {
    alert("Eksport logów do CSV będzie wkrótce dostępny!");
  };

  /**
   * Filtruj logi.
   */
  const filteredLogs = logs.filter((log) => {
    // Filtr wyszukiwania
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      if (
        !log.user_email.toLowerCase().includes(query) &&
        !log.action.toLowerCase().includes(query) &&
        !log.details?.toLowerCase().includes(query)
      ) {
        return false;
      }
    }

    // Filtr akcji
    if (actionFilter !== "all" && log.action !== actionFilter) {
      return false;
    }

    // Filtr statusu
    if (statusFilter !== "all" && log.status !== statusFilter) {
      return false;
    }

    return true;
  });

  /**
   * Kolor dla statusu.
   */
  const getStatusColor = (status: string) => {
    return status === "SUCCESS"
      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
  };

  /**
   * Kolor dla akcji.
   */
  const getActionColor = (action: string) => {
    if (action.includes("LOGIN")) return "text-blue-600 dark:text-blue-400";
    if (action.includes("ROLE")) return "text-purple-600 dark:text-purple-400";
    if (action.includes("BOOK")) return "text-green-600 dark:text-green-400";
    if (action.includes("BLOCK")) return "text-red-600 dark:text-red-400";
    return "text-gray-600 dark:text-gray-400";
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <Button variant="outline" onClick={() => navigate("/admin")} className="mb-4">
            ← Wróć do panelu
          </Button>

          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <FileText size={32} className="text-purple-600 dark:text-purple-400" />
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Logi audytu</h1>
              </div>
              <p className="text-gray-600 dark:text-gray-400">
                Przeglądaj historię działań w systemie (NF19)
              </p>
            </div>

            <Button variant="primary" onClick={handleExport} className="flex items-center gap-2">
              <Download size={18} />
              Eksportuj
            </Button>
          </div>
        </div>

        {/* Filtry */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex items-center gap-2 mb-4">
            <Filter size={20} className="text-gray-600 dark:text-gray-400" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Filtry</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Wyszukiwanie */}
            <Input
              label="Wyszukaj"
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Email, akcja, szczegóły..."
              fullWidth
            />

            {/* Filtr akcji */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Akcja
              </label>
              <select
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white bg-white dark:bg-gray-700"
              >
                <option value="all">Wszystkie</option>
                <option value="USER_ROLE_CHANGED">Zmiana roli</option>
                <option value="BOOK_ISSUED">Wypożyczenie</option>
                <option value="BOOK_RETURNED">Zwrot</option>
                <option value="LOGIN_FAILED">Błąd logowania</option>
                <option value="USER_BLOCKED">Blokada użytkownika</option>
              </select>
            </div>

            {/* Filtr statusu */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white bg-white dark:bg-gray-700"
              >
                <option value="all">Wszystkie</option>
                <option value="SUCCESS">Sukces</option>
                <option value="FAILURE">Błąd</option>
              </select>
            </div>

            {/* Przycisk zastosuj */}
            <div className="flex items-end">
              <Button variant="primary" onClick={handleApplyFilters} fullWidth>
                Zastosuj
              </Button>
            </div>
          </div>
        </div>

        {/* Statystyki */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{logs.length}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Wszystkich zdarzeń</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {logs.filter((l) => l.status === "SUCCESS").length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Udanych akcji</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {logs.filter((l) => l.status === "FAILURE").length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Błędów</div>
          </div>
        </div>

        {/* Loading state */}
        {isLoading && <Loading text="Ładowanie logów..." />}

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

        {/* Brak logów */}
        {!isLoading && !error && filteredLogs.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <FileText size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Brak logów spełniających kryteria
            </p>
          </div>
        )}

        {/* Lista logów (NF19) */}
        {!isLoading && !error && filteredLogs.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredLogs.map((log) => (
                <div key={log.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Timestamp i status */}
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
                          <Calendar size={14} />
                          {formatDateTime(log.timestamp)}
                        </span>
                        <span
                          className={`px-2 py-1 text-xs rounded-full ${getStatusColor(log.status)}`}
                        >
                          {log.status}
                        </span>
                      </div>

                      {/* Akcja */}
                      <div className="mb-2">
                        <span className={`font-semibold ${getActionColor(log.action)}`}>
                          {log.action}
                        </span>
                        <span className="text-gray-600 dark:text-gray-400 ml-2">
                          na {log.resource}
                          {log.resource_id && ` (${log.resource_id})`}
                        </span>
                      </div>

                      {/* Szczegóły */}
                      {log.details && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {log.details}
                        </p>
                      )}

                      {/* User i IP */}
                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-500">
                        <span className="flex items-center gap-1">
                          <User size={12} />
                          {log.user_email}
                        </span>
                        {log.ip_address && <span>IP: {log.ip_address}</span>}
                      </div>
                    </div>
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

export default AuditLogs;
