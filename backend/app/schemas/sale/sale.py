from datetime import datetime
from decimal import Decimal

from datetime import date
from pydantic import Field

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.sale.sale_item import (
    SaleItemCreate,
    SaleItemResponse,
)
from app.schemas.sale.sale_status_history import (
    SaleStatusHistoryResponse,
)


class SaleCreate(BaseModel):
    client_id: int = Field(gt=0)

    seller_id: int = Field(gt=0)

    observacao: str | None = Field(
        default=None,
        max_length=1000,
    )

    itens: list[SaleItemCreate] = Field(
        min_length=1,
    )


class SaleUpdate(BaseModel):
    client_id: int | None = Field(
        default=None,
        gt=0,
    )

    seller_id: int | None = Field(
        default=None,
        gt=0,
    )

    observacao: str | None = Field(
        default=None,
        max_length=1000,
    )


class SaleResponse(BaseModel):
    id: int

    codigo: str

    client_id: int

    seller_id: int

    status: str

    subtotal: Decimal

    desconto: Decimal

    total: Decimal

    observacao: str | None

    criado_por_user_id: int

    confirmado_por_user_id: int | None

    cancelado_por_user_id: int | None

    criado_em: datetime

    atualizado_em: datetime

    confirmado_em: datetime | None

    cancelado_em: datetime | None

    itens: list[SaleItemResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )


class SaleDetailsResponse(SaleResponse):
    historico_status: list[
        SaleStatusHistoryResponse
    ]


class SaleConfirm(BaseModel):
    observacao: str | None = Field(
        default=None,
        max_length=1000,
    )

    total_parcelas: int = Field(
        ge=1,
        le=120,
    )

    primeiro_vencimento: date


class SaleCancel(BaseModel):
    observacao: str = Field(
        min_length=1,
        max_length=1000,
    )