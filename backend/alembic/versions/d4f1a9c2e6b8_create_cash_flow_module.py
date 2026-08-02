"""create cash flow module

Revision ID: d4f1a9c2e6b8
Revises: c8a4e2f91b73
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4f1a9c2e6b8"
down_revision: Union[str, Sequence[str], None] = "c8a4e2f91b73"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cash_flow_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(40), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("codigo"),
        sa.UniqueConstraint("nome"),
        sa.CheckConstraint(
            "tipo IN ('ENTRADA', 'SAIDA')",
            name="ck_cash_flow_categories_valid_type",
        ),
    )
    for column in ["id", "codigo", "nome", "tipo"]:
        op.create_index(
            f"ix_cash_flow_categories_{column}",
            "cash_flow_categories",
            [column],
        )

    op.add_column(
        "cash_flow",
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("cash_flow_categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "cash_flow",
        sa.Column(
            "payment_method_id",
            sa.Integer(),
            sa.ForeignKey("payment_methods.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_cash_flow_category_id", "cash_flow", ["category_id"]
    )
    op.create_index(
        "ix_cash_flow_payment_method_id",
        "cash_flow",
        ["payment_method_id"],
    )

    op.execute(
        """
        INSERT INTO cash_flow_categories
            (codigo, nome, tipo, ativo)
        VALUES
            ('VENDAS', 'Recebimentos de vendas', 'ENTRADA', true),
            ('RECEITAS_DIVERSAS', 'Receitas diversas', 'ENTRADA', true),
            ('AJUSTES_ENTRADA', 'Ajustes positivos', 'ENTRADA', true),
            ('COMPRAS', 'Pagamentos de compras', 'SAIDA', true),
            ('DESPESAS_OPERACIONAIS', 'Despesas operacionais', 'SAIDA', true),
            ('COMISSOES', 'Comissões', 'SAIDA', true),
            ('AJUSTES_SAIDA', 'Ajustes negativos', 'SAIDA', true)
        ON CONFLICT (codigo) DO NOTHING
        """
    )

    op.execute(
        """
        UPDATE cash_flow
        SET category_id = (
            SELECT id FROM cash_flow_categories WHERE codigo = 'VENDAS'
        )
        WHERE tipo = 'ENTRADA' AND origem = 'VENDA'
        """
    )
    op.execute(
        """
        UPDATE cash_flow
        SET category_id = (
            SELECT id FROM cash_flow_categories WHERE codigo = 'COMPRAS'
        )
        WHERE tipo = 'SAIDA' AND origem = 'DESPESA'
          AND reference_type = 'ACCOUNT_PAYABLE_PAYMENT'
        """
    )


def downgrade() -> None:
    op.drop_index("ix_cash_flow_payment_method_id", table_name="cash_flow")
    op.drop_index("ix_cash_flow_category_id", table_name="cash_flow")
    op.drop_column("cash_flow", "payment_method_id")
    op.drop_column("cash_flow", "category_id")
    op.drop_table("cash_flow_categories")
