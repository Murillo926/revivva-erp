from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums.conta_receber_status import ContaReceberStatus
from app.enums.fluxo_caixa_origem import FluxoCaixaOrigem
from app.enums.fluxo_caixa_tipo import FluxoCaixaTipo
from app.models.account_receivable import AccountReceivable
from app.models.account_receivable_history import AccountReceivableHistory
from app.models.account_receivable_payment import AccountReceivablePayment
from app.models.cash_flow import CashFlow
from app.models.sale import Sale
from app.repositores.account_receivable_history_repository import (
    AccountReceivableHistoryRepository,
)
from app.repositores.account_receivable_payment_repository import (
    AccountReceivablePaymentRepository,
)
from app.repositores.account_receivable_repository import (
    AccountReceivableRepository,
)
from app.repositores.cash_flow_repository import CashFlowRepository
from app.repositores.cash_flow_category_repository import CashFlowCategoryRepository
from app.repositores.payment_method_repository import PaymentMethodRepository
from app.repositores.sequence_repository import SequenceRepository


CENTAVOS = Decimal("0.01")
SEQUENCE_NAME_RECEIVABLE = "RECEIVABLE"


class FinanceService:
    """Regras de negócio do módulo financeiro.

    Este service participa da transação aberta pelo serviço de aplicação
    chamador. Ele executa ``flush()``, mas nunca ``commit()`` ou ``rollback()``.
    """

    def __init__(self, db: Session):
        self.db = db

        self.account_repository = AccountReceivableRepository(db)
        self.payment_repository = AccountReceivablePaymentRepository(db)
        self.history_repository = AccountReceivableHistoryRepository(db)
        self.cash_flow_repository = CashFlowRepository(db)
        self.cash_flow_category_repository = CashFlowCategoryRepository(db)
        self.payment_method_repository = PaymentMethodRepository(db)
        self.sequence_repository = SequenceRepository(db)

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    @staticmethod
    def _money(value: Decimal | int | float | str) -> Decimal:
        return Decimal(str(value)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)

    @staticmethod
    def _add_months(base_date: date, months: int) -> date:
        month_index = (base_date.month - 1) + months
        year = base_date.year + month_index // 12
        month = month_index % 12 + 1
        day = min(base_date.day, monthrange(year, month)[1])
        return date(year, month, day)

    @staticmethod
    def _validate_user_id(user_id: int | None) -> None:
        if user_id is not None and user_id <= 0:
            raise ValueError("O usuário informado é inválido.")

    @staticmethod
    def _status_after_payment(account: AccountReceivable) -> str:
        if account.saldo_restante == Decimal("0.00"):
            return ContaReceberStatus.PAGO.value

        if account.valor_recebido > Decimal("0.00"):
            return ContaReceberStatus.PARCIAL.value

        return ContaReceberStatus.PENDENTE.value

    def _next_receivable_code(self) -> str:
        return self.sequence_repository.next_code(
            SEQUENCE_NAME_RECEIVABLE
        )

    def _create_history(
        self,
        account: AccountReceivable,
        previous_status: str | None,
        new_status: str,
        user_id: int | None,
        observation: str | None = None,
    ) -> AccountReceivableHistory:
        history = AccountReceivableHistory(
            account_receivable_id=account.id,
            status_anterior=previous_status,
            status_novo=new_status,
            observacao=observation,
            performed_by_user_id=user_id,
        )

        return self.history_repository.create(history)

    def _create_cash_entry(
        self,
        payment: AccountReceivablePayment,
        account: AccountReceivable,
        user_id: int | None,
    ) -> CashFlow:
        flow = CashFlow(
            tipo=FluxoCaixaTipo.ENTRADA.value,
            origem=FluxoCaixaOrigem.VENDA.value,
            category_id=(
                self.cash_flow_category_repository.get_by_code("VENDAS").id
                if self.cash_flow_category_repository.get_by_code("VENDAS")
                else None
            ),
            payment_method_id=payment.payment_method_id,
            reference_type="ACCOUNT_RECEIVABLE_PAYMENT",
            reference_id=payment.id,
            descricao=(
                f"Recebimento da conta {account.codigo} "
                f"- parcela {account.numero_parcela}/{account.total_parcelas}"
            ),
            valor=self._money(payment.valor),
            performed_by_user_id=user_id,
        )

        return self.cash_flow_repository.create(flow)

    def _get_account_for_update(
        self,
        account_id: int,
    ) -> AccountReceivable | None:
        statement = (
            select(AccountReceivable)
            .where(AccountReceivable.id == account_id)
            .with_for_update()
        )
        return self.db.scalar(statement)

    def _get_sale_accounts_for_update(
        self,
        sale_id: int,
    ) -> list[AccountReceivable]:
        statement = (
            select(AccountReceivable)
            .where(AccountReceivable.sale_id == sale_id)
            .order_by(
                AccountReceivable.data_vencimento.asc(),
                AccountReceivable.numero_parcela.asc(),
            )
            .with_for_update()
        )
        return list(self.db.scalars(statement))

    # ------------------------------------------------------------------
    # Formas de pagamento
    # ------------------------------------------------------------------

    def list_payment_methods(self):
        return self.payment_method_repository.list_active()

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def get_account(self, account_id: int) -> AccountReceivable:
        account = self.account_repository.get_by_id(account_id)

        if account is None:
            raise ValueError("Conta a receber não encontrada.")

        return account

    def get_account_by_code(self, code: str) -> AccountReceivable:
        normalized_code = code.strip().upper()

        if not normalized_code:
            raise ValueError("O código da conta é obrigatório.")

        account = self.account_repository.get_by_codigo(normalized_code)

        if account is None:
            raise ValueError("Conta a receber não encontrada.")

        return account

    def list_accounts(self) -> list[AccountReceivable]:
        return self.account_repository.list_all()

    def list_pending_accounts(self) -> list[AccountReceivable]:
        return self.account_repository.list_pending()

    def list_overdue_accounts(
        self,
        reference_date: date | None = None,
    ) -> list[AccountReceivable]:
        return self.account_repository.list_overdue(
            reference_date or date.today()
        )

    def list_sale_accounts(
        self,
        sale_id: int,
    ) -> list[AccountReceivable]:
        if sale_id <= 0:
            raise ValueError("A venda informada é inválida.")

        return self.account_repository.get_by_sale(sale_id)

    # ------------------------------------------------------------------
    # Geração de parcelas
    # ------------------------------------------------------------------

    def create_accounts_from_sale(
        self,
        sale: Sale,
        total_installments: int,
        first_due_date: date,
        user_id: int | None,
        observation: str | None = None,
    ) -> list[AccountReceivable]:
        """Gera as contas a receber de uma venda confirmada.

        O valor total é dividido em centavos. Qualquer diferença de
        arredondamento fica na última parcela. A transação é concluída
        pelo serviço chamador.
        """
        self._validate_user_id(user_id)

        if sale.id is None:
            raise ValueError("A venda precisa estar salva antes de gerar parcelas.")

        if sale.status != "CONFIRMADA":
            raise ValueError(
                "As contas a receber só podem ser geradas para uma venda confirmada."
            )

        if total_installments <= 0:
            raise ValueError("A quantidade de parcelas deve ser maior que zero.")

        sale_total = self._money(sale.total)

        if sale_total <= Decimal("0.00"):
            raise ValueError("O total da venda deve ser maior que zero.")

        existing_accounts = self.account_repository.get_by_sale(sale.id)

        if existing_accounts:
            raise ValueError("Essa venda já possui contas a receber geradas.")

        regular_amount = (
            sale_total / Decimal(total_installments)
        ).quantize(CENTAVOS, rounding=ROUND_HALF_UP)

        generated_total = regular_amount * total_installments
        last_installment_adjustment = sale_total - generated_total
        accounts: list[AccountReceivable] = []

        for installment_number in range(1, total_installments + 1):
            installment_amount = regular_amount

            if installment_number == total_installments:
                installment_amount += last_installment_adjustment

            installment_amount = self._money(installment_amount)

            account = AccountReceivable(
                codigo=self._next_receivable_code(),
                sale_id=sale.id,
                client_id=sale.client_id,
                numero_parcela=installment_number,
                total_parcelas=total_installments,
                valor_original=installment_amount,
                valor_recebido=Decimal("0.00"),
                saldo_restante=installment_amount,
                data_vencimento=self._add_months(
                    first_due_date,
                    installment_number - 1,
                ),
                status=ContaReceberStatus.PENDENTE.value,
                observacao=observation,
                criado_por_user_id=user_id,
            )

            self.account_repository.create(account)

            self._create_history(
                account=account,
                previous_status=None,
                new_status=ContaReceberStatus.PENDENTE.value,
                user_id=user_id,
                observation=(
                    "Conta criada automaticamente pela confirmação da venda."
                ),
            )
            accounts.append(account)

        self.db.flush()
        return accounts

    # ------------------------------------------------------------------
    # Pagamentos
    # ------------------------------------------------------------------

    def register_payment(
        self,
        account_id: int,
        payment_method_id: int,
        amount: Decimal,
        user_id: int | None,
        observation: str | None = None,
        payment_date: datetime | None = None,
    ) -> list[AccountReceivablePayment]:
        """Distribui o valor entre as parcelas mais antigas da venda.

        A conta indicada serve para identificar a venda. O pagamento começa
        sempre pela parcela aberta mais antiga, conforme a regra do módulo.
        """

        self._validate_user_id(user_id)

        amount = self._money(amount)

        if account_id <= 0:
            raise ValueError("A conta informada é inválida.")

        if payment_method_id <= 0:
            raise ValueError("A forma de pagamento informada é inválida.")

        if amount <= Decimal("0.00"):
            raise ValueError("O valor do pagamento deve ser maior que zero.")

        payment_method = self.payment_method_repository.get_by_id(
            payment_method_id
        )

        if payment_method is None:
            raise ValueError("Forma de pagamento não encontrada.")

        if not payment_method.ativo:
            raise ValueError("A forma de pagamento está inativa.")

        selected_account = self._get_account_for_update(account_id)

        if selected_account is None:
            raise ValueError("Conta a receber não encontrada.")

        sale_accounts = self._get_sale_accounts_for_update(
            selected_account.sale_id
        )

        open_accounts = [
            account
            for account in sale_accounts
            if account.status
            not in {
                ContaReceberStatus.PAGO.value,
                ContaReceberStatus.CANCELADO.value,
            }
            and self._money(account.saldo_restante) > Decimal("0.00")
        ]

        if not open_accounts:
            raise ValueError(
                "Essa venda não possui parcelas abertas para recebimento."
            )

        total_remaining = sum(
            (self._money(account.saldo_restante) for account in open_accounts),
            Decimal("0.00"),
        )

        if amount > total_remaining:
            raise ValueError(
                "O valor informado é maior que o saldo total em aberto da venda."
            )

        remaining_payment = amount
        payments: list[AccountReceivablePayment] = []

        for account in open_accounts:
            if remaining_payment <= Decimal("0.00"):
                break

            account_balance = self._money(account.saldo_restante)
            applied_amount = min(remaining_payment, account_balance)
            applied_amount = self._money(applied_amount)

            previous_status = account.status

            payment = AccountReceivablePayment(
                account_receivable_id=account.id,
                payment_method_id=payment_method_id,
                valor=applied_amount,
                data_pagamento=payment_date or datetime.now(timezone.utc),
                recebido_por_user_id=user_id,
                observacao=observation,
            )

            self.payment_repository.create(payment)

            account.valor_recebido = self._money(
                account.valor_recebido + applied_amount
            )
            account.saldo_restante = self._money(
                account.valor_original - account.valor_recebido
            )
            account.status = self._status_after_payment(account)

            self.db.add(account)
            self.db.flush()

            if account.status != previous_status:
                self._create_history(
                    account=account,
                    previous_status=previous_status,
                    new_status=account.status,
                    user_id=user_id,
                    observation=(
                        f"Pagamento de R$ {applied_amount:.2f} registrado."
                    ),
                )

            self._create_cash_entry(
                payment=payment,
                account=account,
                user_id=user_id,
            )

            payments.append(payment)
            remaining_payment = self._money(
                remaining_payment - applied_amount
            )

        if remaining_payment != Decimal("0.00"):
            raise RuntimeError(
                "Não foi possível distribuir integralmente o pagamento."
            )

        self.db.flush()
        return payments

    # ------------------------------------------------------------------
    # Cancelamento
    # ------------------------------------------------------------------

    def cancel_account(
        self,
        account_id: int,
        user_id: int | None,
        observation: str,
    ) -> AccountReceivable:
        self._validate_user_id(user_id)

        if account_id <= 0:
            raise ValueError("A conta informada é inválida.")

        normalized_observation = observation.strip()

        if not normalized_observation:
            raise ValueError(
                "A observação do cancelamento é obrigatória."
            )

        account = self._get_account_for_update(account_id)

        if account is None:
            raise ValueError("Conta a receber não encontrada.")

        if account.status == ContaReceberStatus.PAGO.value:
            raise ValueError("Uma conta paga não pode ser cancelada.")

        if account.status == ContaReceberStatus.CANCELADO.value:
            raise ValueError("Essa conta já está cancelada.")

        if self._money(account.valor_recebido) > Decimal("0.00"):
            raise ValueError(
                "Uma conta que possui recebimentos não pode ser cancelada."
            )

        previous_status = account.status
        account.status = ContaReceberStatus.CANCELADO.value
        account.observacao = normalized_observation

        self.db.add(account)
        self.db.flush()

        self._create_history(
            account=account,
            previous_status=previous_status,
            new_status=ContaReceberStatus.CANCELADO.value,
            user_id=user_id,
            observation=normalized_observation,
        )

        self.db.flush()
        return account

    def cancel_sale_accounts(
        self,
        sale_id: int,
        user_id: int | None,
        observation: str,
    ) -> list[AccountReceivable]:
        """Cancela todas as parcelas não pagas e sem recebimentos da venda."""

        self._validate_user_id(user_id)

        if sale_id <= 0:
            raise ValueError("A venda informada é inválida.")

        normalized_observation = observation.strip()

        if not normalized_observation:
            raise ValueError(
                "A observação do cancelamento é obrigatória."
            )

        accounts = self._get_sale_accounts_for_update(sale_id)

        if not accounts:
            return []

        for account in accounts:
            if account.status == ContaReceberStatus.PAGO.value:
                raise ValueError(
                    "A venda possui parcela paga e suas contas não podem ser canceladas."
                )

            if self._money(account.valor_recebido) > Decimal("0.00"):
                raise ValueError(
                    "A venda possui parcela com recebimento e suas contas não podem ser canceladas."
                )

        changed_accounts: list[AccountReceivable] = []

        for account in accounts:
            if account.status == ContaReceberStatus.CANCELADO.value:
                continue

            previous_status = account.status
            account.status = ContaReceberStatus.CANCELADO.value
            account.observacao = normalized_observation

            self.db.add(account)
            self.db.flush()

            self._create_history(
                account=account,
                previous_status=previous_status,
                new_status=ContaReceberStatus.CANCELADO.value,
                user_id=user_id,
                observation=normalized_observation,
            )

            changed_accounts.append(account)

        self.db.flush()
        return changed_accounts