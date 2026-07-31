from pydantic import BaseModel, Field


class AccountReceivableCancel(BaseModel):
    observacao: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Motivo do cancelamento.",
    )