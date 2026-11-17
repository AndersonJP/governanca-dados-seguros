-- =====================================================================
-- ETAPA 4 — CAMADA GOLD: modelo DIMENSIONAL + REGRAS DE NEGÓCIO
-- =====================================================================
-- Modelo estrela (Kimball):
--
--        dim_produto        dim_corretor
--               \              /
--             fato_premio  (grão: 1 linha por APÓLICE)
--             fato_sinistro (grão: 1 linha por SINISTRO)
--
-- Cada cálculo traz o código da regra (RN01, RN02...). A descrição
-- oficial de cada regra fica no Catálogo de Regras:
--   metadados/regras_negocio.csv  ->  docs/catalogo_regras.md / Confluence
-- =====================================================================

-- Parâmetro da execução: data de fechamento usada no prêmio ganho
DROP TABLE IF EXISTS param_execucao;
CREATE TABLE param_execucao (dt_base DATE NOT NULL);
INSERT INTO param_execucao VALUES ('2026-10-31');

-- ---------------------------------------------------------------------
-- DIMENSÕES
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS dim_produto;
CREATE TABLE dim_produto (
    cd_produto  INTEGER PRIMARY KEY,
    ds_produto  TEXT NOT NULL
);
INSERT INTO dim_produto SELECT cd_produto, ds_produto FROM silver_produto;

DROP TABLE IF EXISTS dim_corretor;
CREATE TABLE dim_corretor (
    cd_corretor  INTEGER PRIMARY KEY,
    nm_corretor  TEXT NOT NULL,
    pc_comissao  REAL NOT NULL
);
INSERT INTO dim_corretor SELECT cd_corretor, nm_corretor, pc_comissao FROM silver_corretor;

-- ---------------------------------------------------------------------
-- FATO_PREMIO  (grão: apólice)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS fato_premio;
CREATE TABLE fato_premio (
    nr_apolice                   TEXT PRIMARY KEY,
    cd_produto                   INTEGER REFERENCES dim_produto(cd_produto),
    cd_corretor                  INTEGER REFERENCES dim_corretor(cd_corretor),
    dt_inicio_vigencia           DATE NOT NULL,
    st_apolice                   TEXT NOT NULL,
    qt_dias_vigencia             INTEGER NOT NULL,
    qt_dias_decorridos           INTEGER NOT NULL,
    vl_premio_emitido            REAL NOT NULL,
    vl_premio_ganho              REAL NOT NULL,
    vl_restituicao_cancelamento  REAL NOT NULL,
    vl_premio_liquido_final      REAL NOT NULL,
    vl_comissao                  REAL NOT NULL,
    vl_premio_cedido_cosseguro   REAL NOT NULL,
    vl_premio_ganho_retido       REAL NOT NULL
);

INSERT INTO fato_premio
WITH
-- RN01: soma dos endossos de AUMENTO/REDUÇÃO por apólice (JOIN + agregação)
ajuste_endosso AS (
    SELECT nr_apolice, SUM(vl_premio_endosso) AS vl_ajuste
    FROM silver_endosso
    WHERE tp_endosso IN ('AUMENTO', 'REDUCAO')
    GROUP BY nr_apolice
),
base AS (
    SELECT
        a.*,
        c.pc_comissao,
        -- RN01 Prêmio emitido = prêmio original + endossos de aumento/redução
        a.vl_premio_liquido + COALESCE(e.vl_ajuste, 0)                       AS vl_premio_emitido,
        CAST(julianday(a.dt_fim_vigencia) - julianday(a.dt_inicio_vigencia) AS INTEGER)
                                                                             AS qt_dias_vigencia,
        -- RN02/RN03: a exposição ao risco termina no que vier primeiro:
        -- data base do fechamento, cancelamento ou fim da vigência
        MIN(p.dt_base, COALESCE(a.dt_cancelamento, a.dt_fim_vigencia), a.dt_fim_vigencia)
                                                                             AS dt_fim_exposicao
    FROM silver_apolice a
    CROSS JOIN param_execucao p
    LEFT JOIN ajuste_endosso  e ON e.nr_apolice  = a.nr_apolice
    LEFT JOIN silver_corretor c ON c.cd_corretor = a.cd_corretor
),
calculo AS (
    SELECT
        b.*,
        MAX(0, CAST(julianday(dt_fim_exposicao) - julianday(dt_inicio_vigencia) AS INTEGER))
                                                                             AS qt_dias_decorridos,
        -- RN03 Restituição: no cancelamento devolve-se o prêmio NÃO decorrido (valor negativo)
        CASE WHEN st_apolice = 'CANCELADA' THEN
            -ROUND(vl_premio_emitido
                   * (julianday(dt_fim_vigencia) - julianday(dt_cancelamento))
                   / qt_dias_vigencia, 2)
        ELSE 0 END                                                           AS vl_restituicao
    FROM base b
)
SELECT
    nr_apolice,
    cd_produto,
    cd_corretor,
    dt_inicio_vigencia,
    st_apolice,
    qt_dias_vigencia,
    qt_dias_decorridos,
    ROUND(vl_premio_emitido, 2),
    -- RN02 Prêmio ganho (pro rata die) = emitido x dias decorridos / dias de vigência
    ROUND(vl_premio_emitido * qt_dias_decorridos / qt_dias_vigencia, 2),
    vl_restituicao,
    -- RN03 Prêmio líquido final = emitido + restituição (restituição é negativa)
    ROUND(vl_premio_emitido + vl_restituicao, 2),
    -- RN04 Comissão = prêmio líquido final x % do corretor (estorna junto no cancelamento)
    ROUND((vl_premio_emitido + vl_restituicao) * pc_comissao, 2),
    -- RN05 Cosseguro cedido = parte do prêmio que pertence à congênere
    ROUND((vl_premio_emitido + vl_restituicao) * pc_cosseguro_cedido, 2),
    -- RN05 Prêmio ganho retido = prêmio ganho x (1 - % cedido)
    ROUND(vl_premio_emitido * qt_dias_decorridos / qt_dias_vigencia
          * (1 - pc_cosseguro_cedido), 2)
FROM calculo;

-- ---------------------------------------------------------------------
-- FATO_SINISTRO  (grão: sinistro)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS fato_sinistro;
CREATE TABLE fato_sinistro (
    nr_sinistro                 TEXT PRIMARY KEY,
    nr_apolice                  TEXT REFERENCES fato_premio(nr_apolice),
    cd_produto                  INTEGER REFERENCES dim_produto(cd_produto),
    dt_ocorrencia               DATE NOT NULL,
    qt_dias_ate_aviso           INTEGER NOT NULL,
    st_sinistro                 TEXT NOT NULL,
    vl_sinistro_total           REAL NOT NULL,
    vl_sinistro_retido          REAL NOT NULL,
    fl_ocorrencia_na_vigencia   INTEGER NOT NULL
);

INSERT INTO fato_sinistro
SELECT
    s.nr_sinistro,
    s.nr_apolice,
    a.cd_produto,
    s.dt_ocorrencia,
    CAST(julianday(s.dt_aviso) - julianday(s.dt_ocorrencia) AS INTEGER),
    s.st_sinistro,
    -- RN06 Sinistro total = indenização já paga + reserva (provisão do que falta pagar)
    ROUND(s.vl_indenizacao_paga + s.vl_reserva_sinistro, 2),
    -- RN05 Sinistro retido: o cosseguro também divide o sinistro na mesma proporção
    ROUND((s.vl_indenizacao_paga + s.vl_reserva_sinistro) * (1 - a.pc_cosseguro_cedido), 2),
    -- RN07 Sinistro só é coberto se ocorreu DENTRO da vigência (e antes do cancelamento)
    CASE WHEN s.dt_ocorrencia >= a.dt_inicio_vigencia
          AND s.dt_ocorrencia <  COALESCE(a.dt_cancelamento, a.dt_fim_vigencia)
         THEN 1 ELSE 0 END
FROM silver_sinistro s
JOIN silver_apolice  a ON a.nr_apolice = s.nr_apolice;
