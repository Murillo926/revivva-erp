from sqlalchemy.orm import Session

from app.models.cash_flow import CashFlow


class CashFlowRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        flow: CashFlow,
    ) -> CashFlow:

        self.db.add(flow)
        self.db.flush()

        return flow