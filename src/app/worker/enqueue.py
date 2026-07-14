"""Enqueue helpers decoupling request handlers from Celery internals.

Routes call these helpers rather than touching ``.delay()`` directly, so a broker
outage cannot fail an otherwise-successful request. Enqueueing is best-effort: any
failure is logged and swallowed.
"""

from __future__ import annotations

import logging

from app.worker.tasks import process_document

logger = logging.getLogger(__name__)


def enqueue_document_processing(document_id: str) -> None:
    """Enqueue the placeholder processing task; best-effort.

    A broker outage (Redis unreachable, etc.) must not fail an upload, so any
    exception raised while publishing is logged as a warning and swallowed.
    """

    try:
        process_document.delay(document_id)
    except Exception:  # broker unreachable, serialization error, etc.
        logger.warning(
            "Could not enqueue process_document for %s", document_id, exc_info=True
        )
