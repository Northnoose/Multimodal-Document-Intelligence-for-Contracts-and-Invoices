.PHONY: help install verify test run lint db-check migrate migrate-down migration-create storage-init

help:
	@echo "Available targets:"
	@echo "  install           Install runtime + dev dependencies (editable)"
	@echo "  verify            Check the environment and run the test suite"
	@echo "  test              Run the test suite"
	@echo "  run               Start the API locally with auto-reload"
	@echo "  lint              Run ruff over src and tests"
	@echo "  db-check          Probe DATABASE_URL connectivity (needs a reachable DB)"
	@echo "  migrate           Apply all migrations (alembic upgrade head)"
	@echo "  migrate-down      Roll back one migration (alembic downgrade -1)"
	@echo "  migration-create  Create a revision: make migration-create NAME=\"...\""
	@echo "  storage-init      Create the local storage layout under STORAGE_PATH"

install:
	pip install -e ".[dev]"

verify:
	python scripts/verify_env.py
	pytest -q

test:
	pytest -q

run:
	uvicorn app.main:app --reload

lint:
	ruff check src tests

db-check:
	python scripts/check_db.py

migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

migration-create:
	alembic revision -m "$(NAME)"

storage-init:
	python -c "from app.storage.service import ensure_storage_layout; ensure_storage_layout()"
