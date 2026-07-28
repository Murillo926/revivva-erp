from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    stock_id: Mapped[int] = mapped_column(
        ForeignKey(
            "stocks.id",
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

    tipo: Mapped[str] = mapped_column(
        String(30),
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
    )