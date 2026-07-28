from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.enums.sequence_name import SequenceName
from app.models.product import Product
from app.models.stock import Stock
from app.repositores.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.sequence_service import SequenceService


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductRepository(db)
        self.sequence_service = SequenceService(db)

    def create(self, data: ProductCreate) -> Product:
        normalized_name = data.nome.strip()

        existing_product = self.repository.get_by_name(
            normalized_name
        )

        if existing_product:
            raise ValueError(
                "Já existe um produto cadastrado com esse nome."
            )

        try:
            codigo = self.sequence_service.generate_code(
                SequenceName.PRODUCT
            )

            product = Product(
                codigo=codigo,
                nome=normalized_name,
                descricao=(
                    data.descricao.strip()
                    if data.descricao
                    else None
                ),
                preco=data.preco,
            )

            created_product = self.repository.create(product)

            stock = Stock(
                product_id=created_product.id,
                quantidade=0,
            )

            self.db.add(stock)
            self.db.flush()

            self.db.commit()
            self.db.refresh(created_product)

            return created_product

        except IntegrityError as error:
            self.db.rollback()

            raise ValueError(
                "Não foi possível cadastrar o produto. "
                "Verifique se o nome ou o código já está em uso."
            ) from error

        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, product_id: int) -> Product:
        product = self.repository.get_by_id(product_id)

        if product is None:
            raise ValueError("Produto não encontrado.")

        return product

    def list_all(
        self,
        only_active: bool = False,
    ) -> list[Product]:
        return self.repository.list_all(
            only_active=only_active
        )

    def update(
        self,
        product_id: int,
        data: ProductUpdate,
    ) -> Product:
        product = self.get_by_id(product_id)

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            raise ValueError(
                "Nenhuma informação foi enviada para atualização."
            )

        new_name = update_data.get("nome")

        if new_name is not None:
            new_name = new_name.strip()

            existing_product = self.repository.get_by_name(
                new_name
            )

            if (
                existing_product is not None
                and existing_product.id != product.id
            ):
                raise ValueError(
                    "Já existe outro produto cadastrado com esse nome."
                )

            update_data["nome"] = new_name

        if "descricao" in update_data:
            description = update_data["descricao"]

            update_data["descricao"] = (
                description.strip()
                if description
                else None
            )

        for field, value in update_data.items():
            setattr(product, field, value)

        try:
            updated_product = self.repository.update(product)

            self.db.commit()
            self.db.refresh(updated_product)

            return updated_product

        except IntegrityError as error:
            self.db.rollback()

            raise ValueError(
                "Não foi possível atualizar o produto."
            ) from error

        except Exception:
            self.db.rollback()
            raise

    def deactivate(self, product_id: int) -> Product:
        product = self.get_by_id(product_id)

        if not product.ativo:
            raise ValueError(
                "O produto já está desativado."
            )

        product.ativo = False

        try:
            updated_product = self.repository.update(product)

            self.db.commit()
            self.db.refresh(updated_product)

            return updated_product

        except Exception:
            self.db.rollback()
            raise

    def activate(self, product_id: int) -> Product:
        product = self.get_by_id(product_id)

        if product.ativo:
            raise ValueError(
                "O produto já está ativo."
            )

        product.ativo = True

        try:
            updated_product = self.repository.update(product)

            self.db.commit()
            self.db.refresh(updated_product)

            return updated_product

        except Exception:
            self.db.rollback()
            raise