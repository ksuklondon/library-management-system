/**
 * Komponent Modal - okno modalne do wyświetlania dialogów.
 *
 * Zgodność z wymaganiami:
 * - NF11: Intuicyjny interfejs użytkownika
 * - Accessibility - obsługa klawiatury (ESC zamyka modal)
 */

import { X } from "lucide-react";
import React, { type ReactNode, useEffect } from "react";
import Button from "./Button";

/**
 * Props dla komponentu Modal.
 */
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  footer?: ReactNode;
  size?: "small" | "medium" | "large" | "xlarge";
  closeOnOverlayClick?: boolean;
  showCloseButton?: boolean;
}

/**
 * Komponent Modal - okno modalne z overlay.
 *
 * @param isOpen - czy modal jest otwarty
 * @param onClose - funkcja zamykająca modal
 * @param title - tytuł modala
 * @param children - zawartość modala
 * @param footer - stopka modala (przyciski akcji)
 * @param size - rozmiar modala (domyślnie 'medium')
 * @param closeOnOverlayClick - czy kliknięcie w overlay zamyka modal (domyślnie true)
 * @param showCloseButton - czy pokazać przycisk X do zamknięcia (domyślnie true)
 */
const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = "medium",
  closeOnOverlayClick = true,
  showCloseButton = true,
}) => {
  /**
   * Obsługa klawisza ESC - zamknięcie modala (accessibility).
   */
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      // Zablokuj scroll na body gdy modal otwarty
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
      // Przywróć scroll
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  // Jeśli modal zamknięty, nie renderuj nic
  if (!isOpen) return null;

  // Rozmiary modala
  const sizeClasses = {
    small: "max-w-md",
    medium: "max-w-lg",
    large: "max-w-2xl",
    xlarge: "max-w-4xl",
  };

  /**
   * Obsługa kliknięcia w overlay.
   */
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Zamknij tylko jeśli kliknięto w overlay (nie w zawartość modala)
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
    >
      <div
        className={`relative bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full ${sizeClasses[size]} max-h-[90vh] flex flex-col`}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            {title && (
              <h2 id="modal-title" className="text-xl font-semibold text-gray-900 dark:text-white">
                {title}
              </h2>
            )}
            {showCloseButton && (
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                aria-label="Close modal"
              >
                <X size={24} />
              </button>
            )}
          </div>
        )}

        {/* Content */}
        <div className="px-6 py-4 overflow-y-auto flex-1">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Komponent ModalFooter - pomocniczy komponent dla stopki modala.
 * Przykład użycia w footer prop.
 */
export const ModalFooter: React.FC<{
  onCancel?: () => void;
  onConfirm?: () => void;
  cancelText?: string;
  confirmText?: string;
  isLoading?: boolean;
}> = ({
  onCancel,
  onConfirm,
  cancelText = "Anuluj",
  confirmText = "Potwierdź",
  isLoading = false,
}) => {
  return (
    <>
      {onCancel && (
        <Button variant="outline" onClick={onCancel} disabled={isLoading}>
          {cancelText}
        </Button>
      )}
      {onConfirm && (
        <Button onClick={onConfirm} isLoading={isLoading}>
          {confirmText}
        </Button>
      )}
    </>
  );
};

export default Modal;
