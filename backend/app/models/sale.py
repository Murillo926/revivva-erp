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
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.sale_item import SaleItem
    from app.models.sale_status_history import SaleStatusHistory
    from app.models.seller import Seller
    from app.models.user import User


class Sale(Base):
    __tablename__ = "sales"

    __table_args__ = (
        CheckConstraint(
            "subtotal >= 0",
            name="ck_sales_subtotal_non_negative",
        ),
        CheckConstraint(
            "desconto >= 0",
            name="ck_sales_discount_non_negative",
        ),
        CheckConstraint(
            "total >= 0",
            name="ck_sales_total_non_negative",
        ),
        CheckConstraint(
            "desconto <= subtotal",
            name="ck_sales_discount_not_greater_than_subtotal",
        ),
        CheckConstraint(
            (
                "status IN ("
                "'AGUARDANDO_CONFIRMACAO', "
                "'CONFIRMADA', "
                "'CANCELADA'"
                ")"
            ),
            name="ck_sales_valid_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    codigo: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey(
            "clients.id",
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

    status: Mapped[str] = mapped_column(
        String(30),
        default="AGUARDANDO_CONFIRMACAO",
        server_default="AGUARDANDO_CONFIRMACAO",
        nullable=False,
        index=True,
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        server_default="0",
        nullable=False,
    )

    desconto: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        server_default="0",
        nullable=False,
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        server_default="0",
        nullable=False,
    )

    observacao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    criado_por_user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    confirmado_por_user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    cancelado_por_user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
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

    confirmado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cliente: Mapped["Client"] = relationship(
        foreign_keys=[client_id],
    )

    vendedor: Mapped["Seller"] = relationship(
        foreign_keys=[seller_id],
    )

    criado_por: Mapped["User"] = relationship(
        foreign_keys=[criado_por_user_id],
    )

    confirmado_por: Mapped["User | None"] = relationship(
        foreign_keys=[confirmado_por_user_id],
    )

    cancelado_por: Mapped["User | None"] = relationship(
        foreign_keys=[cancelado_por_user_id],
    )

    itens: Mapped[list["SaleItem"]] = relationship(
        back_populates="venda",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="SaleItem.id",
    )

    historico_status: Mapped[list["SaleStatusHistory"]] = relationship(
        back_populates="venda",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="SaleStatusHistory.criado_em",
    )