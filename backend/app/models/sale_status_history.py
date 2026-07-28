from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.sale import Sale
    from app.models.user import User


class SaleStatusHistory(Base):
    __tablename__ = "sale_status_history"

    __table_args__ = (
        CheckConstraint(
            (
                "status_anterior IS NULL OR "
                "status_anterior IN ("
                "'AGUARDANDO_CONFIRMACAO', "
                "'CONFIRMADA', "
                "'CANCELADA'"
                ")"
            ),
            name="ck_sale_status_history_valid_previous_status",
        ),
        CheckConstraint(
            (
                "status_novo IN ("
                "'AGUARDANDO_CONFIRMACAO', "
                "'CONFIRMADA', "
                "'CANCELADA'"
                ")"
            ),
            name="ck_sale_status_history_valid_new_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    sale_id: Mapped[int] = mapped_column(
        ForeignKey(
            "sales.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    status_anterior: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    status_novo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    performed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    observacao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    venda: Mapped["Sale"] = relationship(
        back_populates="historico_status",
    )

    realizado_por: Mapped["User | None"] = relationship(
        foreign_keys=[performed_by_user_id],
    )