from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.account_payable import AccountPayable
    from app.models.payment_method import PaymentMethod
    from app.models.user import User


class AccountPayablePayment(Base):
    __tablename__ = "accounts_payable_payments"
    __table_args__ = (CheckConstraint("valor > 0", name="ck_accounts_payable_payments_amount_positive"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_payable_id: Mapped[int] = mapped_column(ForeignKey("accounts_payable.id", ondelete="RESTRICT"), nullable=False, index=True)
    payment_method_id: Mapped[int] = mapped_column(ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False, index=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_pagamento: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    pago_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    conta_pagar: Mapped["AccountPayable"] = relationship(back_populates="pagamentos")
    forma_pagamento: Mapped["PaymentMethod"] = relationship()
    pago_por: Mapped["User | None"] = relationship(foreign_keys=[pago_por_user_id])
