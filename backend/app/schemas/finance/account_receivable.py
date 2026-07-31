from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountReceivableCreate(BaseModel):
    sale_id: int
    client_id: int

    numero_parcela: int
    total_parcelas: int

    valor_original: Decimal

    data_vencimento: date

    observacao: str | None = None


class AccountReceivableUpdate(BaseModel):
    observacao: str | None = None


class AccountReceivableResponse(BaseModel):
    id: int
    codigo: str

    sale_id: int
    client_id: int

    numero_parcela: int
    total_parcelas: int

    valor_original: Decimal
    valor_recebido: Decimal
    saldo_restante: Decimal

    data_vencimento: date

    status: str

    observacao: str | None

    criado_por_user_id: int | None

    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)