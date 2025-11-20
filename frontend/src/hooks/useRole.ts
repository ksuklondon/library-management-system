/**
 * Custom hook useRole - pomocnicze funkcje do sprawdzania ról użytkownika.
 *
 * Zgodność z wymaganiami:
 * - NF5: RBAC - kontrola dostępu na podstawie ról
 * - Pomocnik dla komponentów sprawdzających uprawnienia
 */

import { UserRole } from "../types/user";
import { useAuth } from "./useAuth";

/**
 * Hook useRole - uproszczone sprawdzanie ról.
 *
 * @returns obiekt z funkcjami sprawdzającymi role
 *
 * @example
 * const { isAdmin, isLibrarian, hasAnyRole } = useRole();
 * if (isAdmin()) {
 *   // Pokaż opcje tylko dla admina
 * }
 */
export const useRole = () => {
  const { user, hasRole } = useAuth();

  /**
   * Sprawdź czy użytkownik ma jedną z podanych ról (NF5).
   */
  const hasAnyRole = (roles: UserRole[]): boolean => {
    return hasRole(roles);
  };

  /**
   * Sprawdź czy użytkownik ma WSZYSTKIE podane role.
   * (W naszym systemie użytkownik ma tylko jedną rolę, więc to zawsze false dla >1 roli)
   */
  const hasAllRoles = (roles: UserRole[]): boolean => {
    if (!user || roles.length === 0) return false;
    if (roles.length === 1) return hasRole(roles);
    // W systemie użytkownik ma tylko jedną rolę
    return false;
  };

  /**
   * Sprawdź czy użytkownik jest ADMIN.
   */
  const isAdmin = (): boolean => {
    return user?.role === UserRole.ADMIN;
  };

  /**
   * Sprawdź czy użytkownik jest LIBRARIAN (lub wyżej).
   */
  const isLibrarian = (): boolean => {
    return user?.role === UserRole.LIBRARIAN || user?.role === UserRole.ADMIN;
  };

  /**
   * Sprawdź czy użytkownik jest READER.
   */
  const isReader = (): boolean => {
    return user?.role === UserRole.READER;
  };

  /**
   * Pobierz nazwę roli po polsku.
   */
  const getRoleName = (role?: UserRole): string => {
    const roleToCheck = role || user?.role;

    switch (roleToCheck) {
      case UserRole.ADMIN:
        return "Administrator";
      case UserRole.LIBRARIAN:
        return "Bibliotekarz";
      case UserRole.READER:
        return "Czytelnik";
      default:
        return "Użytkownik";
    }
  };

  /**
   * Sprawdź czy użytkownik może wykonać akcję na zasobie.
   *
   * @param action - typ akcji (create, read, update, delete)
   * @param resource - typ zasobu (books, users, loans, etc.)
   */
  const canPerform = (
    action: "create" | "read" | "update" | "delete",
    resource: "books" | "users" | "loans" | "reservations"
  ): boolean => {
    if (!user) return false;

    // ADMIN może wszystko
    if (isAdmin()) return true;

    // LIBRARIAN
    if (isLibrarian()) {
      switch (resource) {
        case "books":
          // LIBRARIAN może tworzyć, czytać, edytować książki
          return action !== "delete";
        case "users":
          // LIBRARIAN może czytać i blokować użytkowników
          return action === "read" || action === "update";
        case "loans":
        case "reservations":
          // LIBRARIAN może wszystko z wypożyczeniami i rezerwacjami
          return true;
        default:
          return false;
      }
    }

    // READER
    if (isReader()) {
      switch (resource) {
        case "books":
          // READER może tylko czytać
          return action === "read";
        case "loans":
        case "reservations":
          // READER może czytać swoje wypożyczenia/rezerwacje
          return action === "read";
        case "users":
          // READER nie ma dostępu do zarządzania użytkownikami
          return false;
        default:
          return false;
      }
    }

    return false;
  };

  return {
    // Podstawowe sprawdzenia
    hasAnyRole,
    hasAllRoles,
    isAdmin,
    isLibrarian,
    isReader,

    // Pomocnicze
    getRoleName,
    canPerform,

    // Bezpośredni dostęp do user (z useAuth)
    currentRole: user?.role,
    user,
  };
};

/**
 * Export domyślny.
 */
export default useRole;
