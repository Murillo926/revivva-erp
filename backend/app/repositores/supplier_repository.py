from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.supplier import Supplier

class SupplierRepository:
    def __init__(self, db: Session): self.db=db
    def create(self, supplier: Supplier)->Supplier:
        self.db.add(supplier); self.db.flush(); self.db.refresh(supplier); return supplier
    def save(self, supplier: Supplier)->Supplier:
        self.db.add(supplier); self.db.flush(); self.db.refresh(supplier); return supplier
    def get_by_id(self, supplier_id:int, for_update:bool=False)->Supplier|None:
        stmt=select(Supplier).where(Supplier.id==supplier_id)
        if for_update: stmt=stmt.with_for_update()
        return self.db.scalar(stmt)
    def get_by_document(self, documento:str)->Supplier|None:
        return self.db.scalar(select(Supplier).where(Supplier.documento==documento))
    def list_all(self, only_active:bool=False)->list[Supplier]:
        stmt=select(Supplier)
        if only_active: stmt=stmt.where(Supplier.ativo.is_(True))
        return list(self.db.scalars(stmt.order_by(Supplier.nome)).all())
