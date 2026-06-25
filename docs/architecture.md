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
| `storage/`    | Local storage seam for uploaded documents. Contents are git-ignored.    |
| `migrations/` | Future database migrations. Empty seam for now.                         |
| `scripts/`    | Developer/operational scripts (e.g. `verify_env.py`).                   |

## Application package (`src/app/`)

The package separates concerns so each future capability has a clear home:

- **`api/`** — HTTP layer. `router.py` aggregates feature routers; `routes/`
  holds endpoint modules (currently `health.py`).
- **`core/`** — Cross-cutting concerns. `config.py` provides typed settings via
  pydantic-settings.
- **`db/`** — Database layer. `session.py` is a lazy SQLAlchemy 2.0 engine/session
  seam; no models or migrations yet.
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

## Out of scope (later phases)

Document parsing, OCR, multimodal/LLM extraction, validation rules, confidence
scoring, human review, export, DB models/migrations, auth, upload endpoints, and
deployment are not implemented here.
