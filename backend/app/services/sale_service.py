from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.constants.sale_status import SaleStatus
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.sale_status_history import SaleStatusHistory
from app.models.seller_stock_movement import SellerStockMovement
from app.repositores.client_repository import ClientRepository
from app.repositores.product_repository import ProductRepository
from app.repositores.sale_item_repository import SaleItemRepository
from app.repositores.sale_repository import SaleRepository
from app.repositores.sale_status_history_repository import (
    SaleStatusHistoryRepository,
)
from app.repositores.seller_repository import SellerRepository
from app.repositores.seller_stock_movement_repository import (
    SellerStockMovementRepository,
)
from app.repositores.seller_stock_repository import SellerStockRepository
from app.repositores.sequence_repository import SequenceRepository
from app.services.finance_service import FinanceService
from app.schemas.sale.sale import (
    SaleCreate,
    SaleUpdate,
    SaleConfirm,
    SaleCancel,
)


class SaleService:
    SALE_SEQUENCE_NAME = "SALE"
    SALE_STOCK_MOVEMENT_TYPE = "SAIDA_VENDA"

    def __init__(self, db: Session):
        self.db = db

        self.sale_repository = SaleRepository(db)
        self.sale_item_repository = SaleItemRepository(db)
        self.history_repository = SaleStatusHistoryRepository(db)

        self.client_repository = ClientRepository(db)
        self.seller_repository = SellerRepository(db)
        self.product_repository = ProductRepository(db)
        self.sequence_repository = SequenceRepository(db)

        self.seller_stock_repository = SellerStockRepository(db)
        self.seller_stock_movement_repository = (
            SellerStockMovementRepository(db)
        )
        self.finance_service = FinanceService(db)

    def create(
        self,
        data: SaleCreate,
        performed_by_user_id: int,
    ) -> Sale:
        try:
            self._validate_unique_products(data)

            client = self._validate_client(data.client_id)
            seller = self._validate_seller(data.seller_id)
            products = self._load_products(data)

            sale = self._build_sale(
                data=data,
                client_id=client.id,
                seller_id=seller.id,
                performed_by_user_id=performed_by_user_id,
            )
            self.sale_repository.create(sale)

            items, subtotal = self._build_sale_items(
                sale_id=sale.id,
                data=data,
                products=products,
            )
            self.sale_item_repository.create_many(items)

            sale.subtotal = subtotal
            sale.desconto = Decimal("0.00")
            sale.total = self._money(sale.subtotal - sale.desconto)
            self.sale_repository.save(sale)

            self._create_history(
                sale_id=sale.id,
                previous_status=None,
                new_status=SaleStatus.AGUARDANDO,
                performed_by_user_id=performed_by_user_id,
                observation=(
                    "Venda criada e enviada para confirmação."
                ),
            )

            self.db.commit()
            return self._get_after_transaction(sale.id)

        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, sale_id: int) -> Sale:
        sale = self.sale_repository.get_by_id(sale_id)

        if sale is None:
            raise ValueError("Venda não encontrada.")

        return sale

    def get_by_codigo(self, codigo: str) -> Sale:
        normalized_code = codigo.strip().upper()
        sale = self.sale_repository.get_by_codigo(normalized_code)

        if sale is None:
            raise ValueError("Venda não encontrada.")

        return sale

    def list_all(
        self,
        status: str | None = None,
        client_id: int | None = None,
        seller_id: int | None = None,
    ) -> list[Sale]:
        normalized_status = self._normalize_status(status)

        return self.sale_repository.list_all(
            status=normalized_status,
            client_id=client_id,
            seller_id=seller_id,
        )

    def update(
        self,
        sale_id: int,
        data: SaleUpdate,
    ) -> Sale:
        try:
            sale = self.sale_repository.get_by_id(
                sale_id,
                for_update=True,
                load_relationships=False,
            )

            if sale is None:
                raise ValueError("Venda não encontrada.")

            self._ensure_awaiting_confirmation(sale)
            update_data = data.model_dump(exclude_unset=True)

            if "client_id" in update_data:
                client = self._validate_client(
                    update_data["client_id"]
                )
                sale.client_id = client.id

            if "seller_id" in update_data:
                seller = self._validate_seller(
                    update_data["seller_id"]
                )
                sale.seller_id = seller.id

            if "observacao" in update_data:
                sale.observacao = update_data["observacao"]

            self.sale_repository.save(sale)
            self.db.commit()

            return self._get_after_transaction(sale.id)

        except Exception:
            self.db.rollback()
            raise

    def confirm(
        self,
        sale_id: int,
        data: SaleConfirm,
        performed_by_user_id: int,
    ) -> Sale:
        try:
            sale = self.sale_repository.get_by_id(
                sale_id,
                for_update=True,
                load_relationships=True,
            )

            if sale is None:
                raise ValueError("Venda não encontrada.")

            self._ensure_awaiting_confirmation(sale)
            self._ensure_sale_has_items(sale)

            locked_stocks = self._lock_and_validate_seller_stocks(
                sale
            )
            self._consume_seller_stocks(
                sale=sale,
                locked_stocks=locked_stocks,
                performed_by_user_id=performed_by_user_id,
            )

            previous_status = sale.status
            self._mark_as_confirmed(
                sale=sale,
                performed_by_user_id=performed_by_user_id,
            )
            self.sale_repository.save(sale)

            self._create_history(
                sale_id=sale.id,
                previous_status=previous_status,
                new_status=SaleStatus.CONFIRMADA,
                performed_by_user_id=performed_by_user_id,
                observation=data.observacao or "Venda confirmada.",
            )

            self._after_sale_confirmation(
                sale=sale,
                data=data,
                performed_by_user_id=performed_by_user_id,
            )

            self.db.commit()
            return self._get_after_transaction(sale.id)

        except Exception:
            self.db.rollback()
            raise

    def cancel(
        self,
        sale_id: int,
        performed_by_user_id: int,
        observacao: str,
    ) -> Sale:
        try:
            sale = self.sale_repository.get_by_id(
                sale_id,
                for_update=True,
                load_relationships=False,
            )

            if sale is None:
                raise ValueError("Venda não encontrada.")

            self._ensure_sale_can_be_cancelled(sale)
            normalized_observation = self._normalize_cancel_observation(
                observacao
            )

            previous_status = sale.status
            self._mark_as_cancelled(
                sale=sale,
                performed_by_user_id=performed_by_user_id,
            )
            self.sale_repository.save(sale)

            self._create_history(
                sale_id=sale.id,
                previous_status=previous_status,
                new_status=SaleStatus.CANCELADA,
                performed_by_user_id=performed_by_user_id,
                observation=normalized_observation,
            )

            self.db.commit()
            return self._get_after_transaction(sale.id)

        except Exception:
            self.db.rollback()
            raise

    def _build_sale(
        self,
        data: SaleCreate,
        client_id: int,
        seller_id: int,
        performed_by_user_id: int,
    ) -> Sale:
        return Sale(
            codigo=self._next_sale_code(),
            client_id=client_id,
            seller_id=seller_id,
            status=SaleStatus.AGUARDANDO,
            subtotal=Decimal("0.00"),
            desconto=Decimal("0.00"),
            total=Decimal("0.00"),
            observacao=data.observacao,
            criado_por_user_id=performed_by_user_id,
        )

    def _build_sale_items(
        self,
        sale_id: int,
        data: SaleCreate,
        products: dict[int, Any],
    ) -> tuple[list[SaleItem], Decimal]:
        items: list[SaleItem] = []
        sale_subtotal = Decimal("0.00")

        for item_data in data.itens:
            product = products[item_data.product_id]
            unit_price = self._money(product.preco)
            item_subtotal = self._money(
                unit_price * item_data.quantidade
            )

            items.append(
                SaleItem(
                    sale_id=sale_id,
                    product_id=product.id,
                    codigo_produto=product.codigo,
                    nome_produto=product.nome,
                    quantidade=item_data.quantidade,
                    preco_unitario=unit_price,
                    subtotal=item_subtotal,
                )
            )
            sale_subtotal += item_subtotal

        return items, self._money(sale_subtotal)

    def _validate_client(self, client_id: int) -> Any:
        client = self.client_repository.get_by_id(client_id)

        if client is None:
            raise ValueError("Cliente não encontrado.")

        if not client.ativo:
            raise ValueError("O cliente está inativo.")

        return client

    def _validate_seller(self, seller_id: int) -> Any:
        seller = self.seller_repository.get_by_id(seller_id)

        if seller is None:
            raise ValueError("Vendedor não encontrado.")

        if not seller.ativo:
            raise ValueError("O vendedor está inativo.")

        return seller

    def _load_products(
        self,
        data: SaleCreate,
    ) -> dict[int, Any]:
        products: dict[int, Any] = {}

        for item_data in data.itens:
            product = self.product_repository.get_by_id(
                item_data.product_id
            )

            if product is None:
                raise ValueError(
                    "Produto não encontrado: "
                    f"{item_data.product_id}."
                )

            if not product.ativo:
                raise ValueError(
                    f"O produto {product.nome} está inativo."
                )

            products[product.id] = product

        return products

    def _lock_and_validate_seller_stocks(
        self,
        sale: Sale,
    ) -> dict[int, Any]:
        locked_stocks: dict[int, Any] = {}

        sorted_items = sorted(
            sale.itens,
            key=lambda item: item.product_id,
        )

        for item in sorted_items:
            seller_stock = (
                self.seller_stock_repository
                .get_by_seller_and_product(
                    seller_id=sale.seller_id,
                    product_id=item.product_id,
                    for_update=True,
                )
            )

            if seller_stock is None:
                raise ValueError(
                    "O vendedor não possui estoque do produto "
                    f"{item.nome_produto}."
                )

            if seller_stock.quantidade < item.quantidade:
                raise ValueError(
                    "Estoque insuficiente para o produto "
                    f"{item.nome_produto}. "
                    f"Disponível: {seller_stock.quantidade}. "
                    f"Necessário: {item.quantidade}."
                )

            locked_stocks[item.product_id] = seller_stock

        return locked_stocks

    def _consume_seller_stocks(
        self,
        sale: Sale,
        locked_stocks: dict[int, Any],
        performed_by_user_id: int,
    ) -> None:
        for item in sale.itens:
            seller_stock = locked_stocks[item.product_id]
            previous_quantity = seller_stock.quantidade
            new_quantity = previous_quantity - item.quantidade

            seller_stock.quantidade = new_quantity
            self.seller_stock_repository.save(seller_stock)

            movement = SellerStockMovement(
                seller_stock_id=seller_stock.id,
                seller_id=sale.seller_id,
                product_id=item.product_id,
                performed_by_user_id=performed_by_user_id,
                tipo=self.SALE_STOCK_MOVEMENT_TYPE,
                quantidade=item.quantidade,
                quantidade_anterior=previous_quantity,
                quantidade_posterior=new_quantity,
                observacao=(
                    f"Saída referente à venda {sale.codigo}."
                ),
            )
            self.seller_stock_movement_repository.create(
                movement
            )

    def _create_history(
        self,
        sale_id: int,
        previous_status: str | None,
        new_status: str,
        performed_by_user_id: int,
        observation: str | None,
    ) -> None:
        history = SaleStatusHistory(
            sale_id=sale_id,
            status_anterior=previous_status,
            status_novo=new_status,
            performed_by_user_id=performed_by_user_id,
            observacao=observation,
        )
        self.history_repository.create(history)

    @staticmethod
    def _mark_as_confirmed(
        sale: Sale,
        performed_by_user_id: int,
    ) -> None:
        sale.status = SaleStatus.CONFIRMADA
        sale.confirmado_por_user_id = performed_by_user_id
        sale.confirmado_em = datetime.now(timezone.utc)

    @staticmethod
    def _mark_as_cancelled(
        sale: Sale,
        performed_by_user_id: int,
    ) -> None:
        sale.status = SaleStatus.CANCELADA
        sale.cancelado_por_user_id = performed_by_user_id
        sale.cancelado_em = datetime.now(timezone.utc)

    @staticmethod
    def _ensure_sale_has_items(sale: Sale) -> None:
        if not sale.itens:
            raise ValueError("A venda não possui itens.")

    @staticmethod
    def _ensure_awaiting_confirmation(sale: Sale) -> None:
        if sale.status == SaleStatus.CONFIRMADA:
            raise ValueError("A venda já está confirmada.")

        if sale.status == SaleStatus.CANCELADA:
            raise ValueError("A venda está cancelada.")

        if sale.status != SaleStatus.AGUARDANDO:
            raise ValueError(
                "A venda não está aguardando confirmação."
            )

    @staticmethod
    def _ensure_sale_can_be_cancelled(sale: Sale) -> None:
        if sale.status == SaleStatus.CANCELADA:
            raise ValueError("A venda já está cancelada.")

        if sale.status == SaleStatus.CONFIRMADA:
            raise ValueError(
                "Uma venda confirmada não pode ser "
                "cancelada diretamente. É necessário "
                "estornar a venda."
            )

        if sale.status != SaleStatus.AGUARDANDO:
            raise ValueError(
                "A venda não pode ser cancelada no status atual."
            )

    @staticmethod
    def _normalize_cancel_observation(observacao: str) -> str:
        normalized_observation = observacao.strip()

        if not normalized_observation:
            raise ValueError(
                "Informe o motivo do cancelamento."
            )

        return normalized_observation

    @staticmethod
    def _validate_unique_products(data: SaleCreate) -> None:
        product_ids = [
            item.product_id
            for item in data.itens
        ]

        if len(product_ids) != len(set(product_ids)):
            raise ValueError(
                "Um mesmo produto não pode aparecer "
                "mais de uma vez na venda."
            )

    @staticmethod
    def _normalize_status(status: str | None) -> str | None:
        if status is None:
            return None

        normalized_status = status.strip().upper()

        if normalized_status not in SaleStatus.ALL:
            raise ValueError("Status de venda inválido.")

        return normalized_status

    def _next_sale_code(self) -> str:
        return self.sequence_repository.next_code(
            self.SALE_SEQUENCE_NAME
        )

    @staticmethod
    def _money(value: Decimal | int | float | str) -> Decimal:
        return Decimal(value).quantize(Decimal("0.01"))

    def _after_sale_confirmation(
        self,
        sale: Sale,
        data: SaleConfirm,
        performed_by_user_id: int,
    ) -> None:
        """Executa integrações ligadas à confirmação da venda.

        O financeiro participa da mesma transação da venda. Caso a geração
        das parcelas falhe, o ``rollback`` executado por ``confirm`` desfaz
        também a confirmação e a baixa de estoque.
        """
        self.finance_service.create_accounts_from_sale(
            sale=sale,
            total_installments=data.total_parcelas,
            first_due_date=data.primeiro_vencimento,
            user_id=performed_by_user_id,
            observation=data.observacao,
        )

    def _get_after_transaction(self, sale_id: int) -> Sale:
        sale = self.sale_repository.get_by_id(sale_id)

        if sale is None:
            raise RuntimeError(
                "A venda foi salva, mas não pôde ser recarregada."
            )

        return sale