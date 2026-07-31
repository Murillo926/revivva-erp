from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CashFlowResponse(BaseModel):
    id: int

    tipo: str

    origem: str

    reference_type: str | None

    reference_id: int | None

    descricao: str

    valor: Decimal

    performed_by_user_id: int | None

    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)