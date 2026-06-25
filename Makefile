.PHONY: help install verify test run lint

help:
	@echo "Available targets:"
	@echo "  install   Install runtime + dev dependencies (editable)"
	@echo "  verify    Check the environment and run the test suite"
	@echo "  test      Run the test suite"
	@echo "  run       Start the API locally with auto-reload"
	@echo "  lint      Run ruff over src and tests"

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
