"""create sellers table

Revision ID: ebb0f74547b6
Revises: b0cb1799b69f
Create Date: 2026-07-28 03:21:00.869942

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ebb0f74547b6"
down_revision: Union[str, Sequence[str], None] = "b0cb1799b69f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria a tabela de vendedores e sua sequência de códigos."""

    op.create_table(
        "sellers",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "codigo",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "nome",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "cpf",
            sa.String(length=11),
            nullable=False,
        ),
        sa.Column(
            "telefone",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "percentual_comissao",
            sa.Numeric(precision=5, scale=2),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "ativo",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_sellers_codigo"),
        "sellers",
        ["codigo"],
        unique=True,
    )

    op.create_index(
        op.f("ix_sellers_cpf"),
        "sellers",
        ["cpf"],
        unique=True,
    )

    op.create_index(
        op.f("ix_sellers_id"),
        "sellers",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_sellers_nome"),
        "sellers",
        ["nome"],
        unique=False,
    )

    op.create_index(
        op.f("ix_sellers_user_id"),
        "sellers",
        ["user_id"],
        unique=True,
    )

    op.execute(
        sa.text(
            """
            INSERT INTO system_sequences (
                nome,
                prefixo,
                tamanho,
                ultimo_numero
            )
            VALUES (
                'SELLER',
                'VDR',
                4,
                0
            )
            """
        )
    )


def downgrade() -> None:
    """Remove a tabela de vendedores e sua sequência."""

    op.execute(
        sa.text(
            """
            DELETE FROM system_sequences
            WHERE nome = 'SELLER'
            """
        )
    )

    op.drop_index(
        op.f("ix_sellers_user_id"),
        table_name="sellers",
    )

    op.drop_index(
        op.f("ix_sellers_nome"),
        table_name="sellers",
    )

    op.drop_index(
        op.f("ix_sellers_id"),
        table_name="sellers",
    )

    op.drop_index(
        op.f("ix_sellers_cpf"),
        table_name="sellers",
    )

    op.drop_index(
        op.f("ix_sellers_codigo"),
        table_name="sellers",
    )

    op.drop_table("sellers")