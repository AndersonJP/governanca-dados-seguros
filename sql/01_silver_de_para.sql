-- =====================================================================
-- ETAPA 3 — CAMADA SILVER: aplicação do "DE x PARA"
-- =====================================================================
-- Objetivo: transformar as tabelas do sistema de origem (nomes crípticos,
-- tudo como texto, com duplicatas) em tabelas limpas, TIPADAS, com chave
-- primária declarada e NOMENCLATURA UNIFICADA de negócio.
--
-- Cada coluna abaixo está mapeada em metadados/de_para.csv.
--   Ex.: TB_APOL.VL_PRM_LIQ  ->  silver_apolice.vl_premio_liquido
--
-- Padrão de nomes (nomenclatura unificada):
--   nr_ = número/identificador   dt_ = data      vl_ = valor em R$
--   pc_ = percentual (0 a 1)     cd_ = código    ds_/nm_ = descrição/nome
--   st_ = status                 tp_ = tipo      fl_ = flag (0/1)
--
-- Observação: as FOREIGN KEYs são "informativas" (como no Databricks
-- Unity Catalog, que não as obriga). Por isso o pipeline NÃO as força
-- e quem garante a integridade é a validação V02 (04_validacoes.sql).
-- =====================================================================

-- ---------------------------------------------------------------------
-- Cadastros de apoio: produto e corretor
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS silver_produto;
CREATE TABLE silver_produto (
    cd_produto   INTEGER PRIMARY KEY,
    ds_produto   TEXT    NOT NULL
);
INSERT INTO silver_produto
SELECT CAST(CD_PROD AS INTEGER), DS_PROD
FROM bronze_tb_prod;

DROP TABLE IF EXISTS silver_corretor;
CREATE TABLE silver_corretor (
    cd_corretor  INTEGER PRIMARY KEY,
    nm_corretor  TEXT    NOT NULL,
    pc_comissao  REAL    NOT NULL
);
INSERT INTO silver_corretor
SELECT CAST(CD_CORR AS INTEGER), NM_CORR, CAST(PC_COMS AS REAL)
FROM bronze_tb_corr;

-- ---------------------------------------------------------------------
-- silver_apolice
-- Destaque técnico: deduplicação com WINDOW FUNCTION (ROW_NUMBER).
-- O legado recarregou algumas apólices; mantemos só a carga mais recente.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS silver_apolice;
CREATE TABLE silver_apolice (
    nr_apolice           TEXT PRIMARY KEY,
    cd_produto           INTEGER REFERENCES silver_produto(cd_produto),
    cd_corretor          INTEGER REFERENCES silver_corretor(cd_corretor),
    cd_segurado          TEXT,
    dt_inicio_vigencia   DATE NOT NULL,
    dt_fim_vigencia      DATE NOT NULL,
    vl_premio_liquido    REAL NOT NULL,
    st_apolice           TEXT NOT NULL,
    dt_cancelamento      DATE,
    pc_cosseguro_cedido  REAL NOT NULL,
    dt_carga             DATE NOT NULL
);

INSERT INTO silver_apolice
WITH ranqueado AS (
    SELECT
        b.*,
        ROW_NUMBER() OVER (
            PARTITION BY NR_APOL        -- uma "janela" por apólice
            ORDER BY DT_CARGA DESC      -- a carga mais recente recebe o nº 1
        ) AS rn
    FROM bronze_tb_apol b
)
SELECT
    NR_APOL,
    CAST(CD_PROD AS INTEGER),
    CAST(CD_CORR AS INTEGER),
    CD_SEGD,
    DATE(DT_INI_VIG),
    DATE(DT_FIM_VIG),
    CAST(VL_PRM_LIQ AS REAL),
    CASE ST_APOL WHEN 'A' THEN 'ATIVA' WHEN 'C' THEN 'CANCELADA' END,  -- código -> descrição
    NULLIF(DT_CANC, ''),                                               -- vazio vira NULL
    CAST(PC_COSS_CED AS REAL),
    DATE(DT_CARGA)
FROM ranqueado
WHERE rn = 1;                                                          -- descarta duplicatas

-- ---------------------------------------------------------------------
-- silver_endosso
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS silver_endosso;
CREATE TABLE silver_endosso (
    nr_endosso         TEXT PRIMARY KEY,
    nr_apolice         TEXT REFERENCES silver_apolice(nr_apolice),
    tp_endosso         TEXT NOT NULL,
    dt_emissao         DATE NOT NULL,
    vl_premio_endosso  REAL NOT NULL
);
INSERT INTO silver_endosso
SELECT
    NR_ENDS,
    NR_APOL,
    CASE TP_ENDS WHEN 'AUM' THEN 'AUMENTO'
                 WHEN 'RED' THEN 'REDUCAO'
                 WHEN 'CAN' THEN 'CANCELAMENTO' END,
    DATE(DT_EMIS),
    CAST(VL_PRM_ENDS AS REAL)
FROM bronze_tb_ends;

-- ---------------------------------------------------------------------
-- silver_sinistro
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS silver_sinistro;
CREATE TABLE silver_sinistro (
    nr_sinistro          TEXT PRIMARY KEY,
    nr_apolice           TEXT REFERENCES silver_apolice(nr_apolice),
    dt_ocorrencia        DATE NOT NULL,
    dt_aviso             DATE NOT NULL,
    vl_indenizacao_paga  REAL NOT NULL,
    vl_reserva_sinistro  REAL NOT NULL,
    st_sinistro          TEXT NOT NULL
);
INSERT INTO silver_sinistro
SELECT
    NR_SINI,
    NR_APOL,
    DATE(DT_OCOR),
    DATE(DT_AVIS),
    CAST(VL_INDE AS REAL),
    CAST(VL_RESV AS REAL),
    ST_SINI
FROM bronze_tb_sini;
