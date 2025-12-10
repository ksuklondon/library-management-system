"""
backend/shared/dependencies.py

FastAPI Dependencies - JWT, RBAC, Current User.
Współdzielone przez wszystkie serwisy (auth, catalog, loan).

Odpowiada za:
- Weryfikację tokenów JWT (Wymaganie NF4)
- Sprawdzanie ról użytkowników - RBAC (Wymaganie NF5)
- Pobieranie aktualnie zalogowanego użytkownika
- Dependency injection dla FastAPI endpoints

Użycie w endpointach:
    from shared.dependencies import get_current_user, require_role

    @app.get("/admin-only")
    def admin_endpoint(current_user = Depends(require_role(["ADMIN"]))):
        return {"message": "Witaj adminie!"}
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

# Import z naszych modułów
from shared.config import settings

# ==========================================
# SECURITY SCHEME - Bearer Token
# ==========================================

# HTTPBearer - wyciąga token z nagłówka Authorization: Bearer <token>
security = HTTPBearer()

# ==========================================
# JWT TOKEN FUNCTIONS
# ==========================================


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Tworzy JWT access token.

    Args:
        data: Dane do zakodowania w tokenie (user_id, email, role, etc.)
        expires_delta: Czas ważności tokenu (domyślnie z settings)

    Returns:
        str: Zakodowany JWT token

    Przykład:
        token = create_access_token(
            data={
                "user_id": "uuid-here",
                "email": "jan@example.com",
                "role": "READER"
            }
        )
        # Zwraca: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    # Kopiujemy dane (żeby nie modyfikować oryginału)
    to_encode = data.copy()

    # Ustalamy czas wygaśnięcia
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Domyślnie z settings (30 minut)
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Dodajemy czas wygaśnięcia do payloadu
    to_encode.update({"exp": expire})

    # Kodujemy token
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Tworzy JWT refresh token (Wymaganie F2a).

    Refresh token ma dłuższy czas ważności (14 dni).

    Args:
        data: Dane do zakodowania (zazwyczaj tylko user_id)

    Returns:
        str: Zakodowany refresh token

    Przykład:
        refresh = create_refresh_token({"user_id": "uuid-here"})
    """
    to_encode = data.copy()

    # Refresh token ważny 14 dni
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Weryfikuje i dekoduje JWT token.

    Args:
        token: JWT token do weryfikacji

    Returns:
        Dict: Payload tokenu (dane użytkownika)

    Raises:
        HTTPException: Jeśli token nieprawidłowy/wygasły

    Przykład:
        payload = verify_token("eyJhbGciOiJIUzI1NiI...")
        # {'user_id': 'uuid', 'email': 'jan@example.com', 'role': 'READER'}
    """
    try:
        # Dekodujemy token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Konwertujemy Mapping na Dict
        payload_dict = cast(Dict[str, Any], payload)

        # Sprawdzamy czy token ma wymagane pola
        if payload_dict.get("user_id") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token nieprawidłowy: brak user_id",
            )

        return payload_dict

    except JWTError as e:
        # Token wygasły lub nieprawidłowy
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token nieprawidłowy: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==========================================
# DEPENDENCIES - Current User
# ==========================================


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Dependency - pobiera ID aktualnie zalogowanego użytkownika z tokenu JWT.

    Args:
        credentials: Token Bearer z nagłówka Authorization

    Returns:
        str: UUID użytkownika

    Raises:
        HTTPException 401: Jeśli brak tokenu lub token nieprawidłowy

    Użycie w endpointach:
        @app.get("/profile")
        def get_profile(user_id: str = Depends(get_current_user_id)):
            # user_id to UUID zalogowanego użytkownika
            return {"user_id": user_id}
    """
    # Wyciągamy token z credentials
    token = credentials.credentials

    # Weryfikujemy i dekodujemy token
    payload = verify_token(token)

    # Zwracamy user_id
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token nieprawidłowy: brak user_id",
        )

    return str(user_id)


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Dependency - pobiera pełny payload tokenu JWT (user_id, email, role).

    Args:
        credentials: Token Bearer z nagłówka Authorization

    Returns:
        Dict: Cały payload tokenu

    Użycie:
        @app.get("/profile")
        def get_profile(user: dict = Depends(get_current_user_payload)):
            # user = {"user_id": "...", "email": "...", "role": "READER"}
            return user
    """
    token = credentials.credentials
    payload = verify_token(token)

    return payload


# ==========================================
# DEPENDENCIES - RBAC (Role-Based Access Control)
# ==========================================

# Cache dla require_role - klucz: tuple ról, wartość: dependency function
_role_dependencies_cache = {}


def require_role(allowed_roles: List[str]):
    """
    Factory function - tworzy dependency sprawdzający rolę użytkownika.

    Implementuje RBAC - Role-Based Access Control (Wymaganie NF5).

    WAŻNE: Używa cache - ta sama lista ról zwraca tę samą dependency function.
    To pozwala na dependency_overrides w testach.

    Args:
        allowed_roles: Lista dozwolonych ról (np. ["ADMIN", "LIBRARIAN"])

    Returns:
        Dependency function

    Użycie:
        # Endpoint dostępny tylko dla ADMIN
        @app.delete("/users/{user_id}")
        def delete_user(
            user_id: str,
            current_user = Depends(require_role(["ADMIN"]))
        ):
            # Tylko admin może usuwać użytkowników
            return {"message": "User deleted"}

        # Endpoint dostępny dla ADMIN i LIBRARIAN
        @app.post("/books")
        def create_book(
            book: BookCreate,
            current_user = Depends(require_role(["ADMIN", "LIBRARIAN"]))
        ):
            # Admin i bibliotekarz mogą dodawać książki
            return {"message": "Book created"}
    """
    # Tworzymy klucz cache (tuple posortowanych ról)
    cache_key = tuple(sorted(allowed_roles))

    # Jeśli już mamy dependency dla tych ról, zwróć z cache
    if cache_key in _role_dependencies_cache:
        return _role_dependencies_cache[cache_key]

    async def role_checker(
        user_payload: Dict[str, Any] = Depends(get_current_user_payload),
    ) -> Dict[str, Any]:
        """
        Sprawdza czy użytkownik ma odpowiednią rolę.

        Args:
            user_payload: Payload tokenu JWT (zawiera rolę)

        Returns:
            Dict: Payload użytkownika (jeśli rola OK)

        Raises:
            HTTPException 403: Jeśli brak uprawnień
        """
        # Pobieramy rolę użytkownika z tokenu
        user_role = user_payload.get("role")

        # Sprawdzamy czy rola jest w liście dozwolonych
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Brak uprawnień. Wymagana rola: {', '.join(allowed_roles)}. "
                f"Twoja rola: {user_role}",
            )

        # Rola OK - zwracamy payload
        return user_payload

    # Zapisz w cache
    _role_dependencies_cache[cache_key] = role_checker

    return role_checker


# ==========================================
# DEPENDENCIES - Sprawdzanie statusu konta
# ==========================================


async def verify_active_user(
    user_payload: Dict[str, Any] = Depends(get_current_user_payload),
) -> Dict[str, Any]:
    """
    Dependency - sprawdza czy konto użytkownika jest aktywne (nie zablokowane).

    Implementuje Wymaganie F27 (blokowanie użytkowników).

    Args:
        user_payload: Payload tokenu JWT

    Returns:
        Dict: Payload użytkownika (jeśli aktywny)

    Raises:
        HTTPException 403: Jeśli konto zablokowane

    Użycie:
        @app.get("/books")
        def get_books(user = Depends(verify_active_user)):
            # Tylko aktywni użytkownicy mogą przeglądać książki
            return books
    """
    # Sprawdzamy czy użytkownik jest aktywny
    is_active = user_payload.get("is_active", True)

    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Twoje konto zostało zablokowane. Skontaktuj się z administratorem.",
        )

    return user_payload


# ==========================================
# DEPENDENCIES - Kombinacje (convenience)
# ==========================================


# Sprawdza czy użytkownik jest zalogowany I aktywny
async def get_active_user(
    user_payload: Dict[str, Any] = Depends(verify_active_user),
) -> Dict[str, Any]:
    """
    Dependency - pobiera aktywnego użytkownika (zalogowany + nie zablokowany).

    To jest najczęściej używany dependency - łączy get_current_user + verify_active.

    Użycie:
        @app.get("/my-reservations")
        def get_my_reservations(user = Depends(get_active_user)):
            # user jest zalogowany i aktywny
            return reservations
    """
    return user_payload


# Sprawdza czy użytkownik jest READER (i aktywny)
async def get_active_reader(
    user_payload: Dict[str, Any] = Depends(
        require_role(["READER", "LIBRARIAN", "ADMIN"])
    ),
) -> Dict[str, Any]:
    """
    Dependency - sprawdza czy użytkownik jest czytelnikiem (dowolna rola).

    W praktyce każdy ma dostęp (READER, LIBRARIAN, ADMIN).
    """
    return await verify_active_user(user_payload)


# Sprawdza czy użytkownik jest LIBRARIAN lub ADMIN (i aktywny)
async def get_active_staff(
    user_payload: Dict[str, Any] = Depends(require_role(["LIBRARIAN", "ADMIN"])),
) -> Dict[str, Any]:
    """
    Dependency - sprawdza czy użytkownik jest pracownikiem biblioteki.

    Staff = LIBRARIAN lub ADMIN.

    Użycie:
        @app.post("/loans")
        def create_loan(
            loan: LoanCreate,
            staff = Depends(get_active_staff)
        ):
            # Tylko personel może wypożyczać książki
            return loan
    """
    return await verify_active_user(user_payload)


# Sprawdza czy użytkownik jest ADMIN (i aktywny)
async def get_active_admin(
    user_payload: Dict[str, Any] = Depends(require_role(["ADMIN"])),
) -> Dict[str, Any]:
    """
    Dependency - sprawdza czy użytkownik jest administratorem.

    Użycie:
        @app.delete("/users/{user_id}")
        def delete_user(
            user_id: str,
            admin = Depends(get_active_admin)
        ):
            # Tylko admin może usuwać użytkowników
            return {"message": "deleted"}
    """
    return await verify_active_user(user_payload)


# ==========================================
# OPTIONAL USER (dla endpointów publicznych)
# ==========================================


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """
    Dependency - pobiera użytkownika jeśli jest zalogowany, None jeśli nie.

    Przydatne dla endpointów które są publiczne, ale zachowują się inaczej
    dla zalogowanych użytkowników.

    Args:
        credentials: Token Bearer (opcjonalny)

    Returns:
        Dict lub None: Payload użytkownika jeśli zalogowany, None jeśli nie

    Użycie:
        @app.get("/books")
        def get_books(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                # Zalogowany użytkownik - pokaż dodatkowe info
                return {"books": books, "user_favorites": [...]}
            else:
                # Gość - tylko podstawowe info
                return {"books": books}
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except HTTPException:
        # Token nieprawidłowy - traktujemy jako gościa
        return None


# ==========================================
# EKSPORT
# ==========================================

__all__ = [
    # Token functions
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    # Basic dependencies
    "get_current_user_id",
    "get_current_user_payload",
    "get_optional_user",
    # RBAC dependencies
    "require_role",
    "verify_active_user",
    # Convenience dependencies
    "get_active_user",
    "get_active_reader",
    "get_active_staff",
    "get_active_admin",
    # Security scheme
    "security",
]
