from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.enums.conta_receber_status import ContaReceberStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.account_receivable_history import AccountReceivableHistory
    from app.models.account_receivable_payment import AccountReceivablePayment
    from app.models.client import Client
    from app.models.sale import Sale
    from app.models.user import User

class AccountReceivable(Base, TimestampMixin):
    __tablename__ = "accounts_receivable"
    __table_args__ = (
        UniqueConstraint("sale_id", "numero_parcela", name="uq_accounts_receivable_sale_installment"),
        CheckConstraint("numero_parcela > 0", name="ck_accounts_receivable_installment_positive"),
        CheckConstraint("total_parcelas > 0", name="ck_accounts_receivable_total_installments_positive"),
        CheckConstraint("numero_parcela <= total_parcelas", name="ck_accounts_receivable_installment_within_total"),
        CheckConstraint("valor_original > 0", name="ck_accounts_receivable_original_amount_positive"),
        CheckConstraint("valor_recebido >= 0", name="ck_accounts_receivable_received_amount_nonnegative"),
        CheckConstraint("saldo_restante >= 0", name="ck_accounts_receivable_remaining_amount_nonnegative"),
        CheckConstraint("valor_recebido + saldo_restante = valor_original", name="ck_accounts_receivable_amount_balance"),
        CheckConstraint("status IN ('PENDENTE', 'PARCIAL', 'PAGO', 'CANCELADO')", name="ck_accounts_receivable_valid_status"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False, index=True)
    numero_parcela: Mapped[int] = mapped_column(Integer, nullable=False)
    total_parcelas: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_original: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    valor_recebido: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"), server_default="0.00")
    saldo_restante: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=ContaReceberStatus.PENDENTE.value, server_default=ContaReceberStatus.PENDENTE.value, index=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    venda: Mapped["Sale"] = relationship(foreign_keys=[sale_id])
    cliente: Mapped["Client"] = relationship(foreign_keys=[client_id])
    criado_por: Mapped["User | None"] = relationship(foreign_keys=[criado_por_user_id])
    pagamentos: Mapped[list["AccountReceivablePayment"]] = relationship(back_populates="conta_receber", cascade="all, delete-orphan", order_by="AccountReceivablePayment.data_pagamento")
    historico: Mapped[list["AccountReceivableHistory"]] = relationship(back_populates="conta_receber", cascade="all, delete-orphan", order_by="AccountReceivableHistory.criado_em")
