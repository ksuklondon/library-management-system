# System Obsługi Biblioteki - Wymagania

## Informacje podstawowe

**Projekt:** System Zarządzania Biblioteką  
**Autorzy:** Zespół 2-osobowy  
**Technologie:** FastAPI (Python), React (TypeScript), PostgreSQL, Docker  
**Architektura:** Mikroserwisy (3 serwisy backendowe)

---

## Role użytkowników (RBAC)

System wykorzystuje Role-Based Access Control z trzema rolami:

### Role:

- **Reader** – zwykły użytkownik (czytelnik)
- **Librarian** – pracownik biblioteki (operacje na katalogu i wypożyczeniach)
- **Admin** – administrator (zarządzanie użytkownikami, ustawienia systemowe)

### Hierarchia uprawnień:

Admin > Librarian > Reader

---

# WYMAGANIA FUNKCJONALNE

## Moduł 1: Autoryzacja i konto użytkownika

### F1 (MVP) - Rejestracja użytkownika

**Opis:** Utworzenie nowego konta użytkownika w systemie.

**Zakres:**

- Email (unikalny, walidacja formatu)
- Hasło (minimum 8 znaków, wymaga cyfry i wielkiej litery)
- Imię i nazwisko
- Numer telefonu (opcjonalnie)
- Domyślna rola: Reader
- Opcjonalnie: potwierdzenie email

**Aktorzy:** Gość (niezalogowany użytkownik)

**Walidacja:**

- Email unikalny w systemie
- Hasło spełnia wymagania bezpieczeństwa
- Wszystkie wymagane pola wypełnione

**Rezultat:**

- Utworzenie konta z rolą Reader
- Automatyczne wygenerowanie tokenu JWT

---

### F2 (MVP) - Logowanie

**Opis:** Uwierzytelnianie użytkownika w systemie.

**Zakres:**

- Sprawdzenie danych logowania (email + hasło)
- Wydanie access token (ważny 30 minut)
- Wydanie refresh token (ważny 14 dni)

**Aktorzy:** Reader, Librarian, Admin

**Rezultat:**

- Zwrócenie tokenów JWT
- Dostęp do funkcji odpowiednich dla roli

**Kody błędów:**

- 401: Nieprawidłowy email lub hasło
- 403: Konto zablokowane

---

### F2a (MVP) - Odświeżanie tokenu

**Opis:** Uzyskanie nowego access token bez ponownego logowania.

**Zakres:**

- POST /auth/refresh z refresh tokenem
- Zwrócenie nowego access token

**Aktorzy:** Reader, Librarian, Admin

**Rezultat:**

- Nowy access token (ważny 30 minut)

---

### F3 (MVP) - Wylogowanie

**Opis:** Zakończenie sesji użytkownika.

**Zakres:**

- Usunięcie tokenów z przeglądarki
- Opcjonalnie: unieważnienie refresh token w bazie danych

**Aktorzy:** Reader, Librarian, Admin

**Rezultat:**

- Sesja zakończona
- Użytkownik wylogowany

---

### F20 (DODATEK) - Edycja profilu

**Opis:** Zmiana danych osobowych użytkownika.

**Zakres:**

- Imię i nazwisko
- Numer telefonu
- Zmiana hasła (wymaga podania starego hasła)

**Aktorzy:** Reader, Librarian, Admin (tylko własny profil)

**Rezultat:**

- Zaktualizowane dane użytkownika

---

## Moduł 2: Katalog książek

### F4 (MVP) - Przeglądanie katalogu

**Opis:** Wyświetlanie listy książek dostępnych w bibliotece.

**Zakres:**

- Wyświetlanie: tytuł, autor, ISBN, rok wydania, gatunek, liczba dostępnych egzemplarzy
- Paginacja: parametry `page`, `size` (maksymalnie 50)
- Sortowanie: według `title`, `author`, `year`

**Aktorzy:** Wszyscy (również goście niezalogowani)

**Rezultat:**

- Lista książek z metadanymi paginacji

---

### F5 (MVP) - Wyszukiwanie

**Opis:** Wyszukiwanie książek po różnych kryteriach.

**Zakres:**

- Fraza wyszukiwania działa na: tytuł, autor, ISBN, gatunek
- Częściowe dopasowanie (LIKE %fraza%)
- Case-insensitive

**Aktorzy:** Wszyscy

**Rezultat:**

- Przefiltrowana lista książek pasujących do zapytania

---

### F6 (MVP) - Filtrowanie i sortowanie

**Opis:** Zawężanie wyników wyszukiwania.

**Zakres:**

- Filtry: dostępność, gatunek
- Sortowanie: tytuł/autor/rok + kierunek (asc/desc)

**Aktorzy:** Wszyscy

**Rezultat:**

- Zawężona lista książek według wybranych kryteriów

---

### F7 (MVP) - Szczegóły książki

**Opis:** Wyświetlanie pełnych informacji o książce.

**Zakres:**

- Pełne metadane książki
- Okładka (jeśli dostępna)
- Lista egzemplarzy (numer inwentarzowy, status)

**Aktorzy:** Wszyscy

**Rezultat:**

- Szczegółowa karta książki z listą egzemplarzy

---

### F15 (MVP) - Zarządzanie książkami (CRUD)

**Opis:** Dodawanie, edycja i usuwanie książek z katalogu.

**Zakres:**

- Dodawanie nowej książki (walidacja ISBN - musi być unikalny)
- Edycja metadanych książki
- Usuwanie książki (soft-delete)
- Usunięcie tylko gdy brak aktywnych egzemplarzy/rezerwacji/wypożyczeń

**Aktorzy:**

- Librarian: dodawanie i edycja
- Admin: dodawanie, edycja i usuwanie

**Rezultat:**

- Zaktualizowany katalog książek

---

### F16 (MVP) - Zarządzanie egzemplarzami

**Opis:** Zarządzanie fizycznymi egzemplarzami książek.

**Zakres:**

- Dodawanie nowego egzemplarza (automatyczny numer inwentarzowy)
- Zmiana statusu egzemplarza:
  - AVAILABLE (dostępny)
  - RESERVED (zarezerwowany)
  - LOANED (wypożyczony)
  - MAINTENANCE (konserwacja)
  - DAMAGED (uszkodzony)
  - LOST (zgubiony)
- Usuwanie egzemplarza (soft-delete)
- Usunięcie tylko gdy status NIE jest RESERVED ani LOANED

**Aktorzy:**

- Librarian: dodawanie i zmiana statusu
- Admin: dodawanie, zmiana statusu i usuwanie

**Rezultat:**

- Zaktualizowana lista egzemplarzy książki

---

## Moduł 3: Rezerwacje

### F8 (MVP) - Rezerwacja egzemplarza

**Opis:** Użytkownik rezerwuje dostępny egzemplarz książki.

**Zakres:**

- System weryfikuje limity i stan egzemplarza
- Rezerwacja wygasa automatycznie po 3 dniach
- Operacja w jednej transakcji z blokadą rekordu (SELECT FOR UPDATE)
- Na jeden egzemplarz może istnieć dokładnie 1 rezerwacja w statusie ACTIVE

**Warunki rezerwacji:**

- Maksymalnie 3 aktywne rezerwacje na użytkownika
- Maksymalnie 5 aktywnych wypożyczeń na użytkownika
- Brak przeterminowanych wypożyczeń (status OVERDUE)
- Brak nieopłaconych kar: `SUM(fine_amount WHERE fine_paid=false) = 0`

**Ważność rezerwacji:**

- 3 dni od momentu utworzenia
- Automatyczne wygaszanie przez background job (co 1 godzinę)

**Aktorzy:**

- Reader: może rezerwować dla siebie
- Librarian/Admin: może rezerwować w imieniu czytelnika

**Rezultat:**

- Utworzona rezerwacja w statusie ACTIVE
- Egzemplarz zmieniony na status RESERVED

**Kody błędów:**

- 400: Przekroczono limit rezerwacji
- 403: Użytkownik ma nieopłacone kary
- 409: Egzemplarz już zarezerwowany

---

### F9 (MVP) - Anulowanie rezerwacji

**Opis:** Odwołanie aktywnej rezerwacji.

**Zakres:**

- Użytkownik: może anulować tylko własną rezerwację
- Staff (Librarian/Admin): może anulować dowolną rezerwację z podaniem powodu
- Wpis do audytu (audit log)
- Egzemplarz wraca na status AVAILABLE

**Aktorzy:**

- Reader: własne rezerwacje
- Librarian/Admin: dowolne rezerwacje

**Rezultat:**

- Status rezerwacji: CANCELLED
- Powód anulowania zapisany w bazie
- Egzemplarz dostępny

---

### F10 (MVP) - Moje rezerwacje

**Opis:** Przegląd historii i aktywnych rezerwacji użytkownika.

**Zakres:**

- Lista aktywnych rezerwacji
- Historia rezerwacji (wszystkie statusy)
- Dla każdej rezerwacji: książka, egzemplarz, daty, status, powód anulowania (jeśli był)

**Aktorzy:** Reader, Librarian, Admin (własne rezerwacje)

**Rezultat:**

- Lista rezerwacji użytkownika

---

### F18 (MVP) - Lista wszystkich rezerwacji (widok personelu)

**Opis:** Przegląd i moderacja wszystkich rezerwacji w systemie.

**Zakres:**

- Filtry: status, użytkownik, książka, daty
- Akcje: anulowanie rezerwacji z podaniem powodu

**Aktorzy:**

- Librarian: podgląd i anulowanie
- Admin: pełny dostęp

**Rezultat:**

- Lista wszystkich rezerwacji z możliwością moderacji

---

## Moduł 4: Wypożyczenia

### F11 (MVP) - Checkout (wypożyczenie)

**Opis:** Wydanie książki użytkownikowi.

**Zakres:**

- Wypożyczenie z rezerwacji lub "od ręki"
- Walidacja limitów użytkownika
- Termin zwrotu (due date) = dzisiaj + 14 dni
- Operacja w jednej transakcji ACID:
  - Rezerwacja → COMPLETED
  - Egzemplarz → LOANED
  - Loan → ACTIVE

**Warunki wypożyczenia:**

- Maksymalnie 5 aktywnych wypożyczeń
- Brak przeterminowanych wypożyczeń
- Brak nieopłaconych kar

**Aktorzy:** Librarian, Admin

**Rezultat:**

- Utworzone wypożyczenie w statusie ACTIVE
- Egzemplarz zmieniony na LOANED
- Termin zwrotu = dzisiaj + 14 dni

---

### F12 (MVP) - Zwrot

**Opis:** Przyjęcie zwróconej książki.

**Zakres:**

- Wyliczenie kary (jeśli przeterminowane):
  - Dni kalendarzowe
  - Strefa czasowa: Europe/Warsaw
  - Wzór: `days_overdue = (return_date - due_date).days`
  - Kara: `min(days_overdue × 1.00 PLN, 100.00 PLN)`
- Zapis `fine_amount`, `fine_paid=false`
- Egzemplarz → AVAILABLE
- Operacja w jednej transakcji ACID

**Aktorzy:** Librarian, Admin

**Rezultat:**

- Status wypożyczenia: RETURNED
- Kara naliczona (jeśli przeterminowane)
- Egzemplarz dostępny

---

### F12a (MVP) - Opłata kary

**Opis:** Oznaczenie że kara została zapłacona.

**Zakres:**

- Zmiana `fine_paid = true`
- Odblokowanie możliwości rezerwacji dla użytkownika

**Aktorzy:** Librarian, Admin

**Rezultat:**

- Kara opłacona
- Użytkownik może znów rezerwować książki

---

### F13 (MVP) - Moje wypożyczenia

**Opis:** Widok historii wypożyczeń użytkownika.

**Zakres:**

- Aktywne wypożyczenia:
  - Termin zwrotu
  - Ile dni zostało / ile dni przeterminowane
  - Wysokość kary (jeśli przeterminowane)
- Historia wypożyczeń:
  - Daty wypożyczenia i zwrotu
  - Kary (jeśli były)

**Aktorzy:** Reader, Librarian, Admin (własne wypożyczenia)

**Rezultat:**

- Lista wypożyczeń użytkownika

---

### F14 (DODATEK) - Przedłużenie wypożyczenia

**Opis:** Jednorazowe przedłużenie terminu zwrotu o 14 dni.

**Zakres:**

- Przedłużenie możliwe tylko gdy:
  - Wypożyczenie NIE jest przeterminowane
  - Książka NIE jest zarezerwowana przez kogoś innego
  - Wypożyczenie NIE było wcześniej przedłużane
- Nowy termin = stary termin + 14 dni

**Aktorzy:**

- Reader: własne wypożyczenia
- Librarian/Admin: dowolne wypożyczenia

**Rezultat:**

- Przedłużony termin zwrotu
- Pole `extended_at` zapisane

**Kody błędów:**

- 400: Wypożyczenie przeterminowane
- 409: Książka zarezerwowana przez innego użytkownika
- 409: Wypożyczenie już było przedłużane

---

### F17 (MVP) - Lista wszystkich wypożyczeń

**Opis:** Widok operacyjny wszystkich wypożyczeń.

**Zakres:**

- Filtry: status, użytkownik, książka, daty
- Akcje:
  - Przyjęcie zwrotu
  - Podgląd szczegółów

**Aktorzy:** Librarian, Admin

**Rezultat:**

- Lista wszystkich wypożyczeń z możliwością zarządzania

---

## Moduł 5: Zarządzanie użytkownikami i rolami

### F19 (MVP) - Lista użytkowników

**Opis:** Przegląd wszystkich kont użytkowników.

**Zakres:**

- Librarian: tylko podgląd (np. przy wypożyczaniu książek)
- Admin: pełny dostęp z filtrami i paginacją

**Aktorzy:**

- Librarian: read-only
- Admin: pełny dostęp

**Rezultat:**

- Lista użytkowników z danymi podstawowymi

---

### F26 (MVP) - Zmiana roli użytkownika

**Opis:** Promocja lub degradacja użytkownika.

**Zakres:**

- Możliwe zmiany: Reader ↔ Librarian
- Nie można zmienić własnej roli
- Wpis do audytu

**Aktorzy:** Admin

**Rezultat:**

- Zmieniona rola użytkownika
- Zapisana data i admin który dokonał zmiany

---

### F27/F27a (MVP) - Blokowanie/Odblokowanie użytkownika

**Opis:** Zablokowanie lub przywrócenie dostępu do konta.

**Zakres:**

- Blokada: `is_active = false`, unieważnienie wszystkich sesji
- Nie można zablokować siebie ani innego administratora
- Wpis do audytu

**Aktorzy:** Admin

**Rezultat:**

- Zablokowany użytkownik nie może się zalogować
- Odblokowany użytkownik odzyskuje dostęp

---

### F28 (DODATEK) - Usunięcie użytkownika (GDPR)

**Opis:** Usunięcie danych użytkownika zgodnie z RODO ("prawo do bycia zapomnianym").

**Zakres:**

- Możliwe tylko gdy brak aktywnych wypożyczeń
- Anonimizacja danych osobowych
- Zachowanie historii wypożyczeń bez danych osobowych
- Soft-delete + wpis do audytu

**Aktorzy:** Admin

**Rezultat:**

- Dane osobowe zanonimizowane
- Historia transakcji zachowana

---

## Moduł 6: Powiadomienia (DODATEK)

### F21 (DODATEK) - System powiadomień

**Opis:** Powiadomienia "dzwonek" w interfejsie użytkownika.

**Zakres:**

- Powiadomienia o:
  - Zbliżającym się terminie zwrotu
  - Przeterminowaniu
  - Anulowaniu rezerwacji przez staff
  - Rezerwacji gotowej do odbioru
- Badge z liczbą nieprzeczytanych
- Toasty (wyskakujące powiadomienia)
- Zakładka z listą wszystkich powiadomień

**Aktorzy:** Reader, Librarian, Admin (własne powiadomienia)

**Rezultat:**

- Użytkownik informowany o ważnych wydarzeniach

---

## Moduł 7: Statystyki i audyt (DODATEK)

### F22 (DODATEK) - Historia egzemplarza

**Opis:** Pełna historia wypożyczeń konkretnego egzemplarza.

**Zakres:**

- Kto wypożyczył
- Kiedy wypożyczył i zwrócił
- Czy była kara

**Aktorzy:** Librarian, Admin

**Rezultat:**

- Historia użytkowania egzemplarza

---

### F23 (DODATEK) - Dashboard statystyk

**Opis:** Podsumowanie aktywności biblioteki.

**Zakres:**

- Liczniki: aktywne wypożyczenia, rezerwacje, przeterminowania
- Top 5 najpopularniejszych książek

**Aktorzy:** Librarian, Admin

**Rezultat:**

- Przejrzysty dashboard z kluczowymi metrykami

---

### F24 (DODATEK) - Logi audytowe

**Opis:** Historia krytycznych akcji w systemie.

**Zakres:**

- Krytyczne akcje: logowanie, zmiana roli, blokady, checkout/return
- Filtry: użytkownik, akcja, data
- Tylko do odczytu

**Aktorzy:** Admin

**Rezultat:**

- Pełna historia operacji w systemie

---

## Moduł 8: Ustawienia systemowe (OPCJONALNIE)

### F29 (OPCJONALNIE) - Parametry systemu

**Opis:** Konfiguracja parametrów działania biblioteki.

**Zakres:**

- Czasy: rezerwacja (3 dni), wypożyczenie (14 dni)
- Limity: maksymalne rezerwacje (3), maksymalne wypożyczenia (5)
- Stawki kar

**Aktorzy:** Admin

**Rezultat:**

- Możliwość dostosowania parametrów bez zmiany kodu

---

# WYMAGANIA NIEFUNKCJONALNE

## Bezpieczeństwo

### NF4 (MVP) - Uwierzytelnianie JWT

**Opis:** Bezpieczne uwierzytelnianie przy użyciu tokenów JWT.

**Zakres:**

- Access token: ważny 30 minut
- Refresh token: ważny 14 dni
- Hasła szyfrowane algorytmem bcrypt (koszt ≥12)

**Weryfikacja:** Testy integracyjne autoryzacji

---

### NF5 (MVP) - RBAC (Role-Based Access Control)

**Opis:** Kontrola dostępu oparta na rolach.

**Zakres:**

- Role: Reader, Librarian, Admin
- Endpointy wymagają odpowiedniej roli
- Kod błędu 403 przy braku uprawnień

**Weryfikacja:** Testy jednostkowe i integracyjne autoryzacji

---

### NF6 (PROD) - HTTPS

**Opis:** Szyfrowane połączenie w środowisku produkcyjnym.

**Zakres:**

- TLS 1.2+ w produkcji
- W środowisku developerskim może być HTTP

**Weryfikacja:** Konfiguracja serwera produkcyjnego

---

### NF7 (MVP) - Walidacja danych

**Opis:** Walidacja wszystkich danych wejściowych.

**Zakres:**

- Schematy Pydantic w backendzie
- Podstawowa walidacja w UI
- Błędy 422 z opisem nieprawidłowego pola

**Weryfikacja:** Testy walidacji dla każdego endpointu

---

### NF21 (MVP) - Rate limiting

**Opis:** Ograniczenie liczby żądań na minutę.

**Zakres:**

- Globalnie: 100 żądań/min/IP
- Endpoint logowania: 5 żądań/min/IP
- Odpowiedź 429 przy przekroczeniu limitu

**Weryfikacja:** Testy obciążeniowe

---

## Wydajność i dostępność

### NF1 (MVP) - Czas odpowiedzi

**Opis:** Szybkość odpowiedzi API.

**Zakres:**

- Percentyl p95 ≤ 2 sekundy dla kluczowych endpointów:
  - GET /books
  - GET /reservations
  - GET /loans

**Weryfikacja:** Prosty test obciążeniowy (k6 lub Locust)

---

### NF2 (MVP) - Równoczesność

**Opis:** Obsługa wielu użytkowników jednocześnie.

**Zakres:**

- System obsługuje 50 równoległych użytkowników bez błędów 5xx

**Weryfikacja:** Test współbieżności (concurrency test)

---

### NF3 (MVP) - Dostępność demo

**Opis:** Niezawodność systemu w okresie prezentacji.

**Zakres:**

- Uptime ~99% w okresie prezentacji/staging

**Weryfikacja:** Monitoring i logi

---

## UI/UX

### NF8 (MVP) - Obsługa błędów

**Opis:** Spójne i czytelne komunikaty błędów.

**Zakres:**

- Spójny format JSON: `{error: {code, message, details}}`
- Rozróżnienie: 401 (brak/wygasły token) vs 403 (brak roli)

**Weryfikacja:** Review API contract + testy

---

### NF9 (MVP) - Responsywność UI

**Opis:** Interfejs dostosowany do różnych urządzeń.

**Zakres:**

- Działa od 375px (mobile) przez tablet do desktop

**Weryfikacja:** Testy manualne na różnych urządzeniach

---

### NF10 (MVP) - Kompatybilność przeglądarek

**Opis:** Wsparcie dla głównych przeglądarek.

**Zakres:**

- Ostatnie 2 wersje: Chrome, Firefox, Safari, Edge

**Weryfikacja:** Testy w różnych przeglądarkach

---

## Kod, dokumentacja, testy

### NF11 (MVP) - Dokumentacja API

**Opis:** Pełna dokumentacja wszystkich endpointów.

**Zakres:**

- OpenAPI/Swagger dla każdego serwisu
- Dostępne pod /docs

**Weryfikacja:** Sprawdzenie dostępności Swagger UI

---

### NF12 (MVP) - Czytelność kodu

**Opis:** Kod zgodny ze standardami.

**Zakres:**

- Python: Black + Flake8
- TypeScript: ESLint + Prettier
- Style guide dla zespołu

**Weryfikacja:** Lintery w pipeline CI/CD

---

### NF13 (MVP) - Testy

**Opis:** Pokrycie testami automatycznymi.

**Zakres:**

- Pokrycie backendu ≥70%
- Kluczowe scenariusze:
  - Race condition rezerwacji
  - Transakcyjność checkout/return
  - Autoryzacja 401/403

**Weryfikacja:** Coverage reports

---

### NF16 (MVP) - Logowanie zdarzeń

**Opis:** Strukturalne logowanie operacji.

**Zakres:**

- Structured logging (JSON)
- Format: `{"timestamp", "level", "message", "user_id", "action", "metadata"}`
- Audyt: login, zmiana roli, blokady, checkout/return

**Weryfikacja:** Przegląd logów + logi w pipeline CI

---

## Deployment i operacyjność

### NF14 (MVP) - Konteneryzacja

**Opis:** Uruchamianie całego systemu przez Docker Compose.

**Zakres:**

- `docker compose up` uruchamia:
  - Frontend
  - 3 serwisy API (auth, catalog, loan)
  - PostgreSQL

**Weryfikacja:** Test uruchomienia na czystym systemie

---

### NF17 (MVP) - Czas startu

**Opis:** Szybkie uruchomienie wszystkich kontenerów.

**Zakres:**

- Wszystkie kontenery w stanie "healthy" w ≤60 sekund

**Weryfikacja:** Pomiar czasu startu

---

### NF19 (MVP) - Separacja środowisk

**Opis:** Oddzielne konfiguracje dla różnych środowisk.

**Zakres:**

- Osobne konfiguracje: dev/test/prod
- Pliki .env
- Zmienne środowiskowe
- Różne klucze JWT, ustawienia CORS, poziomy logów

**Weryfikacja:** Trzy pliki konfiguracyjne + uruchomienie w każdym środowisku

---

### NF20 (MVP) - REST API

**Opis:** Poprawne wykorzystanie standardu REST.

**Zakres:**

- Poprawne metody HTTP: GET/POST/PUT/PATCH/DELETE
- Poprawne statusy: 200/201/204/400/401/403/404/409/422/429/500
- Zasobowe URL: `/books`, `/books/{id}/copies`
- Brak efektów ubocznych w GET

**Weryfikacja:** Review kontraktów + testy integracyjne

---

### NF28 (MVP) - Health checks

**Opis:** Sprawdzanie stanu serwisów.

**Zakres:**

- Endpoint `/health` w każdym serwisie
- Health check w Dockerze

**Weryfikacja:** Test endpointów /health

---

### NF31 (MVP) - Migracje bazy danych

**Opis:** Wersjonowane zmiany schematu bazy.

**Zakres:**

- Alembic dla migracji
- Migracje w repozytorium
- Automatyczne uruchamianie przy starcie

**Weryfikacja:** Historia migracji w repo

---

## Integralność i polityka danych

### NF15 (MVP) - Integralność danych

**Opis:** Spójność danych w bazie.

**Zakres:**

- Transakcje ACID dla rezerwacji/checkout/return
- Foreign Keys, UNIQUE, CHECK w bazie danych
- Blokady SELECT FOR UPDATE dla współbieżności

**Weryfikacja:** Testy transakcyjności + race conditions

---

### NF26 (MVP) - Indeksy bazy danych

**Opis:** Optymalizacja zapytań.

**Zakres:**

- `users.email` UNIQUE
- `books.isbn` UNIQUE
- Indeksy statusów i dat:
  - `copies(status)`
  - `loans(due_date) WHERE status='ACTIVE'`
  - `reservations(expires_at) WHERE status='ACTIVE'`
  - `reservations(user_id) WHERE status='ACTIVE'`

**Weryfikacja:** Migracje + EXPLAIN ANALYZE dla kluczowych zapytań

---

### NF29 (MVP) - Polityka kar

**Opis:** Zasady naliczania kar za przetrzymanie.

**Zakres:**

- Strefa czasowa: Europe/Warsaw
- Dni kalendarzowe
- Wzór: `days_overdue = (return_date - due_date).days`
- Kara: `min(days_overdue × 1.00 PLN, 100.00 PLN)`
- Precyzja: DECIMAL(10,2)
- Zwrot w terminie lub wcześniej → kara = 0.00

**Weryfikacja:** Testy jednostkowe (w tym zmiana czasu letni/zimowy)

---

### NF30 (MVP) - Paginacja API

**Opis:** Standardowa paginacja dla wszystkich list.

**Zakres:**

- Wszystkie listy zwracają: `{items, page, size, total, pages}`
- Parametry: `page`, `size`, `sort`, `order`
- Limit: `size ≤ 50`
- Sortowanie deterministyczne (drugorzędnie po `id`)

**Weryfikacja:** Kontrakt API + testy list

---

## Dodatkowe (po MVP)

### NF18 (DODATEK) - Backup i restore

**Opis:** Kopie zapasowe bazy danych.

**Zakres:**

- `pg_dump` dla produkcji
- Automatyczne codzienne backupy
- Procedura restore

**Weryfikacja:** Test restore z backupu

---

### NF33 (DODATEK) - Rozszerzony audyt

**Opis:** Szczegółowe logowanie wszystkich operacji.

**Zakres:**

- Tabela `audit_logs`
- Filtry: użytkownik, akcja, data, typ encji
- Dashboard audytu

**Weryfikacja:** Przegląd logów audytowych

---

# PODSUMOWANIE WYMAGAŃ

## Wymagania funkcjonalne

### MVP (22 FR):

**Moduł 1 - Autoryzacja (4):**

- F1 - Rejestracja
- F2 - Logowanie
- F2a - Odświeżanie tokenu
- F3 - Wylogowanie

**Moduł 2 - Katalog (6):**

- F4 - Przeglądanie katalogu
- F5 - Wyszukiwanie
- F6 - Filtrowanie i sortowanie
- F7 - Szczegóły książki
- F15 - Zarządzanie książkami (CRUD)
- F16 - Zarządzanie egzemplarzami

**Moduł 3 - Rezerwacje (4):**

- F8 - Rezerwacja egzemplarza
- F9 - Anulowanie rezerwacji
- F10 - Moje rezerwacje
- F18 - Lista wszystkich rezerwacji (staff)

**Moduł 4 - Wypożyczenia (5):**

- F11 - Checkout
- F12 - Zwrot
- F12a - Opłata kary
- F13 - Moje wypożyczenia
- F17 - Lista wszystkich wypożyczeń (staff)

**Moduł 5 - Użytkownicy (3):**

- F19 - Lista użytkowników
- F26 - Zmiana roli
- F27/F27a - Blokowanie/Odblokowanie

**Suma MVP: 4 + 6 + 4 + 5 + 3 = 22 FR**

---

### DODATKI (8 FR):

- F14 - Przedłużenie wypożyczenia
- F20 - Edycja profilu
- F21 - Powiadomienia
- F22 - Historia egzemplarza
- F23 - Dashboard statystyk
- F24 - Logi audytowe
- F28 - Usunięcie użytkownika (GDPR)
- F29 - Ustawienia systemowe (OPCJONALNIE)

---

### RAZEM: 30 wymagań funkcjonalnych

---

## Wymagania niefunkcjonalne

### MVP (20 NFR):

**Bezpieczeństwo (5):**

- NF4, NF5, NF6, NF7, NF21

**Wydajność i dostępność (3):**

- NF1, NF2, NF3

**UI/UX (3):**

- NF8, NF9, NF10

**Kod, dokumentacja, testy (4):**

- NF11, NF12, NF13, NF16

**Deployment/Operacyjność (6):**

- NF14, NF17, NF19, NF20, NF28, NF31

**Integralność i polityka (4):**

- NF15, NF26, NF29, NF30

**Suma MVP: 20 NFR**

---

### DODATKI (2 NFR):

- NF18 - Backup/restore
- NF33 - Audyt rozszerzony

---

### RAZEM: 22 wymagania niefunkcjonalne

---

# PODSUMOWANIE CAŁKOWITE

| Kategoria                 | MVP    | Dodatki | Razem  |
| ------------------------- | ------ | ------- | ------ |
| Wymagania funkcjonalne    | 22     | 8       | **30** |
| Wymagania niefunkcjonalne | 20     | 2       | **22** |
| **ŁĄCZNIE**               | **42** | **10**  | **52** |

---

# Stack technologiczny

## Frontend:

- React + TypeScript
- Tailwind CSS (lub Bootstrap)
- Vite dev server (domyślnie :5173)
- Produkcyjnie: serwowany przez Nginx

## Backend (FastAPI):

- **auth-service** – Port 8001
- **catalog-service** – Port 8002
- **loan-service** – Port 8003

## Baza danych:

- PostgreSQL – Port 5432

## Uruchamianie:

```bash
docker compose up
```

Uruchamia:

- Frontend
- 3 serwisy API
- PostgreSQL
- Opcjonalnie: Redis (dla refresh tokenów)

---

**Dokumentacja stworzona zgodnie z wymaganiami projektu i diagramami UML.**
