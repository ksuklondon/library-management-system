/**
 * API calls dla wypożyczeń, rezerwacji i kar.
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

import type {
  Fine,
  FinePaymentRequest,
  FinesResponse,
  Loan,
  LoanCreateRequest,
  LoanExtendRequest,
  LoanReturnRequest,
  LoansResponse,
  Reservation,
  ReservationCreateRequest,
  ReservationsResponse,
} from "../types/loan";
import type {
  AllReservationsResponse,
  BookAvailability,
  CheckReservationEligibilityRequest,
  ReservationEligibilityResponse,
} from "../types/reservation";
import { getErrorMessage, loanClient } from "./client";

// ==================== REZERWACJE (F8-F10) ====================

/**
 * Utworzenie rezerwacji książki (F8 - READER).
 */
export const createReservation = async (data: ReservationCreateRequest): Promise<Reservation> => {
  try {
    const response = await loanClient.post<Reservation>("/api/reservations/", data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie własnych rezerwacji użytkownika (F9 - READER).
 */
export const getMyReservations = async (): Promise<ReservationsResponse> => {
  try {
    const response = await loanClient.get<ReservationsResponse>("/api/reservations/my");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie wszystkich rezerwacji (LIBRARIAN/ADMIN panel).
 */
export const getAllReservations = async (): Promise<AllReservationsResponse> => {
  try {
    const response = await loanClient.get<AllReservationsResponse>("/api/reservations/");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie rezerwacji użytkownika po user_id (LIBRARIAN/ADMIN).
 */
export const getUserReservations = async (userId: string): Promise<Reservation[]> => {
  try {
    const response = await loanClient.get<Reservation[]>(`/api/reservations/user/${userId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie szczegółów rezerwacji (F9).
 */
export const getReservationDetails = async (reservationId: string): Promise<Reservation> => {
  try {
    const response = await loanClient.get<Reservation>(`/api/reservations/${reservationId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Anulowanie rezerwacji (F10 - READER).
 */
export const cancelReservation = async (reservationId: string): Promise<Reservation> => {
  try {
    const response = await loanClient.post<Reservation>(
      `/api/reservations/${reservationId}/cancel`
    );
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Sprawdzenie czy użytkownik może zarezerwować książkę (F8).
 */
export const checkReservationEligibility = async (
  data: CheckReservationEligibilityRequest
): Promise<ReservationEligibilityResponse> => {
  try {
    const response = await loanClient.post<ReservationEligibilityResponse>(
      "/api/reservations/check-eligibility",
      data
    );
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Sprawdzenie dostępności książki do rezerwacji (F8).
 */
export const checkBookAvailability = async (bookId: string): Promise<BookAvailability> => {
  try {
    const response = await loanClient.get<BookAvailability>(
      `/api/reservations/availability/${bookId}`
    );
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// ==================== WYPOŻYCZENIA (F11-F14) ====================

/**
 * Utworzenie wypożyczenia (F11 - LIBRARIAN).
 */
export const createLoan = async (data: LoanCreateRequest): Promise<Loan> => {
  try {
    const response = await loanClient.post<Loan>("/api/loans/", data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie własnych wypożyczeń użytkownika (F13 - READER).
 */
export const getMyLoans = async (): Promise<LoansResponse> => {
  try {
    const response = await loanClient.get<LoansResponse>("/api/loans/my");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie wszystkich wypożyczeń (LIBRARIAN/ADMIN panel).
 */
export const getAllLoans = async (): Promise<LoansResponse> => {
  try {
    const response = await loanClient.get<LoansResponse>("/api/loans/");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie szczegółów wypożyczenia (F13).
 */
export const getLoanDetails = async (loanId: string): Promise<Loan> => {
  try {
    const response = await loanClient.get<Loan>(`/api/loans/${loanId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Zwrot książki (F12 - LIBRARIAN).
 */
export const returnLoan = async (data: LoanReturnRequest): Promise<Loan> => {
  try {
    const response = await loanClient.post<Loan>(`/api/loans/${data.loan_id}/return`, data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Przedłużenie wypożyczenia (F14 - READER, opcjonalne).
 */
export const extendLoan = async (data: LoanExtendRequest): Promise<Loan> => {
  try {
    const response = await loanClient.post<Loan>(`/api/loans/${data.loan_id}/extend`, data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// ==================== KARY (F27) ====================

/**
 * Pobranie własnych kar użytkownika (F27 - READER).
 */
export const getMyFines = async (): Promise<FinesResponse> => {
  try {
    const response = await loanClient.get<FinesResponse>("/api/fines/my");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie wszystkich kar (LIBRARIAN/ADMIN panel).
 */
export const getAllFines = async (): Promise<FinesResponse> => {
  try {
    const response = await loanClient.get<FinesResponse>("/api/fines/");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Opłacenie kary (F27 - READER).
 */
export const payFine = async (data: FinePaymentRequest): Promise<Fine> => {
  try {
    const response = await loanClient.post<Fine>(`/api/fines/${data.fine_id}/pay`, data);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Pobranie szczegółów kary.
 */
export const getFineDetails = async (fineId: string): Promise<Fine> => {
  try {
    const response = await loanClient.get<Fine>(`/api/fines/${fineId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};
