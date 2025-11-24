# Bazowy obraz z Pythonem 3.11 w lekkiej wersji "slim"
FROM python:3.11-slim as base

# Metadane obrazu – kto utrzymuje i czego dotyczy
LABEL maintainer="library-system@example.com"
LABEL service="loan-service"
LABEL version="1.0.0"

# Ustawienia środowiska Pythona:
# - PYTHONUNBUFFERED: logi idą od razu na stdout (bez buforowania)
# - PYTHONDONTWRITEBYTECODE: nie zapisuje plików .pyc
# - PIP_*: szybsze i czyściejsze działanie pip
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalacja dodatkowych narzędzi systemowych:
# - gcc: potrzebny do kompilacji niektórych pakietów Pythona
# - postgresql-client: do narzędzi klienckich PostgreSQL (np. psql)
# - curl: używany w HEALTHCHECK
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Drugi etap – instalacja zależności Pythona
FROM base as dependencies

# Katalog roboczy wewnątrz kontenera
WORKDIR /app

# Kopiujemy plik z zależnościami
COPY requirements.txt .

# Instalujemy pip i wszystkie zależności z requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Trzeci etap – właściwa aplikacja
FROM dependencies as application

# Kopia kodu serwisu loan-service
COPY . .

# Współdzielony kod (np. config, database, dependencies) kopiowany do /app/shared
COPY ../shared /app/shared

# Tworzymy nie-rootowego użytkownika do uruchamiania aplikacji
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Przełączamy się na użytkownika aplikacyjnego (lepsze bezpieczeństwo)
USER appuser

# Otwieramy port 8003 (loan-service nasłuchuje na tym porcie)
EXPOSE 8003

# HEALTHCHECK – prosty test, czy serwis odpowiada na /health
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Komenda startowa: uruchomienie aplikacji FastAPI przez uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
