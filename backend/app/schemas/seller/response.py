from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SellerResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    cpf: str
    telefone: str
    percentual_comissao: Decimal
    user_id: int | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )