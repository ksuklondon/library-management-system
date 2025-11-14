# ==========================================
# AUTH SERVICE - Dockerfile
# ==========================================
# Buduje obraz Docker dla serwisu autoryzacji

# ==========================================
# ETAP 1: BASE - Obraz bazowy Python
# ==========================================
FROM python:3.11-slim as base

# Metadane obrazu
LABEL maintainer="library-system@example.com"
LABEL service="auth-service"
LABEL version="1.0.0"

# Ustawienie zmiennych środowiskowych
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# ETAP 2: DEPENDENCIES - Instalacja bibliotek Python
# ==========================================
FROM base as dependencies

# Utwórz katalog roboczy
WORKDIR /app

# Skopiuj tylko requirements.txt (cache layer)
COPY requirements.txt .

# Zainstaluj zależności Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ==========================================
# ETAP 3: APPLICATION - Kod aplikacji
# ==========================================
FROM dependencies as application

# Skopiuj cały kod aplikacji
COPY . .

# Skopiuj shared modules (wspólny kod)
COPY ../shared /app/shared

# Utwórz użytkownika non-root (bezpieczeństwo)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Przełącz na użytkownika non-root
USER appuser

# Eksponuj port serwisu
EXPOSE 8001

# Health check (sprawdza czy serwis działa)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# ==========================================
# URUCHOMIENIE APLIKACJI
# ==========================================
# Komenda startowa - uruchamia FastAPI przez uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
