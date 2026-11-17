# Visão geral

> Biblioteca de dados dos produtos de seguro: o que existe, o que significa, de onde vem e quem é o dono. Fonte única da verdade: pasta metadados/ no Git.

_Arquivo gerado por `src/gerar_documentacao.py` — edite os CSVs em `metadados/`._

## Tabelas documentadas

| Tabela | Camada | Descrição | Grão | Dono |
|---|---|---|---|---|
| silver_produto | SILVER | Cadastro de produtos de seguro com nomes padronizados. | 1 linha por produto | Atuária |
| silver_corretor | SILVER | Cadastro de corretores e percentual de comissão. | 1 linha por corretor | Comercial |
| silver_apolice | SILVER | Apólices do sistema de emissão, tipadas e sem duplicatas de carga. | 1 linha por apólice | Emissão |
| silver_endosso | SILVER | Endossos (alterações) das apólices. | 1 linha por endosso | Emissão |
| silver_sinistro | SILVER | Sinistros avisados, com indenização paga e reserva. | 1 linha por sinistro | Sinistros |
| dim_produto | GOLD | Dimensão de produtos para análises. | 1 linha por produto | Atuária |
| dim_corretor | GOLD | Dimensão de corretores para análises comerciais. | 1 linha por corretor | Comercial |
| fato_premio | GOLD | Fato de prêmios com as regras de prêmio emitido, ganho, restituição, comissão e cosseguro (RN01 a RN05). | 1 linha por apólice | Atuária |
| fato_sinistro | GOLD | Fato de sinistros com custo total, parte retida e cobertura pela vigência (RN05 a RN07). | 1 linha por sinistro | Sinistros |
| vw_sinistralidade_produto | CONSUMO | Sinistralidade por produto com ranking (RN06). | 1 linha por produto | Atuária |
| vw_premio_mensal | CONSUMO | Evolução mensal do prêmio emitido com variação e acumulado. | 1 linha por mês | Atuária |
| vw_ranking_corretor | CONSUMO | Ranking de corretores por prêmio líquido e comissão. | 1 linha por corretor | Comercial |

## Números da documentação

| Item | Quantidade |
|---|---|
| Tabelas | 12 |
| Colunas no dicionário | 76 |
| Termos no glossário | 20 |
| Regras de negócio | 7 |
| Mapeamentos De x Para | 28 |
