from sqlalchemy.orm import Session

from app.models.account_receivable_payment import (
    AccountReceivablePayment,
)


class AccountReceivablePaymentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        payment: AccountReceivablePayment,
    ) -> AccountReceivablePayment:

        self.db.add(payment)
        self.db.flush()

        return payment