from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.enums.conta_pagar_status import ContaPagarStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.account_payable_history import AccountPayableHistory
    from app.models.account_payable_payment import AccountPayablePayment
    from app.models.purchase import Purchase
    from app.models.supplier import Supplier
    from app.models.user import User


class AccountPayable(Base, TimestampMixin):
    __tablename__ = "accounts_payable"
    __table_args__ = (
        UniqueConstraint("purchase_id", "numero_parcela", name="uq_accounts_payable_purchase_installment"),
        CheckConstraint("numero_parcela > 0", name="ck_accounts_payable_installment_positive"),
        CheckConstraint("total_parcelas > 0", name="ck_accounts_payable_total_installments_positive"),
        CheckConstraint("numero_parcela <= total_parcelas", name="ck_accounts_payable_installment_within_total"),
        CheckConstraint("valor_original > 0", name="ck_accounts_payable_original_amount_positive"),
        CheckConstraint("valor_pago >= 0", name="ck_accounts_payable_paid_amount_nonnegative"),
        CheckConstraint("saldo_restante >= 0", name="ck_accounts_payable_remaining_amount_nonnegative"),
        CheckConstraint("valor_pago + saldo_restante = valor_original", name="ck_accounts_payable_amount_balance"),
        CheckConstraint("status IN ('PENDENTE','PARCIAL','PAGO','CANCELADO')", name="ck_accounts_payable_valid_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id", ondelete="RESTRICT"), nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True)
    numero_parcela: Mapped[int] = mapped_column(Integer, nullable=False)
    total_parcelas: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_original: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    valor_pago: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), server_default="0.00", nullable=False)
    saldo_restante: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default=ContaPagarStatus.PENDENTE.value, server_default=ContaPagarStatus.PENDENTE.value, nullable=False, index=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    compra: Mapped["Purchase"] = relationship(foreign_keys=[purchase_id])
    fornecedor: Mapped["Supplier"] = relationship(foreign_keys=[supplier_id])
    criado_por: Mapped["User | None"] = relationship(foreign_keys=[criado_por_user_id])
    pagamentos: Mapped[list["AccountPayablePayment"]] = relationship(back_populates="conta_pagar", cascade="all, delete-orphan", order_by="AccountPayablePayment.data_pagamento")
    historico: Mapped[list["AccountPayableHistory"]] = relationship(back_populates="conta_pagar", cascade="all, delete-orphan", order_by="AccountPayableHistory.criado_em")
