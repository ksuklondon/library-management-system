"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Identyfikatory migracji używane przez Alembic.
# revision       – unikalny identyfikator tej migracji
# down_revision  – identyfikator poprzedniej migracji (łańcuch migracji)
# branch_labels  – opcjonalne etykiety dla równoległych gałęzi migracji
# depends_on     – zależności od innych migracji
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """
    Migracja w górę – wykonywana podczas:
    - aktualizacji schematu,
    - wdrażania nowych zmian w bazie danych.

    Tutaj Alembic wstawi wygenerowane operacje, np.:
    op.create_table(...), op.add_column(...), op.create_index(...), itd.
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    Migracja w dół – wykonywana przy:
    - rollbacku,
    - powrocie do poprzednich zmian schematu.

    Zawiera odwrotność operacji z upgrade(), np.:
    op.drop_table(...), op.drop_column(...).
    """
    ${downgrades if downgrades else "pass"}
