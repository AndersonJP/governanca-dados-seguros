# Qualidade de dados

> Resultado da última execução das validações (sql/04_validacoes.sql).

_Arquivo gerado por `src/gerar_documentacao.py` — edite os CSVs em `metadados/`._

## Validações

| Código | Validação | Tabela | Registros | Resultado | Ação |
|---|---|---|---|---|---|
| V01 | Chave primária nr_apolice única | silver_apolice | 0 | OK | Bloquear promoção se houver duplicidade |
| V02 | Apólices duplicadas por reprocessamento na origem | bronze_tb_apol | 12 | TRATADO | Deduplicado na silver (ROW_NUMBER, mantém a carga mais recente) |
| V03 | Endosso sem apólice correspondente (órfão) | silver_endosso | 1 | ALERTA | Acionar time do sistema de emissão (SISEG) |
| V04 | Sinistro com ocorrência fora da vigência | fato_sinistro | 3 | ALERTA | Excluído da sinistralidade; enviar à área de Sinistros para análise |
| V05 | Fim de vigência anterior ou igual ao início | silver_apolice | 0 | OK | Bloquear promoção |
| V06 | Apólice CANCELADA sem data de cancelamento | silver_apolice | 0 | OK | Bloquear promoção |
| V07 | Reconciliação de quantidade silver x fato_premio | fato_premio | 0 | OK | Bloquear promoção |
| V08 | Regra RN03: cancelada com ganho diferente do líquido final | fato_premio | 0 | OK | Revisar cálculo de restituição |
| V09 | Aviso de sinistro anterior à ocorrência | fato_sinistro | 0 | OK | Bloquear promoção |
| V10 | Percentual fora do intervalo 0 a 1 | silver_apolice / silver_corretor | 0 | OK | Bloquear promoção |
