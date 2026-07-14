"""Document domain types (DB-free).

Holds the persistence-agnostic pieces of the document slice: the string enums that
describe a document's kind and processing state, and the Pydantic response schema
returned by the upload endpoint. Keeping these here (rather than in the ORM module)
lets the domain layer stay import-light and free of any SQLAlchemy dependency.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentType(str, Enum):
    """Kind of a document. ``UNKNOWN`` until classification exists (future work)."""

    INVOICE = "invoice"
    CONTRACT = "contract"
    UNKNOWN = "unknown"


class DocumentStatus(str, Enum):
    """Processing state of a document.

    Only the initial ``UPLOADED`` state exists in this phase. The set is expected to
    grow (e.g. ``processing``/``failed``); because it is stored as a ``String`` column,
    adding values needs no database migration.
    """

    UPLOADED = "uploaded"


class DocumentResponse(BaseModel):
    """Serialised view of a stored document, returned by the upload endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    original_filename: str
    content_type: str
    storage_path: str
    status: DocumentStatus
    document_type: DocumentType
    upload_timestamp: datetime
