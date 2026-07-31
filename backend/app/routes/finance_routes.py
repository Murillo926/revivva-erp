from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.security.auth import get_current_user

from app.services.finance_service import FinanceService

from app.schemas.finance import (
    AccountReceivableResponse,
    AccountReceivablePaymentCreate,
    AccountReceivablePaymentResponse,
    PaymentMethodResponse,
)
from app.schemas.finance.account_receivable_cancel import (
    AccountReceivableCancel,
)

router = APIRouter(
    prefix="/finance",
    tags=["Finance"],
)


@router.get(
    "/payment-methods",
    response_model=list[PaymentMethodResponse],
)
def list_payment_methods(
    db: Session = Depends(get_db),
):
    service = FinanceService(db)
    return service.list_payment_methods()


@router.get(
    "/accounts",
    response_model=list[AccountReceivableResponse],
)
def list_accounts(
    db: Session = Depends(get_db),
):
    service = FinanceService(db)
    return service.list_accounts()


@router.get(
    "/accounts/pending",
    response_model=list[AccountReceivableResponse],
)
def list_pending_accounts(
    db: Session = Depends(get_db),
):
    service = FinanceService(db)
    return service.list_pending_accounts()


@router.get(
    "/accounts/overdue",
    response_model=list[AccountReceivableResponse],
)
def list_overdue_accounts(
    db: Session = Depends(get_db),
):
    service = FinanceService(db)
    return service.list_overdue_accounts()


@router.get(
    "/accounts/{account_id}",
    response_model=AccountReceivableResponse,
)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
):
    service = FinanceService(db)

    try:
        return service.get_account(account_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.get(
    "/accounts/code/{codigo}",
    response_model=AccountReceivableResponse,
)
def get_account_by_code(
    codigo: str,
    db: Session = Depends(get_db),
):
    service = FinanceService(db)

    try:
        return service.get_account_by_code(codigo)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.get(
    "/sales/{sale_id}/accounts",
    response_model=list[AccountReceivableResponse],
)
def get_sale_accounts(
    sale_id: int,
    db: Session = Depends(get_db),
):
    service = FinanceService(db)

    try:
        return service.list_sale_accounts(sale_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/accounts/{account_id}/payment",
    response_model=list[AccountReceivablePaymentResponse],
)
def register_payment(
    account_id: int,
    data: AccountReceivablePaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = FinanceService(db)

    try:
        return service.register_payment(
            account_id=account_id,
            payment_method_id=data.payment_method_id,
            amount=data.valor,
            user_id=int(current_user["sub"]),
            observation=data.observacao,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/accounts/{account_id}/cancel",
    response_model=AccountReceivableResponse,
)
def cancel_account(
    account_id: int,
    data: AccountReceivableCancel,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = FinanceService(db)

    try:
        return service.cancel_account(
            account_id=account_id,
            user_id=int(current_user["sub"]),
            observation=data.observacao,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/sales/{sale_id}/cancel",
    response_model=list[AccountReceivableResponse],
)
def cancel_sale_accounts(
    sale_id: int,
    data: AccountReceivableCancel,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = FinanceService(db)

    try:
        return service.cancel_sale_accounts(
            sale_id=sale_id,
            user_id=int(current_user["sub"]),
            observation=data.observacao,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )