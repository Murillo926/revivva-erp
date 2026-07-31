from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.constants.purchase_status import PurchaseStatus
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.purchase_status_history import PurchaseStatusHistory
from app.models.stock_movement import StockMovement
from app.repositores.product_repository import ProductRepository
from app.repositores.purchase_item_repository import PurchaseItemRepository
from app.repositores.purchase_repository import PurchaseRepository
from app.repositores.purchase_status_history_repository import PurchaseStatusHistoryRepository
from app.repositores.sequence_repository import SequenceRepository
from app.repositores.stock_movement_repository import StockMovementRepository
from app.repositores.stock_repository import StockRepository
from app.repositores.supplier_repository import SupplierRepository
from app.schemas.purchase import PurchaseCreate, PurchaseUpdate, PurchaseConfirm
from app.services.account_payable_service import AccountPayableService

class PurchaseService:
    SEQUENCE_NAME="PURCHASE"
    def __init__(self,db:Session):
        self.db=db; self.purchase_repository=PurchaseRepository(db); self.item_repository=PurchaseItemRepository(db)
        self.history_repository=PurchaseStatusHistoryRepository(db); self.supplier_repository=SupplierRepository(db)
        self.product_repository=ProductRepository(db); self.stock_repository=StockRepository(db)
        self.movement_repository=StockMovementRepository(db); self.sequence_repository=SequenceRepository(db)
        self.account_payable_service=AccountPayableService(db)
    @staticmethod
    def _money(value): return Decimal(value).quantize(Decimal("0.01"))
    def _supplier(self,supplier_id:int):
        supplier=self.supplier_repository.get_by_id(supplier_id)
        if not supplier: raise ValueError("Fornecedor não encontrado.")
        if not supplier.ativo: raise ValueError("O fornecedor está inativo.")
        return supplier
    def _products(self,data:PurchaseCreate):
        ids=[i.product_id for i in data.itens]
        if len(ids)!=len(set(ids)): raise ValueError("Um mesmo produto não pode aparecer mais de uma vez na compra.")
        result={}
        for pid in ids:
            product=self.product_repository.get_by_id(pid)
            if not product: raise ValueError(f"Produto {pid} não encontrado.")
            if not product.ativo: raise ValueError(f"O produto {product.nome} está inativo.")
            result[pid]=product
        return result
    def _history(self,purchase_id,old,new,user_id,obs):
        self.history_repository.create(PurchaseStatusHistory(purchase_id=purchase_id,status_anterior=old,status_novo=new,performed_by_user_id=user_id,observacao=obs))
    def create(self,data:PurchaseCreate,performed_by_user_id:int)->Purchase:
        try:
            supplier=self._supplier(data.supplier_id); products=self._products(data)
            purchase=Purchase(codigo=self.sequence_repository.next_code(self.SEQUENCE_NAME),supplier_id=supplier.id,status=PurchaseStatus.AGUARDANDO,desconto=self._money(data.desconto),frete=self._money(data.frete),observacao=data.observacao,criado_por_user_id=performed_by_user_id)
            self.purchase_repository.create(purchase)
            subtotal=Decimal("0.00"); items=[]
            for item_data in data.itens:
                p=products[item_data.product_id]; cost=self._money(item_data.custo_unitario); item_sub=self._money(cost*item_data.quantidade); subtotal+=item_sub
                items.append(PurchaseItem(purchase_id=purchase.id,product_id=p.id,codigo_produto=p.codigo,nome_produto=p.nome,quantidade=item_data.quantidade,custo_unitario=cost,subtotal=item_sub))
            self.item_repository.create_many(items); purchase.subtotal=self._money(subtotal)
            if purchase.desconto>purchase.subtotal: raise ValueError("O desconto não pode ser maior que o subtotal.")
            purchase.total=self._money(purchase.subtotal-purchase.desconto+purchase.frete); self.purchase_repository.save(purchase)
            self._history(purchase.id,None,PurchaseStatus.AGUARDANDO,performed_by_user_id,"Compra criada e enviada para confirmação.")
            self.db.commit(); return self.get_by_id(purchase.id)
        except Exception: self.db.rollback(); raise
    def get_by_id(self,purchase_id:int)->Purchase:
        p=self.purchase_repository.get_by_id(purchase_id)
        if not p: raise ValueError("Compra não encontrada.")
        return p
    def get_by_codigo(self,codigo:str)->Purchase:
        p=self.purchase_repository.get_by_codigo(codigo.strip().upper())
        if not p: raise ValueError("Compra não encontrada.")
        return p
    def list_all(self,status:str|None=None,supplier_id:int|None=None):
        normalized=status.strip().upper() if status else None
        if normalized and normalized not in PurchaseStatus.ALL: raise ValueError("Status de compra inválido.")
        return self.purchase_repository.list_all(normalized,supplier_id)
    def update(self,purchase_id:int,data:PurchaseUpdate)->Purchase:
        try:
            p=self.purchase_repository.get_by_id(purchase_id,True)
            if not p: raise ValueError("Compra não encontrada.")
            if p.status!=PurchaseStatus.AGUARDANDO: raise ValueError("Somente compras aguardando confirmação podem ser alteradas.")
            values=data.model_dump(exclude_unset=True)
            if "supplier_id" in values: self._supplier(values["supplier_id"])
            for key,value in values.items(): setattr(p,key,self._money(value) if key in {"desconto","frete"} else value)
            if p.desconto>p.subtotal: raise ValueError("O desconto não pode ser maior que o subtotal.")
            p.total=self._money(p.subtotal-p.desconto+p.frete); self.purchase_repository.save(p); self.db.commit(); return self.get_by_id(p.id)
        except Exception: self.db.rollback(); raise
    def confirm(self,purchase_id:int,data:PurchaseConfirm,performed_by_user_id:int)->Purchase:
        try:
            p=self.purchase_repository.get_by_id(purchase_id,True)
            if not p: raise ValueError("Compra não encontrada.")
            if p.status==PurchaseStatus.CONFIRMADA: raise ValueError("A compra já está confirmada.")
            if p.status==PurchaseStatus.CANCELADA: raise ValueError("A compra está cancelada.")
            if not p.itens: raise ValueError("A compra não possui itens.")
            for item in sorted(p.itens,key=lambda x:x.product_id):
                stock=self.stock_repository.get_by_product_id(item.product_id,for_update=True)
                if stock is None: stock=self.stock_repository.create(item.product_id)
                before=stock.quantidade; stock.quantidade=before+item.quantidade; self.stock_repository.save(stock)
                self.movement_repository.create(StockMovement(stock_id=stock.id,product_id=item.product_id,tipo="ENTRADA_COMPRA",quantidade=item.quantidade,quantidade_anterior=before,quantidade_posterior=stock.quantidade,observacao=f"Entrada referente à compra {p.codigo}."))
            old=p.status; p.status=PurchaseStatus.CONFIRMADA; p.confirmado_por_user_id=performed_by_user_id; p.confirmado_em=datetime.now(timezone.utc); self.purchase_repository.save(p)
            self._history(p.id,old,p.status,performed_by_user_id,data.observacao or "Compra confirmada e estoque atualizado.")
            self.account_payable_service.create_accounts_from_purchase(purchase=p,total_installments=data.total_parcelas,first_due_date=data.primeiro_vencimento,user_id=performed_by_user_id,observation=data.observacao)
            self.db.commit(); return self.get_by_id(p.id)
        except Exception: self.db.rollback(); raise
    def cancel(self,purchase_id:int,performed_by_user_id:int,observacao:str)->Purchase:
        try:
            p=self.purchase_repository.get_by_id(purchase_id,True)
            if not p: raise ValueError("Compra não encontrada.")
            if p.status==PurchaseStatus.CONFIRMADA: raise ValueError("Uma compra confirmada precisa ser estornada, não cancelada.")
            if p.status==PurchaseStatus.CANCELADA: raise ValueError("A compra já está cancelada.")
            obs=observacao.strip()
            if not obs: raise ValueError("Informe o motivo do cancelamento.")
            old=p.status; p.status=PurchaseStatus.CANCELADA; p.cancelado_por_user_id=performed_by_user_id; p.cancelado_em=datetime.now(timezone.utc); self.purchase_repository.save(p)
            self._history(p.id,old,p.status,performed_by_user_id,obs); self.db.commit(); return self.get_by_id(p.id)
        except Exception: self.db.rollback(); raise
