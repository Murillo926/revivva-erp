from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.stock import (
    StockAdjustmentCreate,
    StockEntryCreate,
    StockExitCreate,
    StockMovementResponse,
    StockResponse,
)
from app.services.stock_service import StockService


router = APIRouter(
    prefix="/stock",
    tags=["Stock"],
)


def handle_stock_error(error: ValueError) -> HTTPException:
    message = str(error)

    if message == "Produto não encontrado.":
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return HTTPException(
        status_code=status_code,
        detail=message,
    )


@router.get(
    "",
    response_model=list[StockResponse],
)
def list_stock(
    db: Session = Depends(get_db),
) -> list[StockResponse]:
    service = StockService(db)

    return service.list_all()


@router.get(
    "/{product_id}",
    response_model=StockResponse,
)
def get_product_stock(
    product_id: int,
    db: Session = Depends(get_db),
) -> StockResponse:
    service = StockService(db)

    try:
        return service.get_by_product_id(product_id)

    except ValueError as error:
        raise handle_stock_error(error) from error


@router.get(
    "/{product_id}/movements",
    response_model=list[StockMovementResponse],
)
def list_product_stock_movements(
    product_id: int,
    db: Session = Depends(get_db),
) -> list[StockMovementResponse]:
    service = StockService(db)

    try:
        return service.list_movements(product_id)

    except ValueError as error:
        raise handle_stock_error(error) from error


@router.post(
    "/entry",
    response_model=StockResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_stock_entry(
    data: StockEntryCreate,
    db: Session = Depends(get_db),
) -> StockResponse:
    service = StockService(db)

    try:
        return service.entry(data)

    except ValueError as error:
        raise handle_stock_error(error) from error


@router.post(
    "/exit",
    response_model=StockResponse,
    status_code=status.HTTP_200_OK,
)
def create_stock_exit(
    data: StockExitCreate,
    db: Session = Depends(get_db),
) -> StockResponse:
    service = StockService(db)

    try:
        return service.exit(data)

    except ValueError as error:
        raise handle_stock_error(error) from error


@router.post(
    "/adjustment",
    response_model=StockResponse,
    status_code=status.HTTP_200_OK,
)
def create_stock_adjustment(
    data: StockAdjustmentCreate,
    db: Session = Depends(get_db),
) -> StockResponse:
    service = StockService(db)

    try:
        return service.adjustment(data)

    except ValueError as error:
        raise handle_stock_error(error) from error