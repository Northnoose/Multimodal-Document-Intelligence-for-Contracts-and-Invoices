"""initial empty baseline

Revision ID: 0001_initial_empty
Revises:
Create Date: 2026-07-02

This is the committed baseline revision. It intentionally creates no tables; real
schema is added by later revisions once domain models exist.
"""
from __future__ import annotations

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0001_initial_empty"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
