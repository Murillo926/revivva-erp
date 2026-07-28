from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.enums.sequence_name import SequenceName
from app.models.seller import Seller
from app.models.user import User
from app.repositores.seller_repository import SellerRepository
from app.schemas.seller import (
    SellerCreate,
    SellerUpdate,
)
from app.services.sequence_service import SequenceService


class SellerService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = SellerRepository(db)
        self.sequence_service = SequenceService(db)

    def _get_user(
        self,
        user_id: int,
    ) -> User:
        user = self.db.get(User, user_id)

        if user is None:
            raise ValueError(
                "Usuário não encontrado."
            )

        return user

    def create(
        self,
        data: SellerCreate,
    ) -> Seller:
        existing_seller = self.repository.get_by_cpf(
            data.cpf
        )

        if existing_seller is not None:
            raise ValueError(
                "Já existe um vendedor cadastrado "
                "com esse CPF."
            )

        if data.user_id is not None:
            self._get_user(data.user_id)

            linked_seller = (
                self.repository.get_by_user_id(
                    data.user_id
                )
            )

            if linked_seller is not None:
                raise ValueError(
                    "Esse usuário já está vinculado "
                    "a outro vendedor."
                )

        try:
            codigo = self.sequence_service.generate_code(
                SequenceName.SELLER
            )

            seller = Seller(
                codigo=codigo,
                nome=data.nome.strip(),
                cpf=data.cpf,
                telefone=data.telefone.strip(),
                percentual_comissao=(
                    data.percentual_comissao
                ),
                user_id=data.user_id,
            )

            created_seller = self.repository.create(
                seller
            )

            self.db.commit()
            self.db.refresh(created_seller)

            return created_seller

        except IntegrityError as error:
            self.db.rollback()

            raise ValueError(
                "Não foi possível cadastrar o vendedor. "
                "Verifique se o CPF, código ou usuário "
                "já estão em uso."
            ) from error

        except ValueError:
            self.db.rollback()
            raise

        except Exception:
            self.db.rollback()
            raise

    def get_by_id(
        self,
        seller_id: int,
    ) -> Seller:
        seller = self.repository.get_by_id(
            seller_id
        )

        if seller is None:
            raise ValueError(
                "Vendedor não encontrado."
            )

        return seller

    def list_all(
        self,
        only_active: bool = False,
    ) -> list[Seller]:
        return self.repository.list_all(
            only_active=only_active
        )

    def update(
        self,
        seller_id: int,
        data: SellerUpdate,
    ) -> Seller:
        seller = self.get_by_id(seller_id)

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            raise ValueError(
                "Nenhuma informação foi enviada "
                "para atualização."
            )

        new_cpf = update_data.get("cpf")

        if new_cpf is not None:
            existing_seller = (
                self.repository.get_by_cpf(
                    new_cpf
                )
            )

            if (
                existing_seller is not None
                and existing_seller.id != seller.id
            ):
                raise ValueError(
                    "Já existe outro vendedor "
                    "cadastrado com esse CPF."
                )

        new_name = update_data.get("nome")

        if new_name is not None:
            update_data["nome"] = (
                new_name.strip()
            )

        new_phone = update_data.get("telefone")

        if new_phone is not None:
            update_data["telefone"] = (
                new_phone.strip()
            )

        for field, value in update_data.items():
            setattr(seller, field, value)

        try:
            updated_seller = self.repository.save(
                seller
            )

            self.db.commit()
            self.db.refresh(updated_seller)

            return updated_seller

        except IntegrityError as error:
            self.db.rollback()

            raise ValueError(
                "Não foi possível atualizar "
                "o vendedor."
            ) from error

        except ValueError:
            self.db.rollback()
            raise

        except Exception:
            self.db.rollback()
            raise

    def deactivate(
        self,
        seller_id: int,
    ) -> Seller:
        seller = self.get_by_id(seller_id)

        if not seller.ativo:
            raise ValueError(
                "O vendedor já está desativado."
            )

        seller.ativo = False

        try:
            updated_seller = self.repository.save(
                seller
            )

            self.db.commit()
            self.db.refresh(updated_seller)

            return updated_seller

        except Exception:
            self.db.rollback()
            raise

    def activate(
        self,
        seller_id: int,
    ) -> Seller:
        seller = self.get_by_id(seller_id)

        if seller.ativo:
            raise ValueError(
                "O vendedor já está ativo."
            )

        seller.ativo = True

        try:
            updated_seller = self.repository.save(
                seller
            )

            self.db.commit()
            self.db.refresh(updated_seller)

            return updated_seller

        except Exception:
            self.db.rollback()
            raise

    def link_user(
        self,
        seller_id: int,
        user_id: int,
    ) -> Seller:
        seller = self.get_by_id(seller_id)

        self._get_user(user_id)

        if seller.user_id == user_id:
            raise ValueError(
                "Esse usuário já está vinculado "
                "ao vendedor."
            )

        linked_seller = (
            self.repository.get_by_user_id(
                user_id
            )
        )

        if (
            linked_seller is not None
            and linked_seller.id != seller.id
        ):
            raise ValueError(
                "Esse usuário já está vinculado "
                "a outro vendedor."
            )

        seller.user_id = user_id

        try:
            updated_seller = self.repository.save(
                seller
            )

            self.db.commit()
            self.db.refresh(updated_seller)

            return updated_seller

        except IntegrityError as error:
            self.db.rollback()

            raise ValueError(
                "Não foi possível vincular "
                "o usuário ao vendedor."
            ) from error

        except Exception:
            self.db.rollback()
            raise

    def unlink_user(
        self,
        seller_id: int,
    ) -> Seller:
        seller = self.get_by_id(seller_id)

        if seller.user_id is None:
            raise ValueError(
                "O vendedor não possui "
                "um usuário vinculado."
            )

        seller.user_id = None

        try:
            updated_seller = self.repository.save(
                seller
            )

            self.db.commit()
            self.db.refresh(updated_seller)

            return updated_seller

        except Exception:
            self.db.rollback()
            raise