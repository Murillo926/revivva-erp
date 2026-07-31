from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class AuditoriaMixin:
    criado_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    atualizado_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
