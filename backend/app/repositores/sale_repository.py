from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.sale import Sale


class SaleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        sale: Sale,
    ) -> Sale:
        self.db.add(sale)
        self.db.flush()

        return sale

    def save(
        self,
        sale: Sale,
    ) -> Sale:
        self.db.add(sale)
        self.db.flush()

        return sale

    def get_by_id(
        self,
        sale_id: int,
        for_update: bool = False,
        load_relationships: bool = True,
    ) -> Sale | None:
        statement = select(Sale).where(
            Sale.id == sale_id
        )

        if load_relationships:
            statement = statement.options(
                selectinload(Sale.itens),
                selectinload(Sale.historico_status),
            )

        if for_update:
            statement = statement.with_for_update()

        return self.db.scalar(statement)

    def get_by_codigo(
        self,
        codigo: str,
    ) -> Sale | None:
        statement = (
            select(Sale)
            .options(
                selectinload(Sale.itens),
                selectinload(Sale.historico_status),
            )
            .where(Sale.codigo == codigo)
        )

        return self.db.scalar(statement)

    def list_all(
        self,
        status: str | None = None,
        client_id: int | None = None,
        seller_id: int | None = None,
    ) -> list[Sale]:
        statement = select(Sale).options(
            selectinload(Sale.itens)
        )

        if status is not None:
            statement = statement.where(
                Sale.status == status
            )

        if client_id is not None:
            statement = statement.where(
                Sale.client_id == client_id
            )

        if seller_id is not None:
            statement = statement.where(
                Sale.seller_id == seller_id
            )

        statement = statement.order_by(
            Sale.criado_em.desc(),
            Sale.id.desc(),
        )

        return list(
            self.db.scalars(statement).all()
        )