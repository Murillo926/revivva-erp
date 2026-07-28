from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class SellerUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=3,
        max_length=120,
    )

    cpf: str | None = Field(
        default=None,
        min_length=11,
        max_length=14,
    )

    telefone: str | None = Field(
        default=None,
        min_length=8,
        max_length=20,
    )

    percentual_comissao: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        decimal_places=2,
    )

    @field_validator("cpf")
    @classmethod
    def normalize_cpf(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

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
    def strip_text_fields(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.strip()


class SellerUserLink(BaseModel):
    user_id: int = Field(
        ...,
        gt=0,
    )