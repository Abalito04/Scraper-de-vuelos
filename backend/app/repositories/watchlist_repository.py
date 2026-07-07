from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import TripType
from app.models import User, Watchlist


class WatchlistRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create_dev_user(self) -> User:
        user = self.db.scalar(select(User).where(User.email == "dev@fareradar.local"))
        if user is not None:
            return user
        user = User(name="FareRadar Dev User", email="dev@fareradar.local", preferred_currency="USD")
        self.db.add(user)
        self.db.flush()
        return user

    def add(self, watchlist: Watchlist) -> Watchlist:
        self.db.add(watchlist)
        self.db.flush()
        self.db.refresh(watchlist)
        return watchlist

    def get(self, watchlist_id: int) -> Watchlist | None:
        return self.db.scalar(
            self._base_query().where(Watchlist.id == watchlist_id)
        )

    def list(
        self,
        *,
        active: bool | None,
        trip_type: TripType | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Watchlist], int]:
        filters = []
        if active is not None:
            filters.append(Watchlist.active == active)
        if trip_type is not None:
            filters.append(Watchlist.trip_type == trip_type)

        total = self.db.scalar(select(func.count()).select_from(Watchlist).where(*filters)) or 0
        items = list(
            self.db.scalars(
                self._base_query()
                .where(*filters)
                .order_by(Watchlist.created_at.desc(), Watchlist.id.desc())
                .limit(limit)
                .offset(offset)
            )
        )
        return items, total

    def delete_soft(self, watchlist: Watchlist) -> Watchlist:
        watchlist.active = False
        self.db.flush()
        self.db.refresh(watchlist)
        return watchlist

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def _base_query(self) -> Select[tuple[Watchlist]]:
        return select(Watchlist).options(
            selectinload(Watchlist.origins),
            selectinload(Watchlist.destinations),
            selectinload(Watchlist.date_windows),
            selectinload(Watchlist.segments),
        )
