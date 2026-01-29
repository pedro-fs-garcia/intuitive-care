# Teste de Entrada - Intuitive Care

Resolução do teste técnico para estágio na Intuitive Care.

**Candidato:** Pedro Garcia
**E-mail:** pedrofsgarcia.pro@gmail.com

---

## Sumário

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Requisitos](#requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Decisões Técnicas e Trade-offs](#decisões-técnicas-e-trade-offs)

---

## Visão Geral

Este projeto implementa as 4 partes do teste:

| Parte | Descrição                          | Status     |
| ----- | ---------------------------------- | ---------- |
| 1     | Integração com API Pública (ANS)   | 🔲 Pendente |
| 2     | Transformação e Validação de Dados | 🔲 Pendente |
| 3     | Banco de Dados e Análise (SQL)     | 🔲 Pendente |
| 4     | API REST + Interface Web (Vue.js)  | 🔲 Pendente |

---

## Estrutura do Projeto

```
/
├── backend/                      # Código Python
│   ├── api/                      # Parte 4: FastAPI
│   ├── etl/                      # Partes 1-2: Download, processamento
│   ├── database/                 # Parte 3: Models SQLAlchemy
│   ├── sql/                      # Parte 3: Scripts SQL puros
│   ├── pyproject.toml            # Dependências e config Python
│   └── poetry.lock
│
├── frontend/                     # Parte 4: Vue.js
│
├── data/                         # Arquivos baixados (gitignored)
├── output/                       # Arquivos gerados (gitignored)
│
├── Makefile                      # Comandos de execução
└── README.md
```

### Justificativa da Estrutura

**Separação backend/frontend**: Mantém isolamento claro entre as tecnologias (Python e Node.js), cada uma com seu próprio gerenciador de dependências e configuração. Facilita manutenção e permite que diferentes desenvolvedores trabalhem em paralelo.

**Makefile na raiz**: Centraliza todos os comandos de execução, permitindo que o avaliador rode qualquer parte do projeto sem precisar navegar entre diretórios.

**Pastas data/ e output/**: Separa arquivos de entrada (downloads da ANS) dos arquivos gerados (CSVs consolidados), mantendo o repositório limpo e organizado.

---

## Requisitos

- Python 3.12+
- Poetry 1.8+
- Node.js 20+ (para frontend)
- PostgreSQL 15+ (para Parte 3)

---

## Instalação e Execução

### Setup Inicial

```bash
# Clonar repositório
git clone https://github.com/pedro-fs-garcia/intuitive-care.git
cd intuitive-care

# Instalar dependências do backend
make install
```

### Parte 1 - Integração com API ANS

```bash
# Baixar dados das Demonstrações Contábeis (últimos 3 trimestres)
make download

# Consolidar dados em CSV único
make consolidate
```

**Saída:** `output/consolidado_despesas.zip`

### Parte 2 - Transformação e Validação

```bash
# Validar, enriquecer e agregar dados
make transform
```

**Saída:** `output/despesas_agregadas.csv`

### Parte 3 - Banco de Dados

```bash
# Scripts SQL estão em backend/sql/
# Execute na ordem:
# 1. backend/sql/01_ddl.sql       - Criação das tabelas
# 2. backend/sql/02_import.sql    - Importação dos CSVs
# 3. backend/sql/03_queries.sql   - Queries analíticas
```

### Parte 4 - API e Frontend

```bash
# Terminal 1: Iniciar API
make api

# Terminal 2: Iniciar frontend
make frontend-install  # apenas na primeira vez
make frontend-dev
```

**API:** http://localhost:8000
**Frontend:** http://localhost:5173
**Documentação API:** http://localhost:8000/docs

### Pipeline Completo (Partes 1-2)

```bash
make etl  # Executa download + consolidate + transform
```

---

## Decisões Técnicas e Trade-offs

### 1. Linguagem e Ferramentas

| Decisão             | Escolha                  | Justificativa                                                                                  |
| ------------------- | ------------------------ | ---------------------------------------------------------------------------------------------- |
| Linguagem           | **Python 3.12**          | Melhor ecossistema para ETL e análise de dados (pandas). Tipagem moderna com generics nativos. |
| Gerenciador de deps | **Poetry**               | Lock file determinístico, separação clara entre deps de produção e desenvolvimento.            |
| Qualidade de código | **Ruff + MyPy (strict)** | Ruff é 10-100x mais rápido que flake8/black combinados. MyPy strict garante type safety.       |
| Segurança           | **Bandit**               | Análise estática para vulnerabilidades comuns (SQL injection, etc.).                           |

### 2. Estrutura do Projeto

| Decisão       | Escolha                                     | Alternativa Considerada      | Justificativa                                                                                    |
| ------------- | ------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------ |
| Organização   | **Monorepo com separação backend/frontend** | Repositórios separados       | Monorepo simplifica setup para o avaliador. Separação interna mantém isolamento de concerns.     |
| Config Python | **pyproject.toml em backend/**              | Na raiz                      | Separação estrita. Evita confusão entre configs Python e do projeto geral.                       |
| Orquestração  | **Makefile na raiz**                        | Scripts bash, docker-compose | Make é universal, simples e autodocumentado. O avaliador pode ver todos os comandos disponíveis. |

---

## Comandos Disponíveis

```bash
make install          # Instalar dependências
make lint             # Verificar código (ruff)
make format           # Formatar código (ruff)
make typecheck        # Verificar tipos (mypy)

make download         # Parte 1: Baixar dados ANS
make consolidate      # Parte 1: Consolidar CSVs
make transform        # Parte 2: Validar e transformar
make etl              # Partes 1-2: Pipeline completo

make api              # Parte 4: Iniciar servidor FastAPI
make frontend-dev     # Parte 4: Iniciar dev server Vue

make clean            # Limpar caches
```

---

## Contato

Pedro Garcia - pedrofsgarcia.pro@gmail.com
