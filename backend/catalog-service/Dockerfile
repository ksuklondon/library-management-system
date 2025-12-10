# ===============================
# 🔹 Base image with system deps
# ===============================
FROM python:3.11-slim AS base

LABEL maintainer="library-system@example.com"
LABEL service="catalog-service"
LABEL version="1.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ===============================
# 🔹 Dependencies layer
# ===============================
FROM base AS dependencies

WORKDIR /app

# Kopiuj requirements z catalog-service
COPY catalog-service/requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ===============================
# 🔹 Final application image
# ===============================
FROM dependencies AS application

WORKDIR /app

# Kopiuj kod catalog-service
COPY catalog-service/ /app/

# Kopiuj wspólny moduł shared
COPY shared/ /app/shared/

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
