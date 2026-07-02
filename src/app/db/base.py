"""Declarative base for SQLAlchemy models.

Provides the single ``Base`` that future model modules subclass. Exposing
``Base.metadata`` here lets Alembic's ``env.py`` use it as ``target_metadata`` for
autogenerate in later phases. No table models are defined yet.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base; models register on this class in later phases."""
