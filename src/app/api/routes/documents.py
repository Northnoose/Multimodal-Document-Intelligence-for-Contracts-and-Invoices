"""Document upload route.

Exposes ``POST /documents/upload``: validate the file's MIME type, store the
original under the local storage layout, persist minimal metadata, enqueue the
placeholder processing task, and return the created record. No OCR, parsing,
extraction, validation, or classification happens here — ``document_type`` is always
recorded as ``unknown``.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.models import Document
from app.db.session import get_db_session
from app.domain.documents import DocumentResponse, DocumentStatus, DocumentType
from app.storage.service import (
    ensure_storage_layout,
    get_storage_root,
    resolve_within_storage,
)
from app.worker.enqueue import enqueue_document_processing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {"application/pdf", "image/png", "image/jpeg", "text/plain"}
)


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
) -> DocumentResponse:
    """Store an uploaded document and persist its metadata.

    Validates the client-supplied MIME type against ``ALLOWED_CONTENT_TYPES``, writes
    the original file under ``originals/`` (via traversal-proof storage helpers),
    inserts a ``Document`` row, and best-effort enqueues the placeholder worker task.
    """

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415, detail=f"Unsupported file type: {file.content_type}"
        )

    ensure_storage_layout()
    dest = resolve_within_storage("originals", file.filename or "file")
    try:
        content = await file.read()
        dest.write_bytes(content)
    except OSError:
        logger.exception("Failed to write uploaded file to %s", dest)
        raise HTTPException(status_code=500, detail="Failed to store uploaded file")

    rel_path = dest.relative_to(get_storage_root()).as_posix()

    document = Document(
        original_filename=file.filename or "file",
        content_type=file.content_type,
        storage_path=rel_path,
        status=DocumentStatus.UPLOADED.value,
        document_type=DocumentType.UNKNOWN.value,
    )
    try:
        session.add(document)
        session.commit()
        session.refresh(document)
    except Exception:
        session.rollback()
        dest.unlink(missing_ok=True)
        logger.exception("Failed to persist document metadata for %s", rel_path)
        raise HTTPException(status_code=500, detail="Failed to persist document")

    enqueue_document_processing(str(document.id))

    return DocumentResponse.model_validate(document)
