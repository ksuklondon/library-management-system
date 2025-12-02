/**
 * Komponent Input - wielokrotnego użytku pole tekstowe.
 *
 * Zgodność z wymaganiami:
 * - NF7: Walidacja danych wejściowych
 * - NF10: Responsywny design
 * - NF11: Intuicyjny interfejs użytkownika
 */

import { type InputHTMLAttributes, forwardRef, useId } from "react";

/**
 * Props dla komponentu Input.
 */
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
}

/**
 * Komponent Input - stylizowane pole tekstowe z obsługą błędów.
 *
 * @param label - etykieta nad polem
 * @param error - komunikat błędu (jeśli jest, pole zmienia kolor na czerwony)
 * @param helperText - tekst pomocniczy pod polem
 * @param fullWidth - czy pole ma zajmować pełną szerokość
 * @param required - czy pole jest wymagane
 */
const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { label, error, helperText, fullWidth = false, required = false, className = "", ...props },
    ref
  ) => {
    // ID dla powiązania label z input (React 18+ useId hook)
    const generatedId = useId();
    const inputId = props.id || generatedId;

    // Klasy bazowe
    const baseClasses =
      "block px-3 py-2 border rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-white dark:bg-gray-800";

    // Klasy dla stanu błędu
    const errorClasses = error
      ? "border-red-500 focus:ring-red-500 focus:border-red-500 dark:border-red-400"
      : "border-gray-300 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500";

    // Pełna szerokość
    const widthClass = fullWidth ? "w-full" : "";

    // Połączone klasy
    const inputClasses = `${baseClasses} ${errorClasses} ${widthClass} ${className}`;

    return (
      <div className={fullWidth ? "w-full" : ""}>
        {/* Label */}
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        {/* Input */}
        <input
          ref={ref}
          id={inputId}
          className={inputClasses}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={
            error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
          }
          {...props}
        />

        {/* Komunikat błędu (NF7 - walidacja) */}
        {error && (
          <p
            id={`${inputId}-error`}
            className="mt-1 text-sm text-red-600 dark:text-red-400"
            role="alert"
          >
            {error}
          </p>
        )}

        {/* Tekst pomocniczy */}
        {!error && helperText && (
          <p id={`${inputId}-helper`} className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
