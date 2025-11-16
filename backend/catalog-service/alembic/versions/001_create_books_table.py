"""Create books table

Revision ID: 001_books
Revises:
Create Date: 2024-11-15 21:00:00.000000

Wymaganie NF14: PostgreSQL migrations
Tworzy tabelę books dla katalogu książek.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "001_books"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Tworzy tabelę books.

    Zgodnie z diagramem klas - wszystkie kolumny Book.
    """
    op.create_table(
        "books",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("authors", sa.String(length=500), nullable=False),
        sa.Column("isbn", sa.String(length=20), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("pages", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(length=50), nullable=True, server_default="pl"),
        sa.Column("cover_url", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("genre", sa.String(length=100), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_by", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
    )

    # Indeksy dla wydajności wyszukiwania (Wymaganie F5, F6)
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_authors", "books", ["authors"])
    op.create_index("ix_books_isbn", "books", ["isbn"], unique=True)
    op.create_index("ix_books_genre", "books", ["genre"])

    # Trigger dla automatycznej aktualizacji updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    op.execute("""
        CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """
    Usuwa tabelę books.
    """
    op.execute("DROP TRIGGER IF EXISTS update_books_updated_at ON books;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    op.drop_index("ix_books_genre", table_name="books")
    op.drop_index("ix_books_isbn", table_name="books")
    op.drop_index("ix_books_authors", table_name="books")
    op.drop_index("ix_books_title", table_name="books")

    op.drop_table("books")
