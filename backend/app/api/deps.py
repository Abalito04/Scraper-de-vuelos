from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db


def get_session() -> Generator[Session]:
    yield from get_db()
