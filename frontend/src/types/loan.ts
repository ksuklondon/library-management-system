/**
 * Typy danych dla wypożyczeń i rezerwacji.
 *
 * Zgodność z wymaganiami:
 * - F8: Rezerwacja książki
 * - F9: Przeglądanie własnych rezerwacji
 * - F10: Anulowanie rezerwacji
 * - F11: Wypożyczenie książki
 * - F12: Zwrot książki
 * - F13: Historia wypożyczeń
 * - F14: Przedłużenie wypożyczenia (opcjonalne)
 * - F27: Płatność kar
 */

/**
 * Enum ze statusami rezerwacji (F8-F10).
 */
export enum ReservationStatus {
  ACTIVE = "ACTIVE",
  CANCELLED = "CANCELLED",
  EXPIRED = "EXPIRED",
  COMPLETED = "COMPLETED",
}

/**
 * Enum ze statusami wypożyczenia (F11-F13).
 */
export enum LoanStatus {
  ACTIVE = "ACTIVE",
  RETURNED = "RETURNED",
  OVERDUE = "OVERDUE",
}

/**
 * Interface reprezentujący rezerwację książki.
 * Zgodny z modelem Reservation z backend/loan-service.
 */
export interface Reservation {
  id: string;
  user_id: string;
  book_id: string;
  book_copy_id?: string;
  status: ReservationStatus;
  reserved_at: string;
  expires_at: string;
  created_at: string;
  updated_at: string;
  // Dodatkowe informacje dla frontendu
  book?: {
    title: string;
    authors: string;
    cover_url?: string;
  };
}

/**
 * Interface reprezentujący wypożyczenie książki.
 * Zgodny z modelem Loan z backend/loan-service.
 */
export interface Loan {
  id: string;
  user_id: string;
  book_copy_id: string;
  borrowed_at: string;
  due_date: string;
  returned_at?: string;
  status: LoanStatus;
  fine_amount?: number;
  created_at: string;
  updated_at: string;
  // Dodatkowe informacje dla frontendu
  book_copy?: {
    inventory_no: string;
    book: {
      title: string;
      authors: string;
      cover_url?: string;
    };
  };
}

/**
 * Interface reprezentujący karę za przetrzymanie (F27).
 */
export interface Fine {
  id: string;
  loan_id: string;
  user_id: string;
  amount: number;
  paid: boolean;
  paid_at?: string;
  created_at: string;
  updated_at: string;
  // Dodatkowe informacje dla frontendu
  loan?: {
    book_copy?: {
      book: {
        title: string;
        authors: string;
      };
    };
  };
}

/**
 * Request do utworzenia rezerwacji (F8 - READER).
 */
export interface ReservationCreateRequest {
  book_id: string;
}

/**
 * Request do wypożyczenia książki (F11 - LIBRARIAN).
 */
export interface LoanCreateRequest {
  user_id: string;
  book_copy_id: string;
  due_date?: string;
}

/**
 * Request do zwrotu książki (F12 - LIBRARIAN).
 */
export interface LoanReturnRequest {
  loan_id: string;
  returned_at?: string;
}

/**
 * Request do przedłużenia wypożyczenia (F14 - opcjonalne).
 */
export interface LoanExtendRequest {
  loan_id: string;
  extend_days?: number;
}

/**
 * Request do opłacenia kary (F27 - READER).
 */
export interface FinePaymentRequest {
  fine_id: string;
  payment_method?: string;
}

/**
 * Response z listą rezerwacji użytkownika (F9).
 */
export interface ReservationsResponse {
  reservations: Reservation[];
  total: number;
}

/**
 * Response z listą wypożyczeń użytkownika (F13).
 */
export interface LoansResponse {
  loans: Loan[];
  total: number;
}

/**
 * Response z listą kar użytkownika (F27).
 */
export interface FinesResponse {
  fines: Fine[];
  total_unpaid: number;
  total_amount: number;
}
