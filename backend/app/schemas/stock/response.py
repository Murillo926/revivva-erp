from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StockResponse(BaseModel):
    id: int
    product_id: int
    codigo_produto: str
    nome_produto: str
    quantidade: int
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class StockMovementResponse(BaseModel):
    id: int
    stock_id: int
    product_id: int
    codigo_produto: str
    nome_produto: str
    tipo: str
    quantidade: int
    quantidade_anterior: int
    quantidade_posterior: int
    observacao: str | None
    criado_em: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )