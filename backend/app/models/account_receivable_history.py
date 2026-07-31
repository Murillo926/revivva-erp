from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.account_receivable import AccountReceivable
    from app.models.user import User

class AccountReceivableHistory(Base):
    __tablename__ = "accounts_receivable_history"
    __table_args__ = (
        CheckConstraint("status_anterior IS NULL OR status_anterior IN ('PENDENTE', 'PARCIAL', 'PAGO', 'CANCELADO')", name="ck_accounts_receivable_history_valid_previous_status"),
        CheckConstraint("status_novo IN ('PENDENTE', 'PARCIAL', 'PAGO', 'CANCELADO')", name="ck_accounts_receivable_history_valid_new_status"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_receivable_id: Mapped[int] = mapped_column(ForeignKey("accounts_receivable.id", ondelete="CASCADE"), nullable=False, index=True)
    status_anterior: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status_novo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    conta_receber: Mapped["AccountReceivable"] = relationship(back_populates="historico")
    realizado_por: Mapped["User | None"] = relationship(foreign_keys=[performed_by_user_id])
