# Multimodal Document Intelligence for Contracts and Invoices

Backend system that turns invoices and contracts (messy PDFs, scans, attachments)
into clean, validated, structured data with human review and JSON/CSV export.

See [problemstilling.md](problemstilling.md) and [description.md](description.md)
for the project problem and full description.

> **Status — backend foundation phase.** This phase ships the repository skeleton,
> a predictable local environment, baseline dependencies, the FastAPI entrypoint,
> a `/health` endpoint, and the first feature slice: a `POST /documents/upload`
> endpoint that stores an uploaded file, persists minimal metadata, and enqueues a
> placeholder Celery task. Document parsing, OCR, AI extraction, validation,
> confidence scoring, review, and export are **not** implemented yet.

## Project structure

```
.
├── pyproject.toml          # Dependencies (runtime + dev) and tooling config
├── Makefile                # Developer commands (install, verify, test, run)
├── .python-version         # Supported Python version floor (3.11)
├── .env.example            # Configuration template (copy to .env)
├── alembic.ini             # Alembic config (URL injected from Settings)
├── docs/architecture.md    # Structure & layer documentation
├── scripts/verify_env.py   # Environment verification
├── scripts/check_db.py     # Local DB connectivity check (make db-check)
├── storage/                # Local document storage: originals/ extracted/ exports/
├── migrations/             # Alembic migrations (env.py + versions/)
├── tests/                  # Pytest suite
└── src/app/
    ├── main.py             # FastAPI entrypoint (create_app factory)
    ├── core/config.py      # Typed settings (pydantic-settings)
    ├── api/                # HTTP layer: router + routes/health.py, routes/documents.py
    ├── db/session.py       # SQLAlchemy session seam (lazy) + connectivity check
    ├── db/base.py          # Declarative Base for models / Alembic autogenerate
    ├── db/models.py        # ORM models (Document)
    ├── storage/service.py  # Storage layout + safe-path helpers
    ├── domain/documents.py # Document enums + response schema (DB-free)
    └── worker/             # Celery app + process_document task + enqueue helper
```

See [docs/architecture.md](docs/architecture.md) for details.

## Prerequisites

- Python **3.11+** (see [.python-version](.python-version))
- `pip`

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install runtime + development dependencies (editable)
pip install -e ".[dev]"          # or: make install

# 3. Create your local config (REQUIRED — see Configuration below)
cp .env.example .env
```

No machine-specific paths are required — all commands are relative to the repo root.

## Configuration

Configuration is centralized in [src/app/core/config.py](src/app/core/config.py)
(`Settings`, pydantic-settings) and read by the API, the Celery worker seam, and the
database seam. Values load from the environment / a local `.env` file.

`DATABASE_URL` and `REDIS_URL` are **required** — the app fails fast at startup with a
clear `pydantic.ValidationError` if they are missing. Creating a local `.env`
(`cp .env.example .env`) is therefore a required setup step. The defaults in
`.env.example` are credential-free localhost values suitable for local development;
real secrets/credentials belong only in your untracked `.env` (already git-ignored).

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `APP_TITLE` | No | `Document Intelligence API` | FastAPI title / API metadata |
| `APP_ENV` | No | `local` | Environment name (local/dev/prod) |
| `DATABASE_URL` | **Yes** | — | SQLAlchemy database URL (DB seam) |
| `REDIS_URL` | **Yes** | — | Redis broker/backend URL (Celery seam) |
| `STORAGE_PATH` | No | `storage` | Local upload-storage path (seam) |
| `WORKER_CONCURRENCY` | No | `1` | Celery worker concurrency (int, ≥ 1) |
| `WORKER_QUEUE_NAME` | No | `document_intelligence` | Default Celery queue name |

`APP_VERSION` also exists as a setting but defaults to the package version and is
normally left unset.

## Verify the environment

One command checks the Python version, confirms every core dependency imports, and
runs the test suite:

```bash
make verify
```

(Equivalent to `python scripts/verify_env.py && pytest -q`.)

## Run the API locally

```bash
make run                          # or: uvicorn app.main:app --reload
```

Then open the interactive docs at <http://127.0.0.1:8000/docs>.

## Health check

```bash
curl -i http://127.0.0.1:8000/health
```

Returns HTTP `200` with:

```json
{ "status": "ok", "version": "0.1.0" }
```

The endpoint performs no database or external access.

## Upload a document

`POST /documents/upload` accepts a single multipart file field named `file`. It
validates the content type (`application/pdf`, `image/png`, `image/jpeg`,
`text/plain`), stores the original under `storage/originals/` with a sanitised,
collision-proof filename, persists a metadata row (via the DB session), enqueues the
placeholder `process_document` worker task (best-effort), and returns `201` with the
created record:

```bash
curl -i -F "file=@invoice.pdf;type=application/pdf" \
  http://127.0.0.1:8000/documents/upload
```

```json
{
  "id": "3f1a7c9e-2b8d-4f6a-9c0e-1d2b3a4c5d6e",
  "original_filename": "invoice.pdf",
  "content_type": "application/pdf",
  "storage_path": "originals/9b1f…e2_invoice.pdf",
  "status": "uploaded",
  "document_type": "unknown",
  "upload_timestamp": "2026-07-13T10:15:30.123456+00:00"
}
```

An unsupported content type returns `415`; a missing `file` field returns `422`. No
OCR, parsing, extraction, validation, or classification happens yet —
`document_type` is always `unknown`. Persisting a document requires a reachable
database (the `documents` table must exist; see **Database migrations**).

## Process worker (Celery)

Uploads enqueue a placeholder `process_document` task on the Celery app. Start a
worker (requires a reachable Redis broker configured via `REDIS_URL`):

```bash
make worker   # celery -A app.worker.celery_app worker --loglevel=info -Q document_intelligence
```

The task performs no real work in this phase — it logs a START and COMPLETE line for
the document id. A broker outage does not fail an upload (enqueueing is best-effort).

## Database connectivity check

Probe that the configured `DATABASE_URL` is reachable (issues a single `SELECT 1`):

```bash
make db-check                     # or: python scripts/check_db.py
```

Exits `0` on success and `1` on failure. Connection errors are logged with the
password-hidden URL. This is the only step that needs a reachable PostgreSQL
instance; the app itself never connects at import or startup, and `/health` stays
DB-free.

## Database migrations

Migrations use [Alembic](https://alembic.sqlalchemy.org/). The database URL is taken
from `Settings` (`DATABASE_URL`) via `migrations/env.py`, so it is never hardcoded in
`alembic.ini`.

```bash
make migrate                                   # apply all migrations (upgrade head)
make migrate-down                              # roll back one revision
make migration-create NAME="add documents"     # create a new revision
alembic history                                # inspect revisions
alembic current                                # show the applied revision
```

Committed revisions under `migrations/versions/`: `0001_initial_empty` (baseline) and
`0002_add_documents` (creates the `documents` table).

## Local document storage

Uploaded and derived files live under `STORAGE_PATH` (default `storage/`) in three
subdirectories:

```
storage/
├── originals/    # raw uploaded documents
├── extracted/    # derived / extracted outputs
└── exports/      # generated JSON / CSV exports
```

Create the layout (idempotent) with:

```bash
make storage-init
```

Contents are git-ignored; only the per-directory `.gitkeep` placeholders are tracked.
Caller-supplied filenames are always sanitised and confined to the storage root.

## Tests

```bash
make test                         # or: pytest -q
```
