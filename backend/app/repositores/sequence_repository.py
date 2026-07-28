from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sequence import Sequence


class SequenceRepository:

    def get_by_name(self, name: str) -> Sequence | None:
        return (
            self.db.query(Sequence)
            .filter(Sequence.nome == name)
            .first()
        )

    def save(self, sequence: Sequence):
        self.db.add(sequence)
        self.db.commit()
        self.db.refresh(sequence)

    def __init__(self, db: Session):
        self.db = db

    def get_by_name_for_update(
        self,
        name: str,
    ) -> Sequence | None:
        statement = (
            select(Sequence)
            .where(Sequence.nome == name)
            .with_for_update()
        )

        return self.db.scalar(statement)

    def next_code(
        self,
        name: str,
    ) -> str:
        sequence = self.get_by_name_for_update(name)

        if sequence is None:
            raise ValueError(
                f"Sequência '{name}' não encontrada."
            )

        sequence.ultimo_numero += 1

        code = (
            f"{sequence.prefixo}"
            f"{sequence.ultimo_numero:0{sequence.tamanho}d}"
        )

        self.db.add(sequence)
        self.db.flush()

        return code