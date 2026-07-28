from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class SaleItemResponse(BaseModel):
    id: int

    product_id: int
    codigo_produto: str
    nome_produto: str

    quantidade: int

    preco_unitario: Decimal
    subtotal: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )