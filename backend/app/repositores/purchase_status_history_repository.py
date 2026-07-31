from sqlalchemy.orm import Session
from app.models.purchase_status_history import PurchaseStatusHistory
class PurchaseStatusHistoryRepository:
    def __init__(self,db:Session): self.db=db
    def create(self,history:PurchaseStatusHistory)->PurchaseStatusHistory:
        self.db.add(history); self.db.flush(); return history
