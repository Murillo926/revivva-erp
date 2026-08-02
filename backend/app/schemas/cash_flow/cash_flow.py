from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.cash_flow.category import CashFlowCategoryResponse
from app.schemas.finance.payment_method import PaymentMethodResponse


class CashFlowManualCreate(BaseModel):
    tipo: str
    category_id: int
    payment_method_id: int | None = None
    descricao: str = Field(min_length=2, max_length=1000)
    valor: Decimal = Field(gt=0)


class CashFlowResponse(BaseModel):
    id: int
    tipo: str
    origem: str
    category_id: int | None
    payment_method_id: int | None
    reference_type: str | None
    reference_id: int | None
    descricao: str
    valor: Decimal
    performed_by_user_id: int | None
    criado_em: datetime
    categoria: CashFlowCategoryResponse | None = None
    forma_pagamento: PaymentMethodResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class CashFlowSummaryResponse(BaseModel):
    periodo_inicio: datetime | None
    periodo_fim: datetime | None
    entradas: Decimal
    saidas: Decimal
    saldo_periodo: Decimal
    saldo_atual: Decimal


class CashFlowDailyPointResponse(BaseModel):
    data: date
    entradas: Decimal
    saidas: Decimal
    saldo: Decimal


class CashFlowCategoryTotalResponse(BaseModel):
    category_id: int | None
    categoria: str
    tipo: str
    total: Decimal
