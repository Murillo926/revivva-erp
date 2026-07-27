from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.security.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

service = UserService()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> UserResponse:
    return service.create(db, user)