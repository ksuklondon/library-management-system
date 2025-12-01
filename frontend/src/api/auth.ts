/**
 * API calls dla autentykacji i zarządzania użytkownikami.
 *
 * Zgodność z wymaganiami:
 * - F1: Rejestracja użytkownika
 * - F2: Logowanie użytkownika
 * - F2a: Refresh token
 * - F3: Wylogowanie
 * - F20: Edycja profilu
 * - F19: Przeglądanie użytkowników (LIBRARIAN/ADMIN)
 * - F26: Blokowanie użytkowników (LIBRARIAN/ADMIN)
 * - F28: Zmiana roli użytkownika (ADMIN)
 */

import type {
  LoginRequest,
  LoginResponse,
  RefreshTokenRequest,
  RegisterRequest,
  User,
  UserRole,
  UserUpdateRequest,
} from "../types/user";
import { authClient, clearTokens, getErrorMessage, setTokens } from "./client";

/**
 * Rejestracja nowego użytkownika (F1).
 */
export const register = async (data: RegisterRequest): Promise<User> => {
  try {
    const response = await authClient.post<User>("/api/auth/register", data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Logowanie użytkownika (F2).
 * Zapisuje tokeny do localStorage.
 */
export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  try {
    const response = await authClient.post<LoginResponse>("/api/auth/login", data);

    // Zapisz tokeny (NF4 - JWT)
    const { access_token, refresh_token } = response.data;
    setTokens(access_token, refresh_token);

    // Zapisz podstawowe dane użytkownika do localStorage
    const userData = {
      email: response.data.email,
      role: response.data.role,
    };
    localStorage.setItem("user", JSON.stringify(userData));

    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Odświeżenie tokenu dostępu (F2a - Refresh Token).
 */
export const refreshToken = async (data: RefreshTokenRequest): Promise<string> => {
  try {
    const response = await authClient.post<{ access_token: string; token_type: string }>(
      "/api/auth/refresh",
      data
    );

    // Zapisz nowy access token
    localStorage.setItem("access_token", response.data.access_token);

    return response.data.access_token;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Wylogowanie użytkownika (F3).
 * Usuwa tokeny z localStorage.
 */
export const logout = async (): Promise<void> => {
  try {
    await authClient.post("/api/auth/logout");
  } catch (error) {
    // Ignoruj błędy - i tak czyścimy localStorage
    console.error("Logout error:", error);
  } finally {
    // Zawsze wyczyść tokeny lokalnie
    clearTokens();
  }
};

/**
 * Pobranie danych zalogowanego użytkownika (F2).
 */
export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await authClient.get<User>("/api/auth/me");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie wszystkich użytkowników (F19 - LIBRARIAN/ADMIN).
 */
export const getAllUsers = async (skip = 0, limit = 50): Promise<User[]> => {
  try {
    const response = await authClient.get<User[]>("/api/users/", {
      params: { skip, limit },
    });
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie użytkownika po ID (F19 - LIBRARIAN/ADMIN).
 */
export const getUserById = async (userId: string): Promise<User> => {
  try {
    const response = await authClient.get<User>(`/api/users/${userId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Utworzenie nowego użytkownika (ADMIN).
 */
export const createUser = async (data: RegisterRequest): Promise<User> => {
  try {
    const response = await authClient.post<User>("/api/users/", data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Aktualizacja profilu użytkownika (F20).
 * Użytkownik może edytować swój własny profil.
 */
export const updateUser = async (userId: string, data: UserUpdateRequest): Promise<User> => {
  try {
    const response = await authClient.put<User>(`/api/users/${userId}`, data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Usunięcie użytkownika (ADMIN only).
 */
export const deleteUser = async (userId: string): Promise<void> => {
  try {
    await authClient.delete(`/api/users/${userId}`);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Zablokowanie użytkownika (F26 - LIBRARIAN/ADMIN).
 */
export const blockUser = async (userId: string): Promise<User> => {
  try {
    const response = await authClient.post<User>(`/api/users/${userId}/block`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Odblokowanie użytkownika (F26 - LIBRARIAN/ADMIN).
 */
export const unblockUser = async (userId: string): Promise<User> => {
  try {
    const response = await authClient.post<User>(`/api/users/${userId}/unblock`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Zmiana roli użytkownika (F28 - ADMIN only).
 */
export const changeUserRole = async (userId: string, newRole: UserRole): Promise<User> => {
  try {
    const response = await authClient.patch<User>(`/api/users/${userId}/role`, {
      role: newRole,
    });
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};
