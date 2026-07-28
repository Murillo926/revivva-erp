from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sale_item import SaleItem


class SaleItemRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        item: SaleItem,
    ) -> SaleItem:

        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)

        return item

    def create_many(
        self,
        items: list[SaleItem],
    ) -> None:

        self.db.add_all(items)
        self.db.flush()

    def list_by_sale(
        self,
        sale_id: int,
    ) -> list[SaleItem]:

        statement = (
            select(SaleItem)
            .where(
                SaleItem.sale_id == sale_id
            )
            .order_by(SaleItem.id)
        )

        return list(
            self.db.scalars(statement).all()
        )