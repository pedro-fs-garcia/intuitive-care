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
  - [1. Linguagem e Ferramentas](#1-linguagem-e-ferramentas)
  - [2. Estrutura do Projeto](#2-estrutura-do-projeto)
  - [3. Parte 1 - Integração com API Pública (ANS)](#3-parte-1---integração-com-api-pública-ans)
- [Comandos Disponíveis](#comandos-disponíveis)

---

## Visão Geral

Este projeto implementa as 4 partes do teste:

| Parte | Descrição                          | Status       |
| ----- | ---------------------------------- | ------------ |
| 1     | Integração com API Pública (ANS)   | ✅ Concluído |
| 2     | Transformação e Validação de Dados | 🔲 Pendente  |
| 3     | Banco de Dados e Análise (SQL)     | 🔲 Pendente  |
| 4     | API REST + Interface Web (Vue.js)  | 🔲 Pendente  |

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

### 3. Parte 1 - Integração com API Pública (ANS)

#### 3.1. Estratégia de Filtragem de Dados

**Contexto:**
A especificação do teste solicitava a identificação e processamento exclusivo do *arquivo* contendo "Despesas com Eventos/Sinistros". No entanto, ao analisar os dados baixados do FTP da ANS (estrutura atual de Demonstrações Contábeis), constatei uma divergência: os dados são entregues em um arquivo CSV monolítico ("Balancete"), contendo todas as classes contábeis (Ativo, Passivo, Receitas e Despesas) consolidadas.

**Decisão de Implementação:**
Como não era possível selecionar um arquivo específico, implementei uma **estratégia de filtragem lógica de linhas** baseada no Plano de Contas Padrão da ANS.

**Justificativa da Lógica de Filtro:**
Para garantir a integridade dos dados e capturar exatamente o que foi solicitado ("Despesas com Eventos"), utilizei um filtro composto:

1. **Filtro por Classe Contábil (`CD_CONTA_CONTABIL` iniciado em '4'):**
   - Optei por filtrar estritamente as contas iniciadas pelo dígito **4**, que representam **Despesas** no padrão contábil, de acordo com Resolução Normativa - RN nº 528 de 29/04/2022 da ANS, disponível em [link](https://www.ans.gov.br/component/legislacao/?view=legislacao&task=textoLei&format=raw&id=NDIzNg%3D%3D&ref=blog.contmatic.com.br).
   - *Por que:* Isso evita a ambiguidade com contas de "Provisão de Eventos" (iniciadas em **2**), que representam Passivo (obrigações/dívidas) e não o custo assistencial incorrido no período.

2. **Filtro Semântico (`DESCRICAO` contendo 'EVENTO' ou 'SINISTRO'):**
   - Refinei a busca para capturar apenas as despesas relacionadas à operação assistencial, excluindo despesas administrativas ou comerciais.
   - A inclusão de ambos os termos garante a captura de contas como "EVENTOS INDENIZÁVEIS" e "SINISTROS A LIQUIDAR".

**Abordagem Rejeitada:**
- **Filtragem por variação de saldo (`Saldo Inicial > Saldo Final`):** Descartei essa lógica pois contas de Despesa são de natureza acumulativa ao longo do exercício fiscal, tendendo a apresentar saldo final maior que o inicial (crescimento do custo), ao contrário de contas de Passivo que podem diminuir conforme as obrigações são quitadas.

#### 3.2. Processamento de Arquivos: Incremental vs Em Memória

| Decisão               | Escolha                      | Alternativa            | Justificativa                                                                                                    |
| --------------------- | ---------------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Estratégia de leitura | **Processamento incremental** | Carregar tudo em memória | Cada arquivo de trimestre é processado individualmente e concatenado ao resultado. Reduz pico de uso de memória. |

**Detalhes da implementação:**
- Cada arquivo CSV é lido, filtrado e agregado antes de ser concatenado ao DataFrame final
- Isso permite processar datasets maiores que a memória disponível
- Trade-off: ligeiramente mais lento que processar tudo em memória, mas mais seguro para volumes desconhecidos

#### 3.3. Tratamento de Encoding

| Decisão  | Escolha                      | Justificativa                                                                                    |
| -------- | ---------------------------- | ------------------------------------------------------------------------------------------------ |
| Encoding | **UTF-8 com fallback Latin1** | Arquivos da ANS podem vir em diferentes encodings. Tentativa automática evita falhas silenciosas. |

**Implementação:** O código tenta primeiro UTF-8 (padrão moderno) e, em caso de `UnicodeDecodeError`, faz fallback para Latin1 (ISO-8859-1), comum em sistemas legados brasileiros.

#### 3.4. Segurança: Proteção contra Zip Slip

| Decisão   | Escolha                           | Justificativa                                                                                  |
| --------- | --------------------------------- | ---------------------------------------------------------------------------------------------- |
| Extração  | **Validação de path traversal**    | Previne ataques de Zip Slip onde arquivos maliciosos tentam escapar do diretório de extração. |

**Implementação:** Antes de extrair, cada membro do ZIP é validado para garantir que o caminho final está dentro do diretório de destino (`_safe_extract`).

#### 3.5. Navegação no FTP da ANS

| Decisão           | Escolha                    | Alternativa       | Justificativa                                                                                  |
| ----------------- | -------------------------- | ----------------- | ---------------------------------------------------------------------------------------------- |
| Parsing de índice | **Regex em HTML**          | Biblioteca FTP    | O endpoint da ANS retorna HTML, não é um FTP real. Regex simples é suficiente para extrair links. |
| Ordem de download | **Mais recentes primeiro** | Ordem cronológica | `reversed(years)` e `reversed(files)` garantem que os 3 trimestres mais recentes sejam baixados. |

#### 3.6. Join com Dados Cadastrais (Operadoras)

| Decisão      | Escolha       | Alternativa   | Justificativa                                                                                    |
| ------------ | ------------- | ------------- | ------------------------------------------------------------------------------------------------ |
| Tipo de join | **LEFT JOIN** | INNER JOIN    | Mantém todas as despesas mesmo se a operadora não estiver no cadastro ativo (pode ter sido inativada). |

#### 3.7. Tratamento de Inconsistências

| Inconsistência                  | Tratamento                                      | Justificativa                                                   |
| ------------------------------- | ----------------------------------------------- | --------------------------------------------------------------- |
| Valores não numéricos           | `pd.to_numeric(errors='coerce')` → 0            | Converte para NaN e substitui por 0, evitando perda de registros |
| Datas inválidas                 | `pd.to_datetime(errors='coerce')` → descartados | Registros sem data válida não podem ser atribuídos a um trimestre |
| CNPJs sem match no cadastro     | Mantidos com campos cadastrais vazios           | LEFT JOIN preserva o dado financeiro mesmo sem enriquecimento    |

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
