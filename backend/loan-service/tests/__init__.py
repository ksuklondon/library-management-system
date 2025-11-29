"""
Loan Service - pakiet testów.

Wymaganie: NF9 - Testy jednostkowe i integracyjne

Ten pakiet zawiera kompleksowe testy dla Loan Service:
- test_reservation_routes.py   → testy endpointów rezerwacji (F8–F10)
- test_loan_routes.py          → testy endpointów wypożyczeń (F11–F14, F27)
- test_fine_routes.py          → testy endpointów kar (F27)
- test_reservation_model.py    → testy logiki modelu Reservation
- test_loan_model.py           → testy logiki modelu Loan
- test_fine_model.py           → testy logiki modelu Fine
- test_integration.py          → testy integracyjne end-to-end łączące pełne scenariusze użytkownika
- conftest.py                  → konfiguracja pytest, fixtures, baza testowa, mocki zależności

Struktura ta pokrywa wszystkie scenariusze funkcjonalne F8–F14 i F27,
a także zapewnia zgodność z wymaganiami niefunkcjonalnymi NF9 (testy),
NF19 (soft delete), NF29 (limity użytkownika), NF5 (RBAC), NF8 (migracje)
oraz obsługę transakcji zgodnie z ACID.

Sposoby uruchamiania testów:
    pytest backend/loan-service/tests/                 → uruchamia wszystkie testy
    pytest backend/loan-service/tests/ -v              → tryb verbose
    pytest backend/loan-service/tests/ --cov=app       → z raportowaniem pokrycia kodu
"""

# Wersja pakietu testowego — pomocne przy raportowaniu, CI/CD i weryfikacji zmian
__version__ = "1.0.0"
