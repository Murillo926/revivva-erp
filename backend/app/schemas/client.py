from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import AddressType


class ClientAddressCreate(BaseModel):
    tipo: AddressType
    rua: str = Field(min_length=2, max_length=150)
    numero: str = Field(min_length=1, max_length=20)
    bairro: str = Field(min_length=2, max_length=100)
    cidade: str = Field(min_length=2, max_length=100)
    complemento: str | None = Field(default=None, max_length=150)
    referencia: str | None = Field(default=None, max_length=200)


class ClientCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    cpf: str = Field(min_length=11, max_length=14)
    telefone: str = Field(min_length=8, max_length=20)
    enderecos: list[ClientAddressCreate] = Field(min_length=1, max_length=2)

    @model_validator(mode="after")
    def validate_addresses(self):
        residential_count = sum(
            address.tipo == AddressType.RESIDENCIAL
            for address in self.enderecos
        )

        work_count = sum(
            address.tipo == AddressType.TRABALHO
            for address in self.enderecos
        )

        if residential_count != 1:
            raise ValueError(
                "O cliente deve possuir exatamente um endereço residencial."
            )

        if work_count > 1:
            raise ValueError(
                "O cliente pode possuir no máximo um endereço de trabalho."
            )

        return self


class ClientAddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: AddressType
    rua: str
    numero: str
    bairro: str
    cidade: str
    complemento: str | None
    referencia: str | None


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    cpf: str
    telefone: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    enderecos: list[ClientAddressResponse]