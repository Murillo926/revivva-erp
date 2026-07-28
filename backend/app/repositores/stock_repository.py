from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.stock import Stock


class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product_id: int) -> Stock:
        stock = Stock(
            product_id=product_id,
            quantidade=0,
        )

        self.db.add(stock)
        self.db.flush()
        self.db.refresh(stock)

        return stock

    def get_by_product_id(
        self,
        product_id: int,
        for_update: bool = False,
    ) -> Stock | None:
        statement = select(Stock).where(
            Stock.product_id == product_id
        )

        if for_update:
            statement = statement.with_for_update()

        return self.db.scalar(statement)

    def list_all(self) -> list[tuple[Stock, Product]]:
        statement = (
            select(Stock, Product)
            .join(
                Product,
                Product.id == Stock.product_id,
            )
            .order_by(Product.nome)
        )

        return list(self.db.execute(statement).all())

    def save(self, stock: Stock) -> Stock:
        self.db.add(stock)
        self.db.flush()
        self.db.refresh(stock)

        return stock