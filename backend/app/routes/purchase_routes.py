from fastapi import APIRouter,Depends,HTTPException,Query,status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.security.auth import get_current_user
from app.schemas.purchase import PurchaseCreate,PurchaseUpdate,PurchaseConfirm,PurchaseCancel,PurchaseResponse,PurchaseDetailsResponse
from app.services.purchase_service import PurchaseService
router=APIRouter(prefix="/purchases",tags=["Purchases"])
def uid(user):return int(user["sub"])


@router.post("",response_model=PurchaseResponse,status_code=status.HTTP_201_CREATED)
def create_purchase(data:PurchaseCreate,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    try:return PurchaseService(db).create(data,uid(user))
    except ValueError as e:raise HTTPException(400,str(e)) from e


@router.get("",response_model=list[PurchaseResponse])
def list_purchases(status_filter:str|None=Query(None,alias="status"),supplier_id:int|None=None,db:Session=Depends(get_db)):
    try:return PurchaseService(db).list_all(status_filter,supplier_id)
    except ValueError as e:raise HTTPException(400,str(e)) from e


@router.get("/code/{codigo}",response_model=PurchaseDetailsResponse)
def get_purchase_by_code(codigo:str,db:Session=Depends(get_db)):
    try:return PurchaseService(db).get_by_codigo(codigo)
    except ValueError as e:raise HTTPException(404,str(e)) from e


@router.get("/{purchase_id}",response_model=PurchaseDetailsResponse)
def get_purchase(purchase_id:int,db:Session=Depends(get_db)):
    try:return PurchaseService(db).get_by_id(purchase_id)
    except ValueError as e:raise HTTPException(404,str(e)) from e


@router.patch("/{purchase_id}",response_model=PurchaseResponse)
def update_purchase(purchase_id:int,data:PurchaseUpdate,db:Session=Depends(get_db)):
    try:return PurchaseService(db).update(purchase_id,data)
    except ValueError as e:raise HTTPException(400,str(e)) from e


@router.post("/{purchase_id}/confirm",response_model=PurchaseResponse)
def confirm_purchase(purchase_id:int,data:PurchaseConfirm,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    try:return PurchaseService(db).confirm(purchase_id,data,uid(user))
    except ValueError as e:raise HTTPException(400,str(e)) from e


@router.post("/{purchase_id}/cancel",response_model=PurchaseResponse)
def cancel_purchase(purchase_id:int,data:PurchaseCancel,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    try:return PurchaseService(db).cancel(purchase_id,uid(user),data.observacao)
    except ValueError as e:raise HTTPException(400,str(e)) from e
