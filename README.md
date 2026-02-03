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
  - [4. Parte 2 - Transformação e Validação de Dados](#4-parte-2---transformação-e-validação-de-dados)
  - [5. Parte 3 - Banco de Dados e Análise (SQL)](#5-parte-3---banco-de-dados-e-análise-sql)
  - [6. Parte 4 - API REST e Interface Web](#6-parte-4---api-rest-e-interface-web)
- [Comandos Disponíveis](#comandos-disponíveis)

---

## Visão Geral

Este projeto implementa as 4 partes do teste:

| Parte | Descrição                          | Status      |
| ----- | ---------------------------------- | ----------- |
| 1     | Integração com API Pública (ANS)   | ✅ Concluído |
| 2     | Transformação e Validação de Dados | ✅ Concluído |
| 3     | Banco de Dados e Análise (SQL)     | ✅ Concluído |
| 4     | API REST + Interface Web (Vue.js)  | ✅ Concluído |

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
# Execute na ordem com psql:

# 1. Criar estrutura das tabelas
psql -d <database> -f backend/sql/db_schema.sql

# 2. Importar dados dos CSVs (ajuste os paths no início do arquivo)
psql -d <database> -f backend/sql/load_data.sql

# 3. Executar queries analíticas
psql -d <database> -f backend/sql/queries.sql
```

**Nota:** Antes de executar `load_data.sql`, edite as variáveis no início do arquivo para apontar para os caminhos corretos dos CSVs:

```sql
\set path_operadoras '/caminho/para/operadoras.csv'
\set path_consolidado '/caminho/para/consolidado_despesas.csv'
\set path_agregado '/caminho/para/despesas_agregadas.csv'
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

**Coleção Postman:** Disponível em `postman_collection.json` na raiz do projeto. Importe no Postman para testar todas as rotas da API.

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

#### 3.0. Obtenção de CNPJ e Razão Social

**Contexto:**
A especificação da Parte 1.3 exige que o CSV consolidado contenha as colunas `CNPJ`, `RazaoSocial`, `Trimestre`, `Ano` e `Valor Despesas`. No entanto, os arquivos de Demonstrações Contábeis da ANS contêm apenas o código `REG_ANS` (Registro ANS), sem CNPJ ou Razão Social.

**Decisão de Implementação:**
Como os campos obrigatórios não estão presentes nos arquivos de origem, foi necessário realizar um **join prévio** com o cadastro de operadoras ativas (`Relatorio_cadop.csv`), utilizando `REG_ANS` como chave de ligação.

**Justificativa:**
- A Parte 2.2 especifica que o join deve ser feito "usando o CNPJ como chave", o que pressupõe que o CSV consolidado da Parte 1 já possua essa coluna.
- Antecipar a obtenção do CNPJ/RazaoSocial na Parte 1 garante conformidade com a especificação e permite que a Parte 2.2 adicione apenas as colunas complementares (`RegistroANS`, `Modalidade`, `UF`).

#### 3.1. Estratégia de Filtragem de Dados

**Contexto:**
A especificação do teste solicitava a identificação e processamento exclusivo do *arquivo* contendo "Despesas com Eventos/Sinistros". No entanto, ao analisar os dados baixados do FTP da ANS (estrutura atual de Demonstrações Contábeis), constatei uma divergência: os dados são entregues em um arquivo CSV monolítico ("Balancete"), contendo todas as classes contábeis (Ativo, Passivo, Receitas e Despesas) consolidadas.

**Problema Identificado:**
Além da ausência de separação por arquivo, o Plano de Contas da ANS segue uma estrutura **hierárquica**. Contas de nível superior (ex: conta `4`) já incluem os valores das subcontas. Somar todas as linhas que contêm "EVENTO" ou "SINISTRO" resultaria em **duplicidade** (*double-counting*), inflando artificialmente os totais.

**Decisão de Implementação:**
Como não era possível selecionar um arquivo específico, implementei uma **estratégia de filtragem lógica de linhas** baseada no Plano de Contas Padrão da ANS, com filtro de dupla entrada:

1. **Filtro por Classe Contábil (`CD_CONTA_CONTABIL` iniciado em '4'):**
   - Optei por filtrar estritamente as contas iniciadas pelo dígito **4**, que representam **Despesas** no padrão contábil, de acordo com Resolução Normativa - RN nº 528 de 29/04/2022 da ANS, disponível em [link](https://www.ans.gov.br/component/legislacao/?view=legislacao&task=textoLei&format=raw&id=NDIzNg%3D%3D&ref=blog.contmatic.com.br).
   - *Por que:* Isso evita a ambiguidade com contas de "Provisão de Eventos" (iniciadas em **2**), que representam Passivo (obrigações/dívidas) e não o custo assistencial incorrido no período.

2. **Filtro por Descrição Exata (`DESCRICAO == "DESPESAS COM EVENTOS / SINISTROS"`):**
   - Implementei filtro por **igualdade exata** da descrição após normalização (remoção de espaços e conversão para maiúsculas).
   - Essa abordagem garante a captura apenas dos valores "folha" da hierarquia contábil, refletindo o gasto real sem inflar os totais.
   - Optei por igualdade exata em vez de busca parcial (`LIKE '%EVENTO%'`) para evitar a captura acidental de contas agregadoras ou títulos de grupos que possuam nomes similares.

**Abordagens Rejeitadas:**
- **Filtragem por variação de saldo (`Saldo Inicial > Saldo Final`):** Descartei essa lógica pois contas de Despesa são de natureza acumulativa ao longo do exercício fiscal, tendendo a apresentar saldo final maior que o inicial (crescimento do custo).
- **Filtragem por número de dígitos (>= 9):** Embora funcione, depende da estrutura do plano de contas permanecer estável. O filtro por descrição exata é mais explícito quanto à intenção.

#### 3.1.1. Seleção de Campo Financeiro

**Decisão:** Utilizei o campo `VL_SALDO_FINAL` como base para a coluna `ValorDespesas`.

**Fundamentação:** Nas Demonstrações Contábeis da ANS, as contas de despesas (Grupo 4) registram o saldo acumulado no período. O `VL_SALDO_FINAL` representa o total de eventos e sinistros reconhecidos pela operadora até a data do fechamento do trimestre, sendo o indicador fiel do impacto financeiro no período analisado. O uso do saldo final isolado evita erros de interpretação sobre a competência dos lançamentos contábeis.

#### 3.1.2. Consolidação e Tratamento de Dados Acumulados (YTD)
**Decisão:** Preservação dos Valores Originais (Snapshot). Optei por manter no CSV consolidado o valor bruto do VL_SALDO_FINAL para cada trimestre, sem realizar a desacumulação (subtração do trimestre anterior) nesta etapa.
**Contexto:** O Plano de Contas Padrão da ANS e as normas do DIOPS, as contas de despesa (Grupo 4) registram valores de forma acumulada ao longo do ano civil (Year-to-Date - YTD).
**Justificativa:** 
1. Integridade e Rastreabilidade: Manter o valor original garante que o dado consolidado seja fiel à "Fonte da Verdade" (Portal Brasileiro de Dados Abertos da ANS), facilitando auditorias e conferências manuais. 
2. Robustez do Pipeline: A extração torna-se mais resiliente a falhas pontuais de download. Se um trimestre intermediário estiver ausente ou corrompido, os valores dos trimestres subsequentes permanecem corretos em relação ao acumulado do ano. 
3. Separação de Preocupações (Separation of Concerns): A lógica de "desacumulação" para cálculo de médias e crescimento percentual foi delegada para as queries analíticas de SQL (Teste 3), onde o uso de funções de janela (Window Functions) permite manipular os saldos de forma mais eficiente e performática.

#### 3.2. Suporte a Múltiplos Formatos de Arquivo

**Contexto:**
A especificação menciona que "os arquivos podem ter formatos diferentes (CSV, TXT, XLSX) e estruturas de colunas variadas", exigindo identificação automática.

**Decisão de Implementação:**
Implementei um sistema de leitura com detecção automática em duas camadas:

1. **Detecção de formato por extensão:** O código identifica `.csv`, `.txt`, `.xlsx` e `.xls` e aplica o parser apropriado.

2. **Detecção de encoding e separador (para CSV/TXT):** Tenta combinações de encodings (`utf-8`, `latin1`, `cp1252`) e separadores (`;`, `,`, `\t`, `|`) até encontrar uma que produza múltiplas colunas.

3. **Normalização de colunas:** Um mapeamento de variantes (`REG_ANS` ↔ `REGISTRO_ANS` ↔ `CD_OPERADORA`, etc.) permite que arquivos com nomenclaturas diferentes sejam processados uniformemente.

**Justificativa:**
- A detecção em cascata é mais robusta que assumir um formato fixo
- O fallback de encodings evita falhas silenciosas em arquivos legados
- A normalização de colunas permite absorver variações sem alterar a lógica de negócio

**Trade-off:**
Optei por detectar formato pela extensão ao invés de analisar o conteúdo (magic bytes), pois:
- É mais simples e performático
- Arquivos da ANS seguem convenções de nomenclatura
- Magic bytes exigiria dependência adicional (python-magic)

#### 3.3. Processamento de Arquivos: Incremental vs Em Memória

| Decisão               | Escolha                       | Alternativa              | Justificativa                                                                                                    |
| --------------------- | ----------------------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| Estratégia de leitura | **Processamento incremental** | Carregar tudo em memória | Cada arquivo de trimestre é processado individualmente e concatenado ao resultado. Reduz pico de uso de memória. |

**Detalhes da implementação:**
- Cada arquivo é lido, filtrado e agregado antes de ser concatenado ao DataFrame final
- Isso permite processar datasets maiores que a memória disponível
- Trade-off: ligeiramente mais lento que processar tudo em memória, mas mais seguro para volumes desconhecidos

#### 3.4. Segurança: Proteção contra Zip Slip

| Decisão  | Escolha                         | Justificativa                                                                                 |
| -------- | ------------------------------- | --------------------------------------------------------------------------------------------- |
| Extração | **Validação de path traversal** | Previne ataques de Zip Slip onde arquivos maliciosos tentam escapar do diretório de extração. |

**Implementação:** Antes de extrair, cada membro do ZIP é validado para garantir que o caminho final está dentro do diretório de destino (`_safe_extract`).

#### 3.5. Navegação no FTP da ANS

| Decisão           | Escolha                    | Alternativa       | Justificativa                                                                                     |
| ----------------- | -------------------------- | ----------------- | ------------------------------------------------------------------------------------------------- |
| Parsing de índice | **Regex em HTML**          | Biblioteca FTP    | O endpoint da ANS retorna HTML, não é um FTP real. Regex simples é suficiente para extrair links. |
| Ordem de download | **Mais recentes primeiro** | Ordem cronológica | `reversed(years)` e `reversed(files)` garantem que os 3 trimestres mais recentes sejam baixados.  |

#### 3.6. Join com Dados Cadastrais (Operadoras)

| Decisão      | Escolha                | Alternativa       | Justificativa                                                                    |
| ------------ | ---------------------- | ----------------- | -------------------------------------------------------------------------------- |
| Tipo de join | **LEFT JOIN + filtro** | INNER JOIN direto | LEFT JOIN permite identificar e logar registros sem match antes de descartá-los. |

#### 3.7. Tratamento de Inconsistências

| Inconsistência                               | Tratamento                                      | Justificativa                                                                     |
| -------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------- |
| CNPJs duplicados (razões sociais diferentes) | **Mantido primeiro registro**                   | Cadastro pode conter histórico; primeiro registro representa dados mais atuais    |
| Valores zerados                              | **Mantidos**                                    | Zero indica ausência de eventos no período — dado válido para análise comparativa |
| Valores negativos                            | **Mantidos**                                    | Podem representar estornos ou correções contábeis legítimas                       |
| Valores não numéricos                        | `pd.to_numeric(errors='coerce')` → 0            | Converte para NaN e substitui por 0, evitando perda de registros                  |
| Datas inválidas                              | `pd.to_datetime(errors='coerce')` → descartados | Registros sem data válida não podem ser atribuídos a um trimestre                 |
| REG_ANS sem match no cadastro                | **Removidos com log**                           | Registros sem CNPJ/RazaoSocial não atendem à especificação do CSV                 |

**Decisão sobre CNPJs duplicados:**

Optei por remover duplicatas do cadastro de operadoras **antes** do join, mantendo o primeiro registro de cada `REG_ANS`.

*Abordagem rejeitada:* Permitir que o join gere múltiplas linhas e depois consolidar com `groupby`. Essa abordagem foi descartada porque **inflaria artificialmente os valores de despesas**. Exemplo: se um `REG_ANS` tem 2 registros no cadastro, o join multiplicaria a linha de despesa, e um `groupby sum` somaria o mesmo valor duas vezes.

**Decisão sobre registros sem cadastro:**

Optei por **remover** registros de despesas cujo `REG_ANS` não existe no cadastro de operadoras ativas, pelos seguintes motivos:

1. A especificação exige que o CSV contenha `CNPJ` e `RazaoSocial` — linhas vazias nesses campos são tecnicamente inválidas
2. Provavelmente são operadoras inativadas/canceladas, cujos dados históricos não agregam valor à análise
3. Manter dados sem identificação dificulta auditorias e análises downstream

O código loga quantos registros foram removidos para rastreabilidade.

---

### 4. Parte 2 - Transformação e Validação de Dados

#### 4.1. Validação de Dados (Item 2.1)

**Validações implementadas:**

1. **CNPJ:** Validação completa com verificação dos dígitos verificadores (módulo 11)
2. **ValorDespesas:** Conversão para numérico e filtro de valores > 0
3. **RazaoSocial:** Rejeição de valores nulos ou strings vazias/apenas espaços

**Trade-off: Tratamento de CNPJs inválidos**

| Estratégia           | Prós                              | Contras                                                     |
| -------------------- | --------------------------------- | ----------------------------------------------------------- |
| Descartar registro   | Garante integridade dos dados     | Perde informação                                            |
| Marcar como suspeito | Preserva dado para análise manual | Polui agregações                                            |
| Tentar corrigir      | Recupera dados                    | Alto risco de erro; CNPJ não é corrigível sem fonte externa |

**Escolha:** Descartar registros com CNPJ inválido.

**Justificativa:** CNPJ é a chave de join com os dados cadastrais (item 2.2). Manter registros com CNPJ inválido causaria:
- Falha no enriquecimento (sem match possível)
- Distorção nas agregações por operadora

Como não há forma confiável de corrigir um CNPJ inválido sem acesso a fonte externa, descartar é a abordagem mais segura para garantir qualidade nas etapas seguintes.

#### 4.2. Enriquecimento de Dados (Item 2.2)

**Objetivo:** Realizar join entre o CSV consolidado e os dados cadastrais das operadoras, adicionando as colunas `RegistroANS`, `Modalidade` e `UF`.

**Trade-off: Estratégia de Processamento do Join**

| Estratégia              | Prós                                          | Contras                                                |
| ----------------------- | --------------------------------------------- | ------------------------------------------------------ |
| Pandas em memória       | Simples, rápido para datasets pequenos/médios | Limitado pela RAM                                      |
| Processamento em chunks | Escala para dados maiores                     | Mais complexo; join parcial pode gerar inconsistências |
| Dask/Polars             | Paralelização, escala bem                     | Overhead de setup, dependência extra                   |

**Escolha:** Pandas em memória (`pd.merge`).

**Justificativa:** O volume de dados da ANS (~1.5k operadoras ativas × 3 trimestres) cabe confortavelmente em memória. O arquivo consolidado tem ~50MB. Usar chunks ou Dask seria overengineering para este volume e adicionaria complexidade desnecessária.

**Trade-off: Tipo de Join**

| Estratégia         | Prós                                                          | Contras                   |
| ------------------ | ------------------------------------------------------------- | ------------------------- |
| INNER JOIN         | Garante que todos os registros tenham dados completos         | Perde registros sem match |
| LEFT JOIN + filtro | Permite logar/analisar registros sem match antes de descartar | Mais verboso              |

**Escolha:** INNER JOIN.

**Justificativa:** A especificação exige que o CSV final contenha `RegistroANS`, `Modalidade` e `UF`. Registros sem match no cadastro não podem atender a esse requisito. O INNER JOIN descarta esses registros diretamente, simplificando o código.

**Tratamento de Registros Duplicados no Cadastro**

O cadastro de operadoras pode conter duplicatas por duas razões:
- Mesmo `REG_ANS` com dados diferentes (alterações cadastrais)
- Mesmo `CNPJ` para `REG_ANS` diferentes (operadoras que mudaram de registro)

| Inconsistência    | Tratamento               | Justificativa                               |
| ----------------- | ------------------------ | ------------------------------------------- |
| REG_ANS duplicado | Mantém primeiro registro | Primeiro = mais recente (ordenado por data) |
| CNPJ duplicado    | Mantém primeiro registro | Evita multiplicação de linhas no join       |

**Implementação:**
1. Ordena cadastro por `Data_Registro_ANS` decrescente antes de salvar
2. Aplica `drop_duplicates(subset=["REG_ANS"], keep="first")`
3. Aplica `drop_duplicates(subset=["CNPJ"], keep="first")`

Essa ordem garante que, em caso de conflito, o registro mais recente seja preservado.

#### 4.3. Agregação de Dados (Item 2.3)

**Objetivo:** Agrupar dados por `RazaoSocial` e `UF`, calculando métricas estatísticas.

**Métricas calculadas:**

| Coluna            | Descrição                                             |
| ----------------- | ----------------------------------------------------- |
| `TotalDespesas`   | Soma de todas as despesas da operadora/UF             |
| `MediaTrimestral` | Média de despesas por trimestre                       |
| `DesvioPadrao`    | Desvio padrão das despesas (identifica variabilidade) |

**Trade-off: Estratégia de Ordenação**

| Estratégia                 | Prós                                       | Contras                             |
| -------------------------- | ------------------------------------------ | ----------------------------------- |
| `sort_values()` em memória | Simples, O(n log n), eficiente para N < 1M | Limitado pela RAM                   |
| Ordenação externa (chunks) | Escala para bilhões de registros           | Complexidade alta, I/O intensivo    |
| Heap/Top-K                 | Eficiente se só precisar dos maiores       | Não retorna lista completa ordenada |

**Escolha:** Ordenação em memória via `pandas.sort_values()`.

**Justificativa:** O dataset agregado terá no máximo ~1.5k operadoras × 27 UFs = ~40k linhas. Ordenar 40k registros em memória leva <100ms. Ordenação externa só faria sentido acima de milhões de registros.

**Análise Crítica: Tratamento de Dados Cumulativos (YTD)**

**Problema identificado:** Os dados da ANS são Year-to-Date (acumulados no ano). A soma direta dos trimestres causaria duplicidade de valores — por exemplo, o valor do T3 já inclui T1 e T2.

**Solução:** Implementei uma lógica de desacumulação. Para trimestres do mesmo ano fiscal, o valor real do período é calculado como a diferença entre o saldo atual e o anterior. Quando há mudança de ano, o saldo é tratado como inicial.

```python
df = df.sort_values(["CNPJ", "Ano", "Trimestre"])
df["DespesaTrimestre"] = (
    df.groupby(["CNPJ", "Ano"])["ValorDespesas"]
    .diff()
    .fillna(df["ValorDespesas"])
)
```

**Justificativa:** Essa abordagem é a única que reflete a realidade financeira da operadora e permite o cálculo correto da Média e do Desvio Padrão solicitados no item 2.3. Sem isso, as operadoras maiores pareceriam ter um crescimento exponencial inexistente ao longo do ano.

**Tratamento de Desvio Padrão com N=1:**

Quando uma operadora/UF possui dados de apenas 1 trimestre, o desvio padrão é indefinido (NaN). Optei por preencher com 0, indicando ausência de variação observável.

**Justificativa Técnica: Estrutura do CSV `despesas_agregadas.csv`**

**Decisão:** Mantive as colunas `CNPJ`, `RegistroANS` e `Modalidade` no arquivo final de agregação.

**Justificativa:** Embora o item 2.3 foque em `RazaoSocial` e `UF`, a manutenção dessas chaves e atributos evita o reprocessamento de joins nas etapas de Banco de Dados e API, garantindo a integridade referencial entre as tabelas.

**Praticidade:** Segui o princípio de preparar os dados para o consumo final (Dashboard), onde filtros por `Modalidade` e buscas por `CNPJ` são requisitos funcionais esperados.

---

### 5. Parte 3 - Banco de Dados e Análise (SQL)

Os scripts SQL estão organizados em `backend/sql/`:

| Arquivo         | Descrição                                             |
| --------------- | ----------------------------------------------------- |
| `db_schema.sql` | DDL - Criação das tabelas e índices                   |
| `load_data.sql` | Importação dos CSVs com tratamento de inconsistências |
| `queries.sql`   | Queries analíticas (itens 3.4.1, 3.4.2, 3.4.3)        |

#### 5.1. Estrutura das Tabelas (Item 3.2)

##### Trade-off: Normalização

| Estratégia                  | Prós                                     | Contras                                        |
| --------------------------- | ---------------------------------------- | ---------------------------------------------- |
| **Opção A: Desnormalizada** | Queries simples, menos JOINs             | Redundância de dados, anomalias de atualização |
| **Opção B: Normalizada**    | Sem redundância, integridade referencial | Queries mais complexas com JOINs               |

**Escolha:** Tabelas normalizadas (Opção B).

**Justificativa:**
1. **Integridade referencial:** A tabela `operadoras` é a fonte única de verdade para dados cadastrais. Alterações (ex: razão social) são refletidas automaticamente em todas as queries.
2. **Volume de dados:** Com ~1.500 operadoras e ~4.500 registros de despesas (3 trimestres), o overhead de JOINs é negligível.
3. **Frequência de atualizações:** Dados cadastrais podem mudar (operadora muda de nome, UF). Normalização evita inconsistências.
4. **Queries analíticas:** As queries do item 3.4 naturalmente requerem agregações que se beneficiam da estrutura normalizada.

**Estrutura implementada:**

```
operadoras (1) ←──┬──→ (N) despesas_consolidadas
                  └──→ (N) despesas_agregadas
```

##### Trade-off: Tipos de Dados

| Campo              | Escolha             | Alternativas                  | Justificativa                                                                                                                                         |
| ------------------ | ------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Valores monetários | `DECIMAL(18,2)`     | `FLOAT`, `INTEGER` (centavos) | DECIMAL garante precisão exata para operações financeiras. FLOAT introduz erros de arredondamento. INTEGER (centavos) exigiria conversões constantes. |
| Trimestre/Ano      | `INT`               | `DATE`, `VARCHAR`             | INT é mais eficiente para agregações e comparações. Trimestre é um valor discreto (1-4), não uma data completa.                                       |
| UF                 | `CHAR(2)` com CHECK | `VARCHAR`, `ENUM`             | CHAR(2) é fixo e eficiente. CHECK constraint com lista explícita de UFs válidas garante integridade sem overhead de tabela auxiliar.                  |
| CNPJ               | `VARCHAR(14)`       | `BIGINT`, `CHAR(14)`          | VARCHAR acomoda CNPJs com/sem formatação. Armazenamos apenas dígitos (sem pontuação) para facilitar comparações.                                      |

**Decisão sobre DOMAIN:**

Criei um `DOMAIN uf_brasil` com constraint CHECK para validar UFs no nível do banco. Isso garante que dados inválidos sejam rejeitados na importação, não apenas filtrados.

```sql
CREATE DOMAIN uf_brasil AS CHAR(2)
CHECK (VALUE IN ('AC','AL','AP',...,'TO'));
```

##### Índices

| Tabela                  | Índice                           | Justificativa                                       |
| ----------------------- | -------------------------------- | --------------------------------------------------- |
| `operadoras`            | `(razao_social)`                 | Busca textual por nome da operadora (item 4.3)      |
| `despesas_consolidadas` | `(operadora_id, ano, trimestre)` | Queries analíticas filtram/agrupam por esses campos |

**Nota:** Índice em `cnpj` já existe implicitamente via `UNIQUE` constraint.

#### 5.2. Importação de Dados (Item 3.3)

**Estratégia:** Uso de tabelas de staging (temporárias) para carregar dados brutos antes de transformar e inserir nas tabelas finais.

**Justificativa:**
1. Permite validar e transformar dados em SQL antes da inserção
2. Dados rejeitados não poluem as tabelas finais
3. Facilita debug e auditoria (pode-se inspecionar staging antes de inserir)

##### Tratamento de Inconsistências

| Inconsistência                  | Tratamento                                                                 | Justificativa                                                             |
| ------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **NULL em campos obrigatórios** | Registro rejeitado (`WHERE cnpj IS NOT NULL AND razao_social IS NOT NULL`) | Dados incompletos não atendem requisitos mínimos de integridade           |
| **Strings vazias**              | Rejeitadas (`TRIM(cnpj) <> ''`)                                            | String vazia é funcionalmente equivalente a NULL para campos obrigatórios |
| **Strings em campos numéricos** | Conversão com fallback (`CAST(REPLACE(...) AS DECIMAL)`)                   | Formato brasileiro (1.234,56) é convertido para padrão SQL (1234.56)      |
| **CNPJ com formatação**         | Limpeza via regex (`REGEXP_REPLACE(cnpj, '[^0-9]', '', 'g')`)              | Remove pontos, barras e hífens, mantendo apenas dígitos                   |
| **UF inválida**                 | Registro rejeitado (CHECK constraint)                                      | Apenas UFs brasileiras válidas são aceitas                                |
| **Trimestre fora de range**     | Validação regex (`trimestre ~ '^[1-4]$'`)                                  | Trimestre deve ser 1, 2, 3 ou 4                                           |
| **Ano inválido**                | Validação regex (`ano ~ '^20[0-9]{2}$'`)                                   | Aceita apenas anos no formato 20XX                                        |
| **Valores negativos/zero**      | Rejeitados para despesas (`valor > 0`)                                     | Despesas devem ser positivas; zeros indicam ausência de dado relevante    |

**Decisão sobre registros sem match:**

Na importação de `despesas_consolidadas` e `despesas_agregadas`, uso `INNER JOIN` com a tabela `operadoras`. Registros cujo CNPJ não existe em `operadoras` são automaticamente descartados.

**Justificativa:** A integridade referencial é garantida pela FK. Tentar inserir registros órfãos causaria erro. O INNER JOIN filtra preventivamente.

**Feedback ao usuário:**

Cada bloco de importação inclui um `RAISE NOTICE` reportando quantos registros foram lidos vs. inseridos, permitindo identificar taxa de rejeição.

#### 5.3. Queries Analíticas (Item 3.4)

##### Query 1: Top 5 Operadoras com Maior Crescimento Percentual

**Requisito:** Identificar operadoras com maior crescimento de despesas entre o primeiro e último trimestre.

**Desafio:** Operadoras podem não ter dados em todos os trimestres.

| Estratégia                             | Prós                            | Contras                                         |
| -------------------------------------- | ------------------------------- | ----------------------------------------------- |
| Excluir operadoras incompletas         | Comparação justa entre extremos | Perde operadoras que entraram/saíram do mercado |
| Usar trimestre mais próximo disponível | Inclui mais operadoras          | Distorce comparação (períodos diferentes)       |
| Interpolar valores faltantes           | Mantém todas as operadoras      | Introduz dados artificiais                      |

**Escolha:** Excluir operadoras que não possuem dados em ambos os extremos (primeiro E último trimestre).

**Justificativa:**
1. Calcular crescimento percentual exige dois pontos de referência válidos
2. Usar trimestres diferentes (ex: T1 vs T2 para uma operadora, T1 vs T3 para outra) tornaria a comparação injusta
3. Interpolar valores seria estatisticamente questionável para um teste que pede "crescimento real"

**Implementação:**

```sql
-- Identifica dinamicamente primeiro/último período
WITH periodo AS (
    SELECT MIN(ano * 10 + trimestre) AS primeiro_periodo,
           MAX(ano * 10 + trimestre) AS ultimo_periodo
    FROM despesas_consolidadas
),
-- INNER JOIN garante que só operadoras com dados em AMBOS os extremos são consideradas
...
FROM despesas_primeiro dp
INNER JOIN despesas_ultimo du ON dp.operadora_id = du.operadora_id
```

##### Query 2: Distribuição de Despesas por UF

**Requisito:** Top 5 estados com maiores despesas totais.

**Desafio adicional:** Calcular média de despesas por operadora em cada UF.

**Implementação:**

```sql
SELECT
    o.uf,
    COUNT(DISTINCT o.id) AS qtd_operadoras,
    SUM(dc.valor_despesa) AS total_despesas,
    ROUND(SUM(dc.valor_despesa) / NULLIF(COUNT(DISTINCT o.id), 0), 2) AS media_por_operadora
FROM despesas_consolidadas dc
INNER JOIN operadoras o ON o.id = dc.operadora_id
GROUP BY o.uf
ORDER BY total_despesas DESC
LIMIT 5;
```

**Nota:** `NULLIF(..., 0)` previne divisão por zero em UFs sem operadoras (caso teórico após filtragens).

##### Query 3: Operadoras Acima da Média em 2+ Trimestres

**Requisito:** Contar operadoras que tiveram despesas acima da média geral em pelo menos 2 dos 3 trimestres.

**Trade-off: Abordagem de Implementação**

| Estratégia                      | Prós                      | Contras                                         |
| ------------------------------- | ------------------------- | ----------------------------------------------- |
| Subqueries com agregação (CTEs) | Legível, fácil de debugar | Pode ser menos performático em datasets grandes |
| Window functions                | Elegante, menos código    | Menos intuitivo para manutenção                 |
| Múltiplos JOINs                 | Explícito                 | Verboso, difícil de escalar                     |

**Escolha:** Subqueries com CTEs (Common Table Expressions).

**Justificativa:**
1. **Legibilidade:** Cada CTE tem um propósito claro (`media_geral`, `trimestres_acima_media`), facilitando entendimento
2. **Manutenibilidade:** Alterar a lógica (ex: mudar de 2 para 3 trimestres) requer mudança em um único lugar
3. **Performance:** Para o volume esperado (~4.500 registros), a diferença é imperceptível. Em cenários com milhões de registros, window functions seriam preferíveis
4. **Debugabilidade:** Pode-se executar cada CTE separadamente para verificar resultados intermediários

**Implementação:**

```sql
WITH media_geral AS (
    -- Calcula média única de todas as despesas
    SELECT AVG(valor_despesa) AS media
    FROM despesas_consolidadas
),
trimestres_acima_media AS (
    -- Conta em quantos trimestres cada operadora ficou acima da média
    SELECT dc.operadora_id, COUNT(*) AS trimestres_acima
    FROM despesas_consolidadas dc
    CROSS JOIN media_geral mg
    WHERE dc.valor_despesa > mg.media
    GROUP BY dc.operadora_id
)
SELECT COUNT(*) AS operadoras_acima_media_2_trimestres
FROM trimestres_acima_media
WHERE trimestres_acima >= 2;
```

**Versão alternativa incluída:** O arquivo `queries.sql` também contém uma versão que lista as operadoras (com CNPJ e razão social) ao invés de apenas contar, útil para análise detalhada.

---

### 6. Parte 4 - API REST e Interface Web

#### 6.1. Backend (FastAPI)

##### 6.1.1. Escolha do Framework

| Framework   | Prós                                                                      | Contras                                |
| ----------- | ------------------------------------------------------------------------- | -------------------------------------- |
| **Flask**   | Maduro, comunidade grande, flexível                                       | Sem validação automática, docs manuais |
| **FastAPI** | Tipagem nativa, docs automáticas (OpenAPI), async, validação com Pydantic | Mais recente, menos tutoriais          |

**Escolha:** FastAPI.

**Justificativa:**
1. **Validação automática:** Parâmetros de query (`page`, `limit`) são validados automaticamente com `Query(ge=1)`
2. **Documentação:** Swagger UI disponível em `/docs` sem configuração adicional
3. **Tipagem:** Integra naturalmente com o restante do projeto (MyPy strict)
4. **Performance:** Suporte nativo a async, relevante para I/O com banco de dados

##### 6.1.2. Estratégia de Paginação

| Estratégia       | Prós                                              | Contras                                   |
| ---------------- | ------------------------------------------------- | ----------------------------------------- |
| **Offset-based** | Simples, permite saltar para qualquer página      | Performance degrada com offset alto       |
| **Cursor-based** | Performance constante, ideal para scroll infinito | Não permite saltar para página específica |
| **Keyset**       | Melhor performance que offset                     | Requer ordenação estável, mais complexo   |

**Escolha:** Offset-based (`page` + `limit`).

**Justificativa:**
1. O volume de dados (~1.500 operadoras) não justifica otimizações de cursor
2. Interface com paginação numérica (ir para página X) é mais intuitiva para o usuário
3. Offset alto não é problema neste volume — query com `OFFSET 1000` ainda executa em <10ms

##### 6.1.3. Cache vs Queries Diretas

| Estratégia                  | Prós                                | Contras                               |
| --------------------------- | ----------------------------------- | ------------------------------------- |
| **Query direta**            | Dados sempre atualizados, simples   | Recalcula a cada requisição           |
| **Cache (Redis/in-memory)** | Resposta rápida para dados estáveis | Complexidade, possível inconsistência |
| **Pré-calculado em tabela** | Leitura instantânea                 | Requer job de atualização             |

**Escolha:** Query direta para `/api/estatisticas`.

**Justificativa:**
1. Os dados de despesas são trimestrais — atualização rara (a cada 3 meses)
2. Adicionar Redis ou tabela pré-calculada seria overengineering para este volume
3. Simplicidade > otimização prematura em contexto de teste técnico

##### 6.1.4. Estrutura de Resposta da API

| Estratégia                                    | Prós                    | Contras                                      |
| --------------------------------------------- | ----------------------- | -------------------------------------------- |
| **Apenas dados** (`[{...}]`)                  | Resposta menor, simples | Frontend precisa de request extra para total |
| **Dados + metadados** (`{data, total, page}`) | Tudo em uma request     | Resposta maior                               |

**Escolha:** Dados + metadados.

```json
{
  "data": [...],
  "total": 1523,
  "page": 1,
  "limit": 10,
  "total_pages": 153
}
```

**Justificativa:**
1. Frontend consegue renderizar paginação completa com uma única request
2. `total_pages` evita cálculo duplicado no cliente
3. Overhead de bytes é negligível comparado ao benefício de UX

##### 6.1.5. Connection Pooling

O SQLAlchemy utiliza um pool de conexões para otimizar o acesso ao banco de dados. Configuração implementada:

```python
engine = create_engine(
    DB_URL,
    poolclass=QueuePool,
    pool_size=5,        # Conexões mantidas abertas
    max_overflow=10,    # Conexões extras sob demanda
    pool_pre_ping=True, # Verifica conexões antes de usar
)
```

| Parâmetro        | Valor | Justificativa                                                        |
| ---------------- | ----- | -------------------------------------------------------------------- |
| `pool_size`      | 5     | Suficiente para requests concorrentes típicos de uma API             |
| `max_overflow`   | 10    | Permite picos de até 15 conexões simultâneas sem rejeitar requests   |
| `pool_pre_ping`  | True  | Evita erros de "connection closed" em conexões ociosas por muito tempo |

**Benefício:** Reduz overhead de estabelecer novas conexões TCP a cada request. Em cenários de alta concorrência, a reutilização de conexões pode reduzir latência em até 50ms por request.

#### 6.2. Frontend (Vue.js)

##### 6.2.1. Stack Tecnológica

| Tecnologia                 | Justificativa                                                          |
| -------------------------- | ---------------------------------------------------------------------- |
| **Vue 3**                  | Composition API permite código mais organizado e reutilizável          |
| **TypeScript**             | Tipagem estrita (`strict: true`) garante consistência com tipos da API |
| **Vite**                   | Build rápido, HMR instantâneo, melhor DX que webpack                   |
| **Tailwind CSS**           | Estilização rápida sem CSS custom, classes utilitárias                 |
| **Chart.js + vue-chartjs** | Biblioteca de gráficos leve e bem documentada                          |
| **Axios**                  | Cliente HTTP com interceptors e tipagem                                |
| **Vue Router**             | Roteamento SPA padrão do ecossistema                                   |

##### 6.2.2. Estratégia de Busca/Filtro

| Estratégia            | Prós                                                  | Contras                                   |
| --------------------- | ----------------------------------------------------- | ----------------------------------------- |
| **Busca no servidor** | Escala para qualquer volume, dados sempre atualizados | Latência de rede a cada keystroke         |
| **Busca no cliente**  | Resposta instantânea                                  | Requer carregar todos os dados na memória |
| **Híbrido**           | Melhor de ambos                                       | Complexidade de implementação             |

**Escolha:** Busca no servidor (com debounce).

**Justificativa:**
1. Com ~1.500 operadoras, carregar tudo no cliente seria viável, mas não escalaria
2. Debounce de 300ms evita requests excessivos durante digitação
3. Consistência: mesma lógica de busca funciona com 1.500 ou 150.000 registros

**Implementação:**
```typescript
let searchTimeout: ReturnType<typeof setTimeout> | null = null

function handleSearch(): void {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadOperadoras()
  }, 300)
}
```

##### 6.2.3. Gerenciamento de Estado

| Estratégia       | Prós                          | Contras                       |
| ---------------- | ----------------------------- | ----------------------------- |
| **Props/Events** | Simples, sem dependência      | Prop drilling em apps maiores |
| **Pinia/Vuex**   | Estado global, devtools       | Overhead para apps pequenas   |
| **Composables**  | Reutilizável, sem boilerplate | Requer Vue 3                  |

**Escolha:** Estado local nos componentes (sem store global).

**Justificativa:**
1. A aplicação tem apenas 2 páginas (Home e Detalhes)
2. Não há estado compartilhado entre componentes não relacionados
3. Cada componente gerencia seus próprios dados (`operadoras`, `loading`, `error`)
4. Adicionar Pinia para 2 páginas seria overengineering

##### 6.2.4. Performance da Tabela

| Estratégia              | Prós                         | Contras                               |
| ----------------------- | ---------------------------- | ------------------------------------- |
| **Renderização padrão** | Simples                      | Lenta com milhares de linhas visíveis |
| **Virtualização**       | Performance com muitos itens | Complexidade, scroll não-nativo       |
| **Paginação**           | Simples, performático        | Usuário não vê tudo de uma vez        |

**Escolha:** Paginação server-side (10 itens por página).

**Justificativa:**
1. Paginação já é requisito da especificação (`page`, `limit`)
2. 10 linhas por página renderizam instantaneamente
3. Virtualização seria necessária apenas com scroll infinito de milhares de itens visíveis simultaneamente

##### 6.2.5. Tratamento de Erros e Loading

| Estado                         | Tratamento                              | Justificativa                     |
| ------------------------------ | --------------------------------------- | --------------------------------- |
| **Loading**                    | Texto "Carregando..." centralizado      | Feedback imediato ao usuário      |
| **Erro de rede**               | Mensagem específica em vermelho         | Diferencia erro de "dados vazios" |
| **Dados vazios**               | Mensagem "Nenhuma operadora encontrada" | Não é erro, é resultado válido    |
| **404 (operadora não existe)** | Mensagem + botão voltar                 | Permite recuperação               |

**Decisão sobre mensagens:**

Optei por mensagens **específicas** ao invés de genéricas:
- "Erro ao carregar operadoras. Verifique se o servidor está rodando."
- "Operadora não encontrada."

**Justificativa:** Mensagens específicas ajudam o usuário (e o avaliador) a diagnosticar problemas. "Erro desconhecido" não agrega valor.

##### 6.2.6. Lazy Loading (Code Splitting)

Para otimizar o carregamento inicial da aplicação, componentes que não são imediatamente visíveis são carregados sob demanda:

```typescript
const OperadorasTable = defineAsyncComponent(() => import('../components/OperadorasTable.vue'))
const EstatisticasComplementares = defineAsyncComponent(() => import('../components/EstatisticasComplementares.vue'))
const OperadoraModal = defineAsyncComponent(() => import('../components/OperadoraModal.vue'))
```

| Componente                 | Carregamento | Justificativa                                      |
| -------------------------- | ------------ | -------------------------------------------------- |
| `DespesasChart`            | Síncrono     | Primeiro componente visível (above the fold)       |
| `OperadorasTable`          | Lazy         | Abaixo da dobra, pode aguardar                     |
| `EstatisticasComplementares` | Lazy       | Seção secundária, carrega enquanto usuário lê      |
| `OperadoraModal`           | Lazy         | Só renderiza quando usuário clica em uma operadora |

**Benefício:** Reduz o tamanho do bundle inicial, melhorando o Time to First Paint (TFP). O Vite gera chunks separados automaticamente para cada import dinâmico.

#### 6.3. Integração Backend ↔ Frontend

| Aspecto                    | Implementação                                                   |
| -------------------------- | --------------------------------------------------------------- |
| **CORS**                   | Configurado para `localhost:5173` e `localhost:8080`            |
| **Base URL**               | Centralizada em `services/api.ts` (`http://localhost:8000/api`) |
| **Tipagem**                | Interfaces TypeScript espelham respostas da API                 |
| **Inicialização do banco** | API cria tabelas e importa CSVs automaticamente no startup      |

**Fluxo de inicialização:**

```
1. API inicia (uvicorn)
2. Lifespan verifica se tabelas existem
3. Se não existem ou estão vazias, executa init_db()
4. init_db() lê CSVs de output/ e popula PostgreSQL
5. API pronta para receber requests
```

Isso permite que o avaliador execute `make api` e tenha o sistema funcionando sem setup manual de banco.

---

## Comandos Disponíveis

```bash
# Setup
make install              # Instalar dependências do backend (Poetry)
make frontend-install     # Instalar dependências do frontend (npm)

# Qualidade de código
make lint                 # Verificar código (ruff)
make format               # Formatar código (ruff)
make typecheck            # Verificar tipos (mypy)

# ETL (Partes 1-2)
make download             # Baixar dados da ANS
make consolidate          # Consolidar CSVs
make aggregate            # Validar, enriquecer e agregar
make etl                  # Pipeline completo (download + consolidate + aggregate)

# Aplicação (Parte 4)
make api                  # Iniciar servidor FastAPI (localhost:8000)
make frontend-dev         # Iniciar dev server Vue (localhost:5173)

# Limpeza
make clean                # Limpar caches e arquivos temporários
```

---

## Contato

Pedro Garcia - pedrofsgarcia.pro@gmail.com
