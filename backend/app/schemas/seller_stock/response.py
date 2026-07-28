from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SellerStockResponse(BaseModel):
    id: int
    seller_id: int
    product_id: int
    quantidade: int
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class SellerStockMovementResponse(BaseModel):
    id: int
    seller_stock_id: int
    seller_id: int
    product_id: int
    performed_by_user_id: int | None
    tipo: str
    quantidade: int
    quantidade_anterior: int
    quantidade_posterior: int
    observacao: str | None
    criado_em: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class SellerStockTransferResponse(BaseModel):
    general_stock_product_id: int
    general_stock_quantidade: int
    seller_stock: SellerStockResponse
    movement: SellerStockMovementResponse