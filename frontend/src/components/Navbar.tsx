/**
 * Komponent Navbar - górne menu nawigacyjne aplikacji.
 *
 * Zgodność z wymaganiami:
 * - F3: Wylogowanie użytkownika
 * - NF5: RBAC - różne menu dla różnych ról
 * - NF10: Responsywny design (mobile menu)
 * - NF11: Intuicyjny interfejs użytkownika
 */

import { BookOpen, Library, LogOut, Menu, Moon, Settings, Sun, User, X } from "lucide-react";
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTheme } from "../context/ThemeContext";
import { useAuth } from "../hooks/useAuth";
import Button from "./Button";

/**
 * Komponent Navbar - responsywne menu nawigacyjne.
 */
const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout, isAdmin, isLibrarian } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  /**
   * Obsługa wylogowania (F3).
   */
  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  /**
   * Przełącz mobilne menu (NF10 - responsywność).
   */
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  /**
   * Zamknij mobilne menu po kliknięciu w link.
   */
  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-lg sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo i nazwa */}
          <div className="flex items-center">
            <Link
              to="/"
              className="flex items-center space-x-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
            >
              <BookOpen size={32} />
              <span className="font-bold text-xl hidden sm:inline">Biblioteka</span>
            </Link>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex md:items-center md:space-x-4">
            {/* Link do katalogu (F4) - publiczny */}
            <Link
              to="/catalog"
              className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Katalog
            </Link>

            {/* Zalogowany użytkownik */}
            {isAuthenticated && user && (
              <>
                {/* Moje rezerwacje (F9 - READER+) */}
                <Link
                  to="/my-reservations"
                  className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Rezerwacje
                </Link>

                {/* Moje wypożyczenia (F13 - READER+) */}
                <Link
                  to="/my-loans"
                  className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Wypożyczenia
                </Link>

                {/* Panel bibliotekarza (F15, F16 - LIBRARIAN+) */}
                {isLibrarian() && (
                  <Link
                    to="/librarian"
                    className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1"
                  >
                    <Library size={18} />
                    Panel
                  </Link>
                )}

                {/* Panel admina (F28, NF19 - ADMIN only) */}
                {isAdmin() && (
                  <Link
                    to="/admin"
                    className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1"
                  >
                    <Settings size={18} />
                    Admin
                  </Link>
                )}

                {/* Przycisk dark mode (NF11) */}
                <button
                  onClick={toggleTheme}
                  className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 p-2 rounded-md transition-colors"
                  aria-label="Toggle theme"
                >
                  {theme === "light" ? <Moon size={20} /> : <Sun size={20} />}
                </button>

                {/* Profil użytkownika (F20) */}
                <Link
                  to="/profile"
                  className="flex items-center space-x-2 text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  <User size={20} />
                  <span className="hidden lg:inline">{user.email}</span>
                </Link>

                {/* Wylogowanie (F3) */}
                <Button
                  variant="outline"
                  size="small"
                  onClick={handleLogout}
                  className="flex items-center gap-2"
                >
                  <LogOut size={18} />
                  Wyloguj
                </Button>
              </>
            )}

            {/* Niezalogowany użytkownik */}
            {!isAuthenticated && (
              <>
                <Button variant="outline" size="small" onClick={() => navigate("/login")}>
                  Zaloguj się
                </Button>
                <Button variant="primary" size="small" onClick={() => navigate("/register")}>
                  Zarejestruj się
                </Button>
              </>
            )}
          </div>

          {/* Mobile menu button (NF10 - responsywność) */}
          <div className="md:hidden flex items-center">
            <button
              onClick={toggleMobileMenu}
              className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 p-2"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu (NF10 - responsywność) */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <Link
              to="/catalog"
              onClick={closeMobileMenu}
              className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Katalog
            </Link>

            {isAuthenticated && user && (
              <>
                <Link
                  to="/my-reservations"
                  onClick={closeMobileMenu}
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Rezerwacje
                </Link>
                <Link
                  to="/my-loans"
                  onClick={closeMobileMenu}
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Wypożyczenia
                </Link>
                {isLibrarian() && (
                  <Link
                    to="/librarian"
                    onClick={closeMobileMenu}
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Panel Bibliotekarza
                  </Link>
                )}
                {isAdmin() && (
                  <Link
                    to="/admin"
                    onClick={closeMobileMenu}
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Panel Admina
                  </Link>
                )}
                <Link
                  to="/profile"
                  onClick={closeMobileMenu}
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Profil
                </Link>
                <button
                  onClick={toggleTheme}
                  className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  {theme === "light" ? "Tryb ciemny" : "Tryb jasny"}
                </button>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Wyloguj się
                </button>
              </>
            )}

            {!isAuthenticated && (
              <>
                <Link
                  to="/login"
                  onClick={closeMobileMenu}
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Zaloguj się
                </Link>
                <Link
                  to="/register"
                  onClick={closeMobileMenu}
                  className="block px-3 py-2 rounded-md text-base font-medium text-blue-600 dark:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Zarejestruj się
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
