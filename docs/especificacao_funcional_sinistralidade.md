# Especificação funcional — Painel de Sinistralidade por Produto

| Item | Conteúdo |
|---|---|
| Solicitante | Atuária |
| Usuários | Atuária, Sinistros, Comercial, Diretoria |
| Versão | 1.0 |
| Status | Aprovada |

## 1. Necessidade de negócio (o "porquê")
A Atuária precisa acompanhar, por produto, **quanto do prêmio ganho está sendo consumido por sinistros**,
para revisar preços e identificar produtos deficitários. Hoje cada área calcula de um jeito
(algumas usam prêmio emitido, outras não descontam o cosseguro), e os números não batem entre as áreas.

## 2. Perguntas que o painel responde
1. Qual a sinistralidade de cada produto na data base?
2. Qual produto tem a maior sinistralidade (ranking)?
3. Como evolui o prêmio emitido mês a mês?
4. Quais corretores concentram a produção e quanto recebem de comissão?
5. Os dados são confiáveis? (resultado das validações de qualidade)

## 3. Indicadores e regras
| Indicador | Definição | Regra | Campo |
|---|---|---|---|
| Prêmio emitido | Prêmio original + endossos de aumento e redução | RN01 | `fato_premio.vl_premio_emitido` |
| Prêmio ganho retido | Prêmio proporcional aos dias decorridos, sem a parte cedida em cosseguro | RN02, RN05 | `fato_premio.vl_premio_ganho_retido` |
| Sinistro retido | (Indenização paga + reserva) sem a parte cedida | RN05, RN06 | `fato_sinistro.vl_sinistro_retido` |
| Sinistralidade | Sinistro retido ÷ prêmio ganho retido | RN06 | `vw_sinistralidade_produto.pc_sinistralidade` |
| Comissão | Prêmio líquido final × % do corretor | RN04 | `fato_premio.vl_comissao` |

## 4. Critérios de aceite
- [x] Sinistralidade calculada sobre **prêmio ganho**, não sobre prêmio emitido.
- [x] Prêmio e sinistro sempre **retidos** (cosseguro descontado dos dois lados).
- [x] Sinistros fora da vigência **não entram** no indicador e são listados para a área de Sinistros (RN07 / V04).
- [x] Apólices duplicadas na origem não podem inflar o prêmio (V02).
- [x] Todo campo exibido está no Dicionário de Dados com dono e classificação.
- [x] O dado pessoal `cd_segurado` **não** aparece no painel (LGPD).

## 5. Premissas e limitações (declaradas para a área de negócio)
- Data base de fechamento: 31/10/2026 (`param_execucao`).
- Endossos de aumento/redução são distribuídos por toda a vigência (simplificação).
- Valores sem IOF. Resseguro fora do escopo desta versão.

## 6. Linhagem do indicador principal
`SISEG.TB_SINI.VL_INDE + VL_RESV` → `silver_sinistro` → `fato_sinistro.vl_sinistro_retido`
→ `vw_sinistralidade_produto.pc_sinistralidade` → **Dashboard** e relatório regulatório.
