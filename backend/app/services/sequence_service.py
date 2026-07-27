from app.repositores.sequence_repository import SequenceRepository
from app.core import SequenceName

class SequenceService:

    def __init__(self, repository: SequenceRepository):
        self.repository = repository

    def generate_code(self, name: SequenceName) -> str:

        sequence = self.repository.get_by_name(name.value)

        if sequence is None:
            raise Exception("Sequência não encontrada")

        sequence.ultimo_numero += 1

        self.repository.save(sequence)

        numero = str(sequence.ultimo_numero).zfill(sequence.tamanho)

        return f"{sequence.prefixo}{numero}"