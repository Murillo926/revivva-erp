from sqlalchemy.orm import Session

from app.models.seller_stock import SellerStock
from app.models.seller_stock_movement import SellerStockMovement
from app.models.stock_movement import StockMovement
from app.repositores.product_repository import ProductRepository
from app.repositores.seller_repository import SellerRepository
from app.repositores.seller_stock_movement_repository import (
    SellerStockMovementRepository,
)
from app.repositores.seller_stock_repository import (
    SellerStockRepository,
)
from app.repositores.stock_movement_repository import (
    StockMovementRepository,
)
from app.repositores.stock_repository import StockRepository
from app.schemas.seller_stock import (
    SellerStockReturnCreate,
    SellerStockTransferCreate,
)


class SellerStockService:
    GENERAL_TRANSFER_OUT_TYPE = (
        "SAIDA_TRANSFERENCIA_VENDEDOR"
    )
    SELLER_TRANSFER_IN_TYPE = "ENTRADA_TRANSFERENCIA"

    SELLER_RETURN_OUT_TYPE = "SAIDA_DEVOLUCAO"
    GENERAL_RETURN_IN_TYPE = (
        "ENTRADA_DEVOLUCAO_VENDEDOR"
    )

    def __init__(self, db: Session):
        self.db = db

        self.product_repository = ProductRepository(db)
        self.seller_repository = SellerRepository(db)
        self.stock_repository = StockRepository(db)

        self.stock_movement_repository = (
            StockMovementRepository(db)
        )

        self.seller_stock_repository = (
            SellerStockRepository(db)
        )

        self.seller_stock_movement_repository = (
            SellerStockMovementRepository(db)
        )

    def transfer_to_seller(
        self,
        data: SellerStockTransferCreate,
        performed_by_user_id: int,
    ) -> dict:
        """
        Transfere produtos do estoque geral para o estoque
        de um vendedor.

        A operação:

        1. Valida vendedor e produto.
        2. Bloqueia o estoque geral com FOR UPDATE.
        3. Valida a quantidade disponível.
        4. Cria ou bloqueia o estoque do vendedor.
        5. Diminui o estoque geral.
        6. Aumenta o estoque do vendedor.
        7. Registra as duas movimentações.
        8. Confirma toda a transação.
        """

        if performed_by_user_id <= 0:
            raise ValueError(
                "O usuário responsável pela operação "
                "é obrigatório."
            )

        try:
            seller = self.seller_repository.get_by_id(
                data.seller_id
            )

            if seller is None:
                raise ValueError(
                    "Vendedor não encontrado."
                )

            if not seller.ativo:
                raise ValueError(
                    "Não é possível transferir produtos "
                    "para um vendedor inativo."
                )

            product = self.product_repository.get_by_id(
                data.product_id
            )

            if product is None:
                raise ValueError(
                    "Produto não encontrado."
                )

            if not product.ativo:
                raise ValueError(
                    "Não é possível movimentar o estoque "
                    "de um produto inativo."
                )

            general_stock = (
                self.stock_repository.get_by_product_id(
                    product_id=data.product_id,
                    for_update=True,
                )
            )

            if general_stock is None:
                raise ValueError(
                    "O produto não possui estoque geral."
                )

            if general_stock.quantidade < data.quantidade:
                raise ValueError(
                    "Estoque geral insuficiente. "
                    f"Disponível: {general_stock.quantidade}. "
                    f"Solicitado: {data.quantidade}."
                )

            seller_stock = (
                self.seller_stock_repository
                .get_by_seller_and_product(
                    seller_id=data.seller_id,
                    product_id=data.product_id,
                    for_update=True,
                )
            )

            if seller_stock is None:
                seller_stock = SellerStock(
                    seller_id=data.seller_id,
                    product_id=data.product_id,
                    quantidade=0,
                )

                seller_stock = (
                    self.seller_stock_repository.create(
                        seller_stock
                    )
                )

            general_quantity_before = (
                general_stock.quantidade
            )
            seller_quantity_before = (
                seller_stock.quantidade
            )

            general_quantity_after = (
                general_quantity_before - data.quantidade
            )
            seller_quantity_after = (
                seller_quantity_before + data.quantidade
            )

            general_stock.quantidade = (
                general_quantity_after
            )
            seller_stock.quantidade = (
                seller_quantity_after
            )

            self.stock_repository.save(
                general_stock
            )

            self.seller_stock_repository.save(
                seller_stock
            )

            general_observation = (
                self._build_general_transfer_observation(
                    seller_code=seller.codigo,
                    seller_name=seller.nome,
                    observation=data.observacao,
                )
            )

            seller_observation = (
                self._build_seller_transfer_observation(
                    observation=data.observacao
                )
            )

            general_movement = StockMovement(
                stock_id=general_stock.id,
                product_id=data.product_id,
                tipo=self.GENERAL_TRANSFER_OUT_TYPE,
                quantidade=data.quantidade,
                quantidade_anterior=(
                    general_quantity_before
                ),
                quantidade_posterior=(
                    general_quantity_after
                ),
                observacao=general_observation,
            )

            self.stock_movement_repository.create(
                general_movement
            )

            seller_movement = SellerStockMovement(
                seller_stock_id=seller_stock.id,
                seller_id=data.seller_id,
                product_id=data.product_id,
                performed_by_user_id=(
                    performed_by_user_id
                ),
                tipo=self.SELLER_TRANSFER_IN_TYPE,
                quantidade=data.quantidade,
                quantidade_anterior=(
                    seller_quantity_before
                ),
                quantidade_posterior=(
                    seller_quantity_after
                ),
                observacao=seller_observation,
            )

            seller_movement = (
                self.seller_stock_movement_repository
                .create(seller_movement)
            )

            self.db.commit()

            self.db.refresh(general_stock)
            self.db.refresh(seller_stock)
            self.db.refresh(seller_movement)

            return {
                "general_stock_product_id": (
                    general_stock.product_id
                ),
                "general_stock_quantidade": (
                    general_stock.quantidade
                ),
                "seller_stock": seller_stock,
                "movement": seller_movement,
            }

        except Exception:
            self.db.rollback()
            raise

    def return_to_general(
        self,
        data: SellerStockReturnCreate,
        performed_by_user_id: int,
    ) -> dict:
        """
        Devolve produtos do estoque do vendedor para
        o estoque geral.

        A operação:

        1. Valida vendedor e produto.
        2. Bloqueia o estoque geral.
        3. Bloqueia o estoque do vendedor.
        4. Valida a quantidade disponível.
        5. Diminui o estoque do vendedor.
        6. Aumenta o estoque geral.
        7. Registra as duas movimentações.
        8. Confirma toda a transação.
        """

        if performed_by_user_id <= 0:
            raise ValueError(
                "O usuário responsável pela operação "
                "é obrigatório."
            )

        try:
            seller = self.seller_repository.get_by_id(
                data.seller_id
            )

            if seller is None:
                raise ValueError(
                    "Vendedor não encontrado."
                )

            product = self.product_repository.get_by_id(
                data.product_id
            )

            if product is None:
                raise ValueError(
                    "Produto não encontrado."
                )

            # Mantemos a mesma ordem de locks utilizada
            # na transferência:
            #
            # 1. Estoque geral
            # 2. Estoque do vendedor
            #
            # Isso reduz o risco de deadlock.
            general_stock = (
                self.stock_repository.get_by_product_id(
                    product_id=data.product_id,
                    for_update=True,
                )
            )

            if general_stock is None:
                raise ValueError(
                    "O produto não possui estoque geral."
                )

            seller_stock = (
                self.seller_stock_repository
                .get_by_seller_and_product(
                    seller_id=data.seller_id,
                    product_id=data.product_id,
                    for_update=True,
                )
            )

            if seller_stock is None:
                raise ValueError(
                    "O vendedor não possui estoque "
                    "para este produto."
                )

            if seller_stock.quantidade < data.quantidade:
                raise ValueError(
                    "Estoque do vendedor insuficiente. "
                    f"Disponível: {seller_stock.quantidade}. "
                    f"Solicitado: {data.quantidade}."
                )

            general_quantity_before = (
                general_stock.quantidade
            )
            seller_quantity_before = (
                seller_stock.quantidade
            )

            general_quantity_after = (
                general_quantity_before + data.quantidade
            )
            seller_quantity_after = (
                seller_quantity_before - data.quantidade
            )

            general_stock.quantidade = (
                general_quantity_after
            )
            seller_stock.quantidade = (
                seller_quantity_after
            )

            self.stock_repository.save(
                general_stock
            )

            self.seller_stock_repository.save(
                seller_stock
            )

            seller_observation = (
                self._build_seller_return_observation(
                    observation=data.observacao
                )
            )

            general_observation = (
                self._build_general_return_observation(
                    seller_code=seller.codigo,
                    seller_name=seller.nome,
                    observation=data.observacao,
                )
            )

            seller_movement = SellerStockMovement(
                seller_stock_id=seller_stock.id,
                seller_id=data.seller_id,
                product_id=data.product_id,
                performed_by_user_id=(
                    performed_by_user_id
                ),
                tipo=self.SELLER_RETURN_OUT_TYPE,
                quantidade=data.quantidade,
                quantidade_anterior=(
                    seller_quantity_before
                ),
                quantidade_posterior=(
                    seller_quantity_after
                ),
                observacao=seller_observation,
            )

            seller_movement = (
                self.seller_stock_movement_repository
                .create(seller_movement)
            )

            general_movement = StockMovement(
                stock_id=general_stock.id,
                product_id=data.product_id,
                tipo=self.GENERAL_RETURN_IN_TYPE,
                quantidade=data.quantidade,
                quantidade_anterior=(
                    general_quantity_before
                ),
                quantidade_posterior=(
                    general_quantity_after
                ),
                observacao=general_observation,
            )

            self.stock_movement_repository.create(
                general_movement
            )

            self.db.commit()

            self.db.refresh(general_stock)
            self.db.refresh(seller_stock)
            self.db.refresh(seller_movement)

            return {
                "general_stock_product_id": (
                    general_stock.product_id
                ),
                "general_stock_quantidade": (
                    general_stock.quantidade
                ),
                "seller_stock": seller_stock,
                "movement": seller_movement,
            }

        except Exception:
            self.db.rollback()
            raise

    def get_stock_by_id(
        self,
        seller_stock_id: int,
    ) -> SellerStock:
        seller_stock = (
            self.seller_stock_repository.get_by_id(
                seller_stock_id
            )
        )

        if seller_stock is None:
            raise ValueError(
                "Estoque do vendedor não encontrado."
            )

        return seller_stock

    def get_stock(
        self,
        seller_id: int,
        product_id: int,
    ) -> SellerStock:
        seller = self.seller_repository.get_by_id(
            seller_id
        )

        if seller is None:
            raise ValueError(
                "Vendedor não encontrado."
            )

        product = self.product_repository.get_by_id(
            product_id
        )

        if product is None:
            raise ValueError(
                "Produto não encontrado."
            )

        seller_stock = (
            self.seller_stock_repository
            .get_by_seller_and_product(
                seller_id=seller_id,
                product_id=product_id,
            )
        )

        if seller_stock is None:
            raise ValueError(
                "O vendedor não possui estoque "
                "para este produto."
            )

        return seller_stock

    def list_all(
        self,
    ) -> list[SellerStock]:
        return self.seller_stock_repository.list_all()

    def list_by_seller(
        self,
        seller_id: int,
    ) -> list[SellerStock]:
        seller = self.seller_repository.get_by_id(
            seller_id
        )

        if seller is None:
            raise ValueError(
                "Vendedor não encontrado."
            )

        return (
            self.seller_stock_repository.list_by_seller(
                seller_id
            )
        )

    def list_by_product(
        self,
        product_id: int,
    ) -> list[SellerStock]:
        product = self.product_repository.get_by_id(
            product_id
        )

        if product is None:
            raise ValueError(
                "Produto não encontrado."
            )

        return (
            self.seller_stock_repository.list_by_product(
                product_id
            )
        )

    def list_movements(
        self,
        seller_id: int | None = None,
        product_id: int | None = None,
    ) -> list[SellerStockMovement]:
        if seller_id is not None:
            seller = self.seller_repository.get_by_id(
                seller_id
            )

            if seller is None:
                raise ValueError(
                    "Vendedor não encontrado."
                )

        if product_id is not None:
            product = (
                self.product_repository.get_by_id(
                    product_id
                )
            )

            if product is None:
                raise ValueError(
                    "Produto não encontrado."
                )

        if (
            seller_id is not None
            and product_id is not None
        ):
            return (
                self.seller_stock_movement_repository
                .list_by_seller_and_product(
                    seller_id=seller_id,
                    product_id=product_id,
                )
            )

        if seller_id is not None:
            return (
                self.seller_stock_movement_repository
                .list_by_seller(seller_id)
            )

        if product_id is not None:
            return (
                self.seller_stock_movement_repository
                .list_by_product(product_id)
            )

        return (
            self.seller_stock_movement_repository
            .list_all()
        )

    def get_movement_by_id(
        self,
        movement_id: int,
    ) -> SellerStockMovement:
        movement = (
            self.seller_stock_movement_repository
            .get_by_id(movement_id)
        )

        if movement is None:
            raise ValueError(
                "Movimentação não encontrada."
            )

        return movement

    def list_movements_by_user(
        self,
        user_id: int,
    ) -> list[SellerStockMovement]:
        return (
            self.seller_stock_movement_repository
            .list_by_user(user_id)
        )

    @staticmethod
    def _build_general_transfer_observation(
        seller_code: str,
        seller_name: str,
        observation: str | None,
    ) -> str:
        message = (
            "Transferência para o vendedor "
            f"{seller_code} - {seller_name}."
        )

        if observation:
            message += f" Observação: {observation}"

        return message

    @staticmethod
    def _build_seller_transfer_observation(
        observation: str | None,
    ) -> str:
        message = (
            "Entrada recebida do estoque geral."
        )

        if observation:
            message += f" Observação: {observation}"

        return message

    @staticmethod
    def _build_seller_return_observation(
        observation: str | None,
    ) -> str:
        message = (
            "Saída por devolução ao estoque geral."
        )

        if observation:
            message += f" Observação: {observation}"

        return message

    @staticmethod
    def _build_general_return_observation(
        seller_code: str,
        seller_name: str,
        observation: str | None,
    ) -> str:
        message = (
            "Devolução recebida do vendedor "
            f"{seller_code} - {seller_name}."
        )

        if observation:
            message += f" Observação: {observation}"

        return message