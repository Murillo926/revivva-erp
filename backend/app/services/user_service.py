from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositores.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.security.password import hash_password


class UserService:
    def __init__(self) -> None:
        self.repository = UserRepository()

    def create(self, db: Session, data: UserCreate) -> User:
        normalized_login = data.login.strip().lower()

        existing_user = self.repository.get_by_login(
            db=db,
            login=normalized_login,
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este login já está sendo utilizado.",
            )

        user = User(
            nome=data.nome.strip(),
            login=normalized_login,
            senha_hash=hash_password(data.senha),
            cargo=data.cargo.value,
            ativo=True,
        )

        return self.repository.create(db, user)