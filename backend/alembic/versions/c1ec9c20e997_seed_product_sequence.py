"""seed product sequence

Revision ID: c1ec9c20e997
Revises: 2596385ebcd5
Create Date: 2026-07-28 02:00:24.701964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1ec9c20e997'
down_revision: Union[str, Sequence[str], None] = '2596385ebcd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("""
            INSERT INTO system_sequences
                (nome, prefixo, tamanho, ultimo_numero)
            VALUES
                ('PRODUCT', 'KIT', 4, 0)
        """)
    )


def downgrade() -> None:
    op.execute(
        sa.text("""
            DELETE FROM system_sequences
            WHERE nome = 'PRODUCT'
        """)
    )