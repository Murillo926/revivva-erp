from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositores.user_repository import UserRepository
from app.security.jwt import create_access_token
from app.security.password import verify_password


class AuthService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()

    def authenticate(
        self,
        db: Session,
        login: str,
        senha: str,
    ) -> dict[str, str]:
        normalized_login = login.strip().lower()

        user = self.user_repository.get_by_login(
            db=db,
            login=normalized_login,
        )

        if user is None or not verify_password(
            senha,
            user.senha_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login ou senha inválidos.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este usuário está inativo.",
            )

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "login": user.login,
                "cargo": user.cargo,
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }