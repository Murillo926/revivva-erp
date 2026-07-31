from sqlalchemy.orm import Session
from app.models.account_payable_history import AccountPayableHistory


class AccountPayableHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, history: AccountPayableHistory) -> AccountPayableHistory:
        self.db.add(history)
        self.db.flush()
        return history
