"""create seller stocks

Revision ID: e0940882a83c
Revises: ebb0f74547b6
Create Date: 2026-07-28 14:14:30.217376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0940882a83c'
down_revision: Union[str, Sequence[str], None] = 'ebb0f74547b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria o estoque por vendedor e seu histórico."""

    op.create_table(
        "seller_stocks",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "seller_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "quantidade",
            sa.Integer(),
            server_default="0",
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
        sa.CheckConstraint(
            "quantidade >= 0",
            name="ck_seller_stocks_quantidade_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["sellers.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "seller_id",
            "product_id",
            name="uq_seller_stocks_seller_product",
        ),
    )

    op.create_index(
        op.f("ix_seller_stocks_id"),
        "seller_stocks",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_seller_stocks_product_id"),
        "seller_stocks",
        ["product_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_seller_stocks_seller_id"),
        "seller_stocks",
        ["seller_id"],
        unique=False,
    )

    op.create_table(
        "seller_stock_movements",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "seller_stock_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "seller_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "performed_by_user_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "tipo",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "quantidade",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "quantidade_anterior",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "quantidade_posterior",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "observacao",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantidade > 0",
            name=(
                "ck_seller_stock_movements_"
                "quantidade_positive"
            ),
        ),
        sa.CheckConstraint(
            "quantidade_anterior >= 0",
            name=(
                "ck_seller_stock_movements_"
                "quantidade_anterior_non_negative"
            ),
        ),
        sa.CheckConstraint(
            "quantidade_posterior >= 0",
            name=(
                "ck_seller_stock_movements_"
                "quantidade_posterior_non_negative"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["performed_by_user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["sellers.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["seller_stock_id"],
            ["seller_stocks.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_seller_stock_movements_criado_em"),
        "seller_stock_movements",
        ["criado_em"],
        unique=False,
    )

    op.create_index(
        op.f("ix_seller_stock_movements_id"),
        "seller_stock_movements",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_seller_stock_movements_"
            "performed_by_user_id"
        ),
        "seller_stock_movements",
        ["performed_by_user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_seller_stock_movements_product_id"),
        "seller_stock_movements",
        ["product_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_seller_stock_movements_seller_id"),
        "seller_stock_movements",
        ["seller_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_seller_stock_movements_"
            "seller_stock_id"
        ),
        "seller_stock_movements",
        ["seller_stock_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_seller_stock_movements_tipo"),
        "seller_stock_movements",
        ["tipo"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Remove o estoque por vendedor e seu histórico."""

    op.drop_index(
        op.f("ix_seller_stock_movements_tipo"),
        table_name="seller_stock_movements",
    )

    op.drop_index(
        op.f(
            "ix_seller_stock_movements_"
            "seller_stock_id"
        ),
        table_name="seller_stock_movements",
    )

    op.drop_index(
        op.f("ix_seller_stock_movements_seller_id"),
        table_name="seller_stock_movements",
    )

    op.drop_index(
        op.f("ix_seller_stock_movements_product_id"),
        table_name="seller_stock_movements",
    )

    op.drop_index(
        op.f(
            "ix_seller_stock_movements_"
            "performed_by_user_id"
        ),
        table_name="seller_stock_movements",
    )

    op.drop_index(
        op.f("ix_seller_stock_movements_id"),
        table_name="seller_stock_movements",
    )

    op.drop_index(
        op.f("ix_seller_stock_movements_criado_em"),
        table_name="seller_stock_movements",
    )

    op.drop_table("seller_stock_movements")

    op.drop_index(
        op.f("ix_seller_stocks_seller_id"),
        table_name="seller_stocks",
    )

    op.drop_index(
        op.f("ix_seller_stocks_product_id"),
        table_name="seller_stocks",
    )

    op.drop_index(
        op.f("ix_seller_stocks_id"),
        table_name="seller_stocks",
    )

    op.drop_table("seller_stocks")
    # ### end Alembic commands ###
