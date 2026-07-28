from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=120)
    descricao: str | None = Field(default=None, max_length=255)
    preco: Decimal = Field(..., gt=0)

    model_config = ConfigDict(
        from_attributes=True
    )
    