from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cash_flow_category import CashFlowCategory


class CashFlowCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, category: CashFlowCategory) -> CashFlowCategory:
        self.db.add(category)
        self.db.flush()
        self.db.refresh(category)
        return category

    def get_by_id(self, category_id: int) -> CashFlowCategory | None:
        return self.db.get(CashFlowCategory, category_id)

    def get_by_code(self, code: str) -> CashFlowCategory | None:
        statement = select(CashFlowCategory).where(
            CashFlowCategory.codigo == code
        )
        return self.db.scalar(statement)

    def list_all(
        self,
        only_active: bool = False,
        tipo: str | None = None,
    ) -> list[CashFlowCategory]:
        statement = select(CashFlowCategory)

        if only_active:
            statement = statement.where(CashFlowCategory.ativo.is_(True))

        if tipo is not None:
            statement = statement.where(CashFlowCategory.tipo == tipo)

        statement = statement.order_by(CashFlowCategory.nome)
        return list(self.db.scalars(statement).all())
