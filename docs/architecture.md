# Architecture

This document describes the repository layout for the backend foundation phase. It
is intentionally minimal and extensible: folders exist as seams for later work, but
this phase only ships the application skeleton and a health endpoint.

## Top-level layout

| Path          | Purpose                                                                 |
| ------------- | ----------------------------------------------------------------------- |
| `src/app/`    | Application package (installed, `src`-based layout).                     |
| `tests/`      | Pytest suite.                                                            |
| `docs/`       | Project documentation (this file).                                      |
| `storage/`    | Local document storage: `originals/`, `extracted/`, `exports/`. Contents git-ignored. |
| `migrations/` | Alembic migration environment (`env.py`) and committed `versions/`.     |
| `alembic.ini` | Alembic config; DB URL injected from `Settings` at runtime (blank here). |
| `scripts/`    | Developer/operational scripts (`verify_env.py`, `check_db.py`).         |

## Application package (`src/app/`)

The package separates concerns so each future capability has a clear home:

- **`api/`** — HTTP layer. `router.py` aggregates feature routers; `routes/`
  holds endpoint modules (currently `health.py`).
- **`core/`** — Cross-cutting concerns. `config.py` provides typed settings via
  pydantic-settings.
- **`db/`** — Database layer. `session.py` provides a lazy SQLAlchemy 2.0
  engine/session factory, a `get_db_session()` FastAPI dependency, and a
  `check_database_connection()` probe — all of which connect only when called, never
  at import or startup. `base.py` defines the declarative `Base` used as Alembic's
  `target_metadata`. No table models exist yet.
- **`storage/`** — Local document storage. `service.py` provides a configurable root
  (`Settings.storage_path`), `ensure_storage_layout()` (auto-creates
  `originals/`/`extracted/`/`exports/`), and safe-path helpers (`safe_filename`,
  `resolve_within_storage`) that sanitise caller-supplied names and reject path
  traversal. No filesystem work happens at import.
- **`domain/`** — Business entities and rules (invoices, contracts, validation,
  confidence, review). Empty for now.
- **`worker/`** — Asynchronous processing. `celery_app.py` defines a Celery app
  against Redis; no tasks registered or worker started yet.
- **`main.py`** — FastAPI entrypoint with a `create_app()` factory.

## Entrypoint and startup

`app.main:app` is created by `create_app()`. Settings load eagerly at startup, so a
misconfigured environment fails fast with a clear `pydantic.ValidationError` instead
of failing later on the first request.

## Health endpoint

`GET /health` returns `{"status": "ok", "version": <app version>}` with HTTP 200. It
performs no database, Redis, or other external access, making it a reliable liveness
probe.

## Database migrations

Alembic is configured at the repo root (`alembic.ini`) with `script_location =
migrations`. `migrations/env.py` injects the database URL from `Settings`
(`config.set_main_option("sqlalchemy.url", get_settings().database_url)`), so the URL
is never committed and there is a single source of truth. `target_metadata =
Base.metadata` prepares `--autogenerate` for later phases. A committed
`0001_initial_empty` baseline revision exists; running migrations requires a
reachable database, but importing the app does not run them.

## Out of scope (later phases)

Document parsing, OCR, multimodal/LLM extraction, validation rules, confidence
scoring, human review, export, DB table models, auth, upload endpoints, and
deployment are not implemented here. (Database connectivity, Alembic scaffolding, and
the local storage layout now exist as described above; only the concrete models,
schema migrations, and upload/processing flows remain out of scope.)
