from pydantic import BaseModel, Field, field_validator


class SellerStockTransferCreate(BaseModel):
    seller_id: int = Field(
        ...,
        gt=0,
        description="ID do vendedor que receberá os produtos.",
    )

    product_id: int = Field(
        ...,
        gt=0,
        description="ID do produto transferido.",
    )

    quantidade: int = Field(
        ...,
        gt=0,
        description="Quantidade transferida ao vendedor.",
    )

    observacao: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("observacao")
    @classmethod
    def normalize_observation(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            return None

        return normalized


class SellerStockReturnCreate(BaseModel):
    seller_id: int = Field(
        ...,
        gt=0,
        description="ID do vendedor que devolverá os produtos.",
    )

    product_id: int = Field(
        ...,
        gt=0,
        description="ID do produto devolvido.",
    )

    quantidade: int = Field(
        ...,
        gt=0,
        description="Quantidade devolvida ao estoque geral.",
    )

    observacao: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("observacao")
    @classmethod
    def normalize_observation(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            return None

        return normalized