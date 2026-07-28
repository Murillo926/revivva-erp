from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class SellerCreate(BaseModel):
    nome: str = Field(
        ...,
        min_length=3,
        max_length=120,
    )

    cpf: str = Field(
        ...,
        min_length=11,
        max_length=14,
    )

    telefone: str = Field(
        ...,
        min_length=8,
        max_length=20,
    )

    percentual_comissao: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        decimal_places=2,
    )

    user_id: int | None = Field(
        default=None,
        gt=0,
    )

    @field_validator("cpf")
    @classmethod
    def normalize_cpf(cls, value: str) -> str:
        normalized = "".join(
            character
            for character in value
            if character.isdigit()
        )

        if len(normalized) != 11:
            raise ValueError(
                "O CPF deve possuir exatamente 11 números."
            )

        return normalized

    @field_validator("nome", "telefone")
    @classmethod
    def strip_text_fields(cls, value: str) -> str:
        return value.strip()