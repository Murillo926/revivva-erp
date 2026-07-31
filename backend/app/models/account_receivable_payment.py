from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.account_receivable import AccountReceivable
    from app.models.payment_method import PaymentMethod
    from app.models.user import User

class AccountReceivablePayment(Base):
    __tablename__ = "accounts_receivable_payments"
    __table_args__ = (CheckConstraint("valor > 0", name="ck_accounts_receivable_payments_amount_positive"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_receivable_id: Mapped[int] = mapped_column(ForeignKey("accounts_receivable.id", ondelete="RESTRICT"), nullable=False, index=True)
    payment_method_id: Mapped[int] = mapped_column(ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False, index=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_pagamento: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    recebido_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    conta_receber: Mapped["AccountReceivable"] = relationship(back_populates="pagamentos")
    forma_pagamento: Mapped["PaymentMethod"] = relationship()
    recebido_por: Mapped["User | None"] = relationship(foreign_keys=[recebido_por_user_id])
