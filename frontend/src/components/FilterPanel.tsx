/**
 * Komponent FilterPanel - panel filtrowania książek w katalogu.
 *
 * Zgodność z wymaganiami:
 * - F6: Filtrowanie książek (autor, gatunek, język, wydawca)
 * - NF10: Responsywny design
 * - NF11: Intuicyjny interfejs użytkownika
 */

import { Filter } from "lucide-react";
import React, { useState } from "react";
import { CatalogFilter } from "../types/book";
import Button from "./Button";

/**
 * Props dla komponentu FilterPanel.
 */
interface FilterPanelProps {
  onFilterChange: (filters: CatalogFilter) => void;
  initialFilters?: CatalogFilter;
  showMobileToggle?: boolean;
}

/**
 * Komponent FilterPanel - panel filtrów dla katalogu (F6).
 *
 * @param onFilterChange - funkcja wywoływana przy zmianie filtrów
 * @param initialFilters - początkowe wartości filtrów
 * @param showMobileToggle - czy pokazać przycisk toggle na mobile
 */
const FilterPanel: React.FC<FilterPanelProps> = ({
  onFilterChange,
  initialFilters = {},
  showMobileToggle = true,
}) => {
  // Stan filtrów (F6)
  const [filters, setFilters] = useState<CatalogFilter>(initialFilters);
  const [isOpen, setIsOpen] = useState(false);

  /**
   * Aktualizuj pojedynczy filtr (F6).
   */
  const updateFilter = (key: keyof CatalogFilter, value: string | boolean) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
  };

  /**
   * Zastosuj filtry (F6).
   */
  const applyFilters = () => {
    // Usuń puste wartości
    const cleanedFilters: CatalogFilter = {};

    if (filters.authors?.trim()) {
      cleanedFilters.authors = filters.authors.trim();
    }
    if (filters.genre?.trim()) {
      cleanedFilters.genre = filters.genre.trim();
    }
    if (filters.language?.trim()) {
      cleanedFilters.language = filters.language.trim();
    }
    if (filters.publisher?.trim()) {
      cleanedFilters.publisher = filters.publisher.trim();
    }
    if (filters.available_only !== undefined) {
      cleanedFilters.available_only = filters.available_only;
    }

    onFilterChange(cleanedFilters);

    // Zamknij panel na mobile po zastosowaniu
    if (showMobileToggle) {
      setIsOpen(false);
    }
  };

  /**
   * Wyczyść wszystkie filtry (F6).
   */
  const clearFilters = () => {
    const emptyFilters: CatalogFilter = {
      available_only: false,
    };
    setFilters(emptyFilters);
    onFilterChange({});
  };

  /**
   * Sprawdź czy jakikolwiek filtr jest aktywny.
   */
  const hasActiveFilters =
    filters.authors?.trim() ||
    filters.genre?.trim() ||
    filters.language?.trim() ||
    filters.publisher?.trim() ||
    filters.available_only;

  return (
    <>
      {/* Przycisk toggle dla mobile (NF10) */}
      {showMobileToggle && (
        <div className="lg:hidden mb-4">
          <Button
            variant="outline"
            onClick={() => setIsOpen(!isOpen)}
            className="w-full flex items-center justify-center gap-2"
          >
            <Filter size={18} />
            {isOpen ? "Ukryj filtry" : "Pokaż filtry"}
            {hasActiveFilters && (
              <span className="ml-2 px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full">
                {Object.keys(filters).filter((k) => filters[k as keyof CatalogFilter]).length}
              </span>
            )}
          </Button>
        </div>
      )}

      {/* Panel filtrów */}
      <div
        className={`
          bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 space-y-4
          ${showMobileToggle ? "lg:block" : ""}
          ${showMobileToggle && !isOpen ? "hidden" : ""}
        `}
      >
        {/* Nagłówek */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Filter size={20} />
            Filtry
          </h3>
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              Wyczyść
            </button>
          )}
        </div>

        {/* Filtr: Autor (F6) */}
        <div>
          <label
            htmlFor="filter-author"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Autor
          </label>
          <input
            id="filter-author"
            type="text"
            value={filters.authors || ""}
            onChange={(e) => updateFilter("authors", e.target.value)}
            placeholder="Wpisz nazwisko autora"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Filtr: Gatunek (F6) */}
        <div>
          <label
            htmlFor="filter-genre"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Gatunek
          </label>
          <select
            id="filter-genre"
            value={filters.genre || ""}
            onChange={(e) => updateFilter("genre", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Wszystkie gatunki</option>
            <option value="Fiction">Beletrystyka</option>
            <option value="Non-Fiction">Literatura faktu</option>
            <option value="Science">Nauka</option>
            <option value="History">Historia</option>
            <option value="Biography">Biografia</option>
            <option value="Fantasy">Fantasy</option>
            <option value="Science Fiction">Science Fiction</option>
            <option value="Romance">Romans</option>
            <option value="Thriller">Thriller</option>
            <option value="Horror">Horror</option>
            <option value="Poetry">Poezja</option>
            <option value="Programming">Programowanie</option>
          </select>
        </div>

        {/* Filtr: Język (F6) */}
        <div>
          <label
            htmlFor="filter-language"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Język
          </label>
          <select
            id="filter-language"
            value={filters.language || ""}
            onChange={(e) => updateFilter("language", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Wszystkie języki</option>
            <option value="pl">Polski</option>
            <option value="en">Angielski</option>
            <option value="de">Niemiecki</option>
            <option value="fr">Francuski</option>
            <option value="es">Hiszpański</option>
            <option value="it">Włoski</option>
          </select>
        </div>

        {/* Filtr: Wydawca (F6) */}
        <div>
          <label
            htmlFor="filter-publisher"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Wydawca
          </label>
          <input
            id="filter-publisher"
            type="text"
            value={filters.publisher || ""}
            onChange={(e) => updateFilter("publisher", e.target.value)}
            placeholder="Wpisz nazwę wydawcy"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Filtr: Tylko dostępne (F6) */}
        <div className="flex items-center">
          <input
            id="filter-available"
            type="checkbox"
            checked={filters.available_only || false}
            onChange={(e) => updateFilter("available_only", e.target.checked)}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
          />
          <label
            htmlFor="filter-available"
            className="ml-2 text-sm text-gray-700 dark:text-gray-300"
          >
            Tylko dostępne książki
          </label>
        </div>

        {/* Przycisk zastosuj */}
        <Button variant="primary" fullWidth onClick={applyFilters}>
          Zastosuj filtry
        </Button>

        {/* Licznik aktywnych filtrów */}
        {hasActiveFilters && (
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Aktywne filtry:{" "}
            {Object.keys(filters).filter((k) => filters[k as keyof CatalogFilter]).length}
          </p>
        )}
      </div>
    </>
  );
};

export default FilterPanel;
