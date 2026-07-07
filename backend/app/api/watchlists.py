from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.core.enums import TripType
from app.repositories.watchlist_repository import WatchlistRepository
from app.schemas.common import PaginatedResponse
from app.schemas.watchlist import WatchlistCreate, WatchlistRead, WatchlistSummary, WatchlistUpdate
from app.services.watchlist_service import WatchlistNotFoundError, WatchlistService

router = APIRouter(prefix="/api/v1/watchlists", tags=["watchlists"])


def get_watchlist_service(db: Session = Depends(get_session)) -> WatchlistService:
    return WatchlistService(WatchlistRepository(db))


@router.post("", response_model=WatchlistRead, status_code=status.HTTP_201_CREATED)
def create_watchlist(
    payload: WatchlistCreate,
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistRead:
    return service.create(payload)


@router.get("", response_model=PaginatedResponse[WatchlistSummary])
def list_watchlists(
    active: bool | None = None,
    trip_type: TripType | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: WatchlistService = Depends(get_watchlist_service),
) -> PaginatedResponse[WatchlistSummary]:
    return service.list(active=active, trip_type=trip_type, limit=limit, offset=offset)


@router.get("/{watchlist_id}", response_model=WatchlistRead)
def get_watchlist(
    watchlist_id: int,
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistRead:
    try:
        return service.get(watchlist_id)
    except WatchlistNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Watchlist not found") from exc


@router.patch("/{watchlist_id}", response_model=WatchlistRead)
def update_watchlist(
    watchlist_id: int,
    payload: WatchlistUpdate,
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistRead:
    try:
        return service.update(watchlist_id, payload)
    except WatchlistNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Watchlist not found") from exc


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watchlist(
    watchlist_id: int,
    service: WatchlistService = Depends(get_watchlist_service),
) -> Response:
    try:
        service.delete(watchlist_id)
    except WatchlistNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Watchlist not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
