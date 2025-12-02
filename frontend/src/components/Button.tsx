/**
 * Komponent Button - wielokrotnego użytku przycisk.
 *
 * Zgodność z wymaganiami:
 * - NF10: Responsywny design
 * - NF11: Intuicyjny interfejs użytkownika
 */

import React, { type ButtonHTMLAttributes } from "react";

/**
 * Warianty przycisku.
 */
type ButtonVariant = "primary" | "secondary" | "danger" | "success" | "outline";

/**
 * Rozmiary przycisku.
 */
type ButtonSize = "small" | "medium" | "large";

/**
 * Props dla komponentu Button.
 */
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  fullWidth?: boolean;
  children: React.ReactNode;
}

/**
 * Komponent Button - stylizowany przycisk z różnymi wariantami.
 *
 * @param variant - wariant stylu przycisku (domyślnie 'primary')
 * @param size - rozmiar przycisku (domyślnie 'medium')
 * @param isLoading - czy przycisk jest w stanie ładowania
 * @param fullWidth - czy przycisk ma zajmować pełną szerokość
 * @param disabled - czy przycisk jest wyłączony
 * @param children - zawartość przycisku
 */
const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "medium",
  isLoading = false,
  fullWidth = false,
  disabled = false,
  children,
  className = "",
  ...props
}) => {
  // Style bazowe (wspólne dla wszystkich)
  const baseClasses =
    "inline-flex items-center justify-center font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

  // Style dla wariantów
  const variantClasses = {
    primary:
      "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 dark:bg-blue-500 dark:hover:bg-blue-600",
    secondary:
      "bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500 dark:bg-gray-500 dark:hover:bg-gray-600",
    danger:
      "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 dark:bg-red-500 dark:hover:bg-red-600",
    success:
      "bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 dark:bg-green-500 dark:hover:bg-green-600",
    outline:
      "border-2 border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500 dark:border-blue-400 dark:text-blue-400 dark:hover:bg-gray-800",
  };

  // Style dla rozmiarów
  const sizeClasses = {
    small: "px-3 py-1.5 text-sm",
    medium: "px-4 py-2 text-base",
    large: "px-6 py-3 text-lg",
  };

  // Pełna szerokość
  const widthClass = fullWidth ? "w-full" : "";

  // Połączone klasy
  const buttonClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass} ${className}`;

  return (
    <button className={buttonClasses} disabled={disabled || isLoading} {...props}>
      {isLoading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};

export default Button;
