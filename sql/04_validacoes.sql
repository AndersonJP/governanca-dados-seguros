-- =====================================================================
-- ETAPA 6 — VALIDAÇÕES DE QUALIDADE ("a documentação reflete a realidade?")
-- =====================================================================
-- Cada validação devolve QUANTOS registros têm problema.
--   OK      -> nenhum problema
--   TRATADO -> problema existia na origem e o pipeline já resolveu
--   ALERTA  -> problema real que precisa ser comunicado ao dono do dado
--   ERRO    -> quebra de regra: o pipeline NÃO deve promover para produção
-- O resultado vai para a tabela qualidade_resultado e aparece no dashboard.
-- =====================================================================

DROP TABLE IF EXISTS qualidade_resultado;
CREATE TABLE qualidade_resultado (
    cd_validacao     TEXT PRIMARY KEY,
    ds_validacao     TEXT NOT NULL,
    nm_tabela        TEXT NOT NULL,
    qt_problemas     INTEGER NOT NULL,
    st_resultado     TEXT NOT NULL,
    ds_acao          TEXT NOT NULL
);

INSERT INTO qualidade_resultado

-- V01: a chave primária da apólice é única? (WINDOW FUNCTION: ROW_NUMBER)
SELECT 'V01', 'Chave primária nr_apolice única', 'silver_apolice',
       COUNT(*), CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERRO' END,
       'Bloquear promoção se houver duplicidade'
FROM (SELECT ROW_NUMBER() OVER (PARTITION BY nr_apolice ORDER BY dt_carga) AS rn
      FROM silver_apolice) WHERE rn > 1

UNION ALL
-- V02: duplicatas de carga na origem foram removidas pela deduplicação?
SELECT 'V02', 'Apólices duplicadas por reprocessamento na origem', 'bronze_tb_apol',
       (SELECT COUNT(*) FROM bronze_tb_apol) - (SELECT COUNT(*) FROM silver_apolice),
       'TRATADO', 'Deduplicado na silver (ROW_NUMBER, mantém a carga mais recente)'

UNION ALL
-- V03: integridade referencial — endosso aponta para apólice existente? (LEFT JOIN)
SELECT 'V03', 'Endosso sem apólice correspondente (órfão)', 'silver_endosso',
       COUNT(*), CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERTA' END,
       'Acionar time do sistema de emissão (SISEG)'
FROM silver_endosso e
LEFT JOIN silver_apolice a ON a.nr_apolice = e.nr_apolice
WHERE a.nr_apolice IS NULL

UNION ALL
-- V04: sinistro ocorrido fora da vigência (RN07)
SELECT 'V04', 'Sinistro com ocorrência fora da vigência', 'fato_sinistro',
       COUNT(*), CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERTA' END,
       'Excluído da sinistralidade; enviar à área de Sinistros para análise'
FROM fato_sinistro WHERE fl_ocorrencia_na_vigencia = 0

UNION ALL
-- V05: datas de vigência coerentes
SELECT 'V05', 'Fim de vigência anterior ou igual ao início', 'silver_apolice',
       COUNT(*), CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERRO' END,
       'Bloquear promoção'
FROM silver_apolice WHERE dt_fim_vigencia <= dt_inicio_vigencia

UNION ALL
-- V06: apólice cancelada precisa ter data de cancelamento
SELECT 'V06', 'Apólice CANCELADA sem data de cancelamento', 'silver_apolice',
       COUNT(*), CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERRO' END,
       'Bloquear promoção'
FROM silver_apolice WHERE st_apolice = 'CANCELADA' AND dt_cancelamento IS NULL

UNION ALL
-- V07: reconciliação origem x gold — nenhuma apólice pode "sumir" no caminho
SELECT 'V07', 'Reconciliação de quantidade silver x fato_premio', 'fato_premio',
       ABS((SELECT COUNT(*) FROM silver_apolice) - (SELECT COUNT(*) FROM fato_premio)),
       CASE WHEN (SELECT COUNT(*) FROM silver_apolice) = (SELECT COUNT(*) FROM fato_premio)
            THEN 'OK' ELSE 'ERRO' END,
       'Bloquear promoção'

UNION ALL
-- V08: teste da regra RN03 — na apólice cancelada, prêmio ganho = prêmio líquido final
SELECT 'V08', 'Regra RN03: cancelada com ganho diferente do líquido final', 'fato_premio',
       COUNT(*), CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERRO' END,
       'Revisar cálculo de restituição'
FROM fato_premio
WHERE st_apolice = 'CANCELADA'
  AND ABS(vl_premio_ganho - vl_premio_liquido_final) > 0.05

UNION ALL
-- V09: aviso do sinistro não pode ser anterior à ocorrência
SELECT 'V09', 'Aviso de sinistro anterior à ocorrência', 'fato_sinistro',
       COUNT(*), CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERRO' END,
       'Bloquear promoção'
FROM fato_sinistro WHERE qt_dias_ate_aviso < 0

UNION ALL
-- V10: percentuais de comissão e cosseguro entre 0 e 1
SELECT 'V10', 'Percentual fora do intervalo 0 a 1', 'silver_apolice / silver_corretor',
       (SELECT COUNT(*) FROM silver_apolice  WHERE pc_cosseguro_cedido NOT BETWEEN 0 AND 1)
     + (SELECT COUNT(*) FROM silver_corretor WHERE pc_comissao         NOT BETWEEN 0 AND 1),
       CASE WHEN (SELECT COUNT(*) FROM silver_apolice  WHERE pc_cosseguro_cedido NOT BETWEEN 0 AND 1)
               + (SELECT COUNT(*) FROM silver_corretor WHERE pc_comissao NOT BETWEEN 0 AND 1) = 0
            THEN 'OK' ELSE 'ERRO' END,
       'Bloquear promoção';
