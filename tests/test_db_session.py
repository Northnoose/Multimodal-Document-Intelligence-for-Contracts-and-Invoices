"""Tests for the database session seam (ID 4.1).

All tests use an in-memory sqlite URL (stdlib ``sqlite3``) or an unreachable URL,
so they never require a running PostgreSQL server. The lazy ``lru_cache`` factories
are cleared around each test so per-test ``DATABASE_URL`` overrides take effect.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import (
    check_database_connection,
    get_db_session,
    get_engine,
    get_sessionmaker,
)

_SQLITE_MEMORY_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture(autouse=True)
def _clear_lazy_caches() -> Iterator[None]:
    """Clear the settings + engine + sessionmaker caches around each test."""

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    yield
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()


def test_engine_uses_settings_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _SQLITE_MEMORY_URL)
    assert str(get_engine().url) == _SQLITE_MEMORY_URL


def test_get_db_session_yields_and_closes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _SQLITE_MEMORY_URL)
    gen = get_db_session()
    session = next(gen)
    assert isinstance(session, Session)
    assert session.execute(text("SELECT 1")).scalar() == 1
    # Exhausting the generator triggers the ``finally`` close.
    with pytest.raises(StopIteration):
        next(gen)


def test_check_connection_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _SQLITE_MEMORY_URL)
    assert check_database_connection() is True


def test_check_connection_failure_logs(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://user:secretpw@localhost:1/none"
    )
    with caplog.at_level(logging.ERROR, logger="app.db.session"):
        assert check_database_connection() is False
    assert any(record.levelno >= logging.ERROR for record in caplog.records)
    assert "secretpw" not in caplog.text
