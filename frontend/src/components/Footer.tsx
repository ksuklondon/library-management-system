/**
 * Komponent Footer - stopka aplikacji.
 *
 * Zgodność z wymaganiami:
 * - NF11: Intuicyjny interfejs użytkownika
 * - Informacje o systemie, linki do dokumentacji
 */

import { BookOpen, Github, Heart, Mail } from "lucide-react";
import React from "react";
import { Link } from "react-router-dom";

/**
 * Komponent Footer - stopka ze linkami i informacjami.
 */
const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo i opis */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <BookOpen size={28} className="text-blue-600 dark:text-blue-400" />
              <span className="font-bold text-xl text-gray-900 dark:text-white">
                System Biblioteczny
              </span>
            </div>
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
              Nowoczesny system zarządzania biblioteką z rezerwacjami online, wypożyczeniami i
              katalogiem książek.
            </p>
            <p className="text-gray-500 dark:text-gray-500 text-xs">
              Wersja 1.0.0 | Zgodność z wymaganiami F1-F30, NF1-NF30
            </p>
          </div>

          {/* Szybkie linki */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
              Szybkie linki
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  to="/catalog"
                  className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm transition-colors"
                >
                  Katalog książek
                </Link>
              </li>
              <li>
                <Link
                  to="/my-reservations"
                  className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm transition-colors"
                >
                  Moje rezerwacje
                </Link>
              </li>
              <li>
                <Link
                  to="/my-loans"
                  className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm transition-colors"
                >
                  Moje wypożyczenia
                </Link>
              </li>
              <li>
                <Link
                  to="/profile"
                  className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm transition-colors"
                >
                  Mój profil
                </Link>
              </li>
            </ul>
          </div>

          {/* Pomoc i kontakt */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
              Pomoc
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="/docs"
                  className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm transition-colors flex items-center gap-2"
                >
                  <BookOpen size={16} />
                  Dokumentacja
                </a>
              </li>
              <li>
                <a
                  href="mailto:biblioteka@example.com"
                  className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm transition-colors flex items-center gap-2"
                >
                  <Mail size={16} />
                  Kontakt
                </a>
              </li>
              <li>
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm transition-colors flex items-center gap-2"
                >
                  <Github size={16} />
                  GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Separator */}
        <div className="border-t border-gray-200 dark:border-gray-800 mt-8 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            {/* Copyright */}
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              &copy; {currentYear} System Biblioteczny. Wszystkie prawa zastrzeżone.
            </p>

            {/* Made with love */}
            <p className="text-gray-500 dark:text-gray-400 text-sm flex items-center gap-2">
              Stworzone z <Heart size={16} className="text-red-500" fill="currentColor" /> przez
              zespół
            </p>

            {/* Polityka prywatności i regulamin */}
            <div className="flex space-x-4">
              <Link
                to="/privacy"
                className="text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm transition-colors"
              >
                Prywatność
              </Link>
              <Link
                to="/terms"
                className="text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm transition-colors"
              >
                Regulamin
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
