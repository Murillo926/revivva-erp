from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class SupplierCreate(BaseModel):
    nome: str = Field(min_length=2,max_length=120)
    documento: str | None = Field(default=None,max_length=20)
    email: str | None = Field(default=None,max_length=150)
    telefone: str | None = Field(default=None,max_length=30)
    observacao: str | None = Field(default=None,max_length=1000)

class SupplierUpdate(BaseModel):
    nome: str | None = Field(default=None,min_length=2,max_length=120)
    documento: str | None = Field(default=None,max_length=20)
    email: str | None = Field(default=None,max_length=150)
    telefone: str | None = Field(default=None,max_length=30)
    observacao: str | None = Field(default=None,max_length=1000)
    ativo: bool | None = None

class SupplierResponse(SupplierCreate):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    model_config = ConfigDict(from_attributes=True)
