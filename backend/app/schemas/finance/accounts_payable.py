from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountPayableCancel(BaseModel):
    observacao: str = Field(min_length=1, max_length=1000)


class AccountPayablePaymentCreate(BaseModel):
    payment_method_id: int = Field(gt=0)
    valor: Decimal = Field(gt=0, decimal_places=2)
    observacao: str | None = Field(default=None, max_length=1000)


class AccountPayablePaymentResponse(BaseModel):
    id: int
    account_payable_id: int
    payment_method_id: int
    valor: Decimal
    data_pagamento: datetime
    pago_por_user_id: int | None
    observacao: str | None
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountPayableHistoryResponse(BaseModel):
    id: int
    account_payable_id: int
    status_anterior: str | None
    status_novo: str
    performed_by_user_id: int | None
    observacao: str | None
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountPayableResponse(BaseModel):
    id: int
    codigo: str
    purchase_id: int
    supplier_id: int
    numero_parcela: int
    total_parcelas: int
    valor_original: Decimal
    valor_pago: Decimal
    saldo_restante: Decimal
    data_vencimento: date
    status: str
    observacao: str | None
    criado_por_user_id: int | None
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountPayableDetailsResponse(AccountPayableResponse):
    pagamentos: list[AccountPayablePaymentResponse] = Field(default_factory=list)
    historico: list[AccountPayableHistoryResponse] = Field(default_factory=list)
