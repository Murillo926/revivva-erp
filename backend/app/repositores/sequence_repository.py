from sqlalchemy.orm import Session

from app.models.sequence import Sequence


class SequenceRepository:

    def __init__(self, db: Session):
        self.db = db

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