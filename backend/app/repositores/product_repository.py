from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)

        return product

    def get_by_id(self, product_id: int) -> Product | None:
        statement = select(Product).where(
            Product.id == product_id
        )

        return self.db.scalar(statement)

    def get_by_name(self, name: str) -> Product | None:
        statement = select(Product).where(
            Product.nome == name
        )

        return self.db.scalar(statement)

    def list_all(
        self,
        only_active: bool = False,
    ) -> list[Product]:
        statement = select(Product)

        if only_active:
            statement = statement.where(
                Product.ativo.is_(True)
            )

        statement = statement.order_by(Product.nome)

        return list(self.db.scalars(statement).all())

    def update(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)

        return product