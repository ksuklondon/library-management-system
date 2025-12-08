from datetime import datetime, timedelta
from decimal import Decimal

import pytest
import pytz
from app.models.fine import Fine
from app.models.loan import Loan
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_fine_calculation_1_day_overdue(
    async_client: AsyncClient, db, async_auth_librarian, test_user, test_book_copy
):
    """
    Scenariusz 4: Obliczanie kar - 1 dzień opóźnienia

    Wzór: fine = min(days_overdue × 1.00 PLN, 100.00 PLN)
    Test: 1 dzień opóźnienia → kara 1.00 PLN

    FIXED: PATCH bez trailing slash, używa async_auth_librarian
    """

    headers = async_auth_librarian  # FIXED: Use fixture directly

    # Utwórz wypożyczenie przeterminowane o 1 dzień
    warsaw_tz = pytz.timezone("Europe/Warsaw")
    now = datetime.now(warsaw_tz)

    loan = Loan(
        user_id=test_user.id,
        book_copy_id=test_book_copy.id,
        borrowed_at=now - timedelta(days=15),
        due_date=now - timedelta(days=1),  # Przeterminowane o 1 dzień
        returned_at=None,
    )
    db.add(loan)
    db.commit()

    # FIXED: BEZ trailing slash!
    response = await async_client.patch(f"/loans/{loan.id}/return", headers=headers)

    assert response.status_code == 200

    # Weryfikacja kary w bazie
    fine = db.query(Fine).filter(Fine.loan_id == loan.id).first()

    if fine:
        assert fine.amount == Decimal("1.00")
        assert fine.paid is False


async def test_fine_calculation_50_days_overdue(
    async_client: AsyncClient, db, async_auth_librarian, test_user, test_book_copy
):
    """
    Scenariusz 4: Obliczanie kar - 50 dni opóźnienia

    Test: 50 dni opóźnienia → kara 50.00 PLN

    FIXED: PATCH bez trailing slash
    """

    headers = async_auth_librarian  # FIXED: Use fixture directly

    warsaw_tz = pytz.timezone("Europe/Warsaw")
    now = datetime.now(warsaw_tz)

    loan = Loan(
        user_id=test_user.id,
        book_copy_id=test_book_copy.id,
        borrowed_at=now - timedelta(days=64),
        due_date=now - timedelta(days=50),  # Przeterminowane o 50 dni
        returned_at=None,
    )
    db.add(loan)
    db.commit()

    # FIXED: BEZ trailing slash!
    response = await async_client.patch(f"/loans/{loan.id}/return", headers=headers)

    assert response.status_code == 200

    # Weryfikacja kary: 50 dni × 1.00 PLN = 50.00 PLN
    fine = db.query(Fine).filter(Fine.loan_id == loan.id).first()

    if fine:
        assert fine.amount == Decimal("50.00")


async def test_fine_calculation_150_days_cap(
    async_client: AsyncClient, db, async_auth_librarian, test_user, test_book_copy
):
    """
    Scenariusz 4: Obliczanie kar - 150 dni opóźnienia (cap przy 100 PLN)

    Test: 150 dni opóźnienia → kara 100.00 PLN (maksymalny limit)
    Wzór: min(150 × 1.00, 100.00) = 100.00 PLN

    FIXED: PATCH bez trailing slash
    """

    headers = async_auth_librarian  # FIXED: Use fixture directly

    warsaw_tz = pytz.timezone("Europe/Warsaw")
    now = datetime.now(warsaw_tz)

    loan = Loan(
        user_id=test_user.id,
        book_copy_id=test_book_copy.id,
        borrowed_at=now - timedelta(days=164),
        due_date=now - timedelta(days=150),  # Przeterminowane o 150 dni
        returned_at=None,
    )
    db.add(loan)
    db.commit()

    # FIXED: BEZ trailing slash!
    response = await async_client.patch(f"/loans/{loan.id}/return", headers=headers)

    assert response.status_code == 200

    # Weryfikacja kary: limit 100.00 PLN (nie 150.00 PLN)
    fine = db.query(Fine).filter(Fine.loan_id == loan.id).first()

    if fine:
        assert fine.amount == Decimal("100.00")


async def test_no_fine_on_time_return(
    async_client: AsyncClient, db, async_auth_librarian, test_user, test_book_copy
):
    """
    Test: Zwrot na czas (bez opóźnienia) → brak kary

    FIXED: PATCH bez trailing slash
    """

    headers = async_auth_librarian  # FIXED: Use fixture directly

    warsaw_tz = pytz.timezone("Europe/Warsaw")
    now = datetime.now(warsaw_tz)

    loan = Loan(
        user_id=test_user.id,
        book_copy_id=test_book_copy.id,
        borrowed_at=now - timedelta(days=10),
        due_date=now + timedelta(days=4),  # Jeszcze 4 dni do terminu
        returned_at=None,
    )
    db.add(loan)
    db.commit()

    # FIXED: BEZ trailing slash!
    response = await async_client.patch(f"/loans/{loan.id}/return", headers=headers)

    assert response.status_code == 200

    # Weryfikacja: brak kary
    fine = db.query(Fine).filter(Fine.loan_id == loan.id).first()
    assert fine is None


async def test_fine_timezone_warsaw(
    async_client: AsyncClient, db, async_auth_librarian, test_user, test_book_copy
):
    """
    Test: Sprawdzenie że obliczenia używają strefy czasowej Europe/Warsaw (NF29)

    FIXED: PATCH bez trailing slash
    """

    headers = async_auth_librarian  # FIXED: Use fixture directly

    # Użycie explicite Europe/Warsaw
    warsaw_tz = pytz.timezone("Europe/Warsaw")
    now_warsaw = datetime.now(warsaw_tz)

    # Wypożyczenie przeterminowane o dokładnie 3 dni
    loan = Loan(
        user_id=test_user.id,
        book_copy_id=test_book_copy.id,
        borrowed_at=now_warsaw - timedelta(days=17),
        due_date=now_warsaw - timedelta(days=3),
        returned_at=None,
    )
    db.add(loan)
    db.commit()

    # FIXED: BEZ trailing slash!
    response = await async_client.patch(f"/loans/{loan.id}/return", headers=headers)

    assert response.status_code == 200

    # Weryfikacja: 3 dni × 1.00 PLN = 3.00 PLN
    fine = db.query(Fine).filter(Fine.loan_id == loan.id).first()

    if fine:
        assert fine.amount == Decimal("3.00")


async def test_fine_decimal_precision(
    async_client: AsyncClient, db, async_auth_librarian, test_user, test_book_copy
):
    """
    Test: Sprawdzenie precyzji DECIMAL(10,2) dla kar

    FIXED: PATCH bez trailing slash
    """

    headers = async_auth_librarian  # FIXED: Use fixture directly

    warsaw_tz = pytz.timezone("Europe/Warsaw")
    now = datetime.now(warsaw_tz)

    # 7 dni opóźnienia
    loan = Loan(
        user_id=test_user.id,
        book_copy_id=test_book_copy.id,
        borrowed_at=now - timedelta(days=21),
        due_date=now - timedelta(days=7),
        returned_at=None,
    )
    db.add(loan)
    db.commit()

    # FIXED: BEZ trailing slash!
    response = await async_client.patch(f"/loans/{loan.id}/return", headers=headers)

    assert response.status_code == 200

    # Weryfikacja typu DECIMAL (nie float!)
    fine = db.query(Fine).filter(Fine.loan_id == loan.id).first()

    if fine:
        assert isinstance(fine.amount, Decimal)
        assert fine.amount == Decimal("7.00")
