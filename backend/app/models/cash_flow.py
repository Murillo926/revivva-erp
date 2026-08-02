from __future__ import annotations

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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.cash_flow_category import CashFlowCategory
    from app.models.payment_method import PaymentMethod
    from app.models.user import User


class CashFlow(Base):
    __tablename__ = "cash_flow"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('ENTRADA', 'SAIDA')",
            name="ck_cash_flow_valid_type",
        ),
        CheckConstraint(
            "origem IN ('VENDA', 'DESPESA', 'COMISSAO', 'AJUSTE')",
            name="ck_cash_flow_valid_origin",
        ),
        CheckConstraint("valor > 0", name="ck_cash_flow_amount_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    origem: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("cash_flow_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    payment_method_id: Mapped[int | None] = mapped_column(
        ForeignKey("payment_methods.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    reference_type: Mapped[str | None] = mapped_column(
        String(60), nullable=True, index=True
    )
    reference_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True
    )
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    performed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    categoria: Mapped["CashFlowCategory | None"] = relationship(
        back_populates="lancamentos"
    )
    forma_pagamento: Mapped["PaymentMethod | None"] = relationship()
    realizado_por: Mapped["User | None"] = relationship(
        foreign_keys=[performed_by_user_id]
    )
