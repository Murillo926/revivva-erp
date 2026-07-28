from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.seller_stock_movement import (
    SellerStockMovement,
)


class SellerStockMovementRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        movement: SellerStockMovement,
    ) -> SellerStockMovement:
        self.db.add(movement)
        self.db.flush()
        self.db.refresh(movement)

        return movement

    def get_by_id(
        self,
        movement_id: int,
    ) -> SellerStockMovement | None:
        statement = select(
            SellerStockMovement
        ).where(
            SellerStockMovement.id == movement_id
        )

        return self.db.scalar(statement)

    def list_all(
        self,
    ) -> list[SellerStockMovement]:
        statement = select(
            SellerStockMovement
        ).order_by(
            SellerStockMovement.criado_em.desc(),
            SellerStockMovement.id.desc(),
        )

        return list(
            self.db.scalars(statement).all()
        )

    def list_by_seller(
        self,
        seller_id: int,
    ) -> list[SellerStockMovement]:
        statement = (
            select(SellerStockMovement)
            .where(
                SellerStockMovement.seller_id
                == seller_id
            )
            .order_by(
                SellerStockMovement.criado_em.desc(),
                SellerStockMovement.id.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def list_by_product(
        self,
        product_id: int,
    ) -> list[SellerStockMovement]:
        statement = (
            select(SellerStockMovement)
            .where(
                SellerStockMovement.product_id
                == product_id
            )
            .order_by(
                SellerStockMovement.criado_em.desc(),
                SellerStockMovement.id.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def list_by_seller_and_product(
        self,
        seller_id: int,
        product_id: int,
    ) -> list[SellerStockMovement]:
        statement = (
            select(SellerStockMovement)
            .where(
                SellerStockMovement.seller_id
                == seller_id,
                SellerStockMovement.product_id
                == product_id,
            )
            .order_by(
                SellerStockMovement.criado_em.desc(),
                SellerStockMovement.id.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def list_by_user(
        self,
        user_id: int,
    ) -> list[SellerStockMovement]:
        statement = (
            select(SellerStockMovement)
            .where(
                SellerStockMovement.performed_by_user_id
                == user_id
            )
            .order_by(
                SellerStockMovement.criado_em.desc(),
                SellerStockMovement.id.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )