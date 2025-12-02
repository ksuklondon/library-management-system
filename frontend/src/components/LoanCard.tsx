/**
 * Komponent LoanCard - karta wyświetlająca wypożyczenie.
 *
 * Zgodność z wymaganiami:
 * - F13: Historia wypożyczeń
 * - F14: Przedłużenie wypożyczenia (opcjonalne)
 * - F27: Wyświetlanie kar
 * - NF10: Responsywny design
 */

import { differenceInDays, formatDistanceToNow } from "date-fns";
import { pl } from "date-fns/locale";
import { AlertTriangle, BookOpen, Calendar, CheckCircle, Clock, DollarSign } from "lucide-react";
import React from "react";
import type { Loan } from "../types/loan";
import { LoanStatus } from "../types/loan";
import Button from "./Button";

/**
 * Props dla komponentu LoanCard.
 */
interface LoanCardProps {
  loan: Loan;
  onExtend?: (loanId: string) => void;
  isExtending?: boolean;
  showExtendButton?: boolean;
  showPayFineButton?: boolean;
  onPayFine?: (loanId: string) => void;
  isPayingFine?: boolean;
}

/**
 * Komponent LoanCard - karta wypożyczenia (F13).
 *
 * @param loan - dane wypożyczenia
 * @param onExtend - funkcja przedłużenia (F14)
 * @param isExtending - czy przedłużanie w trakcie
 * @param showExtendButton - czy pokazać przycisk przedłuż
 * @param showPayFineButton - czy pokazać przycisk opłać karę (F27)
 * @param onPayFine - funkcja opłacenia kary
 * @param isPayingFine - czy płatność w trakcie
 */
const LoanCard: React.FC<LoanCardProps> = ({
  loan,
  onExtend,
  isExtending = false,
  showExtendButton = false,
  showPayFineButton = false,
  onPayFine,
  isPayingFine = false,
}) => {
  /**
   * Przedłuż wypożyczenie (F14).
   */
  const handleExtend = () => {
    if (onExtend) {
      onExtend(loan.id);
    }
  };

  /**
   * Opłać karę (F27).
   */
  const handlePayFine = () => {
    if (onPayFine) {
      onPayFine(loan.id);
    }
  };

  /**
   * Kolory i ikony dla statusów wypożyczenia.
   */
  const statusConfig = {
    ACTIVE: {
      icon: <Clock size={16} />,
      color: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
      label: "Aktywne",
    },
    RETURNED: {
      icon: <CheckCircle size={16} />,
      color: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
      label: "Zwrócone",
    },
    OVERDUE: {
      icon: <AlertTriangle size={16} />,
      color: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
      label: "Przetrzymane",
    },
  };

  const status = statusConfig[loan.status];

  /**
   * Oblicz dni do zwrotu / dni przetrzymania.
   */
  const dueDate = new Date(loan.due_date);
  const today = new Date();
  const daysUntilDue = differenceInDays(dueDate, today);
  const isDueSoon = daysUntilDue <= 3 && daysUntilDue >= 0;
  const isOverdue = loan.status === LoanStatus.OVERDUE || daysUntilDue < 0;

  const timeInfo =
    loan.status === LoanStatus.RETURNED
      ? `Zwrócono: ${new Date(loan.returned_at!).toLocaleDateString("pl-PL")}`
      : isOverdue
      ? `Przetrzymane o ${Math.abs(daysUntilDue)} dni`
      : `Do zwrotu: ${formatDistanceToNow(dueDate, { addSuffix: true, locale: pl })}`;

  /**
   * Czy jest kara do zapłacenia (F27).
   */
  const hasFine = loan.fine_amount && loan.fine_amount > 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex flex-col md:flex-row gap-4">
        {/* Ikona książki */}
        <div className="flex-shrink-0">
          <div className="w-24 h-32 bg-gray-200 dark:bg-gray-700 rounded-md overflow-hidden flex items-center justify-center">
            <BookOpen size={48} className="text-gray-400 dark:text-gray-500" />
          </div>
        </div>

        {/* Informacje o wypożyczeniu */}
        <div className="flex-1 min-w-0">
          {/* ID egzemplarza */}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Egzemplarz: {loan.book_copy_id}
          </h3>

          {/* Status */}
          <div className="flex items-center gap-2 mb-3">
            <span
              className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${status.color}`}
            >
              {status.icon}
              {status.label}
            </span>
          </div>

          {/* Daty */}
          <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400 mb-4">
            <div className="flex items-center gap-2">
              <Calendar size={16} />
              <span>Wypożyczono: {new Date(loan.borrowed_at).toLocaleDateString("pl-PL")}</span>
            </div>

            <div
              className={`flex items-center gap-2 ${
                isOverdue
                  ? "text-red-600 dark:text-red-400 font-medium"
                  : isDueSoon
                  ? "text-yellow-600 dark:text-yellow-400 font-medium"
                  : ""
              }`}
            >
              <Clock size={16} />
              <span>
                {timeInfo}
                {isDueSoon && !isOverdue && " ⚠️"}
                {isOverdue && " 🚨"}
              </span>
            </div>
          </div>

          {/* Kara (F27) */}
          {hasFine && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
                <DollarSign size={18} />
                <span className="font-semibold">Kara: {loan.fine_amount!.toFixed(2)} zł</span>
              </div>
            </div>
          )}

          {/* Przyciski akcji */}
          <div className="flex flex-wrap gap-2">
            {/* Przycisk przedłuż (F14 - tylko dla aktywnych) */}
            {showExtendButton && loan.status === LoanStatus.ACTIVE && !isOverdue && onExtend && (
              <Button
                variant="primary"
                size="small"
                onClick={handleExtend}
                isLoading={isExtending}
                disabled={isExtending}
              >
                Przedłuż
              </Button>
            )}

            {/* Przycisk opłać karę (F27) */}
            {showPayFineButton && hasFine && onPayFine && (
              <Button
                variant="success"
                size="small"
                onClick={handlePayFine}
                isLoading={isPayingFine}
                disabled={isPayingFine}
              >
                Opłać karę
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Ostrzeżenie o zbliżającym się terminie zwrotu */}
      {loan.status === LoanStatus.ACTIVE && isDueSoon && !isOverdue && (
        <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
          <p className="text-sm text-yellow-800 dark:text-yellow-200 flex items-center gap-2">
            <AlertTriangle size={16} />
            <span>
              Zbliża się termin zwrotu książki! Zostało {daysUntilDue}{" "}
              {daysUntilDue === 1 ? "dzień" : "dni"}.
            </span>
          </p>
        </div>
      )}

      {/* Ostrzeżenie o przetrzymaniu */}
      {isOverdue && loan.status === LoanStatus.ACTIVE && (
        <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <p className="text-sm text-red-800 dark:text-red-200 flex items-center gap-2">
            <AlertTriangle size={16} />
            <span>
              Książka jest przetrzymana! Zwróć ją jak najszybciej, aby uniknąć dodatkowych kar.
            </span>
          </p>
        </div>
      )}
    </div>
  );
};

export default LoanCard;
