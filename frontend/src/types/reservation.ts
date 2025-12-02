/**
 * Dodatkowe typy dla rezerwacji (rozszerzenie loan.ts).
 *
 * Zgodność z wymaganiami:
 * - F8: Rezerwacja książki
 * - F9: Przeglądanie własnych rezerwacji
 * - F10: Anulowanie rezerwacji
 */

import { type Reservation, ReservationStatus } from "./loan";

/**
 * Rozszerzona informacja o rezerwacji z dodatkowymi danymi książki.
 * Używane w widoku "Moje Rezerwacje" (F9).
 */
export interface ReservationWithDetails extends Reservation {
  book: {
    id: string;
    title: string;
    authors: string;
    cover_url?: string;
    isbn?: string;
  };
  user: {
    id: string;
    email: string;
    full_name?: string;
  };
}

/**
 * Statystyki rezerwacji dla użytkownika.
 * Używane w panelu użytkownika.
 */
export interface ReservationStats {
  active: number;
  cancelled: number;
  expired: number;
  completed: number;
  total: number;
}

/**
 * Parametry filtrowania rezerwacji (panel LIBRARIAN).
 */
export interface ReservationFilterParams {
  status?: ReservationStatus;
  user_id?: string;
  book_id?: string;
  date_from?: string;
  date_to?: string;
}

/**
 * Response dla panelu LIBRARIAN - wszystkie rezerwacje.
 */
export interface AllReservationsResponse {
  reservations: ReservationWithDetails[];
  total: number;
  stats: ReservationStats;
}

/**
 * Informacja o dostępności książki do rezerwacji (F8).
 */
export interface BookAvailability {
  book_id: string;
  can_reserve: boolean;
  reason?: string; // Powód jeśli nie można zarezerwować
  available_copies: number;
  total_reservations: number;
  estimated_available_date?: string; // Przewidywana data dostępności
}

/**
 * Request do sprawdzenia czy użytkownik może zarezerwować książkę (F8).
 */
export interface CheckReservationEligibilityRequest {
  user_id: string;
  book_id: string;
}

/**
 * Response dla sprawdzenia uprawnień do rezerwacji (F8).
 */
export interface ReservationEligibilityResponse {
  can_reserve: boolean;
  reason?: string;
  max_reservations_reached?: boolean;
  already_reserved?: boolean;
  already_borrowed?: boolean;
}
