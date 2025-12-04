/**
 * Strona ManageUsers - zarządzanie użytkownikami biblioteki.
 *
 * Zgodność z wymaganiami:
 * - F26: Zarządzanie użytkownikami (LIBRARIAN)
 * - NF5: RBAC - dostęp tylko dla LIBRARIAN i ADMIN
 */

import { AlertCircle, Search, Shield, Users } from "lucide-react";
import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getAllUsers } from "../../api/users";
import Button from "../../components/Button";
import Input from "../../components/Input";
import Loading from "../../components/Loading";
import { useAuth } from "../../hooks/useAuth";
import type { User } from "../../types/user";
import { formatDate } from "../../utils/formatters";

/**
 * Komponent ManageUsers - zarządzanie użytkownikami (F26).
 */
const ManageUsers: React.FC = () => {
  const navigate = useNavigate();
  const { isLibrarian, isAdmin } = useAuth();

  // Stan danych
  const [users, setUsers] = useState<User[]>([]);

  // Stan UI
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  /**
   * Załaduj użytkowników z API.
   */
  const loadUsers = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getAllUsers(0, 100);
      setUsers(Array.isArray(data) ? data : []);
    } catch (err: unknown) {
      console.error("Error loading users:", err);
      setError(err instanceof Error ? err.message : "Nie udało się załadować użytkowników");
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Załaduj użytkowników przy montowaniu.
   */
  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

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
            Nie masz uprawnień do zarządzania użytkownikami. Wymagana rola: Bibliotekarz.
          </p>
          <Button onClick={() => navigate("/")}>Wróć do strony głównej</Button>
        </div>
      </div>
    );
  }

  /**
   * Obsługa wyszukiwania.
   */
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Wyszukiwanie działa po stronie klienta
  };

  /**
   * Filtruj użytkowników według wyszukiwania.
   */
  const filteredUsers = searchQuery
    ? users.filter(
        (user) =>
          user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
          user.full_name?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : users;

  /**
   * Kolor dla roli.
   */
  const getRoleColor = (role: string) => {
    switch (role) {
      case "ADMIN":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "LIBRARIAN":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200";
      case "READER":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  /**
   * Etykieta roli po polsku.
   */
  const getRoleLabel = (role: string) => {
    switch (role) {
      case "ADMIN":
        return "Administrator";
      case "LIBRARIAN":
        return "Bibliotekarz";
      case "READER":
        return "Czytelnik";
      default:
        return role;
    }
  };

  // Statystyki
  const adminCount = users.filter((u) => u.role === "ADMIN").length;
  const librarianCount = users.filter((u) => u.role === "LIBRARIAN").length;
  const readerCount = users.filter((u) => u.role === "READER").length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <Button variant="outline" onClick={() => navigate("/librarian")} className="mb-4">
            ← Wróć do panelu
          </Button>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
                <Users size={32} />
                Zarządzanie użytkownikami
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Przeglądaj użytkowników systemu bibliotecznego
              </p>
            </div>

            {/* Przycisk do zarządzania rolami */}
            <Button
              variant="primary"
              onClick={() => navigate("/admin/user-roles")}
              className="flex items-center gap-2"
            >
              <Shield size={20} />
              Zarządzaj rolami
            </Button>
          </div>
        </div>

        {/* Wyszukiwarka */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
          <form onSubmit={handleSearch} className="flex gap-2">
            <Input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Szukaj po emailu lub imieniu..."
              fullWidth
            />
            <Button type="submit" variant="primary" className="flex items-center gap-2">
              <Search size={18} />
              Szukaj
            </Button>
          </form>
        </div>

        {/* Statystyki */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{users.length}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Wszystkich użytkowników</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">{adminCount}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Administratorów</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {librarianCount}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Bibliotekarzy</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{readerCount}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Czytelników</div>
          </div>
        </div>

        {/* Loading state */}
        {isLoading && <Loading text="Ładowanie użytkowników..." />}

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

        {/* Brak użytkowników */}
        {!isLoading && !error && filteredUsers.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <Users size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg">Nie znaleziono użytkowników</p>
          </div>
        )}

        {/* Lista użytkowników */}
        {!isLoading && !error && filteredUsers.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Użytkownik
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Rola
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Data rejestracji
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      ID
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {user.full_name || "Brak imienia"}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {user.email}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleColor(
                            user.role
                          )}`}
                        >
                          {getRoleLabel(user.role)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {formatDate(user.created_at, "dd.MM.yyyy")}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {user.id.substring(0, 8)}...
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Informacja */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-blue-400" />
            <div className="ml-3">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <span className="font-semibold">Wskazówka:</span> Aby zmienić rolę użytkownika,
                przejdź do panelu{" "}
                <button
                  onClick={() => navigate("/admin/user-roles")}
                  className="underline font-medium hover:text-blue-600"
                >
                  Zarządzanie rolami
                </button>
                .
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManageUsers;
