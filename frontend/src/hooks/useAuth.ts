/**
 * Custom hook useAuth - eksportowany z AuthContext dla wygody.
 *
 * Zgodność z wymaganiami:
 * - F2: Autentykacja użytkownika
 * - NF5: RBAC - sprawdzanie ról
 *
 * Ten plik re-exportuje useAuth z AuthContext,
 * ale też dodaje dodatkowe pomocnicze funkcje.
 */

import { useAuth as useAuthContext } from "../context/AuthContext";

/**
 * Re-export głównego hooka z contextu.
 * Można używać zarówno:
 * - import { useAuth } from '../context/AuthContext'
 * - import { useAuth } from '../hooks/useAuth'
 */
export { useAuth as default } from "../context/AuthContext";

/**
 * Hook useAuth z dodatkowymi helpers.
 * Zwraca wszystko z AuthContext + dodatkowe funkcje pomocnicze.
 */
export const useAuth = () => {
  const auth = useAuthContext();

  /**
   * Sprawdź czy użytkownik może wykonać akcję (F15, F16 - CRUD operations).
   * @param action - typ akcji do sprawdzenia
   */
  const canPerformAction = (action: "create" | "update" | "delete"): boolean => {
    if (!auth.user) return false;

    switch (action) {
      case "create":
      case "update":
        // LIBRARIAN i ADMIN mogą tworzyć i edytować
        return auth.isLibrarian() || auth.isAdmin();
      case "delete":
        // Tylko ADMIN może usuwać
        return auth.isAdmin();
      default:
        return false;
    }
  };

  /**
   * Sprawdź czy użytkownik może zarządzać użytkownikami (F19, F26).
   */
  const canManageUsers = (): boolean => {
    return auth.isLibrarian() || auth.isAdmin();
  };

  /**
   * Sprawdź czy użytkownik może zmienić role (F28).
   */
  const canChangeRoles = (): boolean => {
    return auth.isAdmin();
  };

  /**
   * Sprawdź czy użytkownik może zarządzać książkami (F15).
   */
  const canManageBooks = (): boolean => {
    return auth.isLibrarian() || auth.isAdmin();
  };

  /**
   * Sprawdź czy użytkownik może zarządzać egzemplarzami (F16).
   */
  const canManageCopies = (): boolean => {
    return auth.isLibrarian() || auth.isAdmin();
  };

  /**
   * Sprawdź czy użytkownik może wypożyczać książki (F11 - LIBRARIAN).
   */
  const canIssueLoan = (): boolean => {
    return auth.isLibrarian() || auth.isAdmin();
  };

  /**
   * Sprawdź czy użytkownik może zwracać książki (F12 - LIBRARIAN).
   */
  const canReturnLoan = (): boolean => {
    return auth.isLibrarian() || auth.isAdmin();
  };

  /**
   * Sprawdź czy użytkownik może rezerwować książki (F8 - READER+).
   */
  const canReserveBook = (): boolean => {
    return !!auth.user; // Każdy zalogowany użytkownik
  };

  /**
   * Sprawdź czy użytkownik może przeglądać audyt (NF19 - ADMIN).
   */
  const canViewAuditLogs = (): boolean => {
    return auth.isAdmin();
  };

  /**
   * Pobierz nazwę roli użytkownika po polsku.
   */
  const getRoleDisplayName = (): string => {
    if (!auth.user) return "Gość";

    switch (auth.user.role) {
      case "ADMIN":
        return "Administrator";
      case "LIBRARIAN":
        return "Bibliotekarz";
      case "READER":
        return "Czytelnik";
      default:
        return "Użytkownik";
    }
  };

  return {
    ...auth,
    // Dodatkowe helpery
    canPerformAction,
    canManageUsers,
    canChangeRoles,
    canManageBooks,
    canManageCopies,
    canIssueLoan,
    canReturnLoan,
    canReserveBook,
    canViewAuditLogs,
    getRoleDisplayName,
  };
};
