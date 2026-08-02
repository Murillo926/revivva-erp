from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.finance.accounts_payable import AccountPayableCancel, AccountPayableDetailsResponse, AccountPayablePaymentCreate, AccountPayablePaymentResponse, AccountPayableResponse
from app.security.auth import get_current_user
from app.services.account_payable_service import AccountPayableService

router = APIRouter(prefix="/accounts-payable", tags=["Accounts Payable"])


def uid(user: dict) -> int:
    return int(user["sub"])


@router.get("", response_model=list[AccountPayableResponse])
def list_accounts(db: Session = Depends(get_db)):
    return AccountPayableService(db).list_accounts()


@router.get("/pending", response_model=list[AccountPayableResponse])
def list_pending(db: Session = Depends(get_db)):
    return AccountPayableService(db).list_pending_accounts()


@router.get("/overdue", response_model=list[AccountPayableResponse])
def list_overdue(db: Session = Depends(get_db)):
    return AccountPayableService(db).list_overdue_accounts()


@router.get("/code/{codigo}", response_model=AccountPayableDetailsResponse)
def get_by_code(codigo: str, db: Session = Depends(get_db)):
    try:
        return AccountPayableService(db).get_account_by_code(codigo)
    except ValueError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error


@router.get("/purchase/{purchase_id}", response_model=list[AccountPayableResponse])
def list_by_purchase(purchase_id: int, db: Session = Depends(get_db)):
    try:
        return AccountPayableService(db).list_purchase_accounts(purchase_id)
    except ValueError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error


@router.get("/{account_id}", response_model=AccountPayableDetailsResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    try:
        return AccountPayableService(db).get_account(account_id)
    except ValueError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error


@router.post("/{account_id}/payment", response_model=list[AccountPayablePaymentResponse])
def register_payment(account_id: int, data: AccountPayablePaymentCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    try:
        return AccountPayableService(db).register_payment(account_id, data.payment_method_id, data.valor, uid(user), data.observacao)
    except ValueError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error


@router.post("/{account_id}/cancel", response_model=AccountPayableDetailsResponse)
def cancel_account(account_id: int, data: AccountPayableCancel, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    try:
        return AccountPayableService(db).cancel_account(account_id, uid(user), data.observacao)
    except ValueError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
