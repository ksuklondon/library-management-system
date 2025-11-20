/**
 * Komponent SearchBar - pasek wyszukiwania książek.
 *
 * Zgodność z wymaganiami:
 * - F5: Wyszukiwanie książek
 * - NF10: Responsywny design
 * - NF11: Intuicyjny interfejs użytkownika
 */

import { Search, X } from "lucide-react";
import React, { FormEvent, useState } from "react";
import Button from "./Button";

/**
 * Typ pola wyszukiwania (F5).
 */
type SearchField = "all" | "title" | "authors" | "isbn";

/**
 * Props dla komponentu SearchBar.
 */
interface SearchBarProps {
  onSearch: (query: string, searchIn: SearchField) => void;
  placeholder?: string;
  isLoading?: boolean;
  initialQuery?: string;
  initialSearchIn?: SearchField;
  showSearchInSelector?: boolean;
}

/**
 * Komponent SearchBar - wyszukiwarka książek (F5).
 *
 * @param onSearch - funkcja wywołana po wyszukaniu
 * @param placeholder - tekst placeholder
 * @param isLoading - czy wyszukiwanie jest w trakcie
 * @param initialQuery - początkowe zapytanie
 * @param initialSearchIn - początkowe pole wyszukiwania
 * @param showSearchInSelector - czy pokazać selektor pola
 */
const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = "Szukaj książek...",
  isLoading = false,
  initialQuery = "",
  initialSearchIn = "all",
  showSearchInSelector = true,
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [searchIn, setSearchIn] = useState<SearchField>(initialSearchIn);

  /**
   * Obsługa wysłania formularza wyszukiwania (F5).
   */
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    // Wywołaj wyszukiwanie tylko jeśli jest jakieś zapytanie
    if (query.trim()) {
      onSearch(query.trim(), searchIn);
    }
  };

  /**
   * Wyczyść pole wyszukiwania.
   */
  const handleClear = () => {
    setQuery("");
    // Opcjonalnie: wywołaj wyszukiwanie z pustym query (pokaż wszystko)
    onSearch("", searchIn);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex flex-col sm:flex-row gap-2">
        {/* Pole wyszukiwania */}
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search size={20} className="text-gray-400 dark:text-gray-500" />
          </div>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            className="block w-full pl-10 pr-10 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 transition-colors"
            disabled={isLoading}
          />

          {/* Przycisk wyczyść */}
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              aria-label="Wyczyść wyszukiwanie"
            >
              <X size={20} />
            </button>
          )}
        </div>

        {/* Selektor pola wyszukiwania (F5) */}
        {showSearchInSelector && (
          <select
            value={searchIn}
            onChange={(e) => setSearchIn(e.target.value as SearchField)}
            className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            disabled={isLoading}
          >
            <option value="all">Wszystkie pola</option>
            <option value="title">Tytuł</option>
            <option value="authors">Autor</option>
            <option value="isbn">ISBN</option>
          </select>
        )}

        {/* Przycisk wyszukaj */}
        <Button
          type="submit"
          variant="primary"
          isLoading={isLoading}
          disabled={isLoading || !query.trim()}
          className="px-6"
        >
          Szukaj
        </Button>
      </div>

      {/* Informacja o wybranym polu wyszukiwania (mobile) */}
      {showSearchInSelector && searchIn !== "all" && (
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
          Wyszukiwanie w:{" "}
          <span className="font-medium">
            {searchIn === "title"
              ? "Tytułach"
              : searchIn === "authors"
              ? "Autorach"
              : searchIn === "isbn"
              ? "ISBN"
              : "Wszystkich polach"}
          </span>
        </p>
      )}
    </form>
  );
};

export default SearchBar;
