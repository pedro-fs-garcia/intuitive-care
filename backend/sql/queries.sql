-- ============================================================================
-- QUERIES ANALÍTICAS (Item 3.4)
-- IMPORTANTE: Os valores em despesas_consolidadas são YTD (Year-to-Date)
-- Por isso, usamos o valor do último trimestre como total do ano ou
-- desacumulamos usando LAG() para obter valores isolados por trimestre
-- ============================================================================

-- QUERY 1: Top 5 operadoras com maior crescimento percentual
-- Compara gasto ISOLADO do primeiro trimestre com gasto ISOLADO do último
WITH periodo AS (
    SELECT
        MIN(ano * 10 + trimestre) AS primeiro_periodo,
        MAX(ano * 10 + trimestre) AS ultimo_periodo
    FROM despesas_consolidadas
),
despesas_com_lag AS (
    SELECT
        dc.operadora_id,
        dc.ano,
        dc.trimestre,
        dc.valor_despesa AS valor_ytd,
        dc.valor_despesa - COALESCE(
            LAG(dc.valor_despesa) OVER (
                PARTITION BY dc.operadora_id, dc.ano 
                ORDER BY dc.trimestre
            ), 0
        ) AS valor_isolado
    FROM despesas_consolidadas dc
),
despesas_primeiro AS (
    SELECT dl.operadora_id, dl.valor_isolado AS valor_despesa
    FROM despesas_com_lag dl
    CROSS JOIN periodo p
    WHERE dl.ano * 10 + dl.trimestre = p.primeiro_periodo
),
despesas_ultimo AS (
    SELECT dl.operadora_id, dl.valor_isolado AS valor_despesa
    FROM despesas_com_lag dl
    CROSS JOIN periodo p
    WHERE dl.ano * 10 + dl.trimestre = p.ultimo_periodo
)
SELECT
    o.cnpj,
    o.razao_social,
    dp.valor_despesa AS despesa_inicial,
    du.valor_despesa AS despesa_final,
    ROUND(
        ((du.valor_despesa - dp.valor_despesa) / NULLIF(dp.valor_despesa, 0)) * 100,
        2
    ) AS crescimento_percentual
FROM despesas_primeiro dp
INNER JOIN despesas_ultimo du ON dp.operadora_id = du.operadora_id
INNER JOIN operadoras o ON o.id = dp.operadora_id
WHERE dp.valor_despesa > 0
ORDER BY crescimento_percentual DESC
LIMIT 5;


-- QUERY 2: Distribuição de despesas por UF (top 5)
-- Usa valores ISOLADOS (desacumulados) para soma e média corretas
WITH despesas_isoladas AS (
    SELECT
        dc.operadora_id,
        dc.ano,
        dc.trimestre,
        dc.valor_despesa - COALESCE(
            LAG(dc.valor_despesa) OVER (
                PARTITION BY dc.operadora_id, dc.ano 
                ORDER BY dc.trimestre
            ), 0
        ) AS valor_isolado
    FROM despesas_consolidadas dc
)
SELECT
    o.uf,
    COUNT(DISTINCT o.id) AS qtd_operadoras,
    SUM(di.valor_isolado) AS total_despesas,
    ROUND(AVG(di.valor_isolado), 2) AS media_por_registro,
    ROUND(SUM(di.valor_isolado) / NULLIF(COUNT(DISTINCT o.id), 0), 2) AS media_por_operadora
FROM despesas_isoladas di
INNER JOIN operadoras o ON o.id = di.operadora_id
GROUP BY o.uf
ORDER BY total_despesas DESC
LIMIT 5;


-- QUERY 3: Operadoras com despesas acima da média em 2+ trimestres
-- Usa valores ISOLADOS para comparação justa entre trimestres
WITH despesas_isoladas AS (
    SELECT
        dc.operadora_id,
        dc.ano,
        dc.trimestre,
        dc.valor_despesa - COALESCE(
            LAG(dc.valor_despesa) OVER (
                PARTITION BY dc.operadora_id, dc.ano 
                ORDER BY dc.trimestre
            ), 0
        ) AS valor_isolado
    FROM despesas_consolidadas dc
),
media_geral AS (
    SELECT AVG(valor_isolado) AS media
    FROM despesas_isoladas
),
trimestres_acima_media AS (
    SELECT
        di.operadora_id,
        COUNT(*) AS trimestres_acima
    FROM despesas_isoladas di
    CROSS JOIN media_geral mg
    WHERE di.valor_isolado > mg.media
    GROUP BY di.operadora_id
)
SELECT COUNT(*) AS operadoras_acima_media_2_trimestres
FROM trimestres_acima_media
WHERE trimestres_acima >= 2;


-- QUERY 3 (versão detalhada): Lista das operadoras acima da média
WITH despesas_isoladas AS (
    SELECT
        dc.operadora_id,
        dc.ano,
        dc.trimestre,
        dc.valor_despesa - COALESCE(
            LAG(dc.valor_despesa) OVER (
                PARTITION BY dc.operadora_id, dc.ano 
                ORDER BY dc.trimestre
            ), 0
        ) AS valor_isolado
    FROM despesas_consolidadas dc
),
media_geral AS (
    SELECT AVG(valor_isolado) AS media
    FROM despesas_isoladas
),
trimestres_acima_media AS (
    SELECT
        di.operadora_id,
        COUNT(*) AS trimestres_acima
    FROM despesas_isoladas di
    CROSS JOIN media_geral mg
    WHERE di.valor_isolado > mg.media
    GROUP BY di.operadora_id
)
SELECT
    o.cnpj,
    o.razao_social,
    tam.trimestres_acima,
    (SELECT media FROM media_geral) AS media_geral_referencia
FROM trimestres_acima_media tam
INNER JOIN operadoras o ON o.id = tam.operadora_id
WHERE tam.trimestres_acima >= 2
ORDER BY tam.trimestres_acima DESC, o.razao_social;
