# Bazowy obraz z Pythonem 3.11 (wersja slim – lżejsza niż pełny obraz).
FROM python:3.11-slim as base

# Metadane obrazu – informacje pomocnicze (np. w rejestrze obrazów).
LABEL maintainer="library-system@example.com"
LABEL service="auth-service"
LABEL version="1.0.0"

# Ustawienia środowiska Pythona:
# - PYTHONUNBUFFERED: logi są wypisywane od razu (bez buforowania),
# - PYTHONDONTWRITEBYTECODE: nie tworzy plików .pyc,
# - PIP_*: przyspieszenie i ograniczenie cache przy instalacji paczek.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalacja systemowych zależności potrzebnych m.in. dla:
# - kompilacji niektórych bibliotek Pythona (gcc),
# - klienta PostgreSQL (psql),
# - narzędzia curl (np. dla HEALTHCHECK).
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Drugi stage – instalacja zależności Pythona.
FROM base as dependencies

# Katalog roboczy wewnątrz kontenera.
WORKDIR /app

# Kopiujemy plik z zależnościami do obrazu.
COPY requirements.txt .

# Instalujemy zależności projektu.
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Trzeci stage – właściwa aplikacja (mniejszy finalny obraz).
FROM dependencies as application

# Kopiujemy kod Auth Service do kontenera.
COPY . .

# Kopiujemy współdzielony kod (np. konfiguracja, baza) z katalogu shared.
COPY ../shared /app/shared

# Tworzymy użytkownika nie-root (lepsze bezpieczeństwo uruchamiania kontenera)
# i zmieniamy właściciela katalogu /app.
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Przełączamy się na użytkownika nieuprzywilejowanego.
USER appuser

# Wystawiamy port 8001 – na nim działa Auth Service wewnątrz kontenera.
EXPOSE 8001

# Healthcheck – prosty test sprawdzający czy serwis odpowiada na /health.
# Jeśli endpoint /health zwróci błąd, kontener będzie oznaczony jako unhealthy.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Komenda startowa – uruchamia serwis FastAPI przy użyciu Uvicorna.
# --reload jest przydatne w środowisku deweloperskim (auto-przeładowanie kodu).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]


