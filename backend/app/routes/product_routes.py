from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import ProductService


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    service = ProductService(db)

    try:
        return service.create(data)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=list[ProductResponse],
)
def list_products(
    only_active: bool = Query(
        default=False,
        description="Retorna apenas produtos ativos.",
    ),
    db: Session = Depends(get_db),
) -> list[ProductResponse]:
    service = ProductService(db)

    return service.list_all(
        only_active=only_active,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductResponse:
    service = ProductService(db)

    try:
        return service.get_by_id(product_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    service = ProductService(db)

    try:
        return service.update(
            product_id=product_id,
            data=data,
        )

    except ValueError as error:
        message = str(error)

        if message == "Produto não encontrado.":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error


@router.patch(
    "/{product_id}/deactivate",
    response_model=ProductResponse,
)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductResponse:
    service = ProductService(db)

    try:
        return service.deactivate(product_id)

    except ValueError as error:
        message = str(error)

        if message == "Produto não encontrado.":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error


@router.patch(
    "/{product_id}/activate",
    response_model=ProductResponse,
)
def activate_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductResponse:
    service = ProductService(db)

    try:
        return service.activate(product_id)

    except ValueError as error:
        message = str(error)

        if message == "Produto não encontrado.":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error