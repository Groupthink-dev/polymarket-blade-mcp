.PHONY: help install install-dev sync test test-cov lint format format-check type-check check clean run

help:
	@echo "Available targets:"
	@echo "  install       Install runtime dependencies"
	@echo "  install-dev   Install runtime + dev + test dependencies"
	@echo "  test          Run unit tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run ruff linter"
	@echo "  format        Auto-format code"
	@echo "  type-check    Run mypy type checker"
	@echo "  check         Run lint + format-check + type-check"
	@echo "  run           Start MCP server (stdio)"
	@echo "  clean         Remove build artifacts"

install:
	uv sync

install-dev:
	uv sync --group dev --group test

sync:
	uv sync --group dev --group test

test:
	uv run pytest tests/ -m "not e2e" -v

test-cov:
	uv run pytest tests/ -m "not e2e" --cov=src/polymarket_mcp --cov-report=term-missing -v

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

format-check:
	uv run ruff format --check src/ tests/

type-check:
	uv run mypy src/polymarket_mcp

check: lint format-check type-check

run:
	uv run polymarket-blade-mcp

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
