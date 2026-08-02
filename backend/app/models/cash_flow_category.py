from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import AtivoMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.cash_flow import CashFlow


class CashFlowCategory(Base, AtivoMixin, TimestampMixin):
    __tablename__ = "cash_flow_categories"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('ENTRADA', 'SAIDA')",
            name="ck_cash_flow_categories_valid_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    lancamentos: Mapped[list["CashFlow"]] = relationship(
        back_populates="categoria"
    )
