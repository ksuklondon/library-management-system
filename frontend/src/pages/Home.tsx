/**
 * Strona Home - strona główna aplikacji.
 *
 * Zgodność z wymaganiami:
 * - NF11: Intuicyjny interfejs użytkownika
 * - F4: Szybki dostęp do katalogu
 */

import { BookOpen, Calendar, Search, Shield, TrendingUp, Users } from "lucide-react";
import React from "react";
import { useNavigate } from "react-router-dom";
import Button from "../components/Button";
import { useAuth } from "../hooks/useAuth";

/**
 * Komponent Home - strona główna z powitaniem i szybkimi linkami.
 */
const Home: React.FC = () => {
  const { isAuthenticated, user, isAdmin, isLibrarian } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <BookOpen size={80} className="text-blue-600 dark:text-blue-400" />
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-4">
            System Biblioteczny
          </h1>

          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Nowoczesne zarządzanie biblioteką. Przeglądaj katalog, rezerwuj książki i zarządzaj
            wypożyczeniami online.
          </p>

          {/* Przyciski CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {!isAuthenticated ? (
              <>
                <Button variant="primary" size="large" onClick={() => navigate("/register")}>
                  Zarejestruj się
                </Button>
                <Button variant="outline" size="large" onClick={() => navigate("/login")}>
                  Zaloguj się
                </Button>
              </>
            ) : (
              <>
                <Button variant="primary" size="large" onClick={() => navigate("/catalog")}>
                  Przeglądaj katalog
                </Button>
                <Button variant="outline" size="large" onClick={() => navigate("/my-reservations")}>
                  Moje rezerwacje
                </Button>
              </>
            )}
          </div>

          {/* Powitanie zalogowanego użytkownika */}
          {isAuthenticated && user && (
            <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p className="text-blue-800 dark:text-blue-200">
                Witaj, <span className="font-semibold">{user.full_name || user.email}</span>!
                {isAdmin() && " (Administrator)"}
                {isLibrarian() && !isAdmin() && " (Bibliotekarz)"}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
          Główne funkcje
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Search size={24} className="text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Wyszukiwanie książek
              </h3>
            </div>
            <p className="text-gray-600 dark:text-gray-400">
              Zaawansowane wyszukiwanie po tytule, autorze, ISBN i gatunku. Łatwo znajdź
              interesujące Cię pozycje.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                <Calendar size={24} className="text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Rezerwacje online
              </h3>
            </div>
            <p className="text-gray-600 dark:text-gray-400">
              Zarezerwuj książki online i odbierz je w bibliotece. Zarządzaj swoimi rezerwacjami w
              jednym miejscu.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <TrendingUp size={24} className="text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Historia wypożyczeń
              </h3>
            </div>
            <p className="text-gray-600 dark:text-gray-400">
              Śledź swoje wypożyczenia, terminy zwrotu i historię przeczytanych książek.
            </p>
          </div>

          {/* Feature 4 - dla Librarian */}
          {isLibrarian() && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                  <Users size={24} className="text-yellow-600 dark:text-yellow-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Panel bibliotekarza
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400">
                Zarządzaj katalogiem, wypożyczeniami i użytkownikami. Pełna kontrola nad biblioteką.
              </p>
              <Button
                variant="outline"
                size="small"
                className="mt-4"
                onClick={() => navigate("/librarian")}
              >
                Przejdź do panelu
              </Button>
            </div>
          )}

          {/* Feature 5 - dla Admin */}
          {isAdmin() && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-red-100 dark:bg-red-900 rounded-lg">
                  <Shield size={24} className="text-red-600 dark:text-red-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Panel administratora
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400">
                Zarządzaj rolami użytkowników, przeglądaj logi audytu i konfiguruj system.
              </p>
              <Button
                variant="outline"
                size="small"
                className="mt-4"
                onClick={() => navigate("/admin")}
              >
                Przejdź do panelu
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-blue-600 dark:bg-blue-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center text-white">
            <div>
              <div className="text-4xl font-bold mb-2">10,000+</div>
              <div className="text-blue-100">Książek w katalogu</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">5,000+</div>
              <div className="text-blue-100">Zarejestrowanych użytkowników</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">24/7</div>
              <div className="text-blue-100">Dostępność online</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      {!isAuthenticated && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Gotowy na start?
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Dołącz do naszej społeczności czytelników już dziś!
          </p>
          <Button variant="primary" size="large" onClick={() => navigate("/register")}>
            Utwórz darmowe konto
          </Button>
        </div>
      )}
    </div>
  );
};

export default Home;
