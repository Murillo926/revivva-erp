from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class PurchaseItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)
    custo_unitario: Decimal = Field(ge=0, decimal_places=2)

class PurchaseItemResponse(BaseModel):
    id:int; product_id:int; codigo_produto:str; nome_produto:str; quantidade:int; custo_unitario:Decimal; subtotal:Decimal
    model_config=ConfigDict(from_attributes=True)

class PurchaseCreate(BaseModel):
    supplier_id:int=Field(gt=0)
    desconto:Decimal=Field(default=Decimal("0.00"),ge=0)
    frete:Decimal=Field(default=Decimal("0.00"),ge=0)
    observacao:str|None=Field(default=None,max_length=1000)
    itens:list[PurchaseItemCreate]=Field(min_length=1)

class PurchaseUpdate(BaseModel):
    supplier_id:int|None=Field(default=None,gt=0)
    desconto:Decimal|None=Field(default=None,ge=0)
    frete:Decimal|None=Field(default=None,ge=0)
    observacao:str|None=Field(default=None,max_length=1000)

class PurchaseConfirm(BaseModel):
    observacao:str|None=Field(default=None,max_length=1000)

class PurchaseCancel(BaseModel):
    observacao:str=Field(min_length=1,max_length=1000)

class PurchaseHistoryResponse(BaseModel):
    id:int; status_anterior:str|None; status_novo:str; performed_by_user_id:int; observacao:str|None; criado_em:datetime
    model_config=ConfigDict(from_attributes=True)

class PurchaseResponse(BaseModel):
    id:int; codigo:str; supplier_id:int; status:str; subtotal:Decimal; desconto:Decimal; frete:Decimal; total:Decimal; observacao:str|None
    criado_por_user_id:int; confirmado_por_user_id:int|None; cancelado_por_user_id:int|None
    criado_em:datetime; atualizado_em:datetime; confirmado_em:datetime|None; cancelado_em:datetime|None
    itens:list[PurchaseItemResponse]
    model_config=ConfigDict(from_attributes=True)
    
class PurchaseDetailsResponse(PurchaseResponse):
    historico_status:list[PurchaseHistoryResponse]
