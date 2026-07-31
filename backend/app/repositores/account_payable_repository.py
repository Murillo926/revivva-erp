from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.account_payable import AccountPayable


class AccountPayableRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, account: AccountPayable) -> AccountPayable:
        self.db.add(account)
        self.db.flush()
        return account

    def get_by_id(self, account_id: int) -> AccountPayable | None:
        statement = select(AccountPayable).options(selectinload(AccountPayable.pagamentos), selectinload(AccountPayable.historico)).where(AccountPayable.id == account_id)
        return self.db.scalar(statement)

    def get_by_codigo(self, codigo: str) -> AccountPayable | None:
        statement = select(AccountPayable).options(selectinload(AccountPayable.pagamentos), selectinload(AccountPayable.historico)).where(AccountPayable.codigo == codigo)
        return self.db.scalar(statement)

    def get_by_purchase(self, purchase_id: int) -> list[AccountPayable]:
        statement = select(AccountPayable).where(AccountPayable.purchase_id == purchase_id).order_by(AccountPayable.numero_parcela)
        return list(self.db.scalars(statement).all())

    def list_all(self) -> list[AccountPayable]:
        statement = select(AccountPayable).order_by(AccountPayable.data_vencimento, AccountPayable.id)
        return list(self.db.scalars(statement).all())

    def list_pending(self) -> list[AccountPayable]:
        statement = select(AccountPayable).where(AccountPayable.status.in_(["PENDENTE", "PARCIAL"])).order_by(AccountPayable.data_vencimento, AccountPayable.id)
        return list(self.db.scalars(statement).all())

    def list_overdue(self, hoje: date) -> list[AccountPayable]:
        statement = select(AccountPayable).where(AccountPayable.data_vencimento < hoje, AccountPayable.status.in_(["PENDENTE", "PARCIAL"])).order_by(AccountPayable.data_vencimento, AccountPayable.id)
        return list(self.db.scalars(statement).all())
