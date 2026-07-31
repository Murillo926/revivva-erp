from sqlalchemy.orm import Session
from app.models.supplier import Supplier
from app.repositores.supplier_repository import SupplierRepository
from app.schemas.purchase import SupplierCreate,SupplierUpdate
class SupplierService:
    def __init__(self,db:Session): self.db=db; self.repository=SupplierRepository(db)
    def create(self,data:SupplierCreate)->Supplier:
        try:
            document=data.documento.strip() if data.documento else None
            if document and self.repository.get_by_document(document): raise ValueError("Já existe fornecedor com este documento.")
            supplier=Supplier(nome=data.nome.strip(),documento=document,email=data.email,telefone=data.telefone,observacao=data.observacao)
            self.repository.create(supplier); self.db.commit(); return self.repository.get_by_id(supplier.id)
        except Exception: self.db.rollback(); raise
    def get_by_id(self,supplier_id:int)->Supplier:
        supplier=self.repository.get_by_id(supplier_id)
        if not supplier: raise ValueError("Fornecedor não encontrado.")
        return supplier
    def list_all(self,only_active:bool=False): return self.repository.list_all(only_active)
    def update(self,supplier_id:int,data:SupplierUpdate)->Supplier:
        try:
            supplier=self.repository.get_by_id(supplier_id,True)
            if not supplier: raise ValueError("Fornecedor não encontrado.")
            values=data.model_dump(exclude_unset=True)
            if "documento" in values and values["documento"]:
                values["documento"]=values["documento"].strip(); existing=self.repository.get_by_document(values["documento"])
                if existing and existing.id!=supplier.id: raise ValueError("Já existe fornecedor com este documento.")
            if "nome" in values and values["nome"]: values["nome"]=values["nome"].strip()
            for key,value in values.items(): setattr(supplier,key,value)
            self.repository.save(supplier); self.db.commit(); return self.repository.get_by_id(supplier.id)
        except Exception: self.db.rollback(); raise
