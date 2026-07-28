from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.seller import (
    SellerCreate,
    SellerResponse,
    SellerUpdate,
    SellerUserLink,
)
from app.services.seller_service import SellerService


router = APIRouter(
    prefix="/sellers",
    tags=["Sellers"],
)


def handle_seller_error(
    error: ValueError,
) -> HTTPException:
    message = str(error)

    not_found_messages = {
        "Vendedor não encontrado.",
        "Usuário não encontrado.",
    }

    if message in not_found_messages:
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return HTTPException(
        status_code=status_code,
        detail=message,
    )


@router.post(
    "",
    response_model=SellerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_seller(
    data: SellerCreate,
    db: Session = Depends(get_db),
) -> SellerResponse:
    service = SellerService(db)

    try:
        return service.create(data)

    except ValueError as error:
        raise handle_seller_error(error) from error


@router.get(
    "",
    response_model=list[SellerResponse],
)
def list_sellers(
    only_active: bool = Query(
        default=False,
        description=(
            "Retorna apenas vendedores ativos."
        ),
    ),
    db: Session = Depends(get_db),
) -> list[SellerResponse]:
    service = SellerService(db)

    return service.list_all(
        only_active=only_active
    )


@router.get(
    "/{seller_id}",
    response_model=SellerResponse,
)
def get_seller(
    seller_id: int,
    db: Session = Depends(get_db),
) -> SellerResponse:
    service = SellerService(db)

    try:
        return service.get_by_id(seller_id)

    except ValueError as error:
        raise handle_seller_error(error) from error


@router.patch(
    "/{seller_id}",
    response_model=SellerResponse,
)
def update_seller(
    seller_id: int,
    data: SellerUpdate,
    db: Session = Depends(get_db),
) -> SellerResponse:
    service = SellerService(db)

    try:
        return service.update(
            seller_id=seller_id,
            data=data,
        )

    except ValueError as error:
        raise handle_seller_error(error) from error


@router.patch(
    "/{seller_id}/deactivate",
    response_model=SellerResponse,
)
def deactivate_seller(
    seller_id: int,
    db: Session = Depends(get_db),
) -> SellerResponse:
    service = SellerService(db)

    try:
        return service.deactivate(seller_id)

    except ValueError as error:
        raise handle_seller_error(error) from error


@router.patch(
    "/{seller_id}/activate",
    response_model=SellerResponse,
)
def activate_seller(
    seller_id: int,
    db: Session = Depends(get_db),
) -> SellerResponse:
    service = SellerService(db)

    try:
        return service.activate(seller_id)

    except ValueError as error:
        raise handle_seller_error(error) from error


@router.patch(
    "/{seller_id}/link-user",
    response_model=SellerResponse,
)
def link_user_to_seller(
    seller_id: int,
    data: SellerUserLink,
    db: Session = Depends(get_db),
) -> SellerResponse:
    service = SellerService(db)

    try:
        return service.link_user(
            seller_id=seller_id,
            user_id=data.user_id,
        )

    except ValueError as error:
        raise handle_seller_error(error) from error


@router.patch(
    "/{seller_id}/unlink-user",
    response_model=SellerResponse,
)
def unlink_user_from_seller(
    seller_id: int,
    db: Session = Depends(get_db),
) -> SellerResponse:
    service = SellerService(db)

    try:
        return service.unlink_user(seller_id)

    except ValueError as error:
        raise handle_seller_error(error) from error