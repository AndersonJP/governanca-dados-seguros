-- Gerado por src/gerar_documentacao.py a partir de metadados/.
-- Rode no Databricks SQL para publicar descrições e tags no Unity Catalog.
-- (Views da camada CONSUMO recebem comentários no próprio CREATE VIEW.)

-- silver_produto
COMMENT ON TABLE seguros.silver.silver_produto IS 'Cadastro de produtos de seguro com nomes padronizados. Grão: 1 linha por produto.';
ALTER TABLE seguros.silver.silver_produto SET TAGS ('dono_dado' = 'Atuária', 'camada' = 'SILVER');
ALTER TABLE seguros.silver.silver_produto ALTER COLUMN cd_produto COMMENT 'Código do produto de seguro (ex.: 103 = Odonto Empresarial).';
ALTER TABLE seguros.silver.silver_produto ALTER COLUMN cd_produto SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_produto ALTER COLUMN ds_produto COMMENT 'Nome comercial do produto de seguro.';
ALTER TABLE seguros.silver.silver_produto ALTER COLUMN ds_produto SET TAGS ('classificacao' = 'PUBLICA');

-- silver_corretor
COMMENT ON TABLE seguros.silver.silver_corretor IS 'Cadastro de corretores e percentual de comissão. Grão: 1 linha por corretor.';
ALTER TABLE seguros.silver.silver_corretor SET TAGS ('dono_dado' = 'Comercial', 'camada' = 'SILVER');
ALTER TABLE seguros.silver.silver_corretor ALTER COLUMN cd_corretor COMMENT 'Código do corretor que intermediou a venda da apólice.';
ALTER TABLE seguros.silver.silver_corretor ALTER COLUMN cd_corretor SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_corretor ALTER COLUMN nm_corretor COMMENT 'Razão social da corretora.';
ALTER TABLE seguros.silver.silver_corretor ALTER COLUMN nm_corretor SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_corretor ALTER COLUMN pc_comissao COMMENT 'Percentual de comissão (corretagem) pago ao corretor sobre o prêmio, de 0 a 1.';
ALTER TABLE seguros.silver.silver_corretor ALTER COLUMN pc_comissao SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN04');

-- silver_apolice
COMMENT ON TABLE seguros.silver.silver_apolice IS 'Apólices do sistema de emissão, tipadas e sem duplicatas de carga. Grão: 1 linha por apólice.';
ALTER TABLE seguros.silver.silver_apolice SET TAGS ('dono_dado' = 'Emissão', 'camada' = 'SILVER');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN nr_apolice COMMENT 'Número da apólice, identificador único do contrato de seguro.';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN nr_apolice SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN cd_produto COMMENT 'Código do produto de seguro (ex.: 103 = Odonto Empresarial).';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN cd_produto SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN cd_corretor COMMENT 'Código do corretor que intermediou a venda da apólice.';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN cd_corretor SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN cd_segurado COMMENT 'Código do segurado (pessoa/empresa protegida). Dado pessoal: acesso restrito (LGPD).';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN cd_segurado SET TAGS ('classificacao' = 'PESSOAL');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN dt_inicio_vigencia COMMENT 'Data em que a cobertura da apólice começa a valer.';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN dt_inicio_vigencia SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN dt_fim_vigencia COMMENT 'Data em que a cobertura da apólice termina.';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN dt_fim_vigencia SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN vl_premio_liquido COMMENT 'Prêmio original da apólice em R$, sem IOF, na emissão.';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN vl_premio_liquido SET TAGS ('classificacao' = 'CONFIDENCIAL');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN st_apolice COMMENT 'Situação da apólice: ATIVA ou CANCELADA.';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN st_apolice SET TAGS ('classificacao' = 'INTERNA', 'regra_negocio' = 'RN03');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN dt_cancelamento COMMENT 'Data do cancelamento. Vazio quando a apólice não foi cancelada.';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN dt_cancelamento SET TAGS ('classificacao' = 'INTERNA', 'regra_negocio' = 'RN03');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN pc_cosseguro_cedido COMMENT 'Parcela do risco (0 a 1) dividida com outra seguradora (congênere).';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN pc_cosseguro_cedido SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN05');
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN dt_carga COMMENT 'Data em que o registro foi carregado do sistema de origem. Usada para deduplicar.';
ALTER TABLE seguros.silver.silver_apolice ALTER COLUMN dt_carga SET TAGS ('classificacao' = 'INTERNA');

-- silver_endosso
COMMENT ON TABLE seguros.silver.silver_endosso IS 'Endossos (alterações) das apólices. Grão: 1 linha por endosso.';
ALTER TABLE seguros.silver.silver_endosso SET TAGS ('dono_dado' = 'Emissão', 'camada' = 'SILVER');
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN nr_endosso COMMENT 'Número do endosso, identificador único da alteração na apólice.';
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN nr_endosso SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN nr_apolice COMMENT 'Número da apólice, identificador único do contrato de seguro.';
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN nr_apolice SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN tp_endosso COMMENT 'Tipo de endosso: AUMENTO, REDUCAO ou CANCELAMENTO.';
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN tp_endosso SET TAGS ('classificacao' = 'INTERNA', 'regra_negocio' = 'RN01');
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN dt_emissao COMMENT 'Data de emissão do endosso.';
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN dt_emissao SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN vl_premio_endosso COMMENT 'Variação de prêmio gerada pelo endosso em R$ (negativo na redução).';
ALTER TABLE seguros.silver.silver_endosso ALTER COLUMN vl_premio_endosso SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN01');

-- silver_sinistro
COMMENT ON TABLE seguros.silver.silver_sinistro IS 'Sinistros avisados, com indenização paga e reserva. Grão: 1 linha por sinistro.';
ALTER TABLE seguros.silver.silver_sinistro SET TAGS ('dono_dado' = 'Sinistros', 'camada' = 'SILVER');
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN nr_sinistro COMMENT 'Número do sinistro, identificador único do evento indenizável.';
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN nr_sinistro SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN nr_apolice COMMENT 'Número da apólice, identificador único do contrato de seguro.';
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN nr_apolice SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN dt_ocorrencia COMMENT 'Data em que o evento (sinistro) aconteceu.';
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN dt_ocorrencia SET TAGS ('classificacao' = 'INTERNA', 'regra_negocio' = 'RN07');
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN dt_aviso COMMENT 'Data em que a seguradora foi avisada do sinistro.';
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN dt_aviso SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN vl_indenizacao_paga COMMENT 'Valor já pago ao segurado/beneficiário em R$.';
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN vl_indenizacao_paga SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN06');
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN vl_reserva_sinistro COMMENT 'Valor provisionado para sinistros avisados e ainda não pagos em R$.';
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN vl_reserva_sinistro SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN06');
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN st_sinistro COMMENT 'Situação do sinistro: PAGO ou ABERTO.';
ALTER TABLE seguros.silver.silver_sinistro ALTER COLUMN st_sinistro SET TAGS ('classificacao' = 'INTERNA');

-- dim_produto
COMMENT ON TABLE seguros.gold.dim_produto IS 'Dimensão de produtos para análises. Grão: 1 linha por produto.';
ALTER TABLE seguros.gold.dim_produto SET TAGS ('dono_dado' = 'Atuária', 'camada' = 'GOLD');
ALTER TABLE seguros.gold.dim_produto ALTER COLUMN cd_produto COMMENT 'Código do produto de seguro (ex.: 103 = Odonto Empresarial).';
ALTER TABLE seguros.gold.dim_produto ALTER COLUMN cd_produto SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.dim_produto ALTER COLUMN ds_produto COMMENT 'Nome comercial do produto de seguro.';
ALTER TABLE seguros.gold.dim_produto ALTER COLUMN ds_produto SET TAGS ('classificacao' = 'PUBLICA');

-- dim_corretor
COMMENT ON TABLE seguros.gold.dim_corretor IS 'Dimensão de corretores para análises comerciais. Grão: 1 linha por corretor.';
ALTER TABLE seguros.gold.dim_corretor SET TAGS ('dono_dado' = 'Comercial', 'camada' = 'GOLD');
ALTER TABLE seguros.gold.dim_corretor ALTER COLUMN cd_corretor COMMENT 'Código do corretor que intermediou a venda da apólice.';
ALTER TABLE seguros.gold.dim_corretor ALTER COLUMN cd_corretor SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.dim_corretor ALTER COLUMN nm_corretor COMMENT 'Razão social da corretora.';
ALTER TABLE seguros.gold.dim_corretor ALTER COLUMN nm_corretor SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.dim_corretor ALTER COLUMN pc_comissao COMMENT 'Percentual de comissão (corretagem) pago ao corretor sobre o prêmio, de 0 a 1.';
ALTER TABLE seguros.gold.dim_corretor ALTER COLUMN pc_comissao SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN04');

-- fato_premio
COMMENT ON TABLE seguros.gold.fato_premio IS 'Fato de prêmios com as regras de prêmio emitido, ganho, restituição, comissão e cosseguro (RN01 a RN05). Grão: 1 linha por apólice.';
ALTER TABLE seguros.gold.fato_premio SET TAGS ('dono_dado' = 'Atuária', 'camada' = 'GOLD');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN nr_apolice COMMENT 'Número da apólice, identificador único do contrato de seguro.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN nr_apolice SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN cd_produto COMMENT 'Código do produto de seguro (ex.: 103 = Odonto Empresarial).';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN cd_produto SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN cd_corretor COMMENT 'Código do corretor que intermediou a venda da apólice.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN cd_corretor SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN dt_inicio_vigencia COMMENT 'Data em que a cobertura da apólice começa a valer.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN dt_inicio_vigencia SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN st_apolice COMMENT 'Situação da apólice: ATIVA ou CANCELADA.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN st_apolice SET TAGS ('classificacao' = 'INTERNA', 'regra_negocio' = 'RN03');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN qt_dias_vigencia COMMENT 'Quantidade de dias entre início e fim de vigência.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN qt_dias_vigencia SET TAGS ('classificacao' = 'INTERNA', 'regra_negocio' = 'RN02');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN qt_dias_decorridos COMMENT 'Dias de exposição ao risco já transcorridos até a data base, cancelamento ou fim da vigência.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN qt_dias_decorridos SET TAGS ('classificacao' = 'INTERNA', 'regra_negocio' = 'RN02');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_emitido COMMENT 'Prêmio original + endossos de aumento/redução, em R$.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_emitido SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN01');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_ganho COMMENT 'Parte do prêmio já "ganha" pela seguradora, proporcional aos dias decorridos (pro rata die).';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_ganho SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN02');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_restituicao_cancelamento COMMENT 'Prêmio devolvido no cancelamento, referente aos dias não decorridos (valor negativo).';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_restituicao_cancelamento SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN03');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_liquido_final COMMENT 'Prêmio emitido após a restituição de cancelamento, em R$.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_liquido_final SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN03');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_comissao COMMENT 'Comissão devida ao corretor, em R$.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_comissao SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN04');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_cedido_cosseguro COMMENT 'Parte do prêmio que pertence à congênere no cosseguro, em R$.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_cedido_cosseguro SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN05');
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_ganho_retido COMMENT 'Prêmio ganho que fica com a seguradora após o cosseguro, em R$.';
ALTER TABLE seguros.gold.fato_premio ALTER COLUMN vl_premio_ganho_retido SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN05');

-- fato_sinistro
COMMENT ON TABLE seguros.gold.fato_sinistro IS 'Fato de sinistros com custo total, parte retida e cobertura pela vigência (RN05 a RN07). Grão: 1 linha por sinistro.';
ALTER TABLE seguros.gold.fato_sinistro SET TAGS ('dono_dado' = 'Sinistros', 'camada' = 'GOLD');
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN nr_sinistro COMMENT 'Número do sinistro, identificador único do evento indenizável.';
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN nr_sinistro SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN nr_apolice COMMENT 'Número da apólice, identificador único do contrato de seguro.';
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN nr_apolice SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN cd_produto COMMENT 'Código do produto de seguro (ex.: 103 = Odonto Empresarial).';
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN cd_produto SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN dt_ocorrencia COMMENT 'Data em que o evento (sinistro) aconteceu.';
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN dt_ocorrencia SET TAGS ('classificacao' = 'INTERNA', 'regra_negocio' = 'RN07');
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN qt_dias_ate_aviso COMMENT 'Dias entre a ocorrência e o aviso do sinistro.';
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN qt_dias_ate_aviso SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN st_sinistro COMMENT 'Situação do sinistro: PAGO ou ABERTO.';
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN st_sinistro SET TAGS ('classificacao' = 'INTERNA');
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN vl_sinistro_total COMMENT 'Indenização paga + reserva, em R$ (custo total do sinistro).';
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN vl_sinistro_total SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN06');
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN vl_sinistro_retido COMMENT 'Custo do sinistro que fica com a seguradora após o cosseguro, em R$.';
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN vl_sinistro_retido SET TAGS ('classificacao' = 'CONFIDENCIAL', 'regra_negocio' = 'RN05');
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN fl_ocorrencia_na_vigencia COMMENT '1 = sinistro ocorreu dentro da vigência (coberto), 0 = fora (não entra na sinistralidade).';
ALTER TABLE seguros.gold.fato_sinistro ALTER COLUMN fl_ocorrencia_na_vigencia SET TAGS ('classificacao' = 'INTERNA', 'regra_negocio' = 'RN07');
