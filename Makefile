.PHONY: install lint format typecheck clean \
        etl download consolidate transform api \
        frontend-install frontend-dev frontend-build

# ============================================
# SETUP
# ============================================
install:
	cd backend && poetry install

# ============================================
# BACKEND - Qualidade de código
# ============================================
lint:
	cd backend && poetry run ruff check .

format:
	cd backend && poetry run ruff format .

typecheck:
	cd backend && poetry run mypy .

# ============================================
# BACKEND - ETL (Partes 1-2)
# ============================================
download:
	cd backend && poetry run task download

consolidate:
	cd backend && poetry run task consolidate

transform:
	cd backend && poetry run task transform

etl:
	cd backend && poetry run task etl

# ============================================
# BACKEND - API (Parte 4)
# ============================================
api:
	cd backend && poetry run task api

# ============================================
# FRONTEND (Parte 4)
# ============================================
frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

# ============================================
# LIMPEZA
# ============================================
clean:
	rm -rf backend/.mypy_cache backend/.ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
