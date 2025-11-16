"""Create book_copies table

Revision ID: 002_book_copies
Revises: 001_books
Create Date: 2024-11-15 21:05:00.000000

Wymaganie NF14: PostgreSQL migrations
Tworzy tabelę book_copies dla egzemplarzy książek.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "002_book_copies"
down_revision = "001_books"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Tworzy tabelę book_copies.

    Zgodnie z diagramem klas - wszystkie kolumny BookCopy.
    """
    # Najpierw tworzymy enum dla statusu
    op.execute("""
        CREATE TYPE copy_status AS ENUM (
            'AVAILABLE',
            'RESERVED',
            'BORROWED',
            'DAMAGED',
            'LOST'
        );
    """)

    op.create_table(
        "book_copies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("book_id", UUID(as_uuid=True), nullable=False),
        sa.Column("inventory_no", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "AVAILABLE",
                "RESERVED",
                "BORROWED",
                "DAMAGED",
                "LOST",
                name="copy_status",
                create_type=False,
            ),
            nullable=False,
            server_default="AVAILABLE",
        ),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        # Foreign key do books
        sa.ForeignKeyConstraint(
            ["book_id"], ["books.id"], name="fk_book_copies_book_id", ondelete="CASCADE"
        ),
    )

    # Indeksy dla wydajności
    op.create_index("ix_book_copies_book_id", "book_copies", ["book_id"])
    op.create_index(
        "ix_book_copies_inventory_no", "book_copies", ["inventory_no"], unique=True
    )
    op.create_index("ix_book_copies_status", "book_copies", ["status"])

    # Trigger dla automatycznej aktualizacji updated_at
    op.execute("""
        CREATE TRIGGER update_book_copies_updated_at BEFORE UPDATE ON book_copies
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    # Constraint: inventory_no musi być unikalny
    op.create_unique_constraint(
        "uq_book_copies_inventory_no", "book_copies", ["inventory_no"]
    )


def downgrade() -> None:
    """
    Usuwa tabelę book_copies.
    """
    op.execute("DROP TRIGGER IF EXISTS update_book_copies_updated_at ON book_copies;")

    op.drop_constraint("uq_book_copies_inventory_no", "book_copies", type_="unique")
    op.drop_constraint("fk_book_copies_book_id", "book_copies", type_="foreignkey")

    op.drop_index("ix_book_copies_status", table_name="book_copies")
    op.drop_index("ix_book_copies_inventory_no", table_name="book_copies")
    op.drop_index("ix_book_copies_book_id", table_name="book_copies")

    op.drop_table("book_copies")

    # Usuń enum type
    op.execute("DROP TYPE IF EXISTS copy_status;")
