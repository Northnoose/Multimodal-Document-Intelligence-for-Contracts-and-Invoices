"""Verify the local development environment.

Checks the running Python version and that every core dependency imports,
printing versions. Exits non-zero with a clear message on the first failure so
``make verify`` fails fast and readably.
"""

from __future__ import annotations

import importlib
import sys

MIN_PYTHON = (3, 11)

# (import name, human label) for each baseline dependency.
CORE_MODULES: list[tuple[str, str]] = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("pydantic", "Pydantic"),
    ("pydantic_settings", "Pydantic Settings"),
    ("sqlalchemy", "SQLAlchemy"),
    ("psycopg", "psycopg (PostgreSQL driver)"),
    ("redis", "redis"),
    ("celery", "Celery"),
]


def _fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_python() -> None:
    if sys.version_info < MIN_PYTHON:
        _fail(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required, "
            f"but {sys.version.split()[0]} is running."
        )
    print(f"OK   Python {sys.version.split()[0]}")


def check_dependencies() -> None:
    for module_name, label in CORE_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            _fail(
                f"Dependency '{label}' is not installed. "
                'Run `pip install -e ".[dev]"` inside your virtual environment.'
            )
        version = getattr(module, "__version__", "unknown")
        print(f"OK   {label} {version}")


def main() -> None:
    print("Verifying environment...")
    check_python()
    check_dependencies()
    print("Environment OK.")


if __name__ == "__main__":
    main()
