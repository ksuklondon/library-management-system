"""
backend/shared/config.py

Globalna konfiguracja systemu - odczytywanie zmiennych środowiskowych.
Współdzielone przez wszystkie serwisy (auth, catalog, loan).

Odpowiada za:
- Odczytywanie zmiennych z pliku .env
- Walidację konfiguracji (przez Pydantic)
- Dostarczanie ustawień do całego systemu
- Różne konfiguracje dla dev/staging/prod (Wymaganie NF19)

Użycie:
```python
from shared.config import settings

print(settings.DATABASE_URL)
print(settings.SECRET_KEY)
```
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings

# ==========================================
# KLASA KONFIGURACJI
# ==========================================


class Settings(BaseSettings):
    """
    Globalne ustawienia aplikacji.

    Pydantic automatycznie:
    - Odczytuje zmienne z pliku .env
    - Waliduje typy danych
    - Konwertuje stringi na właściwe typy (int, bool, list)

    Przykład zmiennej środowiskowej:
    DATABASE_URL=postgresql://user:pass@host:5432/db

    Pydantic automatycznie wczyta to jako settings.DATABASE_URL
    """

    # ==========================================
    # BAZA DANYCH (PostgreSQL)
    # ==========================================

    # Connection string do PostgreSQL
    DATABASE_URL: str = "postgresql://admin:admin123@localhost:5432/biblioteka"

    # URL testowej bazy danych (osobna od głównej)
    TEST_DATABASE_URL: Optional[str] = None

    # ==========================================
    # JWT - Tokeny autoryzacyjne (Wymaganie NF4)
    # ==========================================

    # Tajny klucz do podpisywania tokenów JWT
    # WAŻNE: Zmień w produkcji!
    SECRET_KEY: str = "super-secret-key-change-in-production-min-32-chars"

    # Algorytm szyfrowania JWT
    ALGORITHM: str = "HS256"

    # Czas ważności access token (w minutach)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Czas ważności refresh token (w dniach)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # ==========================================
    # APLIKACJA
    # ==========================================

    # Nazwa aplikacji/serwisu
    SERVICE_NAME: str = "library-management-system"

    # Wersja API
    API_VERSION: str = "1.0.0"

    # Środowisko: development | staging | production
    ENVIRONMENT: str = "development"

    # Poziom logowania: DEBUG | INFO | WARNING | ERROR | CRITICAL
    LOG_LEVEL: str = "INFO"

    # ==========================================
    # CORS - Cross-Origin Resource Sharing (Wymaganie NF6)
    # ==========================================

    # Lista dozwolonych origin (URLs frontend)
    # Format w .env: ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    def get_allowed_origins(self) -> List[str]:
        """
                Konwertuje string z .env na listę URL-i.

                Returns:
                    List[str]: Lista dozwolonych origin

                Przykład:
        ```python
                origins = settings.get_allowed_origins()
                # ['http://localhost:3000', 'http://localhost:5173']
        ```
        """
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # ==========================================
    # RATE LIMITING (Wymaganie NF21)
    # ==========================================

    # Czy włączyć rate limiting
    RATE_LIMIT_ENABLED: bool = True

    # Maksymalna liczba requestów na minutę (globalnie)
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100

    # Maksymalna liczba prób logowania na minutę
    RATE_LIMIT_LOGIN_REQUESTS_PER_MINUTE: int = 5

    # ==========================================
    # REGUŁY BIZNESOWE - Biblioteka (Wymaganie F29)
    # ==========================================

    # --- REZERWACJE ---

    # Czas trwania rezerwacji w dniach (Wymaganie F8)
    RESERVATION_DURATION_DAYS: int = 3

    # Maksymalna liczba aktywnych rezerwacji na użytkownika (Wymaganie F8)
    MAX_RESERVATIONS_PER_USER: int = 3

    # --- WYPOŻYCZENIA ---

    # Czas trwania wypożyczenia w dniach (Wymaganie F11)
    LOAN_DURATION_DAYS: int = 14

    # Maksymalna liczba aktywnych wypożyczeń na użytkownika (Wymaganie F11)
    MAX_LOANS_PER_USER: int = 5

    # Czy można przedłużać wypożyczenia (Wymaganie F14)
    ALLOW_LOAN_EXTENSION: bool = True

    # --- KARY (Wymaganie NF29) ---

    # Wysokość kary za jeden dzień przetrzymania (PLN)
    FINE_PER_DAY: float = 1.00

    # Maksymalna wysokość kary (PLN)
    MAX_FINE_AMOUNT: float = 100.00

    # ==========================================
    # PORTY SERWISÓW
    # ==========================================

    # Port serwisu autoryzacji
    AUTH_SERVICE_PORT: int = 8001

    # Port serwisu katalogu
    CATALOG_SERVICE_PORT: int = 8002

    # Port serwisu wypożyczeń
    LOAN_SERVICE_PORT: int = 8003

    # Port frontendu
    FRONTEND_PORT: int = 3000

    # ==========================================
    # URLS INNYCH SERWISÓW (komunikacja między serwisami)
    # ==========================================

    # URL serwisu autoryzacji (dla innych serwisów)
    AUTH_SERVICE_URL: str = "http://auth-service:8001"

    # URL serwisu katalogu
    CATALOG_SERVICE_URL: str = "http://catalog-service:8002"

    # URL serwisu wypożyczeń
    LOAN_SERVICE_URL: str = "http://loan-service:8003"

    # ==========================================
    # REDIS (opcjonalnie - dla refresh tokens)
    # ==========================================

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # ==========================================
    # EMAIL (opcjonalnie - dla powiadomień, Wymaganie F21)
    # ==========================================

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@biblioteca.pl"

    # ==========================================
    # SENTRY (opcjonalnie - monitoring błędów)
    # ==========================================

    SENTRY_DSN: Optional[str] = None

    # ==========================================
    # PYDANTIC CONFIG
    # ==========================================

    class Config:
        """Konfiguracja Pydantic"""

        # Nazwa pliku z którego czytać zmienne
        env_file = ".env"

        # Kodowanie pliku .env
        env_file_encoding = "utf-8"

        # Czy ignorować dodatkowe zmienne (nie zdefiniowane w Settings)
        extra = "ignore"

        # Case sensitivity dla nazw zmiennych
        case_sensitive = True


# ==========================================
# SINGLETON PATTERN - Jedna instancja dla całej aplikacji
# ==========================================


@lru_cache()
def get_settings() -> Settings:
    """
        Zwraca instancję Settings (singleton pattern).

        Dzięki @lru_cache() Settings jest tworzony tylko RAZ
        i potem zwracany z cache.

        Zalety:
        - Wydajność (nie parsuje .env za każdym razem)
        - Spójność (wszyscy używają tej samej konfiguracji)

        Użycie:
    ```python
        from shared.config import get_settings

        settings = get_settings()
        print(settings.DATABASE_URL)
    ```

        Returns:
            Settings: Instancja konfiguracji
    """
    return Settings()


# ==========================================
# GLOBALNA INSTANCJA (dla wygody)
# ==========================================

# Możesz importować bezpośrednio:
# from shared.config import settings
settings = get_settings()

# ==========================================
# HELPER FUNCTIONS
# ==========================================


def is_production() -> bool:
    """
        Sprawdza czy aplikacja działa w środowisku produkcyjnym.

        Returns:
            bool: True jeśli ENVIRONMENT == "production"

        Użycie:
    ```python
        from shared.config import is_production

        if is_production():
            # Włącz HTTPS, wyłącz debug, etc.
            pass
    ```
    """
    return settings.ENVIRONMENT.lower() == "production"


def is_development() -> bool:
    """
    Sprawdza czy aplikacja działa w środowisku deweloperskim.

    Returns:
        bool: True jeśli ENVIRONMENT == "development"
    """
    return settings.ENVIRONMENT.lower() == "development"


def is_testing() -> bool:
    """
    Sprawdza czy aplikacja działa w trybie testowym.

    Returns:
        bool: True jeśli ENVIRONMENT == "testing"
    """
    return settings.ENVIRONMENT.lower() in ("testing", "test")


# ==========================================
# WALIDACJA KONFIGURACJI
# ==========================================


def validate_config() -> None:
    """
        Waliduje konfigurację - sprawdza czy wszystkie wymagane zmienne są ustawione.

        Rzuca wyjątek jeśli konfiguracja niepoprawna.

        Użycie w main.py:
    ```python
        from shared.config import validate_config

        # Na starcie aplikacji:
        validate_config()
    ```

        Raises:
            ValueError: Jeśli konfiguracja niepoprawna
    """

    # Sprawdź czy SECRET_KEY został zmieniony w produkcji
    if is_production():
        if "change-in-production" in settings.SECRET_KEY.lower():
            raise ValueError(
                "BŁĄD: SECRET_KEY musi być zmieniony w środowisku produkcyjnym! "
                "Wygeneruj bezpieczny klucz: openssl rand -hex 32"
            )

    # Sprawdź czy DATABASE_URL jest ustawiony
    if not settings.DATABASE_URL:
        raise ValueError("BŁĄD: DATABASE_URL nie może być pusty!")

    # Sprawdź czy porty są poprawne (1024-65535)
    ports = [
        settings.AUTH_SERVICE_PORT,
        settings.CATALOG_SERVICE_PORT,
        settings.LOAN_SERVICE_PORT,
    ]

    for port in ports:
        if not (1024 <= port <= 65535):
            raise ValueError(
                f"BŁĄD: Port {port} jest niepoprawny (musi być 1024-65535)"
            )

    print("INFO: Konfiguracja poprawna!")


# ==========================================
# EKSPORT
# ==========================================

__all__ = [
    "Settings",  # Klasa konfiguracji
    "settings",  # Globalna instancja
    "get_settings",  # Funkcja singleton
    "is_production",  # Helper
    "is_development",  # Helper
    "is_testing",  # Helper
    "validate_config",  # Walidacja
]
