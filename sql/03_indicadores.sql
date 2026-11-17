-- =====================================================================
-- ETAPA 5 — INDICADORES (views de consumo para dashboards/relatórios)
-- =====================================================================
-- Aqui ficam as consultas que alimentam o dashboard. Destaque para as
-- WINDOW FUNCTIONS: RANK, LAG, SUM() OVER (acumulado e participação %).
-- =====================================================================

-- ---------------------------------------------------------------------
-- RN06 Sinistralidade por produto = sinistro retido / prêmio ganho retido
-- (só entram sinistros cobertos: RN07 fl_ocorrencia_na_vigencia = 1)
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS vw_sinistralidade_produto;
CREATE VIEW vw_sinistralidade_produto AS
WITH premio AS (
    SELECT cd_produto,
           COUNT(*)                    AS qt_apolices,
           SUM(vl_premio_emitido)      AS vl_premio_emitido,
           SUM(vl_premio_ganho_retido) AS vl_premio_ganho_retido
    FROM fato_premio
    GROUP BY cd_produto
),
sinistro AS (
    SELECT cd_produto,
           COUNT(*)                    AS qt_sinistros,
           SUM(vl_sinistro_retido)     AS vl_sinistro_retido
    FROM fato_sinistro
    WHERE fl_ocorrencia_na_vigencia = 1
    GROUP BY cd_produto
)
SELECT
    d.ds_produto,
    p.qt_apolices,
    COALESCE(s.qt_sinistros, 0)                                   AS qt_sinistros,
    ROUND(p.vl_premio_emitido, 2)                                 AS vl_premio_emitido,
    ROUND(p.vl_premio_ganho_retido, 2)                            AS vl_premio_ganho_retido,
    ROUND(COALESCE(s.vl_sinistro_retido, 0), 2)                   AS vl_sinistro_retido,
    ROUND(COALESCE(s.vl_sinistro_retido, 0)
          / p.vl_premio_ganho_retido, 4)                          AS pc_sinistralidade,
    -- ranking: 1 = produto com MAIOR sinistralidade (ponto de atenção para a Atuária)
    RANK() OVER (ORDER BY COALESCE(s.vl_sinistro_retido, 0)
                          / p.vl_premio_ganho_retido DESC)        AS nr_ranking_sinistralidade
FROM premio p
JOIN dim_produto d    ON d.cd_produto = p.cd_produto
LEFT JOIN sinistro s  ON s.cd_produto = p.cd_produto;

-- ---------------------------------------------------------------------
-- Prêmio emitido por mês de início de vigência
--   LAG  -> valor do mês anterior (para variação %)
--   SUM() OVER (ORDER BY ...) -> acumulado no tempo
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS vw_premio_mensal;
CREATE VIEW vw_premio_mensal AS
WITH mensal AS (
    SELECT strftime('%Y-%m', dt_inicio_vigencia) AS aa_mes,
           COUNT(*)                              AS qt_apolices,
           ROUND(SUM(vl_premio_emitido), 2)      AS vl_premio_emitido
    FROM fato_premio
    GROUP BY 1
)
SELECT
    aa_mes,
    qt_apolices,
    vl_premio_emitido,
    LAG(vl_premio_emitido) OVER (ORDER BY aa_mes)                 AS vl_mes_anterior,
    ROUND(vl_premio_emitido
          / LAG(vl_premio_emitido) OVER (ORDER BY aa_mes) - 1, 4) AS pc_variacao_mes,
    ROUND(SUM(vl_premio_emitido) OVER (ORDER BY aa_mes), 2)       AS vl_acumulado
FROM mensal;

-- ---------------------------------------------------------------------
-- Ranking de corretores (área Comercial)
--   RANK() -> posição;  SUM() OVER () -> total geral para % de participação
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS vw_ranking_corretor;
CREATE VIEW vw_ranking_corretor AS
SELECT
    c.nm_corretor,
    COUNT(*)                                                      AS qt_apolices,
    ROUND(SUM(f.vl_premio_liquido_final), 2)                      AS vl_premio_liquido_final,
    ROUND(SUM(f.vl_comissao), 2)                                  AS vl_comissao,
    ROUND(SUM(f.vl_premio_liquido_final)
          / SUM(SUM(f.vl_premio_liquido_final)) OVER (), 4)       AS pc_participacao,
    RANK() OVER (ORDER BY SUM(f.vl_premio_liquido_final) DESC)    AS nr_ranking
FROM fato_premio f
JOIN dim_corretor c ON c.cd_corretor = f.cd_corretor
GROUP BY c.nm_corretor;
