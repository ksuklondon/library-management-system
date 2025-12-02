/* eslint-disable react-refresh/only-export-components */
/**
 * ThemeContext - zarządzanie motywem (jasny/ciemny) w aplikacji.
 *
 * Zgodność z wymaganiami:
 * - NF10: Responsywny design - dostosowanie UI do preferencji użytkownika
 * - NF11: Intuicyjny interfejs - wybór jasnego/ciemnego motywu
 */

import React, { createContext, type ReactNode, useContext, useEffect, useState } from "react";

/**
 * Typ motywu - 'light' lub 'dark'.
 */
type Theme = "light" | "dark";

/**
 * Interface opisujący stan i metody ThemeContext.
 */
interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

/**
 * Domyślne wartości contextu.
 */
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

/**
 * Props dla ThemeProvider.
 */
interface ThemeProviderProps {
  children: ReactNode;
}

/**
 * ThemeProvider - komponent opakowujący aplikację i udostępniający context motywu.
 */
export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Pobierz zapisany motyw z localStorage lub użyj systemowego
  const [theme, setThemeState] = useState<Theme>(() => {
    // Sprawdź localStorage
    const savedTheme = localStorage.getItem("theme") as Theme | null;
    if (savedTheme) {
      return savedTheme;
    }

    // Sprawdź preferencje systemowe
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }

    // Domyślnie jasny motyw
    return "light";
  });

  /**
   * Zastosuj motyw do dokumentu.
   * Dodaje klasę 'dark' do <html> dla Tailwind CSS.
   */
  useEffect(() => {
    const root = window.document.documentElement;

    // Usuń poprzednią klasę
    root.classList.remove("light", "dark");

    // Dodaj nową klasę
    root.classList.add(theme);

    // Zapisz do localStorage
    localStorage.setItem("theme", theme);
  }, [theme]);

  /**
   * Nasłuchuj zmian preferencji systemowych (NF10).
   */
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleChange = (e: MediaQueryListEvent) => {
      // Zmień motyw tylko jeśli użytkownik nie ustawił ręcznie
      const savedTheme = localStorage.getItem("theme");
      if (!savedTheme) {
        setThemeState(e.matches ? "dark" : "light");
      }
    };

    // Dodaj listener (dla starszych przeglądarek użyj addListener)
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handleChange);
    } else {
      mediaQuery.addListener(handleChange);
    }

    // Cleanup
    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener("change", handleChange);
      } else {
        mediaQuery.removeListener(handleChange);
      }
    };
  }, []);

  /**
   * Przełącz motyw między jasnym a ciemnym (NF11).
   */
  const toggleTheme = () => {
    setThemeState((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
  };

  /**
   * Ustaw konkretny motyw.
   */
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  /**
   * Wartość contextu dostępna dla wszystkich komponentów.
   */
  const value: ThemeContextType = {
    theme,
    toggleTheme,
    setTheme,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

/**
 * Custom hook do używania ThemeContext.
 *
 * @example
 * const { theme, toggleTheme } = useTheme();
 */
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error("useTheme must be used within ThemeProvider");
  }

  return context;
};
