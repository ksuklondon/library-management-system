# Loan Service (Wypożyczenia, rezerwacje, kary)

Serwis odpowiedzialny za obsługę:

- **F8–F10** – rezerwacje książek  
- **F11–F14** – wypożyczenia książek  
- **F27** – kary za przetrzymanie  
- **NF5, NF7, NF8, NF9, NF15, NF19, NF29** – bezpieczeństwo, walidacja, migracje, testy, transakcje, soft delete, reguły biznesowe

## Architektura

- Framework: **FastAPI**
- ORM: **SQLAlchemy 2.x**
- Walidacja: **Pydantic v2**
- Baza danych: **PostgreSQL**
- Migracje: **Alembic**
- Testy: **pytest + pytest-cov**
- Autoryzacja: JWT z wykorzystaniem `backend.shared.auth`
- Wspólne komponenty: pakiet `backend/shared`

## Endpoints (wysoki poziom)

- `GET /health` – health-check serwisu
- `GET /` – podstawowe info o API

### Rezerwacje (`/api/reservations`)

- `POST /` – utwórz rezerwację (F8, max 3 aktywne na użytkownika)
- `GET /user/{user_id}` – rezerwacje użytkownika (F9)
- `GET /{reservation_id}` – szczegóły rezerwacji (F9)
- `PATCH /{reservation_id}` – anulowanie rezerwacji (F10)
- `DELETE /{reservation_id}` – soft delete (NF19, tylko LIBRARIAN/ADMIN)
- `GET /` – lista wszystkich rezerwacji (LIBRARIAN/ADMIN)

### Wypożyczenia (`/api/loans`)

- `POST /` – utwórz wypożyczenie (F11, LIBRARIAN/ADMIN, max 5 aktywnych)
- `GET /user/{user_id}` – wypożyczenia użytkownika (F13)
- `GET /{loan_id}` – szczegóły wypożyczenia (F13)
- `PATCH /{loan_id}/return` – zwrot książki + naliczanie kary (F12, F27)
- `PATCH /{loan_id}/extend` – przedłużenie wypożyczenia (F14)
- `PATCH /{loan_id}` – aktualizacja wypożyczenia (LIBRARIAN/ADMIN)
- `DELETE /{loan_id}` – soft delete (NF19, tylko ADMIN)
- `GET /` – lista wszystkich wypożyczeń (LIBRARIAN/ADMIN)
- `GET /overdue/all` – lista przetrzymanych wypożyczeń (F27)

### Kary (`/api/fines`)

- `POST /` – utwórz karę (F27, LIBRARIAN/ADMIN)
- `GET /user/{user_id}` – kary użytkownika (F27)
- `GET /{fine_id}` – szczegóły kary (F27)
- `PATCH /{fine_id}/pay` – opłacenie kary (F27)
- `DELETE /{fine_id}` – soft delete (NF19, tylko ADMIN)
- `GET /` – lista wszystkich kar (LIBRARIAN/ADMIN)
- `GET /unpaid/total` – suma nieopłaconych kar (globalnie lub dla usera)
- `PATCH /loan/{loan_id}/calculate` – oblicz i utwórz karę dla wypożyczenia

## Uruchomienie lokalne (bez Dockera)

1. Utwórz i aktywuj wirtualne środowisko:

   ```bash
   cd backend/loan-service
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate


Plik 2: backend/loan-service/TESTING.md:
# TESTING – Loan Service

Wymaganie: **NF9 – Testy jednostkowe i integracyjne**

## Stos technologiczny

- `pytest`
- `pytest-asyncio`
- `pytest-cov` – raport pokrycia
- Baza testowa: in-memory **SQLite** (konfiguracja w `tests/conftest.py`)

## Struktura testów

Katalog: `backend/loan-service/tests/`

- `conftest.py` – wspólne fixture'y (DB, klient, użytkownicy, przykładowe dane)
- `test_reservation_routes.py` – testy API rezerwacji (F8–F10)
- `test_loan_routes.py` – testy API wypożyczeń (F11–F14, F27)
- `test_fine_routes.py` – testy API kar (F27)
- `test_reservation_model.py` – testy logiki modelu `Reservation`
- `test_loan_model.py` – testy logiki modelu `Loan`
- `test_fine_model.py` – testy logiki modelu `Fine`
- `test_integration.py` – scenariusze end-to-end (rezerwacje → wypożyczenia → kary)

## Uruchamianie testów

W katalogu `backend/loan-service`:

```bash
# Wszystkie testy
pytest

# Z większą ilością informacji
pytest -v

# Konkretny plik
pytest tests/test_loan_routes.py -v


Plik3: backend/loan-service/.coveragerc
[run]
branch = True
source =
    app
    backend/shared
omit =
    */tests/*
    */alembic/*
    */__init__.py

[report]
show_missing = True
skip_covered = True
exclude_lines =
    pragma: no cover
    if __name__ == "__main__":
    if TYPE_CHECKING:

[html]
directory = htmlcov
