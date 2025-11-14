# Architektura systemu - System Zarządzania Biblioteką

## Przegląd

System zarządzania biblioteką jest zbudowany w architekturze mikroserwisów z trzema niezależnymi serwisami backendowymi i jedną aplikacją frontendową (SPA).

**Kluczowe cechy:**

- Architektura mikroserwisów
- REST API z JSON
- Autoryzacja JWT
- Role-Based Access Control (RBAC)
- Transakcje ACID dla operacji krytycznych
- Docker Compose dla łatwego uruchomienia

---

## Komponenty systemu

### Frontend

- **Technologia:** React 18 + TypeScript
- **Port:** 3000 (dev), 5173 (Vite dev server)
- **Styling:** Tailwind CSS
- **Routing:** React Router
- **HTTP Client:** Axios
- **State Management:** Context API + React Hooks

### Backend - 3 serwisy

#### 1. Auth Service (Port 8001)

**Odpowiedzialność:** Autoryzacja i zarządzanie użytkownikami

**Funkcjonalności:**

- Rejestracja użytkowników (F1)
- Logowanie i wylogowanie (F2, F3)
- Odświeżanie tokenów JWT (F2a)
- Zmiana hasła i edycja profilu (F20)
- Zarządzanie użytkownikami przez administratora (F19, F26-F28)
- Blokowanie/odblokowanie użytkowników (F27/F27a)
- Zmiana ról użytkowników (F26)

**Technologie:**

- FastAPI (framework)
- python-jose (JWT)
- bcrypt (szyfrowanie haseł, koszt 12)
- SQLAlchemy (ORM)
- Pydantic (walidacja)

**Tabele bazy danych:**

- users
- refresh_tokens
- audit_logs (częściowo)

---

#### 2. Catalog Service (Port 8002)

**Odpowiedzialność:** Katalog książek i egzemplarze

**Funkcjonalności:**

- Przeglądanie katalogu (F4)
- Wyszukiwanie książek (F5)
- Filtrowanie i sortowanie (F6, F10)
- Szczegóły książki (F7)
- Zarządzanie książkami - CRUD (F15)
- Zarządzanie egzemplarzami (F16)
- Sprawdzanie dostępności

**Technologie:**

- FastAPI
- SQLAlchemy (z indeksami dla wydajności)
- PostgreSQL Full-Text Search (polskie znaki)
- Pydantic

**Tabele bazy danych:**

- books
- book_copies

---

#### 3. Loan Service (Port 8003)

**Odpowiedzialność:** Wypożyczenia i rezerwacje

**Funkcjonalności:**

- Rezerwacje książek (F8-F10, F18)
- Wypożyczenia (F11-F13, F17)
- Zwroty książek (F12)
- Przedłużanie wypożyczeń (F14)
- Opłacanie kar (F12a)
- Automatyczne naliczanie kar (F29 - background job)
- Powiadomienia (F21 - DODATEK)

**Technologie:**

- FastAPI
- SQLAlchemy (z transakcjami ACID)
- APScheduler (zadania zaplanowane)
- Pydantic

**Tabele bazy danych:**

- reservations
- loans
- notifications (DODATEK)
- settings (OPCJONALNIE)

---

### Baza danych

- **Technologia:** PostgreSQL 15
- **Port:** 5432
- **Nazwa bazy:** biblioteka
- **Kodowanie:** UTF-8
- **Strefa czasowa:** Europe/Warsaw (ważne dla kar!)

**Podejście:** Współdzielona baza danych przez wszystkie serwisy (dla uproszczenia projektu studenckiego)

---

## Przepływ danych

### Scenariusz 1: Rejestracja i logowanie użytkownika

**Krok 1:** Użytkownik wypełnia formularz rejestracji we Frontendzie

**Krok 2:** Frontend → POST /api/auth/register → Auth Service

**Krok 3:** Auth Service:

- Waliduje dane (Pydantic)
- Sprawdza unikalność email
- Szyfruje hasło (bcrypt, koszt 12)
- Zapisuje użytkownika w tabeli users (rola = READER)
- Generuje token JWT (access + refresh)
- Zapisuje refresh token w tabeli refresh_tokens

**Krok 4:** Auth Service → Frontend: tokens + dane użytkownika

**Krok 5:** Frontend zapisuje tokeny w localStorage

**Krok 6:** Użytkownik zalogowany, przekierowanie do strony głównej

---

### Scenariusz 2: Przeglądanie katalogu (niezalogowany)

**Krok 1:** Użytkownik otwiera stronę katalogu

**Krok 2:** Frontend → GET /api/catalog/books?page=1&size=20 → Catalog Service

**Krok 3:** Catalog Service:

- Pobiera książki z tabeli books (JOIN book_copies)
- Liczy dostępne egzemplarze (WHERE status = 'AVAILABLE')
- Aplikuje paginację (LIMIT/OFFSET)
- Zwraca JSON z listą książek + metadane paginacji

**Krok 4:** Frontend renderuje kartki książek

---

### Scenariusz 3: Rezerwacja książki (zalogowany Reader)

**Krok 1:** Reader klika "Rezerwuj" na dostępnej książce

**Krok 2:** Frontend → POST /api/reservations (z JWT w nagłówku Authorization) → Loan Service

**Krok 3:** Loan Service:

- Weryfikuje token JWT (wywołanie do Auth Service lub lokalnie)
- Sprawdza warunki rezerwacji:
  - User nie ma więcej niż 3 aktywnych rezerwacji (query do tabeli reservations)
  - User nie ma nieopłaconych kar (query do tabeli loans WHERE fine_paid = FALSE)
  - Egzemplarz jest dostępny (query do Catalog Service lub tabeli book_copies)
- Rozpoczyna transakcję ACID
- Tworzy rezerwację w tabeli reservations (status = ACTIVE, expires_at = NOW() + 3 dni)
- Zmienia status egzemplarza na RESERVED (UPDATE book_copies przez Catalog Service lub bezpośrednio)
- Commituje transakcję

**Krok 4:** Loan Service → Frontend: dane rezerwacji

**Krok 5:** Frontend wyświetla komunikat sukcesu

---

### Scenariusz 4: Wypożyczenie książki (Librarian)

**Krok 1:** Bibliotekarz skanuje kod kreskowy egzemplarza

**Krok 2:** Frontend → POST /api/loans (z JWT Librarian) → Loan Service

**Krok 3:** Loan Service:

- Weryfikuje rolę (czy LIBRARIAN lub ADMIN)
- Sprawdza warunki wypożyczenia:
  - User nie ma więcej niż 5 aktywnych wypożyczeń
  - User nie ma nieopłaconych kar
  - User nie ma przeterminowanych wypożyczeń (> 7 dni)
  - Egzemplarz jest dostępny
- Rozpoczyna transakcję ACID:
  - Jeśli była rezerwacja: UPDATE reservations SET status = 'COMPLETED'
  - INSERT INTO loans (due_date = NOW() + 14 dni, status = 'ACTIVE')
  - UPDATE book_copies SET status = 'LOANED'
- Commituje transakcję

**Krok 4:** Loan Service → Frontend: dane wypożyczenia

**Krok 5:** Frontend wyświetla potwierdzenie z terminem zwrotu

---

### Scenariusz 5: Automatyczne naliczanie kar (Background Job)

**Krok 1:** APScheduler uruchamia zadanie codziennie o północy (Europe/Warsaw)

**Krok 2:** Loan Service:

- Query: SELECT \* FROM loans WHERE status = 'ACTIVE' AND returned_at IS NULL AND due_date < CURRENT_DATE
- Dla każdego przeterminowanego wypożyczenia:
  - Oblicza dni_przeterminowania = (CURRENT_DATE - due_date).days
  - Oblicza karę = min(dni_przeterminowania × 1.00 PLN, 100.00 PLN)
  - UPDATE loans SET fine_amount = kara, status = 'OVERDUE'

**Krok 3:** (Opcjonalnie) Wysyła powiadomienia email lub tworzy notyfikacje w tabeli notifications

---

### Scenariusz 6: Zwrot książki z karą

**Krok 1:** Bibliotekarz skanuje kod kreskowy książki

**Krok 2:** Frontend → POST /api/loans/{id}/return → Loan Service

**Krok 3:** Loan Service:

- Weryfikuje rolę (LIBRARIAN/ADMIN)
- Sprawdza czy wypożyczenie przeterminowane
- Jeśli tak: oblicza ostateczną karę
- Rozpoczyna transakcję ACID:
  - UPDATE loans SET returned_at = NOW(), fine_amount = kara, status = 'RETURNED'
  - UPDATE book_copies SET status = 'AVAILABLE'
  - Jeśli ktoś czeka w kolejce rezerwacji: tworzy powiadomienie
- Commituje transakcję

**Krok 4:** Loan Service → Frontend: dane z wysokością kary (jeśli jest)

**Krok 5:** Frontend wyświetla komunikat o zwrocie + informację o karze

---

## Bezpieczeństwo

### Uwierzytelnianie (JWT)

**Token JWT:**

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "uuid-here",
    "email": "jan.kowalski@example.com",
    "role": "READER",
    "exp": 1234567890
  },
  "signature": "HMACSHA256(...)"
}
```

**Access Token:**

- Ważność: 30 minut
- Używany przy każdym żądaniu API
- Przesyłany w nagłówku: `Authorization: Bearer <token>`

**Refresh Token:**

- Ważność: 14 dni
- Używany tylko do uzyskania nowego access token
- Przechowywany w tabeli refresh_tokens
- Może być unieważniony (revoked = TRUE) przy wylogowaniu

**Szyfrowanie haseł:**

- Algorytm: bcrypt
- Koszt: 12 rund
- Nigdy nie przechowujemy haseł w postaci jawnej

---

### Autoryzacja (RBAC)

**Role i uprawnienia:**

**READER:**

- ✅ Przeglądanie katalogu
- ✅ Rezerwacje (max 3 aktywne)
- ✅ Przeglądanie swoich wypożyczeń
- ✅ Przedłużanie swoich wypożyczeń (max 2 razy)
- ✅ Edycja własnego profilu
- ❌ Dodawanie książek
- ❌ Wypożyczanie książek (tylko Librarian)
- ❌ Zarządzanie użytkownikami

**LIBRARIAN:**

- ✅ Wszystko co Reader
- ✅ Dodawanie/edycja książek i egzemplarzy
- ✅ Wypożyczanie książek dla czytelników
- ✅ Zwrot książek
- ✅ Opłacanie kar
- ✅ Przeglądanie wszystkich wypożyczeń i rezerwacji
- ❌ Zarządzanie użytkownikami
- ❌ Usuwanie książek

**ADMIN:**

- ✅ Wszystko co Librarian
- ✅ Zarządzanie użytkownikami (blokowanie, zmiana ról)
- ✅ Usuwanie książek i użytkowników
- ✅ Dostęp do logów audytowych
- ✅ Zarządzanie ustawieniami systemowymi

**Implementacja:**

```python
# Dependency w FastAPI
def require_role(allowed_roles: list[str]):
    def dependency(token: str = Depends(oauth2_scheme)):
        payload = verify_token(token)
        if payload["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Brak uprawnień")
        return payload
    return dependency

# Użycie
@app.post("/api/books")
def create_book(
    book: BookCreate,
    user = Depends(require_role(["LIBRARIAN", "ADMIN"]))
):
    # Tylko Librarian i Admin mogą dodawać książki
    ...
```

---

## Komunikacja między serwisami

### Wariant 1: HTTP REST (aktualnie w projekcie)

**Zalety:**

- Prosty i zrozumiały
- Standardowy protokół
- Łatwy w debugowaniu

**Przykład:**

```python
# Loan Service sprawdza uprawnienia użytkownika
import httpx

async def verify_user(user_id: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://auth-service:8001/api/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

---

### Wariant 2: Shared Database (używane w projekcie)

**Dla uproszczenia:** Wszystkie serwisy mają dostęp do tej samej bazy PostgreSQL

**Zalety:**

- Prostsze zapytania (JOIN między tabelami)
- Szybsze (brak network calls)
- Transakcje ACID między serwisami

**Wady:**

- Mniejsza separacja
- Trudniejsze skalowanie w przyszłości

**W produkcji:** Każdy serwis miałby własną bazę + komunikacja przez API

---

## Wydajność

### Strategie optymalizacji

**1. Indeksy bazy danych (NF26)**

- users.email (UNIQUE) - logowanie
- books.isbn (UNIQUE) - dodawanie książek
- book_copies(book_id, status) - sprawdzanie dostępności
- loans(user_id, status) - historia wypożyczeń
- loans(due_date) WHERE status='ACTIVE' - przeterminowane
- reservations(user_id) WHERE status='ACTIVE' - limit rezerwacji

**2. Paginacja (NF30)**

- Wszystkie listy: max 50 elementów na stronę (domyślnie 20)
- Deterministyczne sortowanie (po id jako drugorzędne)

**3. Connection Pool**

- PostgreSQL: 5-20 połączeń
- Timeout: 30 sekund

**4. Full-Text Search**

- PostgreSQL GIN index dla wyszukiwania w tytule/autorze
- Wsparcie dla polskich znaków (to_tsvector('polish', ...))

**5. Eager Loading**

- SQLAlchemy joinedload() dla relacji
- Unikanie problemu N+1 queries

---

## Deployment (Docker)

### Docker Compose

**Plik:** `docker-compose.yml`

**Serwisy:**

```yaml
services:
  postgres:
    image: postgres:15
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]

  auth-service:
    build: ./backend/auth-service
    ports: ["8001:8001"]
    depends_on: [postgres]

  catalog-service:
    build: ./backend/catalog-service
    ports: ["8002:8002"]
    depends_on: [postgres]

  loan-service:
    build: ./backend/loan-service
    ports: ["8003:8003"]
    depends_on: [postgres]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [auth-service, catalog-service, loan-service]
```

**Uruchomienie:**

```bash
# Uruchom wszystko
docker-compose up

# Uruchom w tle
docker-compose up -d

# Zatrzymaj
docker-compose down

# Restart
docker-compose restart

# Logi
docker-compose logs -f auth-service
```

**Po uruchomieniu system dostępny pod:**

- Frontend: http://localhost:3000
- Auth API Docs: http://localhost:8001/docs
- Catalog API Docs: http://localhost:8002/docs
- Loan API Docs: http://localhost:8003/docs
- PostgreSQL: localhost:5432

---

## Zmienne środowiskowe

### Przykładowy plik .env

```bash
# Database
DATABASE_URL=postgresql://admin:haslo@postgres:5432/biblioteka

# JWT (NF4)
SECRET_KEY=super-tajny-klucz-jwt-minimum-32-znaki-losowe
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14

# CORS (NF6)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development  # development | staging | production

# Logging (NF16)
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR

# Rate Limiting (NF21)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# Settings (zgodne z F29)
RESERVATION_DURATION_DAYS=3
LOAN_DURATION_DAYS=14
MAX_RESERVATIONS_PER_USER=3
MAX_LOANS_PER_USER=5
FINE_PER_DAY=1.00
MAX_FINE_AMOUNT=100.00
```

---

## Skalowanie (przyszłość)

### Opcje skalowania poziomego:

**1. API Gateway**

- Nginx lub Kong
- Load balancing między instancjami serwisów
- Rate limiting globalny

**2. Redis**

- Cache dla popularnych książek
- Session storage dla refresh tokenów
- Pub/Sub dla powiadomień

**3. Message Queue**

- RabbitMQ lub Kafka
- Asynchroniczna komunikacja między serwisami
- Kolejka dla powiadomień email

**4. Separate Databases**

- Auth Service: PostgreSQL (users, tokens)
- Catalog Service: PostgreSQL (books, copies)
- Loan Service: PostgreSQL (loans, reservations) + Redis (cache)

---

## Monitorowanie

### Health Checks (NF28)

Każdy serwis ma endpoint `/health`:

```json
{
  "status": "healthy",
  "database": "connected",
  "response_time_ms": 45,
  "version": "1.0.0",
  "service": "auth-service"
}
```

### Logowanie (NF16)

**Format:** Structured JSON logs

```json
{
  "timestamp": "2024-11-15T10:30:00Z",
  "level": "INFO",
  "message": "User logged in successfully",
  "user_id": "uuid-here",
  "action": "USER_LOGIN",
  "ip_address": "192.168.1.1",
  "metadata": {}
}
```

**Poziomy:**

- DEBUG: Szczegóły dla deweloperów
- INFO: Normalne operacje
- WARNING: Coś niepokojącego
- ERROR: Błędy krytyczne

---

## Testowanie

### Typy testów (NF13)

**1. Testy jednostkowe (Unit Tests)**

- Pokrycie: ≥70%
- Framework: pytest (backend), Jest (frontend)
- Testujemy: funkcje biznesowe, walidację, obliczenia kar

**2. Testy integracyjne (Integration Tests)**

- Testujemy: endpointy API, komunikację z bazą
- Ważne scenariusze:
  - Race condition przy rezerwacji (SELECT FOR UPDATE)
  - Transakcyjność checkout/return
  - Autoryzacja 401/403

**3. Testy E2E (opcjonalnie)**

- Framework: Playwright
- Testujemy: pełne user flows (rejestracja → logowanie → rezerwacja)

---

## Podsumowanie architektury

### Kluczowe decyzje:

**✅ Mikroserwisy:**

- Modularność (każdy serwis niezależny)
- Skalowalność (można skalować osobno)
- Czytelność (jasny podział odpowiedzialności)

**✅ Współdzielona baza danych:**

- Prostota (dla projektu studenckiego)
- Transakcje ACID
- Łatwiejsze JOIN'y

**✅ REST API + JSON:**

- Standardowy i popularny
- Łatwy w debugowaniu
- Szeroka kompatybilność
- Dobrze udokumentowany (OpenAPI/Swagger)

**✅ JWT:**

- Bezstanowy (stateless)
- Skalowalny
- Standardowy w przemyśle

**✅ Docker Compose:**

- Łatwe uruchomienie (`docker-compose up`)
- Izolacja środowisk
- Reprodukowalne buildy

### Liczby:

- **3 serwisy backend** (Auth, Catalog, Loan)
- **1 aplikacja frontend** (React SPA)
- **1 baza danych** (PostgreSQL)
- **9 tabel** (users, books, copies, loans, reservations, notifications, audit_logs, settings, refresh_tokens)
- **~40 endpointów API** (zgodnie z api-contract.yaml)
- **3 role** (Reader, Librarian, Admin)
- **52 wymagania** (30 funkcjonalnych + 22 niefunkcjonalnych)

---

**Architektura zaprojektowana zgodnie z wymaganiami projektu, diagramem klas UML i diagramem przypadków użycia.**
