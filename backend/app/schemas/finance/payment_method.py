from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaymentMethodResponse(BaseModel):
    id: int
    nome: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)