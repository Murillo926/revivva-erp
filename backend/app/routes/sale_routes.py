from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.sale.sale import (
    SaleCancel,
    SaleConfirm,
    SaleCreate,
    SaleDetailsResponse,
    SaleResponse,
    SaleUpdate,
)
from app.services.sale_service import SaleService
from app.security.auth import get_current_user

router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
)


@router.post(
    "",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> SaleResponse:
    service = SaleService(db)

    try:
        print(current_user)

        return service.create(
            data=data,
            performed_by_user_id=int(current_user["sub"]),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=list[SaleResponse],
)
def list_sales(
    db: Session = Depends(get_db),
) -> list[SaleResponse]:
    service = SaleService(db)

    return service.list_all()


@router.get(
    "/{sale_id}",
    response_model=SaleDetailsResponse,
)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
) -> SaleDetailsResponse:
    service = SaleService(db)

    try:
        return service.get_by_id(sale_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/code/{codigo}",
    response_model=SaleDetailsResponse,
)
def get_sale_by_code(
    codigo: str,
    db: Session = Depends(get_db),
) -> SaleDetailsResponse:
    service = SaleService(db)

    try:
        return service.get_by_codigo(codigo)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    "/{sale_id}",
    response_model=SaleResponse,
)
def update_sale(
    sale_id: int,
    data: SaleUpdate,
    db: Session = Depends(get_db),
) -> SaleResponse:
    service = SaleService(db)

    try:
        return service.update(
            sale_id=sale_id,
            data=data,
        )

    except ValueError as error:
        message = str(error)

        if message == "Venda não encontrada.":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error


@router.post(
    "/{sale_id}/confirm",
    response_model=SaleResponse,
)
def confirm_sale(
    sale_id: int,
    data: SaleConfirm,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> SaleResponse:
    service = SaleService(db)

    try:
        return service.confirm(
            sale_id=sale_id,
            data=data,
            performed_by_user_id=int(current_user["sub"]),
        )

    except ValueError as error:
        message = str(error)

        if message == "Venda não encontrada.":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error


@router.post(
    "/{sale_id}/cancel",
    response_model=SaleResponse,
)
def cancel_sale(
    sale_id: int,
    data: SaleCancel,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> SaleResponse:
    service = SaleService(db)

    try:
        return service.cancel(
            sale_id=sale_id,
            performed_by_user_id=int(current_user["sub"]),
            observacao=data.observacao,
        )

    except ValueError as error:
        message = str(error)

        if message == "Venda não encontrada.":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error