from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Purchase(Base):
    __tablename__ = "purchases"
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_purchases_subtotal_non_negative"),
        CheckConstraint("desconto >= 0", name="ck_purchases_discount_non_negative"),
        CheckConstraint("frete >= 0", name="ck_purchases_freight_non_negative"),
        CheckConstraint("total >= 0", name="ck_purchases_total_non_negative"),
        CheckConstraint("desconto <= subtotal", name="ck_purchases_discount_not_greater_than_subtotal"),
        CheckConstraint("status IN ('AGUARDANDO_CONFIRMACAO','CONFIRMADA','CANCELADA')", name="ck_purchases_valid_status"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="RESTRICT"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="AGUARDANDO_CONFIRMACAO", server_default="AGUARDANDO_CONFIRMACAO", index=True, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12,2), default=Decimal("0.00"), server_default="0", nullable=False)
    desconto: Mapped[Decimal] = mapped_column(Numeric(12,2), default=Decimal("0.00"), server_default="0", nullable=False)
    frete: Mapped[Decimal] = mapped_column(Numeric(12,2), default=Decimal("0.00"), server_default="0", nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12,2), default=Decimal("0.00"), server_default="0", nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_por_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    confirmado_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    cancelado_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    confirmado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fornecedor = relationship("Supplier")
    itens = relationship("PurchaseItem", back_populates="compra", cascade="all, delete-orphan", order_by="PurchaseItem.id")
    historico_status = relationship("PurchaseStatusHistory", back_populates="compra", cascade="all, delete-orphan", order_by="PurchaseStatusHistory.criado_em")
