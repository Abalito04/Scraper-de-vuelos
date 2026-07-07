from pydantic import BaseModel


class ManualSearchResult(BaseModel):
    watchlist_id: int
    provider: str
    requests_created: int
    offers_found: int
    offers_created: int
    snapshots_created: int
    provider_logs_created: int
    alerts_created: int = 0
    alerts_sent: int = 0
