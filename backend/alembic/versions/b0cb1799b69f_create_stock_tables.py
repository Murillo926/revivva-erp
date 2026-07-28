"""create stock tables

Revision ID: b0cb1799b69f
Revises: c1ec9c20e997
Create Date: 2026-07-28 02:47:59.580686

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b0cb1799b69f"
down_revision: Union[str, Sequence[str], None] = "c1ec9c20e997"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "stocks",
        sa.Column(
            "id",
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
            name="ck_stocks_quantidade_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "product_id",
            name="uq_stocks_product_id",
        ),
    )

    op.create_index(
        op.f("ix_stocks_id"),
        "stocks",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_stocks_product_id"),
        "stocks",
        ["product_id"],
        unique=False,
    )

    op.create_table(
        "stock_movements",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "stock_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "tipo",
            sa.String(length=30),
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
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["stock_id"],
            ["stocks.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_stock_movements_id"),
        "stock_movements",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_stock_movements_product_id"),
        "stock_movements",
        ["product_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_stock_movements_stock_id"),
        "stock_movements",
        ["stock_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_stock_movements_tipo"),
        "stock_movements",
        ["tipo"],
        unique=False,
    )

    # Cria estoque com quantidade 0 para os produtos
    # que já existiam antes desta migration.
    op.execute(
        sa.text(
            """
            INSERT INTO stocks (
                product_id,
                quantidade
            )
            SELECT
                products.id,
                0
            FROM products
            WHERE NOT EXISTS (
                SELECT 1
                FROM stocks
                WHERE stocks.product_id = products.id
            )
            """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_stock_movements_tipo"),
        table_name="stock_movements",
    )

    op.drop_index(
        op.f("ix_stock_movements_stock_id"),
        table_name="stock_movements",
    )

    op.drop_index(
        op.f("ix_stock_movements_product_id"),
        table_name="stock_movements",
    )

    op.drop_index(
        op.f("ix_stock_movements_id"),
        table_name="stock_movements",
    )

    op.drop_table("stock_movements")

    op.drop_index(
        op.f("ix_stocks_product_id"),
        table_name="stocks",
    )

    op.drop_index(
        op.f("ix_stocks_id"),
        table_name="stocks",
    )

    op.drop_table("stocks")