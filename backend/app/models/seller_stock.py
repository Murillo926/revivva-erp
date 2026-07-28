from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.seller import Seller
    from app.models.seller_stock_movement import SellerStockMovement


class SellerStock(Base):
    __tablename__ = "seller_stocks"

    __table_args__ = (
        UniqueConstraint(
            "seller_id",
            "product_id",
            name="uq_seller_stocks_seller_product",
        ),
        CheckConstraint(
            "quantidade >= 0",
            name="ck_seller_stocks_quantidade_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
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

    quantidade: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    vendedor: Mapped["Seller"] = relationship(
        foreign_keys=[seller_id],
    )

    produto: Mapped["Product"] = relationship(
        foreign_keys=[product_id],
    )

    movimentacoes: Mapped[list["SellerStockMovement"]] = relationship(
        back_populates="estoque_vendedor",
        cascade="save-update, merge",
    )