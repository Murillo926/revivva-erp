from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.sale import Sale


class SaleItem(Base):
    __tablename__ = "sale_items"

    __table_args__ = (
        UniqueConstraint(
            "sale_id",
            "product_id",
            name="uq_sale_items_sale_product",
        ),
        CheckConstraint(
            "quantidade > 0",
            name="ck_sale_items_quantity_positive",
        ),
        CheckConstraint(
            "preco_unitario >= 0",
            name="ck_sale_items_unit_price_non_negative",
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="ck_sale_items_subtotal_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    sale_id: Mapped[int] = mapped_column(
        ForeignKey(
            "sales.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    codigo_produto: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    nome_produto: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    quantidade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    preco_unitario: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    venda: Mapped["Sale"] = relationship(
        back_populates="itens",
    )

    produto: Mapped["Product"] = relationship(
        foreign_keys=[product_id],
    )   