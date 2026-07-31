from fastapi import APIRouter,Depends,HTTPException,Query,status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.purchase import SupplierCreate,SupplierUpdate,SupplierResponse
from app.services.supplier_service import SupplierService
router=APIRouter(prefix="/suppliers",tags=["Suppliers"])
@router.post("",response_model=SupplierResponse,status_code=status.HTTP_201_CREATED)
def create_supplier(data:SupplierCreate,db:Session=Depends(get_db)):
    try:return SupplierService(db).create(data)
    except ValueError as e:raise HTTPException(400,str(e)) from e
@router.get("",response_model=list[SupplierResponse])
def list_suppliers(only_active:bool=Query(False),db:Session=Depends(get_db)):return SupplierService(db).list_all(only_active)
@router.get("/{supplier_id}",response_model=SupplierResponse)
def get_supplier(supplier_id:int,db:Session=Depends(get_db)):
    try:return SupplierService(db).get_by_id(supplier_id)
    except ValueError as e:raise HTTPException(404,str(e)) from e
@router.patch("/{supplier_id}",response_model=SupplierResponse)
def update_supplier(supplier_id:int,data:SupplierUpdate,db:Session=Depends(get_db)):
    try:return SupplierService(db).update(supplier_id,data)
    except ValueError as e:raise HTTPException(400,str(e)) from e
