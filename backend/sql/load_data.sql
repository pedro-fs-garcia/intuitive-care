-- IMPORTAÇÃO DE DADOS (Item 3.3)
--
-- COMO EXECUTAR:
--
-- Opção 1 - Via psql (recomendado):
--   psql -d <database> -f load_data.sql
--   (edite os caminhos abaixo antes de executar)
--
-- Opção 2 - Via pgAdmin4:
--   Substitua as variáveis :'path_*' pelos caminhos absolutos dos arquivos.
--   Exemplo: FROM :'path_operadoras'  →  FROM '/home/user/output/operadoras.csv'


-- Ajuste os caminhos para os arquivos CSV gerados nas Partes 1 e 2
\set path_operadoras '../../data/operadoras/operadoras.csv'
\set path_consolidado '../../data/consolidado/consolidado_despesas.csv'
\set path_agregado '../../output/despesas_agregadas.csv'


-- ANSApiClient.download_operadoras_ativas
-- REG_ANS, CNPJ, Razao_Social, Modalidade, UF
CREATE TEMP TABLE staging_operadoras (
    registro_ans TEXT,
    cnpj TEXT,
    razao_social TEXT,
    modalidade TEXT,
    uf TEXT
);

COPY staging_operadoras (registro_ans, cnpj, razao_social, modalidade, uf)
FROM :'path_operadoras'
WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER ';',
    ENCODING 'UTF8',
    NULL ''
);


INSERT INTO operadoras (cnpj, razao_social, registro_ans, modalidade, uf)
SELECT DISTINCT ON (cnpj)
    REGEXP_REPLACE(cnpj, '[^0-9]', '', 'g') AS cnpj,
    TRIM(razao_social),
    NULLIF(TRIM(registro_ans), ''),
    NULLIF(TRIM(modalidade), ''),
    UPPER(TRIM(uf))
FROM staging_operadoras
WHERE
    cnpj IS NOT NULL
    AND TRIM(cnpj) <> ''
    AND razao_social IS NOT NULL
    AND TRIM(razao_social) <> ''
    AND UPPER(TRIM(uf)) IN (
        'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG',
        'PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'
    )
ORDER BY cnpj, razao_social;


DO $$
DECLARE
    total_staging INT;
    total_inserido INT;
BEGIN
    SELECT COUNT(*) INTO total_staging FROM staging_operadoras;
    SELECT COUNT(*) INTO total_inserido FROM operadoras;
    RAISE NOTICE 'Operadoras: % registros no CSV, % inseridos, % rejeitados',
        total_staging, total_inserido, total_staging - total_inserido;
END $$;

DROP TABLE staging_operadoras;



-- DespesasConsolidator.run_batch
-- CNPJ, RazaoSocial, Trimestre, Ano, ValorDespesas
CREATE TEMP TABLE staging_despesas (
    cnpj TEXT,
    razao_social TEXT,
    trimestre TEXT,
    ano TEXT,
    valor_despesas TEXT
);

COPY staging_despesas (cnpj, razao_social, trimestre, ano, valor_despesas)
FROM :'path_consolidado'
WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER ';',
    ENCODING 'UTF8',
    NULL ''
);


INSERT INTO despesas_consolidadas (operadora_id, trimestre, ano, valor_despesa)
SELECT
    o.id,
    CAST(sd.trimestre AS INT),
    CAST(sd.ano AS INT),
    CAST(REPLACE(REPLACE(sd.valor_despesas, '.', ''), ',', '.') AS DECIMAL(18,2))
FROM staging_despesas sd
INNER JOIN operadoras o ON o.cnpj = REGEXP_REPLACE(sd.cnpj, '[^0-9]', '', 'g')
WHERE
    sd.trimestre ~ '^[1-4]$'
    AND sd.ano ~ '^20[0-9]{2}$'
    AND sd.valor_despesas IS NOT NULL
    AND sd.valor_despesas ~ '^-?[0-9.,]+$'
    AND CAST(REPLACE(REPLACE(sd.valor_despesas, '.', ''), ',', '.') AS DECIMAL(18,2)) > 0;

DO $$
DECLARE
    total_staging INT;
    total_inserido INT;
BEGIN
    SELECT COUNT(*) INTO total_staging FROM staging_despesas;
    SELECT COUNT(*) INTO total_inserido FROM despesas_consolidadas;
    RAISE NOTICE 'Despesas consolidadas: % registros no CSV, % inseridos',
        total_staging, total_inserido;
END $$;

DROP TABLE staging_despesas;


-- Caggregator.py
-- CNPJ, RegistroANS, RazaoSocial, Modalidade, UF, TotalDespesas, MediaTrimestral, DesvioPadrao, QtdTrimestres
CREATE TEMP TABLE staging_agregadas (
    cnpj TEXT,
    registro_ans TEXT,
    razao_social TEXT,
    modalidade TEXT,
    uf TEXT,
    total_despesas TEXT,
    media_trimestral TEXT,
    desvio_padrao TEXT,
    qtd_trimestres TEXT
);

COPY staging_agregadas (cnpj, registro_ans, razao_social, modalidade, uf, total_despesas, media_trimestral, desvio_padrao, qtd_trimestres)
FROM :'path_agregado'
WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER ';',
    ENCODING 'UTF8',
    NULL ''
);


INSERT INTO despesas_agregadas (operadora_id, uf, total_despesas, media_trimestral, desvio_padrao, qtd_trimestres)
SELECT DISTINCT ON (o.id, UPPER(TRIM(sa.uf)))
    o.id,
    UPPER(TRIM(sa.uf)),
    CAST(REPLACE(REPLACE(COALESCE(sa.total_despesas, '0'), '.', ''), ',', '.') AS DECIMAL(18,2)),
    CAST(REPLACE(REPLACE(COALESCE(sa.media_trimestral, '0'), '.', ''), ',', '.') AS DECIMAL(18,2)),
    CAST(REPLACE(REPLACE(COALESCE(sa.desvio_padrao, '0'), '.', ''), ',', '.') AS DECIMAL(18,2)),
    COALESCE(CAST(sa.qtd_trimestres AS INT), 0)
FROM staging_agregadas sa
INNER JOIN operadoras o ON o.cnpj = REGEXP_REPLACE(sa.cnpj, '[^0-9]', '', 'g')
WHERE
    UPPER(TRIM(sa.uf)) IN (
        'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG',
        'PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'
    );

DO $$
DECLARE
    total_staging INT;
    total_inserido INT;
BEGIN
    SELECT COUNT(*) INTO total_staging FROM staging_agregadas;
    SELECT COUNT(*) INTO total_inserido FROM despesas_agregadas;
    RAISE NOTICE 'Despesas agregadas: % registros no CSV, % inseridos',
        total_staging, total_inserido;
END $$;

DROP TABLE staging_agregadas;


SELECT 'operadoras' AS tabela, COUNT(*) AS registros FROM operadoras
UNION ALL
SELECT 'despesas_consolidadas', COUNT(*) FROM despesas_consolidadas
UNION ALL
SELECT 'despesas_agregadas', COUNT(*) FROM despesas_agregadas;
