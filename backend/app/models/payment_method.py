from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base
from app.models.mixins import AtivoMixin, TimestampMixin

class PaymentMethod(Base, AtivoMixin, TimestampMixin):
    __tablename__ = "payment_methods"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
