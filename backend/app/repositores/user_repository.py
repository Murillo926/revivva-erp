from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def get_by_login(self, db: Session, login: str) -> User | None:
        statement = select(User).where(User.login == login)
        return db.scalar(statement)

    def create(self, db: Session, user: User) -> User:
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception:
            db.rollback()
            raise