from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.seller import Seller


class SellerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, seller: Seller) -> Seller:
        self.db.add(seller)
        self.db.flush()
        self.db.refresh(seller)

        return seller

    def get_by_id(
        self,
        seller_id: int,
    ) -> Seller | None:
        statement = select(Seller).where(
            Seller.id == seller_id
        )

        return self.db.scalar(statement)

    def get_by_code(
        self,
        code: str,
    ) -> Seller | None:
        statement = select(Seller).where(
            Seller.codigo == code
        )

        return self.db.scalar(statement)

    def get_by_cpf(
        self,
        cpf: str,
    ) -> Seller | None:
        statement = select(Seller).where(
            Seller.cpf == cpf
        )

        return self.db.scalar(statement)

    def get_by_user_id(
        self,
        user_id: int,
    ) -> Seller | None:
        statement = select(Seller).where(
            Seller.user_id == user_id
        )

        return self.db.scalar(statement)

    def list_all(
        self,
        only_active: bool = False,
    ) -> list[Seller]:
        statement = select(Seller)

        if only_active:
            statement = statement.where(
                Seller.ativo.is_(True)
            )

        statement = statement.order_by(
            Seller.nome
        )

        return list(
            self.db.scalars(statement).all()
        )

    def save(self, seller: Seller) -> Seller:
        self.db.add(seller)
        self.db.flush()
        self.db.refresh(seller)

        return seller