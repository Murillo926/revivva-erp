from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Sequence(Base):
    __tablename__ = "system_sequences"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    nome: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    prefixo: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    tamanho: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=4,
    )

    ultimo_numero: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )