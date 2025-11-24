"""
Modele danych dla Loan Service.

Wymaganie: F8-F14, F27 - Rezerwacje, wypożyczenia, kary
Wymaganie: NF15 - ACID transactions
Wymaganie: NF19 - Soft delete

Plik ten pełni rolę "fasady" dla modeli domenowych modułu Loan Service –
umożliwia wygodny import modeli z jednego miejsca, np.:
    from app.models import Reservation, Loan, Fine
"""

# Importujemy konkretne modele i ich enumy statusów z podmodułów:
# - Reservation / ReservationStatus – logika rezerwacji egzemplarzy (F8–F10)
# - Loan / LoanStatus – logika wypożyczeń i zwrotów (F11–F14)
# - Fine – logika naliczania i przechowywania kar (F27)
from app.models.reservation import Reservation, ReservationStatus
from app.models.loan import Loan, LoanStatus
from app.models.fine import Fine

# __all__ definiuje, które symbole będą eksportowane przy:
#     from app.models import *
# Dzięki temu zewnętrzny kod nie musi znać struktury podmodułów.
__all__ = [
    'Reservation',
    'ReservationStatus',
    'Loan',
    'LoanStatus',
    'Fine',
]
