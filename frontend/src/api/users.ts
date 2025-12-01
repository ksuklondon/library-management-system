/**
 * API calls dla zarządzania użytkownikami (rozszerzenie auth.ts).
 *
 * Zgodność z wymaganiami:
 * - F19: Przeglądanie użytkowników (LIBRARIAN/ADMIN)
 * - F26: Blokowanie/Odblokowanie użytkowników (LIBRARIAN/ADMIN)
 * - F28: Zmiana roli użytkownika (ADMIN)
 * - NF19: Audyt zmian
 */

import type { User, UserRole } from "../types/user";
import { authClient, getErrorMessage } from "./client";

/**
 * Interface dla statystyk użytkowników (panel ADMIN/LIBRARIAN).
 */
export interface UserStats {
  total_users: number;
  active_users: number;
  blocked_users: number;
  readers: number;
  librarians: number;
  admins: number;
}

/**
 * Interface dla filtrowania użytkowników (F19).
 */
export interface UserFilterParams {
  role?: UserRole;
  is_active?: boolean;
  is_blocked?: boolean;
  search?: string; // Wyszukiwanie po email lub nazwisku
}

/**
 * Interface dla paginowanej listy użytkowników.
 */
export interface UsersListResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Pobranie statystyk użytkowników (panel ADMIN/LIBRARIAN).
 */
export const getUserStats = async (): Promise<UserStats> => {
  try {
    const response = await authClient.get<UserStats>("/api/users/stats");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie użytkowników z filtrowaniem i paginacją (F19).
 */
export const getUsersList = async (
  page = 1,
  pageSize = 20,
  filters?: UserFilterParams
): Promise<UsersListResponse> => {
  try {
    const response = await authClient.get<UsersListResponse>("/api/users/list", {
      params: {
        page,
        page_size: pageSize,
        ...filters,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Wyszukiwanie użytkowników po email lub nazwisku (F19).
 */
export const searchUsers = async (query: string): Promise<User[]> => {
  try {
    const response = await authClient.get<User[]>("/api/users/search", {
      params: { q: query },
    });
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie użytkowników o konkretnej roli (F19).
 */
export const getUsersByRole = async (role: UserRole): Promise<User[]> => {
  try {
    const response = await authClient.get<User[]>(`/api/users/role/${role}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie zablokowanych użytkowników (F26 - LIBRARIAN/ADMIN).
 */
export const getBlockedUsers = async (): Promise<User[]> => {
  try {
    const response = await authClient.get<User[]>("/api/users/blocked");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Interface dla historii zmian użytkownika (NF19 - audyt).
 */
export interface UserAuditLog {
  id: string;
  user_id: string;
  action: string;
  changed_by: string;
  changed_at: string;
  details?: Record<string, unknown>;
}

/**
 * Pobranie historii zmian użytkownika (NF19 - audyt, ADMIN only).
 */
export const getUserAuditLogs = async (userId: string): Promise<UserAuditLog[]> => {
  try {
    const response = await authClient.get<UserAuditLog[]>(`/api/users/${userId}/audit`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Interface dla bulk operations (operacje na wielu użytkownikach).
 */
export interface BulkUserOperation {
  user_ids: string[];
  action: "block" | "unblock" | "delete";
}

/**
 * Wykonanie operacji na wielu użytkownikach jednocześnie (ADMIN).
 */
export const bulkUserOperation = async (data: BulkUserOperation): Promise<void> => {
  try {
    await authClient.post("/api/users/bulk", data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Export funkcji z auth.ts dla wygody.
 * (aby można było importować wszystko z jednego pliku)
 */
export {
  blockUser,
  changeUserRole,
  createUser,
  deleteUser,
  getAllUsers,
  getUserById,
  unblockUser,
  updateUser,
} from "./auth";
