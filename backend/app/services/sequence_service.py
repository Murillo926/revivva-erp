from sqlalchemy.orm import Session

from app.enums.sequence_name import SequenceName
from app.repositores.sequence_repository import SequenceRepository


class SequenceService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = SequenceRepository(db)

    def generate_code(self, name: SequenceName) -> str:
        sequence = self.repository.get_by_name(name.value)

        if sequence is None:
            raise ValueError(
                f"A sequência '{name.value}' não foi encontrada."
            )

        sequence.ultimo_numero += 1

        self.repository.save(sequence)

        numero_formatado = str(sequence.ultimo_numero).zfill(
            sequence.tamanho
        )

        return f"{sequence.prefixo}{numero_formatado}"