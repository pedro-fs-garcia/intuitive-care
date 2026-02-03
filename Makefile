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
download:
	cd backend && poetry run task consolidate

consolidate:
	cd backend && poetry run task consolidate

transform:
	cd backend && poetry run task aggregate

aggregate:
	cd backend && poetry run task aggregate

etl: download transform

api:
	cd backend && poetry run task api

# Frontend
frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

# LIMPEZA
clean:
	rm -rf backend/.mypy_cache backend/.ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
