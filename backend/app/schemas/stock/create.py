from pydantic import BaseModel, Field


class StockEntryCreate(BaseModel):
    product_id: int = Field(
        ...,
        gt=0,
    )

    quantidade: int = Field(
        ...,
        gt=0,
    )

    observacao: str | None = Field(
        default=None,
        max_length=255,
    )


class StockExitCreate(BaseModel):
    product_id: int = Field(
        ...,
        gt=0,
    )

    quantidade: int = Field(
        ...,
        gt=0,
    )

    observacao: str | None = Field(
        default=None,
        max_length=255,
    )


class StockAdjustmentCreate(BaseModel):
    product_id: int = Field(
        ...,
        gt=0,
    )

    nova_quantidade: int = Field(
        ...,
        ge=0,
    )

    observacao: str = Field(
        ...,
        min_length=3,
        max_length=255,
    )