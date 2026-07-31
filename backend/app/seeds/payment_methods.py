from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.payment_method import PaymentMethod

FORMAS_PAGAMENTO_PADRAO = ("PIX", "DINHEIRO", "CARTAO_CREDITO", "CARTAO_DEBITO", "TRANSFERENCIA", "BOLETO", "PROMISSORIA")

def seed_payment_methods(db: Session) -> None:
    existentes = set(db.scalars(select(PaymentMethod.nome).where(PaymentMethod.nome.in_(FORMAS_PAGAMENTO_PADRAO))).all())
    novos = [PaymentMethod(nome=nome, ativo=True) for nome in FORMAS_PAGAMENTO_PADRAO if nome not in existentes]
    if novos:
        db.add_all(novos)
        db.commit()
