from sqlalchemy.orm import Session

from app.models.account_receivable_history import (
    AccountReceivableHistory,
)


class AccountReceivableHistoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        history: AccountReceivableHistory,
    ) -> AccountReceivableHistory:

        self.db.add(history)
        self.db.flush()

        return history