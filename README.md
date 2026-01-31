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

| Decisão               | Escolha                      | Alternativa            | Justificativa                                                                                                    |
| --------------------- | ---------------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Estratégia de leitura | **Processamento incremental** | Carregar tudo em memória | Cada arquivo de trimestre é processado individualmente e concatenado ao resultado. Reduz pico de uso de memória. |

**Detalhes da implementação:**
- Cada arquivo é lido, filtrado e agregado antes de ser concatenado ao DataFrame final
- Isso permite processar datasets maiores que a memória disponível
- Trade-off: ligeiramente mais lento que processar tudo em memória, mas mais seguro para volumes desconhecidos

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

| Decisão      | Escolha                      | Alternativa        | Justificativa                                                                                    |
| ------------ | ---------------------------- | ------------------ | ------------------------------------------------------------------------------------------------ |
| Tipo de join | **LEFT JOIN + filtro**       | INNER JOIN direto  | LEFT JOIN permite identificar e logar registros sem match antes de descartá-los.                 |

#### 3.7. Tratamento de Inconsistências

| Inconsistência                              | Tratamento                                      | Justificativa                                                                        |
| ------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------ |
| CNPJs duplicados (razões sociais diferentes)| **Mantido primeiro registro**                   | Cadastro pode conter histórico; primeiro registro representa dados mais atuais       |
| Valores zerados                             | **Mantidos**                                    | Zero indica ausência de eventos no período — dado válido para análise comparativa    |
| Valores negativos                           | **Mantidos**                                    | Podem representar estornos ou correções contábeis legítimas                          |
| Valores não numéricos                       | `pd.to_numeric(errors='coerce')` → 0            | Converte para NaN e substitui por 0, evitando perda de registros                     |
| Datas inválidas                             | `pd.to_datetime(errors='coerce')` → descartados | Registros sem data válida não podem ser atribuídos a um trimestre                    |
| REG_ANS sem match no cadastro               | **Removidos com log**                           | Registros sem CNPJ/RazaoSocial não atendem à especificação do CSV                    |

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
