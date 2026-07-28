from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db

# ATENÇÃO:
# Troque este import pelo caminho real do seu arquivo.
# Exemplo:
# from app.dependencies.auth import get_current_user
from app.security.auth import get_current_user

from app.schemas.seller_stock import (
    SellerStockMovementResponse,
    SellerStockResponse,
    SellerStockReturnCreate,
    SellerStockTransferCreate,
    SellerStockTransferResponse,
)
from app.services.seller_stock_service import (
    SellerStockService,
)


router = APIRouter(
    prefix="/seller-stock",
    tags=["Seller Stock"],
)


CurrentUserPayload = Annotated[
    dict[str, Any],
    Depends(get_current_user),
]


def get_authenticated_user_id(
    current_user: dict[str, Any],
) -> int:
    """
    Obtém o ID do usuário a partir do payload do JWT.

    Aceita as chaves:
    - user_id
    - id
    - sub

    Isso evita que pequenas diferenças no payload
    quebrem imediatamente o módulo.
    """

    raw_user_id = (
        current_user.get("user_id")
        or current_user.get("id")
        or current_user.get("sub")
    )

    if raw_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "O token não possui o ID do usuário."
            ),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id = int(raw_user_id)

    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "O ID do usuário presente no token "
                "é inválido."
            ),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "O ID do usuário presente no token "
                "é inválido."
            ),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user_id


def handle_seller_stock_error(
    error: ValueError,
) -> HTTPException:
    message = str(error)

    not_found_messages = {
        "Vendedor não encontrado.",
        "Produto não encontrado.",
        "O produto não possui estoque geral.",
        (
            "O vendedor não possui estoque "
            "para este produto."
        ),
        "Estoque do vendedor não encontrado.",
        "Movimentação não encontrada.",
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
    "/transfer",
    response_model=SellerStockTransferResponse,
    status_code=status.HTTP_201_CREATED,
)
def transfer_to_seller(
    data: SellerStockTransferCreate,
    current_user: CurrentUserPayload,
    db: Session = Depends(get_db),
) -> SellerStockTransferResponse:
    """
    Transfere uma quantidade do estoque geral
    para o estoque de um vendedor.
    """

    service = SellerStockService(db)

    performed_by_user_id = (
        get_authenticated_user_id(current_user)
    )

    try:
        return service.transfer_to_seller(
            data=data,
            performed_by_user_id=(
                performed_by_user_id
            ),
        )

    except ValueError as error:
        raise handle_seller_stock_error(
            error
        ) from error


@router.post(
    "/return",
    response_model=SellerStockTransferResponse,
    status_code=status.HTTP_200_OK,
)
def return_to_general_stock(
    data: SellerStockReturnCreate,
    current_user: CurrentUserPayload,
    db: Session = Depends(get_db),
) -> SellerStockTransferResponse:
    """
    Devolve uma quantidade do estoque do vendedor
    para o estoque geral.
    """

    service = SellerStockService(db)

    performed_by_user_id = (
        get_authenticated_user_id(current_user)
    )

    try:
        return service.return_to_general(
            data=data,
            performed_by_user_id=(
                performed_by_user_id
            ),
        )

    except ValueError as error:
        raise handle_seller_stock_error(
            error
        ) from error


@router.get(
    "/movements",
    response_model=list[
        SellerStockMovementResponse
    ],
)
def list_seller_stock_movements(
    seller_id: int | None = Query(
        default=None,
        gt=0,
        description=(
            "Filtra as movimentações pelo vendedor."
        ),
    ),
    product_id: int | None = Query(
        default=None,
        gt=0,
        description=(
            "Filtra as movimentações pelo produto."
        ),
    ),
    db: Session = Depends(get_db),
) -> list[SellerStockMovementResponse]:
    """
    Lista as movimentações do estoque por vendedor.

    Os filtros seller_id e product_id são opcionais
    e podem ser utilizados juntos.
    """

    service = SellerStockService(db)

    try:
        return service.list_movements(
            seller_id=seller_id,
            product_id=product_id,
        )

    except ValueError as error:
        raise handle_seller_stock_error(
            error
        ) from error


@router.get(
    "/movements/user/{user_id}",
    response_model=list[
        SellerStockMovementResponse
    ],
)
def list_movements_by_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> list[SellerStockMovementResponse]:
    """
    Lista as movimentações realizadas
    por um determinado usuário.
    """

    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O ID do usuário deve ser positivo.",
        )

    service = SellerStockService(db)

    return service.list_movements_by_user(
        user_id=user_id
    )


@router.get(
    "/movements/{movement_id}",
    response_model=SellerStockMovementResponse,
)
def get_seller_stock_movement(
    movement_id: int,
    db: Session = Depends(get_db),
) -> SellerStockMovementResponse:
    """
    Busca uma movimentação por ID.
    """

    service = SellerStockService(db)

    try:
        return service.get_movement_by_id(
            movement_id
        )

    except ValueError as error:
        raise handle_seller_stock_error(
            error
        ) from error


@router.get(
    "",
    response_model=list[SellerStockResponse],
)
def list_seller_stock(
    seller_id: int | None = Query(
        default=None,
        gt=0,
        description=(
            "Filtra o estoque por vendedor."
        ),
    ),
    product_id: int | None = Query(
        default=None,
        gt=0,
        description=(
            "Filtra o estoque por produto."
        ),
    ),
    db: Session = Depends(get_db),
) -> list[SellerStockResponse]:
    """
    Lista os registros de estoque dos vendedores.

    É possível filtrar por vendedor ou produto.
    Não é permitido usar os dois filtros juntos
    neste endpoint.
    """

    service = SellerStockService(db)

    if (
        seller_id is not None
        and product_id is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Utilize apenas seller_id ou "
                "product_id neste endpoint."
            ),
        )

    try:
        if seller_id is not None:
            return service.list_by_seller(
                seller_id
            )

        if product_id is not None:
            return service.list_by_product(
                product_id
            )

        return service.list_all()

    except ValueError as error:
        raise handle_seller_stock_error(
            error
        ) from error


@router.get(
    "/seller/{seller_id}/product/{product_id}",
    response_model=SellerStockResponse,
)
def get_seller_product_stock(
    seller_id: int,
    product_id: int,
    db: Session = Depends(get_db),
) -> SellerStockResponse:
    """
    Consulta o estoque de um produto específico
    pertencente a um vendedor específico.
    """

    service = SellerStockService(db)

    try:
        return service.get_stock(
            seller_id=seller_id,
            product_id=product_id,
        )

    except ValueError as error:
        raise handle_seller_stock_error(
            error
        ) from error


@router.get(
    "/seller/{seller_id}",
    response_model=list[SellerStockResponse],
)
def list_stock_by_seller(
    seller_id: int,
    db: Session = Depends(get_db),
) -> list[SellerStockResponse]:
    """
    Lista todo o estoque de um vendedor.
    """

    service = SellerStockService(db)

    try:
        return service.list_by_seller(
            seller_id
        )

    except ValueError as error:
        raise handle_seller_stock_error(
            error
        ) from error


@router.get(
    "/product/{product_id}",
    response_model=list[SellerStockResponse],
)
def list_stock_by_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> list[SellerStockResponse]:
    """
    Lista o estoque de um produto
    entre todos os vendedores.
    """

    service = SellerStockService(db)

    try:
        return service.list_by_product(
            product_id
        )

    except ValueError as error:
        raise handle_seller_stock_error(
            error
        ) from error


@router.get(
    "/{seller_stock_id}",
    response_model=SellerStockResponse,
)
def get_seller_stock_by_id(
    seller_stock_id: int,
    db: Session = Depends(get_db),
) -> SellerStockResponse:
    """
    Busca um registro de estoque por ID.
    """

    service = SellerStockService(db)

    try:
        return service.get_stock_by_id(
            seller_stock_id
        )

    except ValueError as error:
        raise handle_seller_stock_error(
            error
        ) from error