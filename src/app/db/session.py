"""Database session seam (SQLAlchemy 2.0).

The engine and session factory are created lazily so nothing connects to a
database at import time, and the health endpoint stays DB-free. No models are
defined in this phase; migrations live under ``migrations/`` (Alembic).

This module also provides a FastAPI session dependency (``get_db_session``) and a
local connectivity probe (``check_database_connection``). Both connect only when
called, never at import or application startup.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_engine() -> Engine:
    """Return a lazily-created SQLAlchemy engine.

    Reads ``database_url`` from the central ``Settings`` module when first called.
    ``pool_pre_ping=True`` transparently discards stale/dead connections before
    they are handed out. Because settings are only read inside this function,
    importing the module still does not construct settings or connect to a
    database.
    """

    database_url = get_settings().database_url
    return create_engine(database_url, future=True, pool_pre_ping=True)


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    """Return a session factory bound to the lazily-created engine."""

    return sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)


def get_db_session() -> Iterator[Session]:
    """FastAPI dependency; use via ``Depends(get_db_session)``.

    Opens a session from the lazily-created factory, yields it for the duration
    of a request, and always closes it afterwards. Not wired into any route yet
    (there are no DB-backed endpoints in this phase).
    """

    factory = get_sessionmaker()
    session = factory()
    try:
        yield session
    finally:
        session.close()


def check_database_connection() -> bool:
    """Probe database connectivity by issuing ``SELECT 1``.

    Returns ``True`` on success and ``False`` on any SQLAlchemy error. Connection
    failures are logged with the stack trace and the **password-hidden** database
    URL so credentials are never emitted. Connects only when called.
    """

    engine = get_engine()
    safe_url = engine.url.render_as_string(hide_password=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Database connectivity check failed for %s", safe_url)
        return False
    logger.info("Database connectivity check succeeded for %s", safe_url)
    return True
