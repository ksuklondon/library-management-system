/**
 * AuthContext - zarządzanie stanem autentykacji w całej aplikacji.
 *
 * Zgodność z wymaganiami:
 * - F2: Logowanie użytkownika
 * - F3: Wylogowanie
 * - NF4: JWT tokens
 * - NF5: RBAC - sprawdzanie ról
 *
 * Używa React Context API do udostępniania stanu autentykacji
 * wszystkim komponentom bez prop drilling.
 */

import React, { createContext, ReactNode, useContext, useEffect, useState } from "react";
import {
  getCurrentUser,
  login as loginApi,
  logout as logoutApi,
  register as registerApi,
} from "../api/auth";
import { getAccessToken } from "../api/client";
import { LoginRequest, RegisterRequest, User, UserRole } from "../types/user";

/**
 * Interface opisujący stan i metody AuthContext.
 */
interface AuthContextType {
  // Stan
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Metody
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;

  // Pomocnicze sprawdzanie ról (NF5 - RBAC)
  hasRole: (roles: UserRole[]) => boolean;
  isAdmin: () => boolean;
  isLibrarian: () => boolean;
  isReader: () => boolean;
}

/**
 * Domyślne wartości contextu.
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Props dla AuthProvider.
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider - komponent opakowujący aplikację i udostępniający context.
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  /**
   * Przy montowaniu komponentu, sprawdź czy użytkownik jest zalogowany.
   * Jeśli jest token w localStorage, pobierz dane użytkownika.
   */
  useEffect(() => {
    const initAuth = async () => {
      const token = getAccessToken();

      if (token) {
        try {
          // Pobierz dane zalogowanego użytkownika (F2)
          const userData = await getCurrentUser();
          setUser(userData);
        } catch (error) {
          // Token nieprawidłowy lub wygasł - wyczyść localStorage
          console.error("Failed to fetch user:", error);
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          localStorage.removeItem("user");
          setUser(null);
        }
      }

      setIsLoading(false);
    };

    initAuth();
  }, []);

  /**
   * Logowanie użytkownika (F2).
   */
  const login = async (credentials: LoginRequest): Promise<void> => {
    try {
      setIsLoading(true);

      // Wywołaj API logowania (zapisuje tokeny do localStorage)
      const response = await loginApi(credentials);

      // Pobierz pełne dane użytkownika
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Rejestracja nowego użytkownika (F1).
   */
  const register = async (data: RegisterRequest): Promise<void> => {
    try {
      setIsLoading(true);

      // Zarejestruj użytkownika
      await registerApi(data);

      // Po rejestracji automatycznie zaloguj
      await login({
        email: data.email,
        password: data.password,
      });
    } catch (error) {
      console.error("Registration failed:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Wylogowanie użytkownika (F3).
   */
  const logout = async (): Promise<void> => {
    try {
      setIsLoading(true);

      // Wywołaj API wylogowania (czyści tokeny)
      await logoutApi();

      // Wyczyść lokalny stan
      setUser(null);
    } catch (error) {
      console.error("Logout failed:", error);
      // Nawet jeśli API zwróci błąd, wyloguj lokalnie
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Odświeżenie danych użytkownika z serwera.
   * Przydatne po edycji profilu (F20).
   */
  const refreshUser = async (): Promise<void> => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error("Failed to refresh user:", error);
      throw error;
    }
  };

  /**
   * Sprawdzenie czy użytkownik ma jedną z podanych ról (NF5 - RBAC).
   */
  const hasRole = (roles: UserRole[]): boolean => {
    if (!user) return false;
    return roles.includes(user.role);
  };

  /**
   * Sprawdzenie czy użytkownik jest ADMIN.
   */
  const isAdmin = (): boolean => {
    return user?.role === UserRole.ADMIN;
  };

  /**
   * Sprawdzenie czy użytkownik jest LIBRARIAN.
   */
  const isLibrarian = (): boolean => {
    return user?.role === UserRole.LIBRARIAN || user?.role === UserRole.ADMIN;
  };

  /**
   * Sprawdzenie czy użytkownik jest READER.
   */
  const isReader = (): boolean => {
    return user?.role === UserRole.READER;
  };

  /**
   * Wartość contextu dostępna dla wszystkich komponentów.
   */
  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
    hasRole,
    isAdmin,
    isLibrarian,
    isReader,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Custom hook do używania AuthContext.
 * Używaj tego hooka w komponentach zamiast useContext(AuthContext).
 *
 * @example
 * const { user, login, logout, isAdmin } = useAuth();
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
};

/**
 * Export domyślny - AuthContext (dla zaawansowanych przypadków).
 */
export default AuthContext;
