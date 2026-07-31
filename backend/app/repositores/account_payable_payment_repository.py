from sqlalchemy.orm import Session
from app.models.account_payable_payment import AccountPayablePayment


class AccountPayablePaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payment: AccountPayablePayment) -> AccountPayablePayment:
        self.db.add(payment)
        self.db.flush()
        return payment
