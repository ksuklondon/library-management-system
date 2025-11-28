"""Create initial tables for Loan Service

Revision ID: 001_create_tables
Revises:
Create Date: 2024-11-22 12:00:00.000000

Wymaganie: NF8 - Migracje bazy danych
Wymaganie: F8-F14, F27 - Rezerwacje, wypożyczenia, kary
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# Identyfikatory migracji używane przez Alembic.
# revision       – unikalny identyfikator migracji
# down_revision  – poprzednia migracja (None = pierwsza)
# branch_labels  – etykiety dla równoległych gałęzi
# depends_on     – zależności od innych migracji
revision = '001_create_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Migracja w górę – tworzy wszystkie tabele wymagane
    przez Loan Service (NF8).

    Tworzone encje:
    - reservations  (F8-F10)
    - loans         (F11-F14, F27)
    - fines         (F27)

    Zawiera także definicje enumów oraz indeksów
    przyspieszających zapytania.
    """

    # -----------------------------------------------------
    # ENUM: ReservationStatus (F8-F10)
    # -----------------------------------------------------
    # Tworzymy typ wyliczeniowy dla statusów rezerwacji,
    # aby umożliwić szybkie filtrowanie i walidację na poziomie DB.
    op.execute("""
        CREATE TYPE reservation_status AS ENUM (
            'ACTIVE',
            'CANCELLED',
            'EXPIRED',
            'COMPLETED'
        )
    """)

    # -----------------------------------------------------
    # ENUM: LoanStatus (F11-F14, F27)
    # -----------------------------------------------------
    # Statusy wypożyczeń – wymagane do określenia stanu książki.
    op.execute("""
        CREATE TYPE loan_status AS ENUM (
            'ACTIVE',
            'RETURNED',
            'OVERDUE'
        )
    """)

    # -----------------------------------------------------
    # TABLE: reservations (F8-F10)
    # -----------------------------------------------------
    # Rezerwacje książek – każda może przypadać na user_id + book_id.
    op.create_table(
        'reservations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('book_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('book_copy_id', UUID(as_uuid=True), nullable=True),

        # Status w oparciu o enum DB
        sa.Column(
            'status',
            sa.Enum('ACTIVE', 'CANCELLED', 'EXPIRED', 'COMPLETED', name='reservation_status'),
            nullable=False,
            server_default='ACTIVE',
            index=True
        ),

        sa.Column('reserved_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime, nullable=False),

        # Soft-delete (NF19)
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('deleted_by', sa.String(255), nullable=True),

        # Audyt i logowanie zmian
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Indeksy optymalizujące częste zapytania
    op.create_index('idx_reservations_user_status', 'reservations', ['user_id', 'status'])
    op.create_index('idx_reservations_book_status', 'reservations', ['book_id', 'status'])

    # -----------------------------------------------------
    # TABLE: loans (F11-F14, F27)
    # -----------------------------------------------------
    # Wypożyczenia książek – kluczowy element systemu bibliotecznego.
    op.create_table(
        'loans',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('book_copy_id', UUID(as_uuid=True), nullable=False, index=True),

        sa.Column('borrowed_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('due_date', sa.DateTime, nullable=False),
        sa.Column('returned_at', sa.DateTime, nullable=True),

        # Status wypożyczenia
        sa.Column(
            'status',
            sa.Enum('ACTIVE', 'RETURNED', 'OVERDUE', name='loan_status'),
            nullable=False,
            server_default='ACTIVE',
            index=True
        ),

        # Bieżąca naliczona kara (aktualizowana przy zwrocie)
        sa.Column('fine_amount', sa.Float, nullable=True, server_default='0.0'),

        # Soft-delete (NF19)
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('deleted_by', sa.String(255), nullable=True),

        # Audyt
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Indeksy dla częstych zapytań wypożyczeń
    op.create_index('idx_loans_user_status', 'loans', ['user_id', 'status'])
    op.create_index('idx_loans_due_date', 'loans', ['due_date'])
    op.create_index('idx_loans_book_copy', 'loans', ['book_copy_id'])

    # -----------------------------------------------------
    # TABLE: fines (F27)
    # -----------------------------------------------------
    # Kary za przetrzymanie wypożyczeń.
    op.create_table(
        'fines',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('loan_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),

        sa.Column('amount', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('paid', sa.Boolean, nullable=False, server_default='false', index=True),
        sa.Column('paid_at', sa.DateTime, nullable=True),

        # Soft-delete
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('deleted_by', sa.String(255), nullable=True),

        # Audyt
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Relacja fines → loans
    op.create_foreign_key(
        'fk_fines_loan_id',
        'fines',
        'loans',
        ['loan_id'],
        ['id'],
        ondelete='CASCADE'   # Usunięcie wypożyczenia usuwa karę
    )

    op.create_index('idx_fines_user_paid', 'fines', ['user_id', 'paid'])
    op.create_index('idx_fines_loan', 'fines', ['loan_id'])


def downgrade() -> None:
    """
    Migracja w dół – usuwa wszystkie tabele Loan Service
    oraz powiązane typy ENUM (NF8).
    """

    # Usuwamy tabele w odwrotnej kolejności (zależności!)
    op.drop_table('fines')
    op.drop_table('loans')
    op.drop_table('reservations')

    # Usuwamy typy ENUM (jeżeli istnieją)
    op.execute('DROP TYPE IF EXISTS loan_status')
    op.execute('DROP TYPE IF EXISTS reservation_status')
