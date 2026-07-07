from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/v1/status")
def api_status(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "provider": settings.flight_provider,
    }
