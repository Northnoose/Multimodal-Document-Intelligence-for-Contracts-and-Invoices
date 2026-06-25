# Multimodal Document Intelligence for Contracts and Invoices

Backend system that turns invoices and contracts (messy PDFs, scans, attachments)
into clean, validated, structured data with human review and JSON/CSV export.

See [problemstilling.md](problemstilling.md) and [description.md](description.md)
for the project problem and full description.

> **Status — backend foundation phase.** This phase ships the repository skeleton,
> a predictable local environment, baseline dependencies, the FastAPI entrypoint,
> and a `/health` endpoint. Document parsing, OCR, AI extraction, validation,
> confidence scoring, review, and export are **not** implemented yet.

## Project structure

```
.
├── pyproject.toml          # Dependencies (runtime + dev) and tooling config
├── Makefile                # Developer commands (install, verify, test, run)
├── .python-version         # Supported Python version floor (3.11)
├── .env.example            # Configuration template (copy to .env)
├── docs/architecture.md    # Structure & layer documentation
├── scripts/verify_env.py   # Environment verification
├── storage/                # Uploaded-document storage seam (contents git-ignored)
├── migrations/             # Database migrations seam (future)
├── tests/                  # Pytest suite
└── src/app/
    ├── main.py             # FastAPI entrypoint (create_app factory)
    ├── core/config.py      # Typed settings (pydantic-settings)
    ├── api/                # HTTP layer: router + routes/health.py
    ├── db/session.py       # SQLAlchemy session seam (lazy, unused this phase)
    ├── domain/             # Business entities & rules (future)
    └── worker/celery_app.py# Celery worker seam (future)
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

# 3. (Optional) Configure environment
cp .env.example .env
```

No machine-specific paths are required — all commands are relative to the repo root.

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

## Tests

```bash
make test                         # or: pytest -q
```
