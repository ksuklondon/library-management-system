/**
 * Strona UserRoles - zarządzanie rolami użytkowników.
 *
 * Zgodność z wymaganiami:
 * - F28: Zmiana ról użytkowników (ADMIN)
 * - NF5: RBAC - dostęp tylko dla ADMIN
 */

import { AlertCircle, CheckCircle, Search, Shield, Users } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { changeUserRole, getAllUsers } from "../../api/users";
import Button from "../../components/Button";
import Input from "../../components/Input";
import Loading from "../../components/Loading";
import { useAuth } from "../../hooks/useAuth";
import type { User, UserRole } from "../../types/user";
import { formatDate } from "../../utils/formatters";

/**
 * Komponent UserRoles - zarządzanie rolami (F28).
 */
const UserRoles: React.FC = () => {
  const navigate = useNavigate();
  const { user: currentUser, isAdmin } = useAuth();

  // Stan danych
  const [users, setUsers] = useState<User[]>([]);

  // Stan UI
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [updatingUserId, setUpdatingUserId] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  /**
   * Załaduj użytkowników z API.
   */
  const loadUsers = async () => {
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
  };

  /**
   * Załaduj użytkowników przy montowaniu.
   */
  useEffect(() => {
    loadUsers();
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
            Nie masz uprawnień do zarządzania rolami. Wymagana rola: Administrator.
          </p>
          <Button onClick={() => navigate("/")}>Wróć do strony głównej</Button>
        </div>
      </div>
    );
  }

  /**
   * Zmień rolę użytkownika (F28).
   */
  const handleRoleChange = async (userId: string, newRole: UserRole) => {
    // Nie pozwól zmienić swojej własnej roli
    if (userId === currentUser?.id) {
      alert("Nie możesz zmienić swojej własnej roli!");
      return;
    }

    const confirmed = window.confirm(
      `Czy na pewno chcesz zmienić rolę tego użytkownika na ${newRole}?`
    );

    if (!confirmed) return;

    setUpdatingUserId(userId);
    setSuccessMessage(null);
    setError(null);

    try {
      await changeUserRole(userId, newRole);
      setSuccessMessage("Rola użytkownika została zmieniona pomyślnie!");

      // Odśwież listę użytkowników
      await loadUsers();

      // Ukryj komunikat po 3 sekundach
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      console.error("Error updating user role:", err);
      setError(err instanceof Error ? err.message : "Nie udało się zmienić roli użytkownika");
    } finally {
      setUpdatingUserId(null);
    }
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

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <Button variant="outline" onClick={() => navigate("/admin")} className="mb-4">
            ← Wróć do panelu
          </Button>

          <div className="flex items-center gap-3 mb-2">
            <Shield size={32} className="text-red-600 dark:text-red-400" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Zarządzanie rolami użytkowników
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Zmieniaj role użytkowników w systemie (F28)
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

        {/* Wyszukiwarka */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
          <div className="flex gap-2">
            <Input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Szukaj po emailu lub imieniu..."
              fullWidth
            />
            <Button variant="primary" className="flex items-center gap-2">
              <Search size={18} />
              Szukaj
            </Button>
          </div>
        </div>

        {/* Statystyki ról */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {users.filter((u) => u.role === "ADMIN").length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Administratorów</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {users.filter((u) => u.role === "LIBRARIAN").length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Bibliotekarzy</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {users.filter((u) => u.role === "READER").length}
            </div>
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

        {/* Lista użytkowników (F28) */}
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
                      Aktualna rola
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Data rejestracji
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Zmień rolę
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
                          {user.id === currentUser?.id && (
                            <span className="text-xs text-blue-600 dark:text-blue-400">
                              (To Ty)
                            </span>
                          )}
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          {(["ADMIN", "LIBRARIAN", "READER"] as UserRole[]).map((role) => (
                            <Button
                              key={role}
                              variant={user.role === role ? "primary" : "outline"}
                              size="small"
                              onClick={() => handleRoleChange(user.id, role)}
                              disabled={
                                updatingUserId !== null ||
                                user.role === role ||
                                user.id === currentUser?.id
                              }
                              isLoading={updatingUserId === user.id}
                            >
                              {role}
                            </Button>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Ostrzeżenie */}
        <div className="mt-6 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-yellow-400" />
            <div className="ml-3">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                <span className="font-semibold">Uwaga:</span> Zmiana roli użytkownika natychmiast
                wpływa na jego uprawnienia w systemie. Upewnij się, że rozumiesz konsekwencje przed
                dokonaniem zmiany.
              </p>
              <ul className="text-xs text-yellow-700 dark:text-yellow-300 mt-2 space-y-1 list-disc list-inside">
                <li>ADMIN - pełny dostęp do wszystkich funkcji systemu</li>
                <li>LIBRARIAN - zarządzanie katalogiem, wypożyczeniami i użytkownikami</li>
                <li>READER - podstawowy dostęp do przeglądania i rezerwacji</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserRoles;
