from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AccountReceivableHistoryResponse(BaseModel):
    id: int

    account_receivable_id: int

    status_anterior: str | None

    status_novo: str

    performed_by_user_id: int | None

    observacao: str | None

    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)