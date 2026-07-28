from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.seller import Seller
    from app.models.seller_stock import SellerStock
    from app.models.user import User


class SellerStockMovement(Base):
    __tablename__ = "seller_stock_movements"

    __table_args__ = (
        CheckConstraint(
            "quantidade > 0",
            name="ck_seller_stock_movements_quantidade_positive",
        ),
        CheckConstraint(
            "quantidade_anterior >= 0",
            name=(
                "ck_seller_stock_movements_"
                "quantidade_anterior_non_negative"
            ),
        ),
        CheckConstraint(
            "quantidade_posterior >= 0",
            name=(
                "ck_seller_stock_movements_"
                "quantidade_posterior_non_negative"
            ),
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    seller_stock_id: Mapped[int] = mapped_column(
        ForeignKey(
            "seller_stocks.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    seller_id: Mapped[int] = mapped_column(
        ForeignKey(
            "sellers.id",
            ondelete="RESTRICT",
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

    performed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    quantidade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    quantidade_anterior: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    quantidade_posterior: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    observacao: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    estoque_vendedor: Mapped["SellerStock"] = relationship(
        back_populates="movimentacoes",
        foreign_keys=[seller_stock_id],
    )

    vendedor: Mapped["Seller"] = relationship(
        foreign_keys=[seller_id],
    )

    produto: Mapped["Product"] = relationship(
        foreign_keys=[product_id],
    )

    realizado_por: Mapped["User | None"] = relationship(
        foreign_keys=[performed_by_user_id],
    )