"""create accounts payable module

Revision ID: c8a4e2f91b73
Revises: a13c9e7d41b2
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c8a4e2f91b73"
down_revision: Union[str, Sequence[str], None] = "a13c9e7d41b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts_payable",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(30), nullable=False),
        sa.Column("purchase_id", sa.Integer(), sa.ForeignKey("purchases.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("numero_parcela", sa.Integer(), nullable=False),
        sa.Column("total_parcelas", sa.Integer(), nullable=False),
        sa.Column("valor_original", sa.Numeric(12, 2), nullable=False),
        sa.Column("valor_pago", sa.Numeric(12, 2), server_default="0.00", nullable=False),
        sa.Column("saldo_restante", sa.Numeric(12, 2), nullable=False),
        sa.Column("data_vencimento", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), server_default="PENDENTE", nullable=False),
        sa.Column("observacao", sa.Text()),
        sa.Column("criado_por_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("codigo"),
        sa.UniqueConstraint("purchase_id", "numero_parcela", name="uq_accounts_payable_purchase_installment"),
        sa.CheckConstraint("numero_parcela > 0", name="ck_accounts_payable_installment_positive"),
        sa.CheckConstraint("total_parcelas > 0", name="ck_accounts_payable_total_installments_positive"),
        sa.CheckConstraint("numero_parcela <= total_parcelas", name="ck_accounts_payable_installment_within_total"),
        sa.CheckConstraint("valor_original > 0", name="ck_accounts_payable_original_amount_positive"),
        sa.CheckConstraint("valor_pago >= 0", name="ck_accounts_payable_paid_amount_nonnegative"),
        sa.CheckConstraint("saldo_restante >= 0", name="ck_accounts_payable_remaining_amount_nonnegative"),
        sa.CheckConstraint("valor_pago + saldo_restante = valor_original", name="ck_accounts_payable_amount_balance"),
        sa.CheckConstraint("status IN ('PENDENTE','PARCIAL','PAGO','CANCELADO')", name="ck_accounts_payable_valid_status"),
    )
    for column in ["id", "codigo", "purchase_id", "supplier_id", "data_vencimento", "status", "criado_por_user_id"]:
        op.create_index(f"ix_accounts_payable_{column}", "accounts_payable", [column])

    op.create_table(
        "accounts_payable_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_payable_id", sa.Integer(), sa.ForeignKey("accounts_payable.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("payment_method_id", sa.Integer(), sa.ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        sa.Column("data_pagamento", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("pago_por_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("observacao", sa.Text()),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("valor > 0", name="ck_accounts_payable_payments_amount_positive"),
    )
    for column in ["id", "account_payable_id", "payment_method_id", "data_pagamento", "pago_por_user_id"]:
        op.create_index(f"ix_accounts_payable_payments_{column}", "accounts_payable_payments", [column])

    op.create_table(
        "accounts_payable_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_payable_id", sa.Integer(), sa.ForeignKey("accounts_payable.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status_anterior", sa.String(20)),
        sa.Column("status_novo", sa.String(20), nullable=False),
        sa.Column("observacao", sa.Text()),
        sa.Column("performed_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status_anterior IS NULL OR status_anterior IN ('PENDENTE','PARCIAL','PAGO','CANCELADO')", name="ck_accounts_payable_history_valid_previous_status"),
        sa.CheckConstraint("status_novo IN ('PENDENTE','PARCIAL','PAGO','CANCELADO')", name="ck_accounts_payable_history_valid_new_status"),
    )
    for column in ["id", "account_payable_id", "status_novo", "performed_by_user_id", "criado_em"]:
        op.create_index(f"ix_accounts_payable_history_{column}", "accounts_payable_history", [column])

    op.execute("INSERT INTO system_sequences (nome, prefixo, tamanho, ultimo_numero) VALUES ('PAYABLE','PAG',6,0) ON CONFLICT (nome) DO NOTHING")


def downgrade() -> None:
    op.execute("DELETE FROM system_sequences WHERE nome='PAYABLE'")
    op.drop_table("accounts_payable_history")
    op.drop_table("accounts_payable_payments")
    op.drop_table("accounts_payable")
