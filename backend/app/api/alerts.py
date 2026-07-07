from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertRead
from app.schemas.common import PaginatedResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


def get_alert_service(db: Session = Depends(get_session)) -> AlertService:
    return AlertService(alert_repository=AlertRepository(db))


@router.get("", response_model=PaginatedResponse[AlertRead])
def list_alerts(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: AlertService = Depends(get_alert_service),
) -> PaginatedResponse[AlertRead]:
    return service.list(watchlist_id=None, limit=limit, offset=offset)
