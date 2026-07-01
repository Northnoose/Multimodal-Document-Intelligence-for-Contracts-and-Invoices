"""Application configuration backed by environment variables / a local .env file.

Uses pydantic-settings so configuration is typed and validated at startup. Invalid
values raise a clear ``pydantic.ValidationError`` before the app accepts traffic.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import __version__


class Settings(BaseSettings):
    """Runtime settings for the API, worker, and database seam.

    ``database_url`` and ``redis_url`` are required (no default): a missing value
    fails fast at startup with a clear ``pydantic.ValidationError`` naming the
    field. All other fields carry safe local-development defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_title: str = "Document Intelligence API"
    app_version: str = __version__
    app_env: str = "local"

    database_url: str
    redis_url: str

    storage_path: str = "storage"
    worker_concurrency: int = Field(default=1, ge=1)
    worker_queue_name: str = "document_intelligence"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Cached so configuration is parsed once per process. Missing required fields
    (``database_url`` / ``redis_url``) or invalid values surface here as a
    ``ValidationError`` the moment settings are first loaded (at application
    startup), producing a clear, readable failure before traffic is served.
    """

    return Settings()
