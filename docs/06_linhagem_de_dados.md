# Linhagem de dados

> Caminho do dado desde o sistema de origem até o dashboard e o relatório regulatório. Exemplo: TB_SINI.VL_INDE + VL_RESV -> silver_sinistro -> fato_sinistro.vl_sinistro_retido -> vw_sinistralidade_produto.pc_sinistralidade -> Dashboard.

_Arquivo gerado por `src/gerar_documentacao.py` — edite os CSVs em `metadados/`._

## Fluxo tabela a tabela

| Origem | Destino | Camada do destino | O que acontece |
|---|---|---|---|
| SISEG.TB_APOL | bronze_tb_apol | BRONZE | Cópia fiel da tabela de apólices |
| SISEG.TB_ENDS | bronze_tb_ends | BRONZE | Cópia fiel da tabela de endossos |
| SISEG.TB_SINI | bronze_tb_sini | BRONZE | Cópia fiel da tabela de sinistros |
| SISEG.TB_PROD | bronze_tb_prod | BRONZE | Cópia fiel do cadastro de produtos |
| SISEG.TB_CORR | bronze_tb_corr | BRONZE | Cópia fiel do cadastro de corretores |
| bronze_tb_apol | silver_apolice | SILVER | De x Para + deduplicação |
| bronze_tb_ends | silver_endosso | SILVER | De x Para |
| bronze_tb_sini | silver_sinistro | SILVER | De x Para |
| bronze_tb_prod | silver_produto | SILVER | De x Para |
| bronze_tb_corr | silver_corretor | SILVER | De x Para |
| silver_produto | dim_produto | GOLD | Dimensão produto |
| silver_corretor | dim_corretor | GOLD | Dimensão corretor |
| silver_apolice | fato_premio | GOLD | RN01 a RN05 |
| silver_endosso | fato_premio | GOLD | RN01 (aumento/redução) |
| silver_corretor | fato_premio | GOLD | RN04 (% de comissão) |
| silver_sinistro | fato_sinistro | GOLD | RN05, RN06, RN07 |
| silver_apolice | fato_sinistro | GOLD | Vigência e cosseguro da apólice |
| fato_premio | vw_sinistralidade_produto | CONSUMO | RN06 |
| fato_sinistro | vw_sinistralidade_produto | CONSUMO | RN06 (apenas sinistros cobertos) |
| dim_produto | vw_sinistralidade_produto | CONSUMO | Nome do produto |
| fato_premio | vw_premio_mensal | CONSUMO | Evolução mensal (LAG, SUM OVER) |
| fato_premio | vw_ranking_corretor | CONSUMO | Ranking comercial (RANK) |
| dim_corretor | vw_ranking_corretor | CONSUMO | Nome do corretor |
| vw_sinistralidade_produto | Dashboard de Sinistralidade | DASHBOARD | Uso: Atuária |
| vw_premio_mensal | Dashboard de Sinistralidade | DASHBOARD | Uso: Atuária e Diretoria |
| vw_ranking_corretor | Dashboard de Sinistralidade | DASHBOARD | Uso: Comercial |
| vw_sinistralidade_produto | Relatório regulatório (ex.: FIP/SUSEP) | REGULATORIO | Prêmio ganho e sinistros retidos |
