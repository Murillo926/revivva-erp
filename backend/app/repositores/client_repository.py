from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.client import Client


class ClientRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        client: Client,
    ) -> Client:
        self.db.add(client)
        self.db.flush()
        self.db.refresh(client)

        return client

    def get_by_id(
        self,
        client_id: int,
    ) -> Client | None:
        statement = (
            select(Client)
            .options(
                selectinload(Client.enderecos)
            )
            .where(Client.id == client_id)
        )

        return self.db.scalar(statement)

    def get_by_cpf(
        self,
        cpf: str,
    ) -> Client | None:
        statement = (
            select(Client)
            .options(
                selectinload(Client.enderecos)
            )
            .where(Client.cpf == cpf)
        )

        return self.db.scalar(statement)

    def list_all(
        self,
        only_active: bool = False,
    ) -> list[Client]:

        statement = (
            select(Client)
            .options(
                selectinload(Client.enderecos)
            )
        )

        if only_active:
            statement = statement.where(
                Client.ativo.is_(True)
            )

        statement = statement.order_by(
            Client.nome
        )

        return list(
            self.db.scalars(statement).all()
        )

    def save(
        self,
        client: Client,
    ) -> Client:
        self.db.add(client)
        self.db.flush()
        self.db.refresh(client)

        return client