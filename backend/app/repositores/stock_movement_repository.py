from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.stock_movement import StockMovement


class StockMovementRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        movement: StockMovement,
    ) -> StockMovement:
        self.db.add(movement)
        self.db.flush()
        self.db.refresh(movement)

        return movement

    def list_by_product_id(
        self,
        product_id: int,
    ) -> list[tuple[StockMovement, Product]]:
        statement = (
            select(StockMovement, Product)
            .join(
                Product,
                Product.id == StockMovement.product_id,
            )
            .where(
                StockMovement.product_id == product_id
            )
            .order_by(
                StockMovement.criado_em.desc(),
                StockMovement.id.desc(),
            )
        )

        return list(self.db.execute(statement).all())