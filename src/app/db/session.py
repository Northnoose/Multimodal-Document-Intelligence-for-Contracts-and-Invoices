"""Database session seam (SQLAlchemy 2.0).

Placeholder for future phases. The engine and session factory are created lazily so
nothing connects to a database at import time, and the health endpoint stays
DB-free. No models or migrations are defined in this phase.
"""

from __future__ import annotations

import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


@lru_cache
def get_engine() -> Engine:
    """Return a lazily-created SQLAlchemy engine.

    Reads ``DATABASE_URL`` from the environment when first called. Not used by any
    runtime code yet; wired up in a later phase alongside models and migrations.
    """

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://localhost:5432/document_intelligence",
    )
    return create_engine(database_url, future=True)


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    """Return a session factory bound to the lazily-created engine."""

    return sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)
