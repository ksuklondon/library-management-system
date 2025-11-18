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

import {
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
import {
  AllReservationsResponse,
  BookAvailability,
  CheckReservationEligibilityRequest,
  ReservationEligibilityResponse,
} from "../types/reservation";
import apiClient, { getErrorMessage } from "./client";

/**
 * Bazowy URL dla loan-service.
 */
const LOAN_SERVICE_URL = import.meta.env.VITE_LOAN_SERVICE_URL || "http://localhost:8003";

// ==================== REZERWACJE (F8-F10) ====================

/**
 * Utworzenie rezerwacji książki (F8 - READER).
 */
export const createReservation = async (data: ReservationCreateRequest): Promise<Reservation> => {
  try {
    const response = await apiClient.post<Reservation>(
      `${LOAN_SERVICE_URL}/api/reservations/`,
      data
    );
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
    const response = await apiClient.get<ReservationsResponse>(
      `${LOAN_SERVICE_URL}/api/reservations/my`
    );
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
    const response = await apiClient.get<AllReservationsResponse>(
      `${LOAN_SERVICE_URL}/api/reservations/`
    );
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
    const response = await apiClient.get<Reservation>(
      `${LOAN_SERVICE_URL}/api/reservations/${reservationId}`
    );
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
    const response = await apiClient.post<Reservation>(
      `${LOAN_SERVICE_URL}/api/reservations/${reservationId}/cancel`
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
    const response = await apiClient.post<ReservationEligibilityResponse>(
      `${LOAN_SERVICE_URL}/api/reservations/check-eligibility`,
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
    const response = await apiClient.get<BookAvailability>(
      `${LOAN_SERVICE_URL}/api/reservations/availability/${bookId}`
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
    const response = await apiClient.post<Loan>(`${LOAN_SERVICE_URL}/api/loans/`, data);
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
    const response = await apiClient.get<LoansResponse>(`${LOAN_SERVICE_URL}/api/loans/my`);
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
    const response = await apiClient.get<LoansResponse>(`${LOAN_SERVICE_URL}/api/loans/`);
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
    const response = await apiClient.get<Loan>(`${LOAN_SERVICE_URL}/api/loans/${loanId}`);
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
    const response = await apiClient.post<Loan>(
      `${LOAN_SERVICE_URL}/api/loans/${data.loan_id}/return`,
      data
    );
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
    const response = await apiClient.post<Loan>(
      `${LOAN_SERVICE_URL}/api/loans/${data.loan_id}/extend`,
      data
    );
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
    const response = await apiClient.get<FinesResponse>(`${LOAN_SERVICE_URL}/api/fines/my`);
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
    const response = await apiClient.get<FinesResponse>(`${LOAN_SERVICE_URL}/api/fines/`);
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
    const response = await apiClient.post<Fine>(
      `${LOAN_SERVICE_URL}/api/fines/${data.fine_id}/pay`,
      data
    );
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
    const response = await apiClient.get<Fine>(`${LOAN_SERVICE_URL}/api/fines/${fineId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};
