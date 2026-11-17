# Dicionário de dados

> Todas as colunas das camadas Silver, Gold e Consumo: tipo, chaves, significado, classificação (LGPD) e dono. Validado automaticamente contra o banco a cada mudança.

_Arquivo gerado por `src/gerar_documentacao.py` — edite os CSVs em `metadados/`._

## silver_apolice (SILVER)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| nr_apolice | TEXT | PK |  | Número da apólice, identificador único do contrato de seguro. | Apólice |  | INTERNA | APROVADO |
| cd_produto | INTEGER | FK | silver_produto.cd_produto | Código do produto de seguro (ex.: 103 = Odonto Empresarial). | Produto |  | INTERNA | APROVADO |
| cd_corretor | INTEGER | FK | silver_corretor.cd_corretor | Código do corretor que intermediou a venda da apólice. | Corretor |  | INTERNA | APROVADO |
| cd_segurado | TEXT |  |  | Código do segurado (pessoa/empresa protegida). Dado pessoal: acesso restrito (LGPD). | Segurado |  | PESSOAL | APROVADO |
| dt_inicio_vigencia | DATE |  |  | Data em que a cobertura da apólice começa a valer. | Vigência |  | INTERNA | APROVADO |
| dt_fim_vigencia | DATE |  |  | Data em que a cobertura da apólice termina. | Vigência |  | INTERNA | APROVADO |
| vl_premio_liquido | REAL |  |  | Prêmio original da apólice em R$, sem IOF, na emissão. | Prêmio |  | CONFIDENCIAL | APROVADO |
| st_apolice | TEXT |  |  | Situação da apólice: ATIVA ou CANCELADA. | Cancelamento | RN03 | INTERNA | APROVADO |
| dt_cancelamento | DATE |  |  | Data do cancelamento. Vazio quando a apólice não foi cancelada. | Cancelamento | RN03 | INTERNA | APROVADO |
| pc_cosseguro_cedido | REAL |  |  | Parcela do risco (0 a 1) dividida com outra seguradora (congênere). | Cosseguro | RN05 | CONFIDENCIAL | APROVADO |
| dt_carga | DATE |  |  | Data em que o registro foi carregado do sistema de origem. Usada para deduplicar. | Data de carga |  | INTERNA | APROVADO |

## silver_corretor (SILVER)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| cd_corretor | INTEGER | PK |  | Código do corretor que intermediou a venda da apólice. | Corretor |  | INTERNA | APROVADO |
| nm_corretor | TEXT |  |  | Razão social da corretora. | Corretor |  | INTERNA | APROVADO |
| pc_comissao | REAL |  |  | Percentual de comissão (corretagem) pago ao corretor sobre o prêmio, de 0 a 1. | Comissão | RN04 | CONFIDENCIAL | APROVADO |

## silver_endosso (SILVER)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| nr_endosso | TEXT | PK |  | Número do endosso, identificador único da alteração na apólice. | Endosso |  | INTERNA | APROVADO |
| nr_apolice | TEXT | FK | silver_apolice.nr_apolice | Número da apólice, identificador único do contrato de seguro. | Apólice |  | INTERNA | APROVADO |
| tp_endosso | TEXT |  |  | Tipo de endosso: AUMENTO, REDUCAO ou CANCELAMENTO. | Endosso | RN01 | INTERNA | APROVADO |
| dt_emissao | DATE |  |  | Data de emissão do endosso. | Endosso |  | INTERNA | APROVADO |
| vl_premio_endosso | REAL |  |  | Variação de prêmio gerada pelo endosso em R$ (negativo na redução). | Endosso | RN01 | CONFIDENCIAL | APROVADO |

## silver_produto (SILVER)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| cd_produto | INTEGER | PK |  | Código do produto de seguro (ex.: 103 = Odonto Empresarial). | Produto |  | INTERNA | APROVADO |
| ds_produto | TEXT |  |  | Nome comercial do produto de seguro. | Produto |  | PUBLICA | APROVADO |

## silver_sinistro (SILVER)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| nr_sinistro | TEXT | PK |  | Número do sinistro, identificador único do evento indenizável. | Sinistro |  | INTERNA | APROVADO |
| nr_apolice | TEXT | FK | silver_apolice.nr_apolice | Número da apólice, identificador único do contrato de seguro. | Apólice |  | INTERNA | APROVADO |
| dt_ocorrencia | DATE |  |  | Data em que o evento (sinistro) aconteceu. | Sinistro | RN07 | INTERNA | APROVADO |
| dt_aviso | DATE |  |  | Data em que a seguradora foi avisada do sinistro. | Aviso de sinistro |  | INTERNA | APROVADO |
| vl_indenizacao_paga | REAL |  |  | Valor já pago ao segurado/beneficiário em R$. | Indenização | RN06 | CONFIDENCIAL | APROVADO |
| vl_reserva_sinistro | REAL |  |  | Valor provisionado para sinistros avisados e ainda não pagos em R$. | Reserva de sinistro | RN06 | CONFIDENCIAL | APROVADO |
| st_sinistro | TEXT |  |  | Situação do sinistro: PAGO ou ABERTO. | Sinistro |  | INTERNA | APROVADO |

## dim_corretor (GOLD)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| cd_corretor | INTEGER | PK |  | Código do corretor que intermediou a venda da apólice. | Corretor |  | INTERNA | APROVADO |
| nm_corretor | TEXT |  |  | Razão social da corretora. | Corretor |  | INTERNA | APROVADO |
| pc_comissao | REAL |  |  | Percentual de comissão (corretagem) pago ao corretor sobre o prêmio, de 0 a 1. | Comissão | RN04 | CONFIDENCIAL | APROVADO |

## dim_produto (GOLD)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| cd_produto | INTEGER | PK |  | Código do produto de seguro (ex.: 103 = Odonto Empresarial). | Produto |  | INTERNA | APROVADO |
| ds_produto | TEXT |  |  | Nome comercial do produto de seguro. | Produto |  | PUBLICA | APROVADO |

## fato_premio (GOLD)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| nr_apolice | TEXT | PK |  | Número da apólice, identificador único do contrato de seguro. | Apólice |  | INTERNA | APROVADO |
| cd_produto | INTEGER | FK | dim_produto.cd_produto | Código do produto de seguro (ex.: 103 = Odonto Empresarial). | Produto |  | INTERNA | APROVADO |
| cd_corretor | INTEGER | FK | dim_corretor.cd_corretor | Código do corretor que intermediou a venda da apólice. | Corretor |  | INTERNA | APROVADO |
| dt_inicio_vigencia | DATE |  |  | Data em que a cobertura da apólice começa a valer. | Vigência |  | INTERNA | APROVADO |
| st_apolice | TEXT |  |  | Situação da apólice: ATIVA ou CANCELADA. | Cancelamento | RN03 | INTERNA | APROVADO |
| qt_dias_vigencia | INTEGER |  |  | Quantidade de dias entre início e fim de vigência. | Vigência | RN02 | INTERNA | APROVADO |
| qt_dias_decorridos | INTEGER |  |  | Dias de exposição ao risco já transcorridos até a data base, cancelamento ou fim da vigência. | Prêmio ganho | RN02 | INTERNA | APROVADO |
| vl_premio_emitido | REAL |  |  | Prêmio original + endossos de aumento/redução, em R$. | Prêmio emitido | RN01 | CONFIDENCIAL | APROVADO |
| vl_premio_ganho | REAL |  |  | Parte do prêmio já "ganha" pela seguradora, proporcional aos dias decorridos (pro rata die). | Prêmio ganho | RN02 | CONFIDENCIAL | APROVADO |
| vl_restituicao_cancelamento | REAL |  |  | Prêmio devolvido no cancelamento, referente aos dias não decorridos (valor negativo). | Restituição de prêmio | RN03 | CONFIDENCIAL | APROVADO |
| vl_premio_liquido_final | REAL |  |  | Prêmio emitido após a restituição de cancelamento, em R$. | Prêmio emitido | RN03 | CONFIDENCIAL | APROVADO |
| vl_comissao | REAL |  |  | Comissão devida ao corretor, em R$. | Comissão | RN04 | CONFIDENCIAL | APROVADO |
| vl_premio_cedido_cosseguro | REAL |  |  | Parte do prêmio que pertence à congênere no cosseguro, em R$. | Cosseguro | RN05 | CONFIDENCIAL | APROVADO |
| vl_premio_ganho_retido | REAL |  |  | Prêmio ganho que fica com a seguradora após o cosseguro, em R$. | Prêmio retido | RN05 | CONFIDENCIAL | APROVADO |

## fato_sinistro (GOLD)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| nr_sinistro | TEXT | PK |  | Número do sinistro, identificador único do evento indenizável. | Sinistro |  | INTERNA | APROVADO |
| nr_apolice | TEXT | FK | fato_premio.nr_apolice | Número da apólice, identificador único do contrato de seguro. | Apólice |  | INTERNA | APROVADO |
| cd_produto | INTEGER | FK | dim_produto.cd_produto | Código do produto de seguro (ex.: 103 = Odonto Empresarial). | Produto |  | INTERNA | APROVADO |
| dt_ocorrencia | DATE |  |  | Data em que o evento (sinistro) aconteceu. | Sinistro | RN07 | INTERNA | APROVADO |
| qt_dias_ate_aviso | INTEGER |  |  | Dias entre a ocorrência e o aviso do sinistro. | Aviso de sinistro |  | INTERNA | APROVADO |
| st_sinistro | TEXT |  |  | Situação do sinistro: PAGO ou ABERTO. | Sinistro |  | INTERNA | APROVADO |
| vl_sinistro_total | REAL |  |  | Indenização paga + reserva, em R$ (custo total do sinistro). | Sinistro | RN06 | CONFIDENCIAL | APROVADO |
| vl_sinistro_retido | REAL |  |  | Custo do sinistro que fica com a seguradora após o cosseguro, em R$. | Sinistro | RN05 | CONFIDENCIAL | APROVADO |
| fl_ocorrencia_na_vigencia | INTEGER |  |  | 1 = sinistro ocorreu dentro da vigência (coberto), 0 = fora (não entra na sinistralidade). | Vigência | RN07 | INTERNA | APROVADO |

## vw_premio_mensal (CONSUMO)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| aa_mes | TEXT |  |  | Ano-mês de início de vigência (AAAA-MM). | Vigência |  | INTERNA | APROVADO |
| qt_apolices | INTEGER |  |  | Quantidade de apólices. | Apólice |  | INTERNA | APROVADO |
| vl_premio_emitido | REAL |  |  | Prêmio original + endossos de aumento/redução, em R$. | Prêmio emitido | RN01 | CONFIDENCIAL | APROVADO |
| vl_mes_anterior | REAL |  |  | Prêmio emitido do mês anterior (função LAG). | Prêmio emitido | RN01 | CONFIDENCIAL | APROVADO |
| pc_variacao_mes | REAL |  |  | Variação do prêmio emitido contra o mês anterior. | Prêmio emitido | RN01 | INTERNA | APROVADO |
| vl_acumulado | REAL |  |  | Prêmio emitido acumulado desde o primeiro mês (SUM OVER). | Prêmio emitido | RN01 | CONFIDENCIAL | APROVADO |

## vw_ranking_corretor (CONSUMO)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| nm_corretor | TEXT |  |  | Razão social da corretora. | Corretor |  | INTERNA | APROVADO |
| qt_apolices | INTEGER |  |  | Quantidade de apólices. | Apólice |  | INTERNA | APROVADO |
| vl_premio_liquido_final | REAL |  |  | Prêmio emitido após a restituição de cancelamento, em R$. | Prêmio emitido | RN03 | CONFIDENCIAL | APROVADO |
| vl_comissao | REAL |  |  | Comissão devida ao corretor, em R$. | Comissão | RN04 | CONFIDENCIAL | APROVADO |
| pc_participacao | REAL |  |  | Participação do corretor no prêmio líquido total da carteira. | Corretor | RN04 | INTERNA | APROVADO |
| nr_ranking | INTEGER |  |  | Posição do corretor no ranking de prêmio líquido (1 = maior). | Corretor |  | INTERNA | APROVADO |

## vw_sinistralidade_produto (CONSUMO)

| Coluna | Tipo | Chave | Referência | Descrição | Termo | Regra | Classificação | Status |
|---|---|---|---|---|---|---|---|---|
| ds_produto | TEXT |  |  | Nome comercial do produto de seguro. | Produto |  | PUBLICA | APROVADO |
| qt_apolices | INTEGER |  |  | Quantidade de apólices. | Apólice |  | INTERNA | APROVADO |
| qt_sinistros | INTEGER |  |  | Quantidade de sinistros cobertos. | Sinistro | RN07 | INTERNA | APROVADO |
| vl_premio_emitido | REAL |  |  | Prêmio original + endossos de aumento/redução, em R$. | Prêmio emitido | RN01 | CONFIDENCIAL | APROVADO |
| vl_premio_ganho_retido | REAL |  |  | Prêmio ganho que fica com a seguradora após o cosseguro, em R$. | Prêmio retido | RN05 | CONFIDENCIAL | APROVADO |
| vl_sinistro_retido | REAL |  |  | Custo do sinistro que fica com a seguradora após o cosseguro, em R$. | Sinistro | RN05 | CONFIDENCIAL | APROVADO |
| pc_sinistralidade | REAL |  |  | Sinistralidade: custo de sinistros retido dividido pelo prêmio ganho retido (0,65 = 65%). | Sinistralidade | RN06 | CONFIDENCIAL | APROVADO |
| nr_ranking_sinistralidade | INTEGER |  |  | Posição do produto no ranking de sinistralidade (1 = maior). | Sinistralidade | RN06 | INTERNA | APROVADO |
