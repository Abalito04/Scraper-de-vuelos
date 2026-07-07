from sqlalchemy.orm import Session

from app.models import ProviderLog


class ProviderLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, log: ProviderLog) -> ProviderLog:
        self.db.add(log)
        self.db.flush()
        return log
