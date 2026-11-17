# De x Para (origem -> modelo)

> Mapeamento campo a campo do sistema de emissão SISEG para a camada Silver.

_Arquivo gerado por `src/gerar_documentacao.py` — edite os CSVs em `metadados/`._

## Mapeamento

| Tabela origem | Coluna origem | Tabela destino | Coluna destino | Tipo destino | Transformação |
|---|---|---|---|---|---|
| TB_PROD | CD_PROD | silver_produto | cd_produto | INTEGER | Conversão para inteiro |
| TB_PROD | DS_PROD | silver_produto | ds_produto | TEXT | Cópia direta |
| TB_CORR | CD_CORR | silver_corretor | cd_corretor | INTEGER | Conversão para inteiro |
| TB_CORR | NM_CORR | silver_corretor | nm_corretor | TEXT | Cópia direta |
| TB_CORR | PC_COMS | silver_corretor | pc_comissao | REAL | Conversão para decimal (0 a 1) |
| TB_APOL | NR_APOL | silver_apolice | nr_apolice | TEXT | Cópia direta, com deduplicação por ROW_NUMBER mantendo a maior DT_CARGA |
| TB_APOL | CD_PROD | silver_apolice | cd_produto | INTEGER | Conversão para inteiro |
| TB_APOL | CD_CORR | silver_apolice | cd_corretor | INTEGER | Conversão para inteiro |
| TB_APOL | CD_SEGD | silver_apolice | cd_segurado | TEXT | Cópia direta (dado pessoal: classificar como PESSOAL) |
| TB_APOL | DT_INI_VIG | silver_apolice | dt_inicio_vigencia | DATE | Conversão para data |
| TB_APOL | DT_FIM_VIG | silver_apolice | dt_fim_vigencia | DATE | Conversão para data |
| TB_APOL | VL_PRM_LIQ | silver_apolice | vl_premio_liquido | REAL | Conversão para decimal |
| TB_APOL | ST_APOL | silver_apolice | st_apolice | TEXT | Decodificação: A = ATIVA, C = CANCELADA |
| TB_APOL | DT_CANC | silver_apolice | dt_cancelamento | DATE | Texto vazio vira NULL |
| TB_APOL | PC_COSS_CED | silver_apolice | pc_cosseguro_cedido | REAL | Conversão para decimal (0 a 1) |
| TB_APOL | DT_CARGA | silver_apolice | dt_carga | DATE | Conversão para data |
| TB_ENDS | NR_ENDS | silver_endosso | nr_endosso | TEXT | Cópia direta |
| TB_ENDS | NR_APOL | silver_endosso | nr_apolice | TEXT | Cópia direta |
| TB_ENDS | TP_ENDS | silver_endosso | tp_endosso | TEXT | Decodificação: AUM = AUMENTO, RED = REDUCAO, CAN = CANCELAMENTO |
| TB_ENDS | DT_EMIS | silver_endosso | dt_emissao | DATE | Conversão para data |
| TB_ENDS | VL_PRM_ENDS | silver_endosso | vl_premio_endosso | REAL | Conversão para decimal |
| TB_SINI | NR_SINI | silver_sinistro | nr_sinistro | TEXT | Cópia direta |
| TB_SINI | NR_APOL | silver_sinistro | nr_apolice | TEXT | Cópia direta |
| TB_SINI | DT_OCOR | silver_sinistro | dt_ocorrencia | DATE | Conversão para data |
| TB_SINI | DT_AVIS | silver_sinistro | dt_aviso | DATE | Conversão para data |
| TB_SINI | VL_INDE | silver_sinistro | vl_indenizacao_paga | REAL | Conversão para decimal |
| TB_SINI | VL_RESV | silver_sinistro | vl_reserva_sinistro | REAL | Conversão para decimal |
| TB_SINI | ST_SINI | silver_sinistro | st_sinistro | TEXT | Cópia direta |
