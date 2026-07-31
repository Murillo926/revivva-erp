from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    __table_args__ = (UniqueConstraint("purchase_id","product_id",name="uq_purchase_items_purchase_product"), CheckConstraint("quantidade > 0",name="ck_purchase_items_quantity_positive"), CheckConstraint("custo_unitario >= 0",name="ck_purchase_items_cost_non_negative"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), index=True, nullable=False)
    codigo_produto: Mapped[str] = mapped_column(String(20), nullable=False)
    nome_produto: Mapped[str] = mapped_column(String(120), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    custo_unitario: Mapped[Decimal] = mapped_column(Numeric(12,2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12,2), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    compra = relationship("Purchase", back_populates="itens")
