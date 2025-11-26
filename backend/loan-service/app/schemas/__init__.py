"""
Schemas dla Loan Service.

Wymaganie: F8-F14, F27 - Rezerwacje, wypożyczenia, kary
Wymaganie: NF7 - Walidacja danych wejściowych
"""

from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
    ReservationStatus
)

from app.schemas.loan import (
    LoanCreate,
    LoanResponse,
    LoanUpdate,
    LoanStatus
)

from app.schemas.fine import (
    FineCreate,
    FineResponse,
    FinePayment
)

__all__ = [
    'ReservationCreate',
    'ReservationResponse',
    'ReservationUpdate',
    'ReservationStatus',
    'LoanCreate',
    'LoanResponse',
    'LoanUpdate',
    'LoanStatus',
    'FineCreate',
    'FineResponse',
    'FinePayment',
]
