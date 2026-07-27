from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import UserRole


class UserCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    login: str = Field(min_length=3, max_length=80)
    senha: str = Field(min_length=8, max_length=128)
    cargo: UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    login: str
    cargo: UserRole
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    ultimo_login: datetime | None