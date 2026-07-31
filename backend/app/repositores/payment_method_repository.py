from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment_method import PaymentMethod


class PaymentMethodRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        payment_method_id: int,
    ) -> PaymentMethod | None:

        return self.db.get(
            PaymentMethod,
            payment_method_id,
        )

    def list_active(self) -> list[PaymentMethod]:

        stmt = (
            select(PaymentMethod)
            .where(
                PaymentMethod.ativo.is_(True)
            )
            .order_by(
                PaymentMethod.nome
            )
        )

        return list(
            self.db.scalars(stmt)
        )