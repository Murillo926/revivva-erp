from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.client import ClientCreate, ClientResponse
from app.security.auth import get_current_user
from app.services.client_service import ClientService


router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
)


@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ClientResponse:

    service = ClientService(db)

    return service.create(
        data=client,
    )