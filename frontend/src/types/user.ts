/**
 * Typy danych dla użytkowników i autentykacji.
 *
 * Zgodność z wymaganiami:
 * - F1: Rejestracja użytkownika
 * - F2: Logowanie użytkownika
 * - F20: Edycja profilu użytkownika
 * - NF5: RBAC - role użytkowników
 */

/**
 * Enum z rolami użytkowników (NF5 - RBAC).
 */
export enum UserRole {
  ADMIN = "ADMIN",
  LIBRARIAN = "LIBRARIAN",
  READER = "READER",
}

/**
 * Interface reprezentujący użytkownika w systemie.
 * Zgodny z modelem User z backend/auth-service.
 */
export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  is_blocked: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Request do logowania (F2).
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Request do rejestracji (F1).
 */
export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

/**
 * Response z tokenami po zalogowaniu (F2, NF4 - JWT).
 */
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  email: string;
  role: UserRole;
}

/**
 * Request do odświeżenia tokenu (F2a - Refresh Token).
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * Request do aktualizacji profilu użytkownika (F20).
 */
export interface UserUpdateRequest {
  email?: string;
  full_name?: string;
  password?: string;
}
