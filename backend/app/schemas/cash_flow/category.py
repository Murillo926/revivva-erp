from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CashFlowCategoryCreate(BaseModel):
    codigo: str = Field(min_length=2, max_length=40)
    nome: str = Field(min_length=2, max_length=100)
    tipo: str


class CashFlowCategoryResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    tipo: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)
