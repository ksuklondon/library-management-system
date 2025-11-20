/**
 * Komponent Loading - wyświetlanie spinnera ładowania.
 *
 * Zgodność z wymaganiami:
 * - NF12: Responsywność UI - feedback dla użytkownika podczas ładowania
 */

import React from "react";

/**
 * Props dla komponentu Loading.
 */
interface LoadingProps {
  size?: "small" | "medium" | "large";
  text?: string;
  fullScreen?: boolean;
}

/**
 * Komponent Loading - spinner ładowania.
 *
 * @param size - rozmiar spinnera (domyślnie 'medium')
 * @param text - opcjonalny tekst pod spinnerem
 * @param fullScreen - czy spinner ma zajmować cały ekran
 */
const Loading: React.FC<LoadingProps> = ({ size = "medium", text, fullScreen = false }) => {
  // Rozmiary spinnera
  const sizeClasses = {
    small: "w-8 h-8 border-2",
    medium: "w-12 h-12 border-3",
    large: "w-16 h-16 border-4",
  };

  // Spinner element
  const spinner = (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`${sizeClasses[size]} border-gray-300 border-t-blue-600 rounded-full animate-spin`}
        role="status"
        aria-label="Loading"
      />
      {text && <p className="text-gray-600 text-sm font-medium">{text}</p>}
    </div>
  );

  // Jeśli fullScreen, wyśrodkuj spinner na całym ekranie
  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
        {spinner}
      </div>
    );
  }

  // Normalny spinner
  return <div className="flex items-center justify-center p-8">{spinner}</div>;
};

export default Loading;
