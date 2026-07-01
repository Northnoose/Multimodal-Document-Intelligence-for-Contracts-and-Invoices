"""Database session seam (SQLAlchemy 2.0).

Placeholder for future phases. The engine and session factory are created lazily so
nothing connects to a database at import time, and the health endpoint stays
DB-free. No models or migrations are defined in this phase.
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Return a lazily-created SQLAlchemy engine.

    Reads ``database_url`` from the central ``Settings`` module when first called.
    Not used by any runtime code yet; wired up in a later phase alongside models
    and migrations. Because settings are only read inside this function, importing
    the module still does not construct settings or connect to a database.
    """

    database_url = get_settings().database_url
    return create_engine(database_url, future=True)


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    """Return a session factory bound to the lazily-created engine."""

    return sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)
