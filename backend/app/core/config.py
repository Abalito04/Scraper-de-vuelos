from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FareRadar"
    app_env: str = "local"
    app_debug: bool = True
    app_version: str = "0.1.0"

    backend_host: str = "0.0.0.0"
    backend_port: int = Field(default=8000, validation_alias="PORT")
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://fare_radar:fare_radar@postgres:5432/fare_radar"
    redis_url: str = "redis://redis:6379/0"
    flight_provider: str = "mock"
    mock_provider_seed: int = 12345
    mock_provider_min_price: int = 500
    mock_provider_max_price: int = 1800
    max_combinations_per_watchlist: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
