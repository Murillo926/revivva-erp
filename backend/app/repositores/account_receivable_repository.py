from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account_receivable import AccountReceivable


class AccountReceivableRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        conta: AccountReceivable,
    ) -> AccountReceivable:

        self.db.add(conta)
        self.db.flush()
        self.db.refresh(conta)

        return conta

    def create_many(
        self,
        contas: list[AccountReceivable],
    ) -> list[AccountReceivable]:

        self.db.add_all(contas)
        self.db.flush()

        for conta in contas:
            self.db.refresh(conta)

        return contas

    def get_by_id(
        self,
        conta_id: int,
    ) -> AccountReceivable | None:

        return self.db.get(
            AccountReceivable,
            conta_id,
        )

    def get_by_codigo(
        self,
        codigo: str,
    ) -> AccountReceivable | None:

        stmt = (
            select(AccountReceivable)
            .where(
                AccountReceivable.codigo == codigo
            )
        )

        return self.db.scalar(stmt)

    def get_by_sale(
        self,
        sale_id: int,
    ) -> list[AccountReceivable]:

        stmt = (
            select(AccountReceivable)
            .where(
                AccountReceivable.sale_id == sale_id
            )
            .order_by(
                AccountReceivable.numero_parcela
            )
        )

        return list(
            self.db.scalars(stmt)
        )

    def list_all(self) -> list[AccountReceivable]:

        stmt = (
            select(AccountReceivable)
            .order_by(
                AccountReceivable.data_vencimento
            )
        )

        return list(
            self.db.scalars(stmt)
        )

    def list_pending(self) -> list[AccountReceivable]:

        stmt = (
            select(AccountReceivable)
            .where(
                AccountReceivable.status != "PAGO"
            )
            .order_by(
                AccountReceivable.data_vencimento
            )
        )

        return list(
            self.db.scalars(stmt)
        )

    def list_overdue(
        self,
        hoje: date,
    ) -> list[AccountReceivable]:

        stmt = (
            select(AccountReceivable)
            .where(
                AccountReceivable.data_vencimento < hoje,
                AccountReceivable.status != "PAGO",
                AccountReceivable.status != "CANCELADO",
            )
            .order_by(
                AccountReceivable.data_vencimento
            )
        )

        return list(
            self.db.scalars(stmt)
        )

    def update(
        self,
        conta: AccountReceivable,
    ) -> AccountReceivable:

        self.db.flush()
        self.db.refresh(conta)

        return conta

    def delete(
        self,
        conta: AccountReceivable,
    ) -> None:

        self.db.delete(conta)
        self.db.flush()