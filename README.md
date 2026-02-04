# Teste de Entrada - Intuitive Care

Resolução do teste técnico para estágio na Intuitive Care.

**Candidato:** Pedro Garcia  
**E-mail:** pedrofsgarcia.pro@gmail.com

---

## Sumário

- [Visão Geral](#visão-geral)
- [Requisitos](#requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Decisões Técnicas e Trade-offs](#decisões-técnicas-e-trade-offs)

---

## Visão Geral

As 4 partes do teste foram implementadas conforme especificação:

| Parte | Descrição                          | Status      |
| ----- | ---------------------------------- | ----------- |
| 1     | Integração com API Pública (ANS)   | ✅ Concluído |
| 2     | Transformação e Validação de Dados | ✅ Concluído |
| 3     | Banco de Dados e Análise (SQL)     | ✅ Concluído |
| 4     | API REST + Interface Web (Vue.js)  | ✅ Concluído |

---

## Requisitos

- Python 3.12+
- Poetry 1.8+
- Node.js 20+ (para frontend)
- PostgreSQL 15+ (para Parte 3)

> **Nota:** Os scripts SQL foram desenvolvidos e testados em PostgreSQL 15, mas seguem padrão ANSI SQL compatível com PostgreSQL >10.0 e MySQL 8.0 conforme solicitado no enunciado.

### Configuração do Banco de Dados

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env` com suas configurações do PostgreSQL:

```env
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=suasenha
PG_DATABASE=intuitive_care
```

---

## Instalação e Execução

### Início Rápido

Para instalar tudo, processar os dados e subir a aplicação de uma vez:

```bash
make all
```

Use `Ctrl + C` para encerrar os serviços quando terminar.

---

<details>
<summary><b>Execução sem Make/Poetry (Windows ou pip)</b></summary>

Se você não tem `make` ou `poetry` instalado, use os comandos equivalentes:

**Instalação:**
```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

**Parte 1 (Consolidação):**
```bash
cd backend && python -m etl.run_ex_1
```

**Parte 2 (Agregação):**
```bash
cd backend && python -m etl.run_ex_2
```

**Parte 4 (API + Frontend):**
```bash
# Terminal 1 - Backend
cd backend && python -m api.api

# Terminal 2 - Frontend
cd frontend && npm run dev
```

</details>

---

### Avaliação Parte a Parte

Antes de executar qualquer parte, instale as dependências:

```bash
make install
```

#### Parte 1 — Integração com API Pública (ANS)

```bash
make parte-1
```

Baixa os arquivos de Demonstrações Contábeis da ANS, filtra despesas com eventos/sinistros e consolida em um único CSV.

**Arquivo gerado:** `output/consolidado_despesas.zip`  
**Colunas:** `CNPJ`, `RazaoSocial`, `Trimestre`, `Ano`, `ValorDespesas`

#### Parte 2 — Transformação e Validação de Dados

```bash
make parte-2
```

Valida CNPJs, enriquece os dados com informações cadastrais das operadoras e gera agregações por operadora/UF.

**Arquivo gerado:** `output/despesas_agregadas.csv`  
**Colunas:** `CNPJ`, `RegistroANS`, `RazaoSocial`, `Modalidade`, `UF`, `TotalDespesas`, `MediaTrimestral`, `DesvioPadrao`, `QtdTrimestres`

#### Parte 3 — Banco de Dados e Análise (SQL)

Não há comando `make` para esta parte. Os scripts SQL estão em `backend/sql/` para leitura e avaliação:

| Arquivo         | Conteúdo                                       |
| --------------- | ---------------------------------------------- |
| db_schema.sql   | DDL — criação das tabelas, índices e constraints |
| load_data.sql   | Importação dos CSVs para o banco               |
| queries.sql     | Queries analíticas (itens 3.4.1, 3.4.2, 3.4.3) |

<details>
<summary>Execução opcional em PostgreSQL</summary>

**Via psql (recomendado):**

```bash
psql -d <database> -f backend/sql/db_schema.sql   # Criar tabelas
psql -d <database> -f backend/sql/load_data.sql   # Importar dados
psql -d <database> -f backend/sql/queries.sql     # Executar queries
```

Os caminhos dos CSVs estão configurados como variáveis `\set` no início de `load_data.sql`. Ajuste se necessário para caminhos absolutos.

**Via pgAdmin4:**

Substitua as variáveis `:'path_*'` pelos caminhos absolutos. Exemplo:
```sql
-- De:  FROM :'path_operadoras'
-- Para: FROM '/caminho/absoluto/data/operadoras/operadoras.csv'
```

</details>

#### Parte 4 — API REST + Interface Web (Vue.js)

```bash
make parte-4
```

Sobe o servidor FastAPI e o frontend Vue.js simultaneamente.

| Serviço           | URL                        |
| ----------------- | -------------------------- |
| Frontend          | http://localhost:5173      |
| Backend           | http://localhost:8000      |
| Documentação API  | http://localhost:8000/docs |

A coleção Postman está em `postman_collection.json` na raiz do projeto.

---

### Arquivos Exigidos

| Parte | Arquivo                  | Localização                       |
| ----- | ------------------------ | --------------------------------- |
| 1     | consolidado_despesas.zip | `output/consolidado_despesas.zip` |
| 2     | despesas_agregadas.csv   | `output/despesas_agregadas.csv`   |
| 3     | Scripts SQL              | `backend/sql/`                    |
| 4     | Coleção Postman          | `postman_collection.json`         |

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

## Decisões Técnicas e Trade-offs

### 1. Linguagem e Ferramentas

| Decisão             | Escolha                  | Justificativa                                                                                  |
| ------------------- | ------------------------ | ---------------------------------------------------------------------------------------------- |
| Linguagem           | **Python 3.12**          | Melhor ecossistema para ETL e análise de dados (pandas). Tipagem moderna com generics nativos. |
| Gerenciador de deps | **Poetry**               | Lock file determinístico, separação clara entre deps de produção e desenvolvimento.            |
| Qualidade de código | **Ruff + MyPy (strict)** | Ruff é 10-100x mais rápido que flake8/black combinados. MyPy strict garante type safety.       |

### 2. Estrutura do Projeto

| Decisão       | Escolha                                     | Alternativa Considerada      | Justificativa                                                                                    |
| ------------- | ------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------ |
| Organização   | **Monorepo com separação backend/frontend** | Repositórios separados       | Monorepo simplifica setup para o avaliador. Separação interna mantém isolamento de concerns.     |
| Config Python | **pyproject.toml em backend/**              | Na raiz                      | Separação estrita. Evita confusão entre configs Python e do projeto geral.                       |
| Orquestração  | **Makefile na raiz**                        | Scripts bash, docker-compose | Make é universal, simples e autodocumentado. O avaliador pode ver todos os comandos disponíveis. |

### 3. Parte 1 - Integração com API Pública (ANS)

| Trade-off | Escolha | Justificativa |
|-----------|---------|---------------|
| Processamento | **Incremental** | Reduz pico de memória; cada trimestre é processado e concatenado |
| Filtragem | **Descrição exata + Classe 4** | Evita double-counting da hierarquia contábil |
| Valores YTD | **Preservados** | Mantém fidelidade à fonte; desacumulação feita no SQL |
| Formatos | **Detecção automática** | Suporta CSV, TXT, XLSX com encodings variados |

<details>
<summary>Ver justificativas detalhadas</summary>

#### Obtenção de CNPJ e Razão Social

Os arquivos de Demonstrações Contábeis da ANS contêm apenas `REG_ANS`, sem CNPJ ou Razão Social. Foi necessário realizar um **join prévio** com o cadastro de operadoras ativas, usando `REG_ANS` como chave.

#### Estratégia de Filtragem

O Plano de Contas da ANS segue estrutura **hierárquica** — contas de nível superior já incluem valores das subcontas. Para evitar duplicidade:

1. **Filtro por Classe Contábil**: contas iniciadas em `4` (Despesas)
2. **Filtro por Descrição Exata**: `DESCRICAO == "DESPESAS COM EVENTOS / SINISTROS"`

#### Tratamento de Dados YTD

Os dados são Year-to-Date (acumulados). Optei por preservar os valores originais no CSV consolidado e delegar a desacumulação para as queries SQL (Window Functions).

#### Suporte a Múltiplos Formatos

- Detecção por extensão (`.csv`, `.txt`, `.xlsx`)
- Fallback de encodings (`utf-8`, `latin1`, `cp1252`)
- Normalização de colunas (`REG_ANS` ↔ `REGISTRO_ANS`)

#### Tratamento de Inconsistências (Análise Crítica - Item 1.3)

| Inconsistência | Tratamento | Justificativa |
|----------------|------------|---------------|
| CNPJs duplicados (razões sociais diferentes) | **Mantido primeiro registro** | Variação de grafia não impacta cálculo financeiro; preserva integridade da chave |
| Valores zerados | **Mantidos** | Zero indica ausência de eventos no período — dado válido para análise comparativa |
| Valores negativos | **Mantidos** | Podem representar estornos ou correções contábeis legítimas |
| REG_ANS sem match no cadastro | **Removidos com log** | Provavelmente operadoras inativadas; registros sem CNPJ/RazaoSocial não atendem à especificação |
| Datas/trimestres inconsistentes | **Descartados** | Registros sem período válido não podem ser atribuídos a um trimestre |

</details>

---

### 4. Parte 2 - Transformação e Validação de Dados

| Trade-off | Escolha | Justificativa |
|-----------|---------|---------------|
| CNPJs inválidos | **Descartar** | CNPJ é chave do join; não há como corrigir sem fonte externa |
| Estratégia de join | **Pandas em memória** | Volume (~60MB) cabe em RAM; Dask seria overengineering |
| Tipo de join | **INNER JOIN** | Registros sem match não atendem requisitos do CSV |
| Ordenação | **Em memória** | <1000 linhas ordena em <100ms |
| Dados YTD | **Desacumulação via diff()** | Evita duplicidade ao calcular média/desvio |

<details>
<summary>Ver justificativas detalhadas</summary>

#### Validação de Dados

- **CNPJ:** Validação completa com dígitos verificadores (módulo 11)
- **ValorDespesas:** Conversão para numérico, filtro > 0
- **RazaoSocial:** Rejeição de nulos/vazios

#### Enriquecimento (Join)

Join com cadastro de operadoras adiciona `RegistroANS`, `Modalidade`, `UF`. Duplicatas no cadastro são tratadas mantendo o registro mais recente (`drop_duplicates` após ordenação por data).

#### Tratamento YTD

Os dados da ANS são acumulados no ano. Implementei desacumulação:

```python
df["DespesaTrimestre"] = df.groupby(["CNPJ", "Ano"])["ValorDespesas"].diff().fillna(df["ValorDespesas"])
```

#### Métricas Calculadas

| Coluna | Descrição |
|--------|-----------|
| `TotalDespesas` | Soma das despesas |
| `MediaTrimestral` | Média por trimestre |
| `DesvioPadrao` | Variabilidade (0 se N=1) |

</details>

---

### 5. Parte 3 - Banco de Dados e Análise (SQL)

| Trade-off (enunciado) | Opção Escolhida | Justificativa |
|-----------------------|-----------------|---------------|
| Normalização (3.2) | **Opção B: Tabelas normalizadas** | Integridade referencial; overhead de JOINs negligível para ~2.1k registros |
| Valores monetários (3.2) | **DECIMAL(18,2)** (vs FLOAT/INTEGER) | Precisão exata para operações financeiras; FLOAT introduz erros de arredondamento |
| Datas (3.2) | **INT** para trimestre/ano (vs DATE/VARCHAR) | Valores discretos (1-4); INT é mais eficiente para agregações |
| Query 3.4.3 | **CTEs** (vs Window Functions/JOINs) | Legibilidade e debugabilidade; performance similar para este volume |

<details>
<summary>Ver justificativas detalhadas</summary>

#### Estrutura das Tabelas

```
operadoras (1) ←──┬──→ (N) despesas_consolidadas
                  └──→ (N) despesas_agregadas
```

| Campo | Tipo | Justificativa |
|-------|------|---------------|
| Valores monetários | `DECIMAL(18,2)` | Precisão exata |
| Trimestre/Ano | `INT` | Eficiente para agregações |
| UF | `CHAR(2)` + DOMAIN | Validação no nível do banco |

#### Importação de Dados

Uso de tabelas de staging (temporárias) com tratamento de:
- NULL/strings vazias → rejeitados
- Formato brasileiro (1.234,56) → convertido
- CNPJ formatado → limpeza via regex

Cada importação reporta via `RAISE NOTICE` quantos registros foram inseridos vs. rejeitados.

#### Queries Analíticas

**Query 1 (Crescimento):** Exclui operadoras sem dados em ambos os extremos (primeiro E último trimestre). INNER JOIN garante comparação justa.

**Query 2 (UF):** Agrupa por UF, calcula total e média por operadora. `NULLIF` previne divisão por zero.

**Query 3 (Acima da média):** CTEs para calcular média geral e contar trimestres acima. Versão detalhada também disponível.

</details>

---

### 6. Parte 4 - API REST e Interface Web

#### Backend (Trade-offs 4.2.1 a 4.2.4)

| Trade-off (enunciado) | Opção Escolhida | Justificativa |
|-----------------------|-----------------|---------------|
| 4.2.1 Framework | **Opção B: FastAPI** | Validação automática com Pydantic, docs em `/docs`, tipagem nativa, async |
| 4.2.2 Paginação | **Opção A: Offset-based** | Simples; volume (~1.5k operadoras) não justifica cursor/keyset |
| 4.2.3 Cache | **Opção A: Calcular sempre** | Dados trimestrais (atualização rara); Redis/pré-cálculo seria overengineering |
| 4.2.4 Resposta | **Opção B: Dados + metadados** | Frontend renderiza paginação completa com uma única request |

#### Frontend (Trade-offs 4.3.1 a 4.3.4)

| Trade-off (enunciado) | Opção Escolhida | Justificativa |
|-----------------------|-----------------|---------------|
| 4.3.1 Busca/Filtro | **Opção A: Servidor** (+ debounce 300ms) | Escala para qualquer volume; evita requests excessivos |
| 4.3.2 Estado | **Opção C: Composables** | App pequena; Pinia seria overhead desnecessário |
| 4.3.3 Performance Tabela | **Paginação server-side** | 10 itens/página renderiza instantaneamente |
| 4.3.4 Erros/Loading | **Mensagens específicas** | Ajuda diagnóstico; "Erro desconhecido" não agrega valor |

<details>
<summary>Ver justificativas detalhadas</summary>

#### Stack Backend
- **FastAPI:** Swagger UI em `/docs`, validação com Pydantic, async nativo
- **SQLAlchemy:** Connection pooling (`pool_size=5`, `max_overflow=10`)

#### Stack Frontend
- **Vue 3 + TypeScript:** Composition API, tipagem estrita
- **Vite:** Build rápido, HMR instantâneo
- **Tailwind CSS:** Estilização utilitária
- **Chart.js:** Gráfico de distribuição por UF

#### Estrutura de Resposta
```json
{
  "data": [...],
  "total": 1523,
  "page": 1,
  "limit": 10,
  "total_pages": 153
}
```

#### Lazy Loading
Componentes abaixo da dobra (`OperadorasTable`, `OperadoraModal`) são carregados sob demanda via `defineAsyncComponent`.

#### Integração
- CORS configurado para `localhost:5173`
- API inicializa banco automaticamente no startup (cria tabelas e importa CSVs)
- Avaliador executa `make parte-4` e sistema funciona sem setup manual

</details>

---

## Contato

Pedro Garcia - pedrofsgarcia.pro@gmail.com
