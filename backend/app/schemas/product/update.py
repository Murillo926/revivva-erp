from decimal import Decimal

from pydantic import BaseModel, Field


class ProductUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=3,
        max_length=120,
    )

    descricao: str | None = Field(
        default=None,
        max_length=255,
    )

    preco: Decimal | None = Field(
        default=None,
        gt=0,
    )

    ativo: bool | None = None