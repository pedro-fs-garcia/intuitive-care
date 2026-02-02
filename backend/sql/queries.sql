WITH periodo AS (
    SELECT
        MIN(ano * 10 + trimestre) AS primeiro_periodo,
        MAX(ano * 10 + trimestre) AS ultimo_periodo
    FROM despesas_consolidadas
),
despesas_primeiro AS (
    SELECT
        dc.operadora_id,
        dc.valor_despesa
    FROM despesas_consolidadas dc
    CROSS JOIN periodo p
    WHERE dc.ano * 10 + dc.trimestre = p.primeiro_periodo
),
despesas_ultimo AS (
    SELECT
        dc.operadora_id,
        dc.valor_despesa
    FROM despesas_consolidadas dc
    CROSS JOIN periodo p
    WHERE dc.ano * 10 + dc.trimestre = p.ultimo_periodo
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
WHERE dp.valor_despesa > 0  -- Evita divisão por zero
ORDER BY crescimento_percentual DESC
LIMIT 5;


SELECT
    o.uf,
    COUNT(DISTINCT o.id) AS qtd_operadoras,
    SUM(dc.valor_despesa) AS total_despesas,
    ROUND(AVG(dc.valor_despesa), 2) AS media_por_registro,
    ROUND(SUM(dc.valor_despesa) / NULLIF(COUNT(DISTINCT o.id), 0), 2) AS media_por_operadora
FROM despesas_consolidadas dc
INNER JOIN operadoras o ON o.id = dc.operadora_id
GROUP BY o.uf
ORDER BY total_despesas DESC
LIMIT 5;


WITH media_geral AS (
    SELECT AVG(valor_despesa) AS media
    FROM despesas_consolidadas
),
trimestres_acima_media AS (
    SELECT
        dc.operadora_id,
        COUNT(*) AS trimestres_acima
    FROM despesas_consolidadas dc
    CROSS JOIN media_geral mg
    WHERE dc.valor_despesa > mg.media
    GROUP BY dc.operadora_id
)
SELECT COUNT(*) AS operadoras_acima_media_2_trimestres
FROM trimestres_acima_media
WHERE trimestres_acima >= 2;


-- QUERY 3: Versão detalhada com lista das operadoras
WITH media_geral AS (
    SELECT AVG(valor_despesa) AS media
    FROM despesas_consolidadas
),
trimestres_acima_media AS (
    SELECT
        dc.operadora_id,
        COUNT(*) AS trimestres_acima
    FROM despesas_consolidadas dc
    CROSS JOIN media_geral mg
    WHERE dc.valor_despesa > mg.media
    GROUP BY dc.operadora_id
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
