from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

class AtivoMixin:
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
