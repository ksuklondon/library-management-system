# System Zarządzania Biblioteką

> Projekt z przedmiotu: Metodyki Tworzenia Oprogramowania  
> Architektura: Mikroserwisy (FastAPI + React + PostgreSQL)

---

## Spis treści

- [O projekcie](#o-projekcie)
- [Technologie](#technologie)
- [Architektura](#architektura)
- [Wymagania systemowe](#wymagania-systemowe)
- [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
- [Struktura projektu](#struktura-projektu)
- [API Documentation](#api-documentation)
- [Testowanie](#testowanie)
- [Metodyka](#metodyka)
- [Zespół](#zespół)
- [Troubleshooting](#troubleshooting)
- [Licencja](#licencja)

---

## O projekcie

System obsługi biblioteki to aplikacja webowa umożliwiająca:

**Czytelnikom:**

- Przeglądanie katalogu książek
- Rezerwowanie dostępnych egzemplarzy
- Zarządzanie swoimi wypożyczeniami
- Przedłużanie wypożyczeń

**Bibliotekarzom:**

- Zarządzanie katalogiem książek i egzemplarzy
- Wypożyczanie i przyjmowanie zwrotów
- Naliczanie kar za przetrzymanie
- Zarządzanie rezerwacjami

**Administratorom:**

- Zarządzanie użytkownikami i rolami
- Blokowanie kont
- Dostęp do logów audytowych
- Konfiguracja parametrów systemu

### Kluczowe funkcjonalności

- ✅ Autoryzacja JWT z rolami (RBAC)
- ✅ Rezerwacje z automatycznym wygaszaniem (3 dni)
- ✅ Wypożyczenia z naliczaniem kar za przetrzymanie
- ✅ Wyszukiwanie i filtrowanie książek
- ✅ Transakcyjność operacji (ACID)
- ✅ Rate limiting
- ✅ Health checks

---

## Technologie

### Backend

- **FastAPI** 0.115.3 - Framework webowy
- **SQLAlchemy** 2.0.34 - ORM (mapowanie obiektowo-relacyjne)
- **Alembic** 1.13.2 - Migracje bazy danych
- **Pydantic** 2.9.2 - Walidacja danych
- **python-jose** - JWT (tokeny autoryzacyjne)
- **passlib[bcrypt]** - Hashowanie haseł
- **uvicorn** - ASGI server

### Frontend

- **React** 18 + TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Stylowanie
- **Axios** - HTTP client
- **React Router** - Routing

### Baza danych

- **PostgreSQL** 15 - Relacyjna baza danych

### DevOps

- **Docker** + **Docker Compose** - Konteneryzacja
- **pytest** - Testy
- **GitHub Actions** - CI/CD (opcjonalnie)

---

## Architektura

System zbudowany jest w architekturze **mikroserwisów** z trzema niezależnymi serwisami backendowymi:

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│                     http://localhost:3000                    │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth Service │  │Catalog Service│  │ Loan Service │      │
│  │   :8001      │  │    :8002      │  │    :8003     │      │
│  │              │  │               │  │              │      │
│  │- Rejestracja │  │- Książki      │  │- Rezerwacje  │      │
│  │- Logowanie   │  │- Egzemplarze  │  │- Wypożyczenia│      │
│  │- JWT         │  │- Wyszukiwanie │  │- Zwroty      │      │
│  │- Użytkownicy │  │- Filtrowanie  │  │- Kary        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           ↓                ↓                  ↓              │
└───────────┼────────────────┼──────────────────┼──────────────┘
            └────────────────┼──────────────────┘
                             ↓
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │     :5432       │
                    │                 │
                    │ Shared Database │
                    └─────────────────┘
```

### Komunikacja między serwisami

- **Frontend → Backend:** REST API (JSON)
- **Backend ↔ Backend:** HTTP (przez Docker network)
- **Backend ↔ Database:** SQLAlchemy ORM

---

## Wymagania systemowe

### Opcja 1: Docker (REKOMENDOWANE ✅)

- **Docker Desktop** 4.0+ ([Pobierz tutaj](https://www.docker.com/products/docker-desktop))
- **RAM:** 4GB minimum (8GB zalecane)
- **Dysk:** 5GB wolnego miejsca

### Opcja 2: Ręczna instalacja

- **Python** 3.11+
- **PostgreSQL** 15+
- **Node.js** 18+ (dla frontendu)
- **Git**

---

## Instalacja i uruchomienie

### Metoda 1: Docker Compose (ŁATWA - POLECANA) 🐳

#### 1. Sklonuj repozytorium

```bash
git clone https://github.com/ksuklondon/library-management-system
cd library-management-system
```

#### 2. Skopiuj plik konfiguracyjny

```bash
# Windows PowerShell:
Copy-Item .env.example .env

# Linux/Mac:
cp .env.example .env
```

#### 3. Edytuj `.env` (OPCJONALNIE)

```bash
# Możesz zmienić hasła, porty, etc.
# Domyślne wartości działają od razu!
```

#### 4. Uruchom wszystkie serwisy

```bash
# Uruchomienie w tle (background):
docker compose up -d

# Uruchomienie z logami (foreground):
docker compose up

# Pierwsze uruchomienie zajmie 2-5 minut (pobieranie obrazów)
```

#### 5. Sprawdź czy działa

Otwórz przeglądarkę:

- **Auth Service API:** http://localhost:8001/docs
- **Catalog Service API:** http://localhost:8002/docs
- **Loan Service API:** http://localhost:8003/docs
- **Frontend:** http://localhost:3000 (gdy gotowy)

#### 6. Zatrzymanie

```bash
# Zatrzymanie wszystkich serwisów:
docker compose down

# Zatrzymanie + usunięcie danych (UWAGA!):
docker compose down -v
```

---

### Metoda 2: Ręczna instalacja (DLA DEVELOPERÓW)

#### 1. Zainstaluj PostgreSQL

```bash
# Windows: Pobierz instalator z postgresql.org
# Linux (Ubuntu/Debian):
sudo apt update
sudo apt install postgresql-15

# Utwórz bazę danych:
sudo -u postgres psql
CREATE DATABASE biblioteka;
CREATE USER admin WITH PASSWORD 'admin123';
GRANT ALL PRIVILEGES ON DATABASE biblioteka TO admin;
\q
```

#### 2. Backend - Auth Service

```bash
cd backend/auth-service

# Utwórz wirtualne środowisko:
python -m venv venv

# Aktywuj:
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Zainstaluj zależności:
pip install -r requirements.txt

# Skopiuj .env:
cp .env.example .env

# Uruchom migracje:
alembic upgrade head

# Uruchom serwis:
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 3. Backend - Catalog Service

```bash
cd backend/catalog-service
python -m venv venv
# ... powtórz kroki jak wyżej, port 8002
```

#### 4. Backend - Loan Service

```bash
cd backend/loan-service
python -m venv venv
# ... powtórz kroki jak wyżej, port 8003
```

#### 5. Frontend

```bash
cd frontend

# Zainstaluj zależności:
npm install

# Uruchom dev server:
npm run dev
```

---

## Struktura projektu

```
LIBRARY-MANAGEMENT-SYSTEM/
├── backend/
│   ├── shared/                     # Wspólny kod dla wszystkich serwisów
│   │   ├── database.py            # Konfiguracja SQLAlchemy
│   │   ├── config.py              # Ustawienia globalne
│   │   └── dependencies.py        # FastAPI dependencies (JWT, etc.)
│   │
│   ├── auth-service/              # Serwis autoryzacji (Port 8001)
│   │   ├── app/
│   │   │   ├── api/              # Endpointy REST
│   │   │   ├── core/             # Logika biznesowa (JWT, security)
│   │   │   ├── models/           # Modele SQLAlchemy (User, etc.)
│   │   │   ├── schemas/          # Schematy Pydantic (walidacja)
│   │   │   └── main.py           # Główny plik aplikacji FastAPI
│   │   ├── alembic/              # Migracje bazy danych
│   │   ├── tests/                # Testy (pytest)
│   │   ├── Dockerfile            # Obraz Docker
│   │   └── requirements.txt      # Zależności Python
│   │
│   ├── catalog-service/          # Serwis katalogu (Port 8002)
│   │   └── ... (analogiczna struktura)
│   │
│   └── loan-service/             # Serwis wypożyczeń (Port 8003)
│       └── ... (analogiczna struktura)
│
├── frontend/                      # Aplikacja React
│   ├── src/
│   │   ├── components/           # Komponenty React
│   │   ├── pages/                # Strony (routing)
│   │   ├── api/                  # Axios HTTP client
│   │   └── App.tsx               # Główny komponent
│   ├── public/                   # Pliki statyczne
│   └── package.json              # Zależności npm
│
├── docs/                          # Dokumentacja projektu
│   ├── api-contract.yaml         # OpenAPI specification
│   ├── architecture.md           # Opis architektury
│   ├── database-schema.md        # Schemat bazy danych
│   └── requirements.md           # Wymagania funkcjonalne/niefunkcjonalne
│
├── .env.example                   # Przykładowy plik środowiskowy
├── .gitignore                    # Pliki ignorowane przez GIT
├── docker-compose.yml            # Orkiestracja kontenerów
└── README.md                     # Ten plik!
```

---

## API Documentation

### Automatyczna dokumentacja (Swagger UI)

Po uruchomieniu projektu, dokumentacja API jest dostępna pod:

- **Auth Service:** http://localhost:8001/docs
- **Catalog Service:** http://localhost:8002/docs
- **Loan Service:** http://localhost:8003/docs

### Przykładowe endpointy

#### Auth Service (Port 8001)

```
POST   /api/auth/register      # Rejestracja użytkownika (F1)
POST   /api/auth/login         # Logowanie (F2)
POST   /api/auth/refresh       # Odświeżenie tokenu (F2a)
POST   /api/auth/logout        # Wylogowanie (F3)
GET    /api/auth/me            # Pobranie profilu
PATCH  /api/auth/profile       # Edycja profilu (F20)
GET    /api/users              # Lista użytkowników (F19)
PATCH  /api/users/{id}/role    # Zmiana roli (F26)
POST   /api/users/{id}/block   # Blokowanie użytkownika (F27)
```

#### Catalog Service (Port 8002)

```
GET    /api/catalog/books          # Przeglądanie katalogu (F4)
GET    /api/catalog/books/{id}     # Szczegóły książki (F7)
POST   /api/books                  # Dodanie książki (F15)
PATCH  /api/books/{id}             # Edycja książki (F15)
DELETE /api/books/{id}             # Usunięcie książki (F15)
POST   /api/books/{id}/copies      # Dodanie egzemplarza (F16)
PATCH  /api/copies/{id}/status     # Zmiana statusu egzemplarza (F16)
```

#### Loan Service (Port 8003)

```
POST   /api/reservations           # Rezerwacja (F8)
GET    /api/reservations           # Moje rezerwacje (F10)
DELETE /api/reservations/{id}      # Anulowanie rezerwacji (F9)
POST   /api/loans                  # Wypożyczenie (F11)
POST   /api/loans/{id}/return      # Zwrot (F12)
POST   /api/loans/{id}/pay-fine    # Opłata kary (F12a)
GET    /api/loans                  # Moje wypożyczenia (F13)
POST   /api/loans/{id}/extend      # Przedłużenie (F14)
```

---

## Testowanie

### Testy automatyczne (pytest)

```bash
# Testy dla auth-service:
cd backend/auth-service
pytest

# Testy z pokryciem kodu:
pytest --cov=app --cov-report=html

# Testy dla wszystkich serwisów:
cd backend
pytest auth-service/tests catalog-service/tests loan-service/tests
```

### Testy manualne (Postman/Swagger)

1. Otwórz Swagger UI: http://localhost:8001/docs
2. Kliknij "Try it out" na endpoincie
3. Wypełnij dane
4. Kliknij "Execute"
5. Sprawdź odpowiedź

### Przykładowy scenariusz testowy

```
1. Zarejestruj użytkownika (POST /api/auth/register)
2. Zaloguj się (POST /api/auth/login) → otrzymasz token
3. Skopiuj token z odpowiedzi
4. W Swagger: kliknij "Authorize" i wklej token
5. Przeglądaj książki (GET /api/catalog/books)
6. Zarezerwuj książkę (POST /api/reservations)
7. Sprawdź swoje rezerwacje (GET /api/reservations)
```

---

## Metodyka

Projekt realizowany jest zgodnie z metodyką **Kanban**:

### Dlaczego Kanban?

- ✅ Elastyczny flow zadań
- ✅ Łatwy w zarządzaniu dla małych zespołów (2 osoby)
- ✅ Wizualizacja postępów (GitHub Projects)
- ✅ Brak sztywnych sprintów

### Board Kanban - Przykład

```
┌──────────────┬───────────────┬──────────────┬──────────┐
│   BACKLOG    │  TO DO (Next) │ IN PROGRESS  │   DONE   │
├──────────────┼───────────────┼──────────────┼──────────┤
│ M3: Catalog  │ M2: Register  │ M1: Setup    │ Docs     │
│ M4: Loans    │ M2: Login     │ Docker       │ Structure│
│ M5: Frontend │ M2: JWT       │              │          │
└──────────────┴───────────────┴──────────────┴──────────┘

WIP LIMIT: Max 2 zadania "IN PROGRESS" jednocześnie
```

### Milestones

- **M1:** Setup & Infrastructure
- **M2:** Auth Service MVP
- **M3:** Catalog Service
- **M4:** Loan Service
- **M5:** Frontend React
- **M6:** Docker + Integracja

---

## Zespół

| Imię                | Rola                   |
| ------------------- | ---------------------- |
| Kalina Staniszewska | Developer              |
| Ewelina Świderska   | Developer-Collaborator |

---

## Troubleshooting

### Problem: `docker compose up` nie działa

**Rozwiązanie:**

```bash
# Sprawdź czy Docker Desktop działa:
docker --version
docker compose version

# Jeśli nie, uruchom Docker Desktop
```

### Problem: Port jest już zajęty (8001/8002/8003/5432)

**Rozwiązanie:**

```bash
# Sprawdź co używa portu:
# Windows:
netstat -ano | findstr :8001

# Linux/Mac:
lsof -i :8001

# Zmień port w .env:
AUTH_SERVICE_PORT=8011
```

### Problem: Błąd połączenia z bazą danych

**Rozwiązanie:**

```bash
# Sprawdź czy PostgreSQL działa:
docker ps

# Jeśli nie widać postgres:
docker compose up postgres -d

# Sprawdź logi:
docker compose logs postgres
```

### Problem: Migracje Alembic nie działają

**Rozwiązanie:**

```bash
# Wejdź do kontenera:
docker compose exec auth-service bash

# Ręcznie uruchom migracje:
alembic upgrade head

# Sprawdź current version:
alembic current
```

---

## Licencja

Ten projekt jest tworzony w ramach zajęć akademickich z przedmiotu "Metodyki Tworzenia Oprogramowania".

---

**Dziękujemy za zainteresowanie projektem!**
