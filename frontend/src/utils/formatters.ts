/**
 * Formatters - funkcje pomocnicze do formatowania danych.
 *
 * Zgodność z wymaganiami:
 * - NF11: Intuicyjny interfejs użytkownika - czytelne formatowanie dat, cen, etc.
 */

import { format, formatDistance, formatDistanceToNow, parseISO } from "date-fns";
import { pl } from "date-fns/locale";

/**
 * Formatuj datę do czytelnego formatu polskiego (np. "15 listopada 2024").
 *
 * @param date - data jako string ISO lub obiekt Date
 * @param formatStr - opcjonalny format (domyślnie 'dd MMMM yyyy')
 */
export const formatDate = (date: string | Date, formatStr = "dd MMMM yyyy"): string => {
  try {
    const dateObj = typeof date === "string" ? parseISO(date) : date;
    return format(dateObj, formatStr, { locale: pl });
  } catch (error) {
    console.error("Error formatting date:", error);
    return "Nieprawidłowa data";
  }
};

/**
 * Formatuj datę do krótkiego formatu (np. "15.11.2024").
 *
 * @param date - data jako string ISO lub obiekt Date
 */
export const formatDateShort = (date: string | Date): string => {
  return formatDate(date, "dd.MM.yyyy");
};

/**
 * Formatuj datę z godziną (np. "15 listopada 2024, 14:30").
 *
 * @param date - data jako string ISO lub obiekt Date
 */
export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, "dd MMMM yyyy, HH:mm");
};

/**
 * Formatuj datę jako "X dni temu" lub "za X dni" (relatywnie).
 *
 * @param date - data jako string ISO lub obiekt Date
 * @param addSuffix - czy dodać "temu" / "za" (domyślnie true)
 */
export const formatRelativeDate = (date: string | Date, addSuffix = true): string => {
  try {
    const dateObj = typeof date === "string" ? parseISO(date) : date;
    return formatDistanceToNow(dateObj, {
      addSuffix,
      locale: pl,
    });
  } catch (error) {
    console.error("Error formatting relative date:", error);
    return "Nieprawidłowa data";
  }
};

/**
 * Formatuj dystans między dwiema datami (np. "3 dni").
 *
 * @param dateLeft - pierwsza data
 * @param dateRight - druga data
 */
export const formatDateDistance = (dateLeft: string | Date, dateRight: string | Date): string => {
  try {
    const leftObj = typeof dateLeft === "string" ? parseISO(dateLeft) : dateLeft;
    const rightObj = typeof dateRight === "string" ? parseISO(dateRight) : dateRight;
    return formatDistance(leftObj, rightObj, { locale: pl });
  } catch (error) {
    console.error("Error formatting date distance:", error);
    return "Nieprawidłowy zakres dat";
  }
};

/**
 * Formatuj kwotę pieniężną (np. "12.50 zł").
 *
 * @param amount - kwota jako liczba
 * @param currency - waluta (domyślnie 'zł')
 */
export const formatCurrency = (amount: number, currency = "zł"): string => {
  try {
    return `${amount.toFixed(2)} ${currency}`;
  } catch (error) {
    console.error("Error formatting currency:", error);
    return "0.00 zł";
  }
};

/**
 * Formatuj liczbę z separatorem tysięcy (np. "1 234 567").
 *
 * @param num - liczba do formatowania
 */
export const formatNumber = (num: number): string => {
  try {
    return num.toLocaleString("pl-PL");
  } catch (error) {
    console.error("Error formatting number:", error);
    return String(num);
  }
};

/**
 * Formatuj ISBN - dodaj myślniki (np. "978-83-246-1234-5").
 *
 * @param isbn - numer ISBN jako string
 */
export const formatISBN = (isbn: string): string => {
  // Usuń wszystkie myślniki i spacje
  const cleaned = isbn.replace(/[-\s]/g, "");

  // ISBN-10: 83-246-1234-5
  if (cleaned.length === 10) {
    return `${cleaned.slice(0, 2)}-${cleaned.slice(2, 5)}-${cleaned.slice(5, 9)}-${cleaned.slice(
      9
    )}`;
  }

  // ISBN-13: 978-83-246-1234-5
  if (cleaned.length === 13) {
    return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 5)}-${cleaned.slice(5, 8)}-${cleaned.slice(
      8,
      12
    )}-${cleaned.slice(12)}`;
  }

  // Jeśli nieprawidłowa długość, zwróć oryginalny
  return isbn;
};

/**
 * Skróć tekst do określonej długości z "..." na końcu.
 *
 * @param text - tekst do skrócenia
 * @param maxLength - maksymalna długość (domyślnie 100)
 */
export const truncateText = (text: string, maxLength = 100): string => {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength).trim()}...`;
};

/**
 * Formatuj nazwisko autora (zamień "Kowalski Jan" na "Jan Kowalski").
 * Jeśli autor w formacie "LastName, FirstName", zamień na "FirstName LastName".
 *
 * @param author - nazwa autora
 */
export const formatAuthorName = (author: string): string => {
  if (author.includes(",")) {
    const [lastName, firstName] = author.split(",").map((s) => s.trim());
    return `${firstName} ${lastName}`;
  }
  return author;
};

/**
 * Formatuj listę autorów (np. "Jan Kowalski, Anna Nowak, Piotr Zieliński").
 *
 * @param authors - string z autorami oddzielonymi przecinkami lub średnikami
 */
export const formatAuthors = (authors: string): string => {
  // Rozdziel po przecinkach lub średnikach
  const authorList = authors.split(/[,;]/).map((a) => a.trim());

  // Formatuj każdego autora
  const formatted = authorList.map(formatAuthorName);

  // Połącz z powrotem
  if (formatted.length <= 2) {
    return formatted.join(" i ");
  }

  return formatted.slice(0, -1).join(", ") + " i " + formatted[formatted.length - 1];
};

/**
 * Formatuj status rezerwacji/wypożyczenia po polsku.
 *
 * @param status - status jako string z API
 */
export const formatStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    // Rezerwacje
    ACTIVE: "Aktywna",
    CANCELLED: "Anulowana",
    EXPIRED: "Wygasła",
    COMPLETED: "Zrealizowana",

    // Wypożyczenia
    BORROWED: "Wypożyczone",
    RETURNED: "Zwrócone",
    OVERDUE: "Przetrzymane",

    // Egzemplarze
    AVAILABLE: "Dostępny",
    RESERVED: "Zarezerwowany",
    DAMAGED: "Uszkodzony",
    LOST: "Zgubiony",
  };

  return statusMap[status] || status;
};

/**
 * Formatuj email - ukryj część (np. "jan****@example.com").
 *
 * @param email - adres email
 * @param visibleChars - ile znaków pokazać przed @ (domyślnie 3)
 */
export const formatEmailMasked = (email: string, visibleChars = 3): string => {
  const [localPart, domain] = email.split("@");

  if (localPart.length <= visibleChars) {
    return email;
  }

  const visible = localPart.slice(0, visibleChars);
  const masked = "*".repeat(localPart.length - visibleChars);

  return `${visible}${masked}@${domain}`;
};

/**
 * Formatuj rozmiar pliku (bajty) do czytelnego formatu (np. "1.5 MB").
 *
 * @param bytes - rozmiar w bajtach
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return "0 B";

  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
};
