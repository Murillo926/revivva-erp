from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.enums.fluxo_caixa_origem import FluxoCaixaOrigem
from app.enums.fluxo_caixa_tipo import FluxoCaixaTipo
from app.models.cash_flow import CashFlow
from app.models.cash_flow_category import CashFlowCategory
from app.repositores.cash_flow_category_repository import (
    CashFlowCategoryRepository,
)
from app.repositores.cash_flow_repository import CashFlowRepository
from app.repositores.payment_method_repository import PaymentMethodRepository
from app.schemas.cash_flow import CashFlowCategoryCreate, CashFlowManualCreate

CENTAVOS = Decimal("0.01")
VALID_TYPES = {item.value for item in FluxoCaixaTipo}
VALID_ORIGINS = {item.value for item in FluxoCaixaOrigem}


class CashFlowService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = CashFlowRepository(db)
        self.category_repository = CashFlowCategoryRepository(db)
        self.payment_method_repository = PaymentMethodRepository(db)

    @staticmethod
    def _money(value) -> Decimal:
        return Decimal(str(value)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)

    @staticmethod
    def _normalize_type(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized not in VALID_TYPES:
            raise ValueError("Tipo de lançamento inválido.")
        return normalized

    @staticmethod
    def _normalize_origin(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized not in VALID_ORIGINS:
            raise ValueError("Origem do lançamento inválida.")
        return normalized

    @staticmethod
    def _date_bounds(
        start_date: date | None,
        end_date: date | None,
    ) -> tuple[datetime | None, datetime | None]:
        if start_date and end_date and end_date < start_date:
            raise ValueError("A data final não pode ser anterior à inicial.")

        start_at = (
            datetime.combine(start_date, time.min, tzinfo=timezone.utc)
            if start_date
            else None
        )
        end_at = (
            datetime.combine(
                end_date + timedelta(days=1), time.min, tzinfo=timezone.utc
            )
            if end_date
            else None
        )
        return start_at, end_at

    def create_category(
        self,
        data: CashFlowCategoryCreate,
    ) -> CashFlowCategory:
        try:
            codigo = data.codigo.strip().upper().replace(" ", "_")
            nome = data.nome.strip()
            tipo = self._normalize_type(data.tipo)

            if self.category_repository.get_by_code(codigo):
                raise ValueError("Já existe uma categoria com esse código.")

            category = CashFlowCategory(
                codigo=codigo,
                nome=nome,
                tipo=tipo,
                ativo=True,
            )
            result = self.category_repository.create(category)
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise

    def list_categories(
        self,
        only_active: bool = True,
        tipo: str | None = None,
    ) -> list[CashFlowCategory]:
        return self.category_repository.list_all(
            only_active=only_active,
            tipo=self._normalize_type(tipo),
        )

    def get_by_id(self, flow_id: int) -> CashFlow:
        flow = self.repository.get_by_id(flow_id)
        if flow is None:
            raise ValueError("Lançamento de caixa não encontrado.")
        return flow

    def list_entries(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        tipo: str | None = None,
        origem: str | None = None,
        category_id: int | None = None,
        payment_method_id: int | None = None,
        limit: int = 500,
    ) -> list[CashFlow]:
        if limit < 1 or limit > 2000:
            raise ValueError("O limite deve estar entre 1 e 2000.")

        start_at, end_at = self._date_bounds(start_date, end_date)
        return self.repository.list_all(
            start_at=start_at,
            end_at=end_at,
            tipo=self._normalize_type(tipo),
            origem=self._normalize_origin(origem),
            category_id=category_id,
            payment_method_id=payment_method_id,
            limit=limit,
        )

    def create_manual_entry(
        self,
        data: CashFlowManualCreate,
        user_id: int,
    ) -> CashFlow:
        try:
            tipo = self._normalize_type(data.tipo)
            category = self.category_repository.get_by_id(data.category_id)

            if category is None:
                raise ValueError("Categoria de caixa não encontrada.")
            if not category.ativo:
                raise ValueError("A categoria de caixa está inativa.")
            if category.tipo != tipo:
                raise ValueError(
                    "O tipo do lançamento deve ser igual ao tipo da categoria."
                )

            if data.payment_method_id is not None:
                method = self.payment_method_repository.get_by_id(
                    data.payment_method_id
                )
                if method is None:
                    raise ValueError("Forma de pagamento não encontrada.")
                if not method.ativo:
                    raise ValueError("A forma de pagamento está inativa.")

            description = data.descricao.strip()
            amount = self._money(data.valor)

            flow = CashFlow(
                tipo=tipo,
                origem=(
                    FluxoCaixaOrigem.AJUSTE.value
                    if tipo == FluxoCaixaTipo.ENTRADA.value
                    else FluxoCaixaOrigem.DESPESA.value
                ),
                category_id=category.id,
                payment_method_id=data.payment_method_id,
                reference_type="MANUAL",
                reference_id=None,
                descricao=description,
                valor=amount,
                performed_by_user_id=user_id,
            )
            self.repository.create(flow)
            self.db.commit()
            return self.get_by_id(flow.id)
        except Exception:
            self.db.rollback()
            raise

    def summary(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        start_at, end_at = self._date_bounds(start_date, end_date)
        entradas, saidas = self.repository.totals(start_at, end_at)
        all_entries, all_exits = self.repository.totals()

        return {
            "periodo_inicio": start_at,
            "periodo_fim": end_at,
            "entradas": self._money(entradas),
            "saidas": self._money(saidas),
            "saldo_periodo": self._money(entradas - saidas),
            "saldo_atual": self._money(all_entries - all_exits),
        }

    def daily_evolution(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict]:
        start_at, end_at = self._date_bounds(start_date, end_date)
        assert start_at is not None and end_at is not None

        grouped = {
            row.data: (self._money(row.entradas), self._money(row.saidas))
            for row in self.repository.totals_grouped_by_day(start_at, end_at)
        }

        result: list[dict] = []
        current = start_date
        while current <= end_date:
            entradas, saidas = grouped.get(
                current, (Decimal("0.00"), Decimal("0.00"))
            )
            result.append(
                {
                    "data": current,
                    "entradas": entradas,
                    "saidas": saidas,
                    "saldo": self._money(entradas - saidas),
                }
            )
            current += timedelta(days=1)
        return result

    def totals_by_category(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        start_at, end_at = self._date_bounds(start_date, end_date)
        categories = {
            category.id: category.nome
            for category in self.category_repository.list_all()
        }
        return [
            {
                "category_id": row.category_id,
                "categoria": categories.get(row.category_id, "Sem categoria"),
                "tipo": row.tipo,
                "total": self._money(row.total),
            }
            for row in self.repository.totals_grouped_by_category(
                start_at, end_at
            )
        ]
