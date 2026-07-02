"""Tests for the local document-storage layout and safe-path helpers (ID 6.1).

Each test points ``STORAGE_PATH`` at a ``tmp_path`` and clears the settings cache so
the override takes effect, keeping the suite hermetic and side-effect free.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.storage.service import (
    STORAGE_SUBDIRS,
    ensure_storage_layout,
    get_storage_root,
    resolve_within_storage,
    safe_filename,
)


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_root_from_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    assert get_storage_root() == tmp_path.resolve()


def test_ensure_layout_creates_subdirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    layout = ensure_storage_layout()
    for subdir in STORAGE_SUBDIRS:
        assert (tmp_path / subdir).is_dir()
        assert layout[subdir] == (tmp_path / subdir).resolve()


def test_ensure_layout_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    ensure_storage_layout()
    ensure_storage_layout()  # must not raise
    assert (tmp_path / STORAGE_SUBDIRS[0]).is_dir()


def test_safe_filename_strips_path() -> None:
    result = safe_filename("../../etc/passwd", add_unique_prefix=False)
    assert "/" not in result
    assert ".." not in result
    assert result == "passwd"


def test_safe_filename_sanitizes_chars() -> None:
    assert safe_filename("in voice#1!.pdf", add_unique_prefix=False) == "in_voice_1_.pdf"
    assert safe_filename("...", add_unique_prefix=False) == "file"


def test_safe_filename_unique_prefix() -> None:
    a = safe_filename("report.pdf")
    b = safe_filename("report.pdf")
    assert a != b
    assert a.endswith("_report.pdf")


def test_resolve_within_storage_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    path = resolve_within_storage("originals", "report.pdf")
    assert path.is_relative_to(tmp_path.resolve())
    assert path.parent == (tmp_path / "originals").resolve()


def test_resolve_within_storage_rejects_bad_subdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    with pytest.raises(ValueError):
        resolve_within_storage("elsewhere", "report.pdf")


def test_resolve_within_storage_rejects_traversal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    # Even a traversal attempt resolves to a safe basename under the subdir.
    path = resolve_within_storage("originals", "../../../etc/passwd")
    assert path.is_relative_to((tmp_path / "originals").resolve())
