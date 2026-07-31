from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class PurchaseStatusHistory(Base):
    __tablename__ = "purchase_status_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id", ondelete="CASCADE"), index=True, nullable=False)
    status_anterior: Mapped[str | None] = mapped_column(String(30))
    status_novo: Mapped[str] = mapped_column(String(30), nullable=False)
    performed_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    compra = relationship("Purchase", back_populates="historico_status")
