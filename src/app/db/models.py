"""SQLAlchemy ORM models.

Defines the persistence-layer tables registered on the declarative ``Base``. The
first model is ``Document``, which records minimal metadata about an uploaded file.
Enum *values* are stored as plain ``String`` columns (not native database enums) so
the value sets can grow without ``ALTER TYPE`` migrations; validity is enforced in
the application via the ``domain`` enums and the Pydantic schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.documents import DocumentStatus, DocumentType


class Document(Base):
    """Metadata for an uploaded document (the file itself lives under storage)."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(127), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=DocumentStatus.UPLOADED.value, index=True
    )
    document_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default=DocumentType.UNKNOWN.value
    )
    upload_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
