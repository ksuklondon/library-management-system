/**
 * Axios client z konfiguracją dla komunikacji z backendem.
 *
 * Zgodność z wymaganiami:
 * - NF4: JWT tokens (access + refresh)
 * - NF6: CORS handling
 * - NF12: Timeout < 2s dla responsywności
 * - F2a: Automatyczne odświeżanie tokenów
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";

/**
 * Bazowy URL dla API (z .env).
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const AUTH_SERVICE_URL = import.meta.env.VITE_AUTH_SERVICE_URL || "http://localhost:8001";

/**
 * Główny klient Axios dla wszystkich requestów.
 * Zawiera automatyczne dołączanie JWT tokenów i refresh logic.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000, // NF12: timeout 5s (bezpieczny margines)
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Klient Axios specjalnie dla auth-service.
 */
export const authClient: AxiosInstance = axios.create({
  baseURL: AUTH_SERVICE_URL,
  timeout: 5000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Pobierz access token z localStorage (NF4 - JWT).
 */
export const getAccessToken = (): string | null => {
  return localStorage.getItem("access_token");
};

/**
 * Pobierz refresh token z localStorage (F2a).
 */
export const getRefreshToken = (): string | null => {
  return localStorage.getItem("refresh_token");
};

/**
 * Zapisz tokeny do localStorage (NF4).
 */
export const setTokens = (accessToken: string, refreshToken: string): void => {
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
};

/**
 * Usuń tokeny z localStorage (F3 - logout).
 */
export const clearTokens = (): void => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
};

/**
 * Request interceptor - automatycznie dołącza JWT token do każdego requesta (NF4).
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();

    // Jeśli jest token, dodaj do headers
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - automatyczne odświeżanie tokenu gdy wygaśnie (F2a).
 */
apiClient.interceptors.response.use(
  (response) => {
    // Jeśli response OK, zwróć go normalnie
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Jeśli błąd 401 (unauthorized) i nie próbowaliśmy jeszcze odświeżyć tokenu
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = getRefreshToken();

      if (refreshToken) {
        try {
          // Spróbuj odświeżyć token (F2a)
          const response = await authClient.post("/api/auth/refresh", {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;

          // Zapisz nowy token
          localStorage.setItem("access_token", access_token);

          // Zaktualizuj header w oryginalnym requeście
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }

          // Wyślij ponownie oryginalny request z nowym tokenem
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Jeśli refresh nie działa, wyloguj użytkownika
          clearTokens();
          window.location.href = "/login";
          return Promise.reject(refreshError);
        }
      } else {
        // Brak refresh tokenu - przekieruj na login
        clearTokens();
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Helper do obsługi błędów API.
 * Wyciąga czytelny komunikat błędu z response.
 */
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    // Błąd z backendu
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }

    // Błąd timeout
    if (error.code === "ECONNABORTED") {
      return "Przekroczono limit czasu żądania. Spróbuj ponownie.";
    }

    // Błąd sieci
    if (error.message === "Network Error") {
      return "Błąd połączenia z serwerem. Sprawdź połączenie internetowe.";
    }

    return error.message;
  }

  return "Wystąpił nieoczekiwany błąd.";
};

/**
 * Export domyślny - główny klient API.
 */
export default apiClient;
