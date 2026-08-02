from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.cash_flow import (
    CashFlowCategoryCreate,
    CashFlowCategoryResponse,
    CashFlowCategoryTotalResponse,
    CashFlowDailyPointResponse,
    CashFlowManualCreate,
    CashFlowResponse,
    CashFlowSummaryResponse,
)
from app.security.auth import get_current_user
from app.services.cash_flow_service import CashFlowService

router = APIRouter(prefix="/cash-flow", tags=["Cash Flow"])


def current_user_id(user: dict) -> int:
    return int(user["sub"])


@router.get("", response_model=list[CashFlowResponse])
def list_entries(
    start_date: date | None = None,
    end_date: date | None = None,
    tipo: str | None = None,
    origem: str | None = None,
    category_id: int | None = None,
    payment_method_id: int | None = None,
    limit: int = Query(default=500, ge=1, le=2000),
    db: Session = Depends(get_db),
):
    try:
        return CashFlowService(db).list_entries(
            start_date=start_date,
            end_date=end_date,
            tipo=tipo,
            origem=origem,
            category_id=category_id,
            payment_method_id=payment_method_id,
            limit=limit,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/summary", response_model=CashFlowSummaryResponse)
def summary(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return CashFlowService(db).summary(start_date, end_date)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/daily-evolution",
    response_model=list[CashFlowDailyPointResponse],
)
def daily_evolution(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
):
    try:
        return CashFlowService(db).daily_evolution(start_date, end_date)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/by-category",
    response_model=list[CashFlowCategoryTotalResponse],
)
def totals_by_category(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return CashFlowService(db).totals_by_category(start_date, end_date)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/categories", response_model=list[CashFlowCategoryResponse])
def list_categories(
    only_active: bool = True,
    tipo: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return CashFlowService(db).list_categories(only_active, tipo)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post(
    "/categories",
    response_model=CashFlowCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: CashFlowCategoryCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    _ = current_user_id(user)
    try:
        return CashFlowService(db).create_category(data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post(
    "/manual",
    response_model=CashFlowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_manual_entry(
    data: CashFlowManualCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    try:
        return CashFlowService(db).create_manual_entry(
            data=data,
            user_id=current_user_id(user),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/{flow_id}", response_model=CashFlowResponse)
def get_entry(flow_id: int, db: Session = Depends(get_db)):
    try:
        return CashFlowService(db).get_by_id(flow_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
