from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountReceivablePaymentCreate(BaseModel):
    payment_method_id: int

    valor: Decimal

    observacao: str | None = None


class AccountReceivablePaymentResponse(BaseModel):
    id: int

    account_receivable_id: int

    payment_method_id: int

    valor: Decimal

    data_pagamento: datetime

    recebido_por_user_id: int | None

    observacao: str | None

    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)