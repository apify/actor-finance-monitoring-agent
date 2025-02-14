.PHONY: clean
clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache build dist

.PHONY: install-dev
install-dev:
	uv sync --frozen --all-groups

.PHONY: lint
lint:
	uv run ruff format --check
	uv run ruff check --preview

.PHONY: type-check
type-check:
	uv run mypy

.PHONY: format
format:
	uv run ruff check --fix
	uv run ruff format

.PHONY: unit-test
unit-test:
	uv run --directory tests/ pytest

.PHONY: check
check: lint type-check unit-test
