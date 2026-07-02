"""Local document-storage package.

Re-exports the public storage API. Importing this package runs no filesystem work;
directories are created only via ``ensure_storage_layout()``.
"""

from __future__ import annotations

from app.storage.service import (
    EXPORTS_DIR,
    EXTRACTED_DIR,
    ORIGINALS_DIR,
    STORAGE_SUBDIRS,
    ensure_storage_layout,
    get_storage_root,
    resolve_within_storage,
    safe_filename,
)

__all__ = [
    "EXPORTS_DIR",
    "EXTRACTED_DIR",
    "ORIGINALS_DIR",
    "STORAGE_SUBDIRS",
    "ensure_storage_layout",
    "get_storage_root",
    "resolve_within_storage",
    "safe_filename",
]
