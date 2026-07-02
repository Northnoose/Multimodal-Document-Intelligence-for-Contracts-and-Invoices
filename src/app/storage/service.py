"""Local document-storage layout and safe-path helpers.

Defines the on-disk layout for uploaded and derived files and the helpers used to
create it and to turn caller-supplied names into safe paths. The storage root is
configurable via ``Settings.storage_path``; directories are created only through
``ensure_storage_layout()`` (never implicitly at import). All caller-supplied names
are sanitised before use, and final paths are re-checked to be contained within the
storage root to prevent path traversal.
"""

from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings

ORIGINALS_DIR = "originals"
EXTRACTED_DIR = "extracted"
EXPORTS_DIR = "exports"
STORAGE_SUBDIRS: tuple[str, ...] = (ORIGINALS_DIR, EXTRACTED_DIR, EXPORTS_DIR)

_DISALLOWED_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def get_storage_root() -> Path:
    """Return the resolved storage root from ``Settings.storage_path``.

    Reads settings on call (not at import) and performs no filesystem writes.
    """

    return Path(get_settings().storage_path).resolve()


def ensure_storage_layout() -> dict[str, Path]:
    """Create the storage root and each subdirectory if missing.

    Idempotent (``mkdir(parents=True, exist_ok=True)``). This is the only function
    that creates directories. Returns a mapping of subdir name to its resolved path
    (plus ``"root"``).
    """

    root = get_storage_root()
    root.mkdir(parents=True, exist_ok=True)
    layout: dict[str, Path] = {"root": root}
    for subdir in STORAGE_SUBDIRS:
        path = root / subdir
        path.mkdir(parents=True, exist_ok=True)
        layout[subdir] = path
    return layout


def safe_filename(original_name: str, *, add_unique_prefix: bool = True) -> str:
    """Turn a caller-supplied name into a safe, single-segment filename.

    Reduces the input to its basename (dropping any directory components including
    ``..``), replaces characters outside ``[A-Za-z0-9._-]`` with ``_``, strips
    leading/trailing ``.``/``_``, and falls back to ``"file"`` if nothing remains.
    By default a ``uuid4`` hex prefix is prepended to avoid collisions and guarantee
    a safe generated identifier.
    """

    base = Path(original_name).name
    cleaned = _DISALLOWED_CHARS.sub("_", base).strip("._")
    if not cleaned:
        cleaned = "file"
    if add_unique_prefix:
        return f"{uuid4().hex}_{cleaned}"
    return cleaned


def resolve_within_storage(subdir: str, filename: str) -> Path:
    """Resolve ``filename`` inside ``subdir`` under the storage root, safely.

    ``subdir`` must be one of ``STORAGE_SUBDIRS``. The filename is sanitised via
    ``safe_filename`` and the final resolved path is verified to be contained within
    the storage root as defence-in-depth against traversal. Raises ``ValueError`` on
    an unknown subdir or if the resolved path escapes the root.
    """

    if subdir not in STORAGE_SUBDIRS:
        raise ValueError(f"Unknown storage subdir: {subdir!r}")
    root = get_storage_root()
    candidate = (root / subdir / safe_filename(filename)).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Resolved path escapes the storage root")
    return candidate
