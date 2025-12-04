/**
 * Validators - funkcje walidacji danych wejściowych.
 *
 * Zgodność z wymaganiami:
 * - NF7: Walidacja danych wejściowych
 * - Sprawdzanie poprawności email, hasła, ISBN, etc.
 */

/**
 * Waliduj adres email (NF7).
 *
 * @param email - adres email do walidacji
 * @returns true jeśli email prawidłowy, false w przeciwnym razie
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Waliduj hasło (NF7).
 * Wymagania:
 * - Minimum 8 znaków
 * - Przynajmniej jedna wielka litera
 * - Przynajmniej jedna mała litera
 * - Przynajmniej jedna cyfra
 *
 * @param password - hasło do walidacji
 * @returns obiekt z wynikiem walidacji i komunikatem błędu
 */
export const validatePassword = (
  password: string
): {
  isValid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push("Hasło musi mieć minimum 8 znaków");
  }

  if (!/[A-Z]/.test(password)) {
    errors.push("Hasło musi zawierać przynajmniej jedną wielką literę");
  }

  if (!/[a-z]/.test(password)) {
    errors.push("Hasło musi zawierać przynajmniej jedną małą literę");
  }

  if (!/[0-9]/.test(password)) {
    errors.push("Hasło musi zawierać przynajmniej jedną cyfrę");
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Waliduj siłę hasła (NF7).
 *
 * @param password - hasło do oceny
 * @returns ocena siły hasła (weak, medium, strong)
 */
export const getPasswordStrength = (password: string): "weak" | "medium" | "strong" => {
  let strength = 0;

  // Długość
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;

  // Wielkie litery
  if (/[A-Z]/.test(password)) strength++;

  // Małe litery
  if (/[a-z]/.test(password)) strength++;

  // Cyfry
  if (/[0-9]/.test(password)) strength++;

  // Znaki specjalne
  if (/[^A-Za-z0-9]/.test(password)) strength++;

  if (strength <= 2) return "weak";
  if (strength <= 4) return "medium";
  return "strong";
};

/**
 * Waliduj ISBN (NF7).
 * Obsługuje ISBN-10 i ISBN-13.
 *
 * @param isbn - numer ISBN do walidacji
 * @returns true jeśli ISBN prawidłowy, false w przeciwnym razie
 */
export const isValidISBN = (isbn: string): boolean => {
  // Usuń myślniki i spacje
  const cleaned = isbn.replace(/[-\s]/g, "");

  // ISBN-10
  if (cleaned.length === 10) {
    return /^\d{9}[\dX]$/.test(cleaned);
  }

  // ISBN-13
  if (cleaned.length === 13) {
    return /^\d{13}$/.test(cleaned);
  }

  return false;
};

/**
 * Waliduj numer telefonu polskiego (NF7).
 *
 * @param phone - numer telefonu
 * @returns true jeśli numer prawidłowy, false w przeciwnym razie
 */
export const isValidPhoneNumber = (phone: string): boolean => {
  // Usuń spacje, myślniki, nawiasy
  const cleaned = phone.replace(/[\s\-()]/g, "");

  // Polski numer: 9 cyfr lub +48 i 9 cyfr
  return /^(\+48)?[0-9]{9}$/.test(cleaned);
};

/**
 * Waliduj datę (czy nie jest w przeszłości).
 *
 * @param date - data do sprawdzenia
 * @returns true jeśli data w przyszłości lub dzisiaj, false jeśli w przeszłości
 */
export const isFutureDate = (date: Date | string): boolean => {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return dateObj >= today;
};

/**
 * Waliduj datę (czy nie jest w przyszłości).
 *
 * @param date - data do sprawdzenia
 * @returns true jeśli data w przeszłości lub dzisiaj, false jeśli w przyszłości
 */
export const isPastDate = (date: Date | string): boolean => {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  const today = new Date();
  today.setHours(23, 59, 59, 999);

  return dateObj <= today;
};

/**
 * Waliduj zakres dat (czy data końcowa jest po dacie początkowej).
 *
 * @param startDate - data początkowa
 * @param endDate - data końcowa
 * @returns true jeśli zakres prawidłowy, false w przeciwnym razie
 */
export const isValidDateRange = (startDate: Date | string, endDate: Date | string): boolean => {
  const start = typeof startDate === "string" ? new Date(startDate) : startDate;
  const end = typeof endDate === "string" ? new Date(endDate) : endDate;

  return start <= end;
};

/**
 * Waliduj długość tekstu (NF7).
 *
 * @param text - tekst do walidacji
 * @param minLength - minimalna długość
 * @param maxLength - maksymalna długość
 * @returns true jeśli długość prawidłowa, false w przeciwnym razie
 */
export const isValidLength = (text: string, minLength: number, maxLength: number): boolean => {
  return text.length >= minLength && text.length <= maxLength;
};

/**
 * Waliduj URL (NF7).
 *
 * @param url - adres URL do walidacji
 * @returns true jeśli URL prawidłowy, false w przeciwnym razie
 */
export const isValidURL = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Waliduj czy string zawiera tylko litery i spacje (NF7).
 *
 * @param text - tekst do walidacji
 * @returns true jeśli tylko litery i spacje, false w przeciwnym razie
 */
export const isOnlyLettersAndSpaces = (text: string): boolean => {
  return /^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s]+$/.test(text);
};

/**
 * Waliduj czy string zawiera tylko cyfry (NF7).
 *
 * @param text - tekst do walidacji
 * @returns true jeśli tylko cyfry, false w przeciwnym razie
 */
export const isOnlyDigits = (text: string): boolean => {
  return /^\d+$/.test(text);
};

/**
 * Waliduj kwotę pieniężną (NF7).
 *
 * @param amount - kwota do walidacji
 * @param min - minimalna kwota (domyślnie 0)
 * @param max - maksymalna kwota (domyślnie Infinity)
 * @returns true jeśli kwota prawidłowa, false w przeciwnym razie
 */
export const isValidAmount = (amount: number, min = 0, max = Infinity): boolean => {
  return !isNaN(amount) && amount >= min && amount <= max && amount % 0.01 === 0;
};

/**
 * Sanityzuj tekst (usuń potencjalnie niebezpieczne znaki) (NF7).
 *
 * @param text - tekst do sanityzacji
 * @returns oczyszczony tekst
 */
export const sanitizeText = (text: string): string => {
  return text
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;")
    .replace(/\//g, "&#x2F;");
};

/**
 * Waliduj czy wartość nie jest pusta (NF7).
 *
 * @param value - wartość do sprawdzenia
 * @returns true jeśli wartość nie jest pusta, false w przeciwnym razie
 */
export const isNotEmpty = (value: unknown): boolean => {
  if (value === null || value === undefined) return false;
  if (typeof value === "string") return value.trim().length > 0;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "object") return Object.keys(value).length > 0;
  return true;
};

/**
 * Waliduj formularz (obiekt z polami) (NF7).
 *
 * @param data - obiekt z danymi formularza
 * @param rules - reguły walidacji dla każdego pola
 * @returns obiekt z błędami walidacji (puste jeśli wszystko OK)
 */
export const validateForm = <T extends Record<string, unknown>>(
  data: T,
  rules: Record<keyof T, (value: unknown) => string | null>
): Record<keyof T, string | null> => {
  const errors: Record<keyof T, string | null> = {} as Record<keyof T, string | null>;

  for (const field in rules) {
    const error = rules[field](data[field]);
    if (error) {
      errors[field] = error;
    }
  }

  return errors;
};

/**
 * Sprawdź czy formularz ma błędy.
 *
 * @param errors - obiekt z błędami walidacji
 * @returns true jeśli są błędy, false jeśli nie ma
 */
export const hasFormErrors = (errors: Record<string, string | null>): boolean => {
  return Object.values(errors).some((error) => error !== null && error !== "");
};
