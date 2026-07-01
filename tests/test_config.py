"""Tests for the centralized settings module (backlog item 3.2).

Each test constructs ``Settings(_env_file=None, ...)`` to bypass any developer
``.env`` and exercise defaults, environment overrides, and required-field
validation deterministically.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app import __version__
from app.core.config import Settings


def test_defaults_load() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://localhost/db",
        redis_url="redis://localhost:6379/0",
    )

    assert settings.app_title == "Document Intelligence API"
    assert settings.app_version == __version__
    assert settings.app_env == "local"
    assert settings.storage_path == "storage"
    assert settings.worker_concurrency == 1
    assert settings.worker_queue_name == "document_intelligence"


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("STORAGE_PATH", "/var/data")
    monkeypatch.setenv("WORKER_CONCURRENCY", "4")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://db-host/prod")
    monkeypatch.setenv("REDIS_URL", "redis://redis-host:6379/2")

    settings = Settings(_env_file=None)

    assert settings.app_env == "production"
    assert settings.storage_path == "/var/data"
    assert settings.worker_concurrency == 4
    assert isinstance(settings.worker_concurrency, int)
    assert settings.database_url == "postgresql+psycopg://db-host/prod"
    assert settings.redis_url == "redis://redis-host:6379/2"


def test_missing_required_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    message = str(exc_info.value)
    assert "database_url" in message
    assert "redis_url" in message


def test_invalid_worker_concurrency_raises() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://localhost/db",
            redis_url="redis://localhost:6379/0",
            worker_concurrency=0,
        )
