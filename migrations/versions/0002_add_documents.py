"""add documents

Revision ID: 0002_add_documents
Revises: 0001_initial_empty
Create Date: 2026-07-13

Creates the ``documents`` table holding minimal upload metadata. ``document_type``
and ``status`` are plain ``String`` columns (not native database enums) so their
value sets can grow without ``ALTER TYPE`` migrations; validity is enforced in the
application layer.
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_add_documents"
down_revision: str | None = "0001_initial_empty"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=127), nullable=False),
        sa.Column("storage_path", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("document_type", sa.String(length=32), nullable=False),
        sa.Column("upload_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_status", "documents", ["status"])


def downgrade() -> None:
    op.drop_index("ix_documents_status", "documents")
    op.drop_table("documents")
