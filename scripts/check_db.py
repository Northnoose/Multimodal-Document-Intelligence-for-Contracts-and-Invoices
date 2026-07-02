"""Local database connectivity check.

Runs a single ``SELECT 1`` against the configured ``DATABASE_URL`` and reports
the result, exiting non-zero on failure so it can gate local setup. This script
is a standalone operator tool: it is never imported by the application, and it
connects only when run.

Usage::

    python scripts/check_db.py   # or: make db-check
"""

from __future__ import annotations

import logging

from app.db.session import check_database_connection


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ok = check_database_connection()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
