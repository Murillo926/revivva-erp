from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models.purchase import Purchase

class PurchaseRepository:
    def __init__(self, db:Session): self.db=db
    def create(self,purchase:Purchase)->Purchase:
        self.db.add(purchase); self.db.flush(); return purchase
    def save(self,purchase:Purchase)->Purchase:
        self.db.add(purchase); self.db.flush(); return purchase
    def get_by_id(self,purchase_id:int,for_update:bool=False,load_relationships:bool=True)->Purchase|None:
        stmt=select(Purchase).where(Purchase.id==purchase_id)
        if load_relationships: stmt=stmt.options(selectinload(Purchase.itens),selectinload(Purchase.historico_status))
        if for_update: stmt=stmt.with_for_update()
        return self.db.scalar(stmt)
    def get_by_codigo(self,codigo:str)->Purchase|None:
        return self.db.scalar(select(Purchase).where(Purchase.codigo==codigo).options(selectinload(Purchase.itens),selectinload(Purchase.historico_status)))
    def list_all(self,status:str|None=None,supplier_id:int|None=None)->list[Purchase]:
        stmt=select(Purchase).options(selectinload(Purchase.itens))
        if status: stmt=stmt.where(Purchase.status==status)
        if supplier_id: stmt=stmt.where(Purchase.supplier_id==supplier_id)
        return list(self.db.scalars(stmt.order_by(Purchase.criado_em.desc(),Purchase.id.desc())).all())
