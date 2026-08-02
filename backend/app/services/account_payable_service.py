from calendar import monthrange
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums.conta_pagar_status import ContaPagarStatus
from app.enums.fluxo_caixa_origem import FluxoCaixaOrigem
from app.enums.fluxo_caixa_tipo import FluxoCaixaTipo
from app.models.account_payable import AccountPayable
from app.models.account_payable_history import AccountPayableHistory
from app.models.account_payable_payment import AccountPayablePayment
from app.models.cash_flow import CashFlow
from app.models.purchase import Purchase
from app.repositores.account_payable_history_repository import AccountPayableHistoryRepository
from app.repositores.account_payable_payment_repository import AccountPayablePaymentRepository
from app.repositores.account_payable_repository import AccountPayableRepository
from app.repositores.cash_flow_repository import CashFlowRepository
from app.repositores.cash_flow_category_repository import CashFlowCategoryRepository
from app.repositores.payment_method_repository import PaymentMethodRepository
from app.repositores.sequence_repository import SequenceRepository

CENTAVOS = Decimal("0.01")
SEQUENCE_NAME_PAYABLE = "PAYABLE"


class AccountPayableService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repository = AccountPayableRepository(db)
        self.payment_repository = AccountPayablePaymentRepository(db)
        self.history_repository = AccountPayableHistoryRepository(db)
        self.cash_flow_repository = CashFlowRepository(db)
        self.cash_flow_category_repository = CashFlowCategoryRepository(db)
        self.payment_method_repository = PaymentMethodRepository(db)
        self.sequence_repository = SequenceRepository(db)

    @staticmethod
    def _money(value) -> Decimal:
        return Decimal(str(value)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)

    @staticmethod
    def _add_months(base_date: date, months: int) -> date:
        month_index = base_date.month - 1 + months
        year = base_date.year + month_index // 12
        month = month_index % 12 + 1
        day = min(base_date.day, monthrange(year, month)[1])
        return date(year, month, day)

    def _next_code(self) -> str:
        return self.sequence_repository.next_code(SEQUENCE_NAME_PAYABLE)

    def _history(self, account, old, new, user_id, observation=None):
        return self.history_repository.create(AccountPayableHistory(account_payable_id=account.id, status_anterior=old, status_novo=new, performed_by_user_id=user_id, observacao=observation))

    def _get_for_update(self, account_id: int) -> AccountPayable | None:
        return self.db.scalar(select(AccountPayable).where(AccountPayable.id == account_id).with_for_update())

    def _purchase_accounts_for_update(self, purchase_id: int) -> list[AccountPayable]:
        statement = select(AccountPayable).where(AccountPayable.purchase_id == purchase_id).order_by(AccountPayable.data_vencimento, AccountPayable.numero_parcela).with_for_update()
        return list(self.db.scalars(statement).all())

    def list_accounts(self):
        return self.account_repository.list_all()

    def list_pending_accounts(self):
        return self.account_repository.list_pending()

    def list_overdue_accounts(self, reference_date: date | None = None):
        return self.account_repository.list_overdue(reference_date or date.today())

    def get_account(self, account_id: int):
        account = self.account_repository.get_by_id(account_id)
        if account is None:
            raise ValueError("Conta a pagar não encontrada.")
        return account

    def get_account_by_code(self, codigo: str):
        account = self.account_repository.get_by_codigo(codigo.strip().upper())
        if account is None:
            raise ValueError("Conta a pagar não encontrada.")
        return account

    def list_purchase_accounts(self, purchase_id: int):
        if purchase_id <= 0:
            raise ValueError("A compra informada é inválida.")
        return self.account_repository.get_by_purchase(purchase_id)

    def create_accounts_from_purchase(self, purchase: Purchase, total_installments: int, first_due_date: date, user_id: int | None, observation: str | None = None):
        if purchase.id is None:
            raise ValueError("A compra precisa estar salva antes de gerar contas a pagar.")
        if purchase.status != "CONFIRMADA":
            raise ValueError("As contas a pagar só podem ser geradas para uma compra confirmada.")
        if total_installments <= 0:
            raise ValueError("A quantidade de parcelas deve ser maior que zero.")
        if self.account_repository.get_by_purchase(purchase.id):
            raise ValueError("Essa compra já possui contas a pagar geradas.")
        total = self._money(purchase.total)
        if total <= 0:
            raise ValueError("O total da compra deve ser maior que zero.")
        regular = (total / Decimal(total_installments)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
        adjustment = total - regular * total_installments
        accounts = []
        for number in range(1, total_installments + 1):
            amount = regular + (adjustment if number == total_installments else Decimal("0.00"))
            amount = self._money(amount)
            account = AccountPayable(codigo=self._next_code(), purchase_id=purchase.id, supplier_id=purchase.supplier_id, numero_parcela=number, total_parcelas=total_installments, valor_original=amount, valor_pago=Decimal("0.00"), saldo_restante=amount, data_vencimento=self._add_months(first_due_date, number - 1), status=ContaPagarStatus.PENDENTE.value, observacao=observation, criado_por_user_id=user_id)
            self.account_repository.create(account)
            self._history(account, None, ContaPagarStatus.PENDENTE.value, user_id, "Conta criada automaticamente pela confirmação da compra.")
            accounts.append(account)
        self.db.flush()
        return accounts

    def register_payment(self, account_id: int, payment_method_id: int, amount: Decimal, user_id: int | None, observation: str | None = None, payment_date: datetime | None = None):
        try:
            amount = self._money(amount)
            if amount <= 0:
                raise ValueError("O valor do pagamento deve ser maior que zero.")
            method = self.payment_method_repository.get_by_id(payment_method_id)
            if method is None:
                raise ValueError("Forma de pagamento não encontrada.")
            if not method.ativo:
                raise ValueError("A forma de pagamento está inativa.")
            selected = self._get_for_update(account_id)
            if selected is None:
                raise ValueError("Conta a pagar não encontrada.")
            open_accounts = [a for a in self._purchase_accounts_for_update(selected.purchase_id) if a.status not in {ContaPagarStatus.PAGO.value, ContaPagarStatus.CANCELADO.value} and self._money(a.saldo_restante) > 0]
            if not open_accounts:
                raise ValueError("Essa compra não possui parcelas abertas para pagamento.")
            total_remaining = sum((self._money(a.saldo_restante) for a in open_accounts), Decimal("0.00"))
            if amount > total_remaining:
                raise ValueError("O valor informado é maior que o saldo total em aberto da compra.")
            remaining = amount
            payments = []
            for account in open_accounts:
                if remaining <= 0:
                    break
                applied = self._money(min(remaining, self._money(account.saldo_restante)))
                old = account.status
                payment = AccountPayablePayment(account_payable_id=account.id, payment_method_id=payment_method_id, valor=applied, data_pagamento=payment_date or datetime.now(timezone.utc), pago_por_user_id=user_id, observacao=observation)
                self.payment_repository.create(payment)
                account.valor_pago = self._money(account.valor_pago + applied)
                account.saldo_restante = self._money(account.valor_original - account.valor_pago)
                account.status = ContaPagarStatus.PAGO.value if account.saldo_restante == 0 else ContaPagarStatus.PARCIAL.value
                self.db.add(account)
                self.db.flush()
                if old != account.status:
                    self._history(account, old, account.status, user_id, f"Pagamento de R$ {applied:.2f} registrado.")
                category = self.cash_flow_category_repository.get_by_code("COMPRAS")
                self.cash_flow_repository.create(
                    CashFlow(
                        tipo=FluxoCaixaTipo.SAIDA.value,
                        origem=FluxoCaixaOrigem.DESPESA.value,
                        category_id=category.id if category else None,
                        payment_method_id=payment_method_id,
                        reference_type="ACCOUNT_PAYABLE_PAYMENT",
                        reference_id=payment.id,
                        descricao=(
                            f"Pagamento da conta {account.codigo} - parcela "
                            f"{account.numero_parcela}/{account.total_parcelas}"
                        ),
                        valor=applied,
                        performed_by_user_id=user_id,
                    )
                )
                payments.append(payment)
                remaining = self._money(remaining - applied)
            self.db.commit()
            return payments
        except Exception:
            self.db.rollback()
            raise

    def cancel_account(self, account_id: int, user_id: int | None, observation: str):
        try:
            obs = observation.strip()
            if not obs:
                raise ValueError("A observação do cancelamento é obrigatória.")
            account = self._get_for_update(account_id)
            if account is None:
                raise ValueError("Conta a pagar não encontrada.")
            if account.status == ContaPagarStatus.PAGO.value:
                raise ValueError("Uma conta paga não pode ser cancelada.")
            if account.status == ContaPagarStatus.CANCELADO.value:
                raise ValueError("Essa conta já está cancelada.")
            if self._money(account.valor_pago) > 0:
                raise ValueError("Uma conta que possui pagamentos não pode ser cancelada.")
            old = account.status
            account.status = ContaPagarStatus.CANCELADO.value
            account.observacao = obs
            self.db.add(account)
            self._history(account, old, account.status, user_id, obs)
            self.db.commit()
            return self.get_account(account.id)
        except Exception:
            self.db.rollback()
            raise
