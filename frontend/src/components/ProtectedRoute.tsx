/**
 * Komponent ProtectedRoute - ochrona tras przed nieautoryzowanym dostępem.
 *
 * Zgodność z wymaganiami:
 * - NF5: RBAC - kontrola dostępu na podstawie ról
 * - F2: Autentykacja - przekierowanie na login jeśli niezalogowany
 */

import type { ReactNode } from "react";
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { UserRole } from "../types/user";
import Loading from "./Loading";

/**
 * Props dla komponentu ProtectedRoute.
 */
interface ProtectedRouteProps {
  children: ReactNode;
  roles?: UserRole[];
  requireAuth?: boolean;
}

/**
 * Komponent ProtectedRoute - chroni trasy przed nieautoryzowanym dostępem.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, roles, requireAuth = true }) => {
  const { isAuthenticated, isLoading, user, hasRole } = useAuth();
  const location = useLocation();

  // Czekaj na załadowanie stanu autentykacji
  if (isLoading) {
    return <Loading fullScreen text="Sprawdzanie uprawnień..." />;
  }

  // Jeśli wymaga autentykacji i użytkownik niezalogowany
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Jeśli określono role i użytkownik ich nie ma (NF5 - RBAC)
  if (roles && roles.length > 0 && !hasRole(roles)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            403 - Brak dostępu
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Nie masz uprawnień do przeglądania tej strony.
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500">
            Wymagana rola: {roles.join(" lub ")}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mb-8">
            Twoja rola: {user?.role || "brak"}
          </p>
          <button
            onClick={() => (window.location.href = "/")}
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Wróć do strony głównej
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
