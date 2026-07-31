from sqlalchemy.orm import Session
from app.models.purchase_item import PurchaseItem
class PurchaseItemRepository:
    def __init__(self,db:Session): self.db=db
    def create_many(self,items:list[PurchaseItem])->list[PurchaseItem]:
        self.db.add_all(items); self.db.flush(); return items
    def delete_all(self,items:list[PurchaseItem])->None:
        for item in list(items): self.db.delete(item)
        self.db.flush()
