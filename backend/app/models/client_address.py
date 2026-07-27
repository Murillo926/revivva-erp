from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.client import Client


class ClientAddress(Base):
    __tablename__ = "client_addresses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    rua: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    bairro: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    cidade: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    complemento: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    referencia: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    cliente: Mapped["Client"] = relationship(
        back_populates="enderecos",
    )