from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sale_status_history import (
    SaleStatusHistory,
)


class SaleStatusHistoryRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        history: SaleStatusHistory,
    ) -> SaleStatusHistory:

        self.db.add(history)
        self.db.flush()
        self.db.refresh(history)

        return history

    def list_by_sale(
        self,
        sale_id: int,
    ) -> list[SaleStatusHistory]:

        statement = (
            select(SaleStatusHistory)
            .where(
                SaleStatusHistory.sale_id == sale_id
            )
            .order_by(
                SaleStatusHistory.criado_em
            )
        )

        return list(
            self.db.scalars(statement).all()
        )