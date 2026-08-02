from datetime import datetime
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.cash_flow import CashFlow


class CashFlowRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, flow: CashFlow) -> CashFlow:
        self.db.add(flow)
        self.db.flush()
        self.db.refresh(flow)
        return flow

    def get_by_id(self, flow_id: int) -> CashFlow | None:
        statement = (
            select(CashFlow)
            .options(
                selectinload(CashFlow.categoria),
                selectinload(CashFlow.forma_pagamento),
            )
            .where(CashFlow.id == flow_id)
        )
        return self.db.scalar(statement)

    def list_all(
        self,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        tipo: str | None = None,
        origem: str | None = None,
        category_id: int | None = None,
        payment_method_id: int | None = None,
        limit: int = 500,
    ) -> list[CashFlow]:
        statement = select(CashFlow).options(
            selectinload(CashFlow.categoria),
            selectinload(CashFlow.forma_pagamento),
        )

        if start_at is not None:
            statement = statement.where(CashFlow.criado_em >= start_at)
        if end_at is not None:
            statement = statement.where(CashFlow.criado_em < end_at)
        if tipo is not None:
            statement = statement.where(CashFlow.tipo == tipo)
        if origem is not None:
            statement = statement.where(CashFlow.origem == origem)
        if category_id is not None:
            statement = statement.where(CashFlow.category_id == category_id)
        if payment_method_id is not None:
            statement = statement.where(
                CashFlow.payment_method_id == payment_method_id
            )

        statement = statement.order_by(
            CashFlow.criado_em.desc(), CashFlow.id.desc()
        ).limit(limit)
        return list(self.db.scalars(statement).all())

    def totals(
        self,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> tuple[Decimal, Decimal]:
        entry_value = case(
            (CashFlow.tipo == "ENTRADA", CashFlow.valor), else_=0
        )
        exit_value = case(
            (CashFlow.tipo == "SAIDA", CashFlow.valor), else_=0
        )
        statement = select(
            func.coalesce(func.sum(entry_value), 0),
            func.coalesce(func.sum(exit_value), 0),
        )

        if start_at is not None:
            statement = statement.where(CashFlow.criado_em >= start_at)
        if end_at is not None:
            statement = statement.where(CashFlow.criado_em < end_at)

        entradas, saidas = self.db.execute(statement).one()
        return Decimal(entradas), Decimal(saidas)

    def totals_grouped_by_day(
        self,
        start_at: datetime,
        end_at: datetime,
    ) -> list[tuple]:
        day = func.date(CashFlow.criado_em)
        entry_value = case(
            (CashFlow.tipo == "ENTRADA", CashFlow.valor), else_=0
        )
        exit_value = case(
            (CashFlow.tipo == "SAIDA", CashFlow.valor), else_=0
        )
        statement = (
            select(
                day.label("data"),
                func.coalesce(func.sum(entry_value), 0).label("entradas"),
                func.coalesce(func.sum(exit_value), 0).label("saidas"),
            )
            .where(
                CashFlow.criado_em >= start_at,
                CashFlow.criado_em < end_at,
            )
            .group_by(day)
            .order_by(day)
        )
        return list(self.db.execute(statement).all())

    def totals_grouped_by_category(
        self,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[tuple]:
        statement = select(
            CashFlow.category_id,
            CashFlow.tipo,
            func.sum(CashFlow.valor).label("total"),
        )

        if start_at is not None:
            statement = statement.where(CashFlow.criado_em >= start_at)
        if end_at is not None:
            statement = statement.where(CashFlow.criado_em < end_at)

        statement = statement.group_by(CashFlow.category_id, CashFlow.tipo)
        return list(self.db.execute(statement).all())
