"""Tests for the Alembic migration scaffolding (ID 4.2).

These checks are DB-free: they inspect the Alembic config and revision files
statically rather than running migrations against a real database.
"""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ALEMBIC_INI = _REPO_ROOT / "alembic.ini"


def _config() -> Config:
    return Config(str(_ALEMBIC_INI))


def test_alembic_config_loads() -> None:
    config = _config()
    assert config.get_main_option("script_location") == "migrations"


def test_env_uses_settings_url() -> None:
    # Static check: env.py must derive the URL from Settings, not hardcode it.
    env_source = (_REPO_ROOT / "migrations" / "env.py").read_text(encoding="utf-8")
    assert "get_settings" in env_source
    assert "set_main_option" in env_source


def test_initial_revision_present() -> None:
    script = ScriptDirectory.from_config(_config())
    assert list(script.get_bases()) == ["0001_initial_empty"]
    revision = script.get_revision("0001_initial_empty")
    assert revision.down_revision is None
