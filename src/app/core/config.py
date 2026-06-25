"""Application configuration backed by environment variables / a local .env file.

Uses pydantic-settings so configuration is typed and validated at startup. Invalid
values raise a clear ``pydantic.ValidationError`` before the app accepts traffic.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app import __version__


class Settings(BaseSettings):
    """Runtime settings for the API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_title: str = "Document Intelligence API"
    app_version: str = __version__
    app_env: str = "local"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Cached so configuration is parsed once per process. A malformed environment
    surfaces here as a ``ValidationError`` the moment settings are first loaded
    (at application startup), producing a clear, readable failure.
    """

    return Settings()
