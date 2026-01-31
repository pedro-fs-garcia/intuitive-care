.PHONY: install lint format typecheck clean \
        etl download consolidate transform api \
        frontend-install frontend-dev frontend-build

# SETUP
install:
	cd backend && poetry install

# Qualidade de código
lint:
	cd backend && poetry run ruff check . --fix

format:
	cd backend && poetry run ruff format .

typecheck:
	cd backend && poetry run mypy .

# ETL (Partes 1-2)
consolidate:
	cd backend && poetry run task consolidate


# LIMPEZA
clean:
	rm -rf backend/.mypy_cache backend/.ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
