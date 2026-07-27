from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.client import Client


class ClientRepository:
    def get_by_cpf(
        self,
        db: Session,
        cpf: str,
    ) -> Client | None:
        statement = (
            select(Client)
            .options(selectinload(Client.enderecos))
            .where(Client.cpf == cpf)
        )

        return db.scalar(statement)

    def create(
        self,
        db: Session,
        client: Client,
    ) -> Client:
        try:
            db.add(client)
            db.commit()
            db.refresh(client)

            return self.get_by_cpf(
                db=db,
                cpf=client.cpf,
            )

        except Exception:
            db.rollback()
            raise