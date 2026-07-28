from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.seller_stock import SellerStock


class SellerStockRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        seller_stock: SellerStock,
    ) -> SellerStock:
        self.db.add(seller_stock)
        self.db.flush()
        self.db.refresh(seller_stock)

        return seller_stock

    def get_by_id(
        self,
        seller_stock_id: int,
        for_update: bool = False,
    ) -> SellerStock | None:
        statement = select(SellerStock).where(
            SellerStock.id == seller_stock_id
        )

        if for_update:
            statement = statement.with_for_update()

        return self.db.scalar(statement)

    def get_by_seller_and_product(
        self,
        seller_id: int,
        product_id: int,
        for_update: bool = False,
    ) -> SellerStock | None:
        statement = select(SellerStock).where(
            SellerStock.seller_id == seller_id,
            SellerStock.product_id == product_id,
        )

        if for_update:
            statement = statement.with_for_update()

        return self.db.scalar(statement)

    def list_all(self) -> list[SellerStock]:
        statement = select(SellerStock).order_by(
            SellerStock.seller_id,
            SellerStock.product_id,
        )

        return list(
            self.db.scalars(statement).all()
        )

    def list_by_seller(
        self,
        seller_id: int,
    ) -> list[SellerStock]:
        statement = (
            select(SellerStock)
            .where(
                SellerStock.seller_id == seller_id
            )
            .order_by(
                SellerStock.product_id
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def list_by_product(
        self,
        product_id: int,
    ) -> list[SellerStock]:
        statement = (
            select(SellerStock)
            .where(
                SellerStock.product_id == product_id
            )
            .order_by(
                SellerStock.seller_id
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def save(
        self,
        seller_stock: SellerStock,
    ) -> SellerStock:
        self.db.add(seller_stock)
        self.db.flush()
        self.db.refresh(seller_stock)

        return seller_stock