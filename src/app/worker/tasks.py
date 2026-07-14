"""Celery tasks for document processing.

Registers the placeholder ``process_document`` task on the Celery app. This is a
Sprint-1 no-op: it only logs start/completion and echoes the document id. No OCR,
extraction, parsing, or validation happens here — that is future work.
"""

from __future__ import annotations

import logging

from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="documents.process_document")
def process_document(document_id: str) -> str:
    """Placeholder document-processing task; performs no real work.

    Logs a START and COMPLETE line for the given ``document_id`` and returns it so a
    result backend has something to store. Kept intentionally trivial as the async
    seam for the future extraction pipeline.
    """

    logger.info("process_document START document_id=%s", document_id)
    # Sprint 1 placeholder: no OCR/extraction/parsing/validation.
    logger.info("process_document COMPLETE document_id=%s", document_id)
    return document_id
