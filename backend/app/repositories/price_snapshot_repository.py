from sqlalchemy.orm import Session

from app.models import PriceSnapshot


class PriceSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, snapshot: PriceSnapshot) -> PriceSnapshot:
        self.db.add(snapshot)
        self.db.flush()
        return snapshot
