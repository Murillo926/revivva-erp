from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.repositores.product_repository import ProductRepository
from app.repositores.stock_movement_repository import (
    StockMovementRepository,
)
from app.repositores.stock_repository import StockRepository
from app.schemas.stock import (
    StockAdjustmentCreate,
    StockEntryCreate,
    StockExitCreate,
)


class StockService:
    ENTRY_TYPE = "ENTRADA_MANUAL"
    EXIT_TYPE = "SAIDA_MANUAL"
    ADJUSTMENT_TYPE = "AJUSTE_MANUAL"

    def __init__(self, db: Session):
        self.db = db
        self.product_repository = ProductRepository(db)
        self.stock_repository = StockRepository(db)
        self.movement_repository = StockMovementRepository(db)

    def _get_product(self, product_id: int) -> Product:
        product = self.product_repository.get_by_id(product_id)

        if product is None:
            raise ValueError("Produto não encontrado.")

        return product

    def _validate_active_product(
        self,
        product: Product,
    ) -> None:
        if not product.ativo:
            raise ValueError(
                "Não é possível movimentar o estoque de um "
                "produto desativado."
            )

    def _get_or_create_stock(
        self,
        product_id: int,
        for_update: bool = False,
    ) -> Stock:
        stock = self.stock_repository.get_by_product_id(
            product_id=product_id,
            for_update=for_update,
        )

        if stock is None:
            stock = self.stock_repository.create(product_id)

        return stock

    @staticmethod
    def _clean_observation(
        observation: str | None,
    ) -> str | None:
        if observation is None:
            return None

        cleaned_observation = observation.strip()

        return cleaned_observation or None

    @staticmethod
    def _build_stock_response(
        stock: Stock,
        product: Product,
    ) -> dict:
        return {
            "id": stock.id,
            "product_id": stock.product_id,
            "codigo_produto": product.codigo,
            "nome_produto": product.nome,
            "quantidade": stock.quantidade,
            "criado_em": stock.criado_em,
            "atualizado_em": stock.atualizado_em,
        }

    @staticmethod
    def _build_movement_response(
        movement: StockMovement,
        product: Product,
    ) -> dict:
        return {
            "id": movement.id,
            "stock_id": movement.stock_id,
            "product_id": movement.product_id,
            "codigo_produto": product.codigo,
            "nome_produto": product.nome,
            "tipo": movement.tipo,
            "quantidade": movement.quantidade,
            "quantidade_anterior": (
                movement.quantidade_anterior
            ),
            "quantidade_posterior": (
                movement.quantidade_posterior
            ),
            "observacao": movement.observacao,
            "criado_em": movement.criado_em,
        }

    def get_by_product_id(
        self,
        product_id: int,
    ) -> dict:
        product = self._get_product(product_id)

        stock = self.stock_repository.get_by_product_id(
            product_id
        )

        if stock is None:
            stock = Stock(
                id=0,
                product_id=product.id,
                quantidade=0,
                criado_em=product.criado_em,
                atualizado_em=product.atualizado_em,
            )

        return self._build_stock_response(
            stock=stock,
            product=product,
        )

    def list_all(self) -> list[dict]:
        rows = self.stock_repository.list_all()

        return [
            self._build_stock_response(
                stock=stock,
                product=product,
            )
            for stock, product in rows
        ]

    def entry(
        self,
        data: StockEntryCreate,
    ) -> dict:
        product = self._get_product(data.product_id)
        self._validate_active_product(product)

        try:
            stock = self._get_or_create_stock(
                product_id=product.id,
                for_update=True,
            )

            previous_quantity = stock.quantidade
            posterior_quantity = (
                previous_quantity + data.quantidade
            )

            stock.quantidade = posterior_quantity

            self.stock_repository.save(stock)

            movement = StockMovement(
                stock_id=stock.id,
                product_id=product.id,
                tipo=self.ENTRY_TYPE,
                quantidade=data.quantidade,
                quantidade_anterior=previous_quantity,
                quantidade_posterior=posterior_quantity,
                observacao=self._clean_observation(
                    data.observacao
                ),
            )

            self.movement_repository.create(movement)

            self.db.commit()
            self.db.refresh(stock)

            return self._build_stock_response(
                stock=stock,
                product=product,
            )

        except IntegrityError as error:
            self.db.rollback()

            raise ValueError(
                "Não foi possível registrar a entrada "
                "de estoque."
            ) from error

        except Exception:
            self.db.rollback()
            raise

    def exit(
        self,
        data: StockExitCreate,
    ) -> dict:
        product = self._get_product(data.product_id)
        self._validate_active_product(product)

        try:
            stock = self._get_or_create_stock(
                product_id=product.id,
                for_update=True,
            )

            if stock.quantidade < data.quantidade:
                raise ValueError(
                    "Estoque insuficiente. "
                    f"Disponível: {stock.quantidade}. "
                    f"Solicitado: {data.quantidade}."
                )

            previous_quantity = stock.quantidade
            posterior_quantity = (
                previous_quantity - data.quantidade
            )

            stock.quantidade = posterior_quantity

            self.stock_repository.save(stock)

            movement = StockMovement(
                stock_id=stock.id,
                product_id=product.id,
                tipo=self.EXIT_TYPE,
                quantidade=-data.quantidade,
                quantidade_anterior=previous_quantity,
                quantidade_posterior=posterior_quantity,
                observacao=self._clean_observation(
                    data.observacao
                ),
            )

            self.movement_repository.create(movement)

            self.db.commit()
            self.db.refresh(stock)

            return self._build_stock_response(
                stock=stock,
                product=product,
            )

        except ValueError:
            self.db.rollback()
            raise

        except IntegrityError as error:
            self.db.rollback()

            raise ValueError(
                "Não foi possível registrar a saída "
                "de estoque."
            ) from error

        except Exception:
            self.db.rollback()
            raise

    def adjustment(
        self,
        data: StockAdjustmentCreate,
    ) -> dict:
        product = self._get_product(data.product_id)
        self._validate_active_product(product)

        try:
            stock = self._get_or_create_stock(
                product_id=product.id,
                for_update=True,
            )

            previous_quantity = stock.quantidade
            posterior_quantity = data.nova_quantidade
            difference = (
                posterior_quantity - previous_quantity
            )

            if difference == 0:
                raise ValueError(
                    "A nova quantidade é igual à quantidade "
                    "atual do estoque."
                )

            stock.quantidade = posterior_quantity

            self.stock_repository.save(stock)

            movement = StockMovement(
                stock_id=stock.id,
                product_id=product.id,
                tipo=self.ADJUSTMENT_TYPE,
                quantidade=difference,
                quantidade_anterior=previous_quantity,
                quantidade_posterior=posterior_quantity,
                observacao=data.observacao.strip(),
            )

            self.movement_repository.create(movement)

            self.db.commit()
            self.db.refresh(stock)

            return self._build_stock_response(
                stock=stock,
                product=product,
            )

        except ValueError:
            self.db.rollback()
            raise

        except IntegrityError as error:
            self.db.rollback()

            raise ValueError(
                "Não foi possível realizar o ajuste "
                "de estoque."
            ) from error

        except Exception:
            self.db.rollback()
            raise

    def list_movements(
        self,
        product_id: int,
    ) -> list[dict]:
        self._get_product(product_id)

        rows = self.movement_repository.list_by_product_id(
            product_id
        )

        return [
            self._build_movement_response(
                movement=movement,
                product=product,
            )
            for movement, product in rows
        ]