.PHONY: install check clean parte-1 parte-2 etl api frontend parte-4

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala dependências (back e front)"
	@echo "  make etl      - Executa a consolidação e agregação de dados"
	@echo "  make parte-4  - Roda API e Frontend simultaneamente"
	@echo "  make check    - Roda Lint, Format e Typecheck"


setup:
	@echo "Instalando dependências..."
	@make install
	@echo "Executando pipeline de dados (ETL)..."
	@make etl
	@echo "Tudo pronto! Iniciando backend e frontend"

all:
	@make setup
	@make parte-4

# Qualidade de código
check:
	cd backend && poetry run ruff check . --fix
	cd backend && poetry run ruff format .
	cd backend && poetry run mypy .

# instala dependencias
frontend-install:
	cd frontend && npm install

backend-install:
	cd backend && poetry install

install: frontend-install backend-install


# ETL (Partes 1 e 2)
parte-1:
	cd backend && poetry run task consolidate

parte-2:
	cd backend && poetry run task aggregate

etl: parte-1 parte-2

# API e frontend (parte 4)
api:
	cd backend && poetry run task api

frontend:
	cd frontend && npm run dev

parte-4:
	@echo "Subindo serviços... (Use Ctrl+C para parar)"
	(make api) & (make frontend)


clean:
	-rm -rf backend/.mypy_cache backend/.ruff_cache
	-find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true