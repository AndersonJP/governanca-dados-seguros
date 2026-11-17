"""
ETAPA 9 — DASHBOARD HTML (consumo final do dado)
=================================================

Gera dashboard/index.html: um arquivo único, sem dependências externas,
que abre em qualquer navegador (duplo clique) e pode ser publicado no
GitHub Pages.

Diferencial de governança: cada gráfico mostra a REGRA (RNxx) e a FONTE
(view/tabela) de onde o número vem — o usuário de negócio sabe exatamente
o que está vendo. O dicionário de dados também fica pesquisável no painel.

Uso: python src/gerar_dashboard.py
"""

import csv
import json
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BANCO = RAIZ / "data" / "seguros.db"


def consultar(con, sql):
    con.row_factory = sqlite3.Row
    return [dict(r) for r in con.execute(sql)]


def ler_csv(nome):
    with open(RAIZ / "metadados" / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def coletar_dados():
    con = sqlite3.connect(BANCO)
    kpi = consultar(con, """
        SELECT (SELECT dt_base FROM param_execucao)                        AS dt_base,
               (SELECT COUNT(*) FROM fato_premio)                          AS qt_apolices,
               (SELECT SUM(vl_premio_emitido) FROM fato_premio)            AS vl_premio_emitido,
               (SELECT SUM(vl_premio_ganho_retido) FROM fato_premio)       AS vl_premio_ganho_retido,
               (SELECT SUM(vl_comissao) FROM fato_premio)                  AS vl_comissao,
               (SELECT SUM(vl_sinistro_retido) FROM fato_sinistro
                 WHERE fl_ocorrencia_na_vigencia = 1)                      AS vl_sinistro_retido
    """)[0]
    kpi["pc_sinistralidade"] = kpi["vl_sinistro_retido"] / kpi["vl_premio_ganho_retido"]

    governanca = json.loads((RAIZ / "data" / "relatorio_governanca.json").read_text(encoding="utf-8"))
    return {
        "kpi": kpi,
        "sinistralidade": consultar(con, "SELECT * FROM vw_sinistralidade_produto "
                                         "ORDER BY nr_ranking_sinistralidade"),
        "mensal": consultar(con, "SELECT * FROM vw_premio_mensal ORDER BY aa_mes"),
        "corretores": consultar(con, "SELECT * FROM vw_ranking_corretor ORDER BY nr_ranking"),
        "qualidade": consultar(con, "SELECT * FROM qualidade_resultado ORDER BY cd_validacao"),
        "governanca": {"cobertura": governanca["cobertura"],
                       "colunas": governanca["colunas_governadas"],
                       "termos": len(ler_csv("glossario.csv")),
                       "regras": len(ler_csv("regras_negocio.csv")),
                       "de_para": len(ler_csv("de_para.csv"))},
        "dicionario": [{k: d[k] for k in ("camada", "tabela", "coluna", "tipo_dado", "chave",
                                          "descricao", "termo_glossario", "regra", "classificacao")}
                       for d in ler_csv("dicionario_dados.csv")],
    }


# O HTML fica num template; os dados entram no lugar de __DADOS__ como JSON.
TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel de Sinistralidade e Governança de Dados — Seguros</title>
<style>
  :root {
    --plano: #f9f9f7; --superficie: #fcfcfb; --tinta: #0b0b0b; --tinta-2: #52514e;
    --tinta-3: #898781; --grade: #e1e0d9; --base: #c3c2b7; --borda: rgba(11,11,11,.10);
    --serie: #2a78d6; --serie-clara: #cfe0f6;
    --ok: #0ca30c; --ok-texto: #006300; --alerta: #fab219; --erro: #d03b3b; --info: #2a78d6;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--plano); color: var(--tinta);
         font: 14px/1.45 Inter, "Segoe UI", system-ui, -apple-system, sans-serif; }
  header { padding: 28px 32px 8px; max-width: 1240px; margin: 0 auto; }
  header h1 { margin: 0 0 4px; font-size: 22px; letter-spacing: -.01em; }
  header p { margin: 0; color: var(--tinta-2); }
  .selo { display: inline-block; padding: 2px 8px; border-radius: 99px; background: #eef3fb;
          color: #1d5aa6; font-size: 12px; font-weight: 600; margin-left: 6px; }
  main { max-width: 1240px; margin: 0 auto; padding: 16px 32px 40px; display: grid; gap: 16px; }
  .linha { display: grid; gap: 16px; }
  .k5 { grid-template-columns: repeat(5, 1fr); } .k4 { grid-template-columns: repeat(4, 1fr); }
  .c2 { grid-template-columns: 1fr 1fr; }
  @media (max-width: 960px) { .k5, .k4, .c2 { grid-template-columns: 1fr 1fr; } }
  .cartao { background: var(--superficie); border: 1px solid var(--borda); border-radius: 12px; padding: 16px 18px; }
  .rotulo { color: var(--tinta-2); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
  .valor { font-size: 24px; font-weight: 650; margin-top: 4px; font-variant-numeric: tabular-nums; }
  .nota { color: var(--tinta-3); font-size: 12px; margin-top: 4px; }
  h2 { font-size: 15px; margin: 0 0 2px; }
  .secao { color: var(--tinta-2); font-size: 12px; text-transform: uppercase; letter-spacing: .06em;
           margin: 12px 0 -4px; font-weight: 600; }
  .fonte { color: var(--tinta-3); font-size: 12px; margin-bottom: 12px; }
  .fonte code { background: #f1f0ec; padding: 1px 5px; border-radius: 4px; color: var(--tinta-2); }
  /* barras horizontais */
  .hbar { display: grid; grid-template-columns: 160px 1fr 70px; align-items: center; gap: 10px; margin: 7px 0; }
  .hbar .nome { font-size: 13px; color: var(--tinta-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .hbar .trilho { height: 18px; position: relative; border-left: 1px solid var(--base); }
  .hbar .barra { height: 100%; background: var(--serie); border-radius: 0 4px 4px 0; }
  .hbar .num { font-variant-numeric: tabular-nums; font-size: 13px; text-align: right; }
  /* colunas mensais */
  .colunas { display: flex; align-items: flex-end; gap: 2px; height: 180px; border-bottom: 1px solid var(--base);
 }
  .colunas div { flex: 1; background: var(--serie); border-radius: 4px 4px 0 0; min-width: 6px; }
  .colunas div:hover, .hbar:hover .barra { background: #1d5aa6; }
  .eixo { display: flex; justify-content: space-between; color: var(--tinta-3); font-size: 11px; margin-top: 6px; }
  /* tabelas */
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { text-align: left; color: var(--tinta-2); font-weight: 600; border-bottom: 1px solid var(--base); padding: 6px 8px; }
  td { border-bottom: 1px solid var(--grade); padding: 6px 8px; vertical-align: top; }
  td.n { text-align: right; font-variant-numeric: tabular-nums; }
  .status { display: inline-flex; align-items: center; gap: 6px; font-weight: 600; font-size: 12px; }
  .status i { width: 16px; height: 16px; border-radius: 50%; display: inline-grid; place-items: center;
              font-style: normal; font-size: 11px; color: #fff; }
  /* linhagem */
  .fluxo { display: grid; grid-template-columns: repeat(5, 1fr); gap: 22px; }
  .etapa { border: 1px solid var(--borda); border-radius: 10px; padding: 10px 12px; position: relative; background: #fff; }
  .etapa b { display: block; font-size: 13px; } .etapa span { color: var(--tinta-2); font-size: 12px; }
  .etapa:not(:last-child)::after { content: "→"; position: absolute; right: -18px; top: 50%;
                                   transform: translateY(-50%); color: var(--tinta-3); font-size: 16px; }
  input { width: 100%; padding: 8px 10px; border: 1px solid var(--base); border-radius: 8px; font: inherit; margin-bottom: 10px; }
  .rolagem { max-height: 360px; overflow: auto; }
  .tag { font-size: 11px; padding: 1px 6px; border-radius: 4px; background: #f1f0ec; color: var(--tinta-2); white-space: nowrap; }
  .tag.PESSOAL { background: #fbe4e4; color: #9b2222; } .tag.CONFIDENCIAL { background: #fdf1d6; color: #7a5600; }
  #dica { position: fixed; pointer-events: none; background: #0b0b0b; color: #fff; font-size: 12px;
          padding: 6px 9px; border-radius: 6px; opacity: 0; transition: opacity .1s; white-space: pre; }
  footer { text-align: center; color: var(--tinta-3); font-size: 12px; padding-bottom: 24px; }
</style>
</head>
<body>
<header>
  <h1>Painel de Sinistralidade e Governança de Dados <span class="selo">dados fictícios</span></h1>
  <p id="sub"></p>
</header>
<main>
  <div class="secao">Indicadores de negócio</div>
  <div class="linha k5" id="kpis"></div>

  <div class="secao">Saúde da documentação</div>
  <div class="linha k4" id="gov"></div>

  <div class="linha c2">
    <div class="cartao">
      <h2>Sinistralidade por produto</h2>
      <div class="fonte">Regra <b>RN06</b> · fonte <code>vw_sinistralidade_produto</code> · prêmio e sinistro retidos (RN05)</div>
      <div id="g_sin"></div>
    </div>
    <div class="cartao">
      <h2>Prêmio emitido por mês de início de vigência</h2>
      <div class="fonte">Regra <b>RN01</b> · fonte <code>vw_premio_mensal</code> · passe o mouse para ver variação (LAG) e acumulado</div>
      <div class="colunas" id="g_mes"></div>
      <div class="eixo" id="g_mes_eixo"></div>
    </div>
  </div>

  <div class="linha c2">
    <div class="cartao">
      <h2>Ranking de corretores — prêmio líquido final</h2>
      <div class="fonte">Regras <b>RN03 e RN04</b> · fonte <code>vw_ranking_corretor</code></div>
      <div id="g_cor"></div>
    </div>
    <div class="cartao">
      <h2>Qualidade de dados — última execução</h2>
      <div class="fonte">fonte <code>qualidade_resultado</code> (sql/04_validacoes.sql)</div>
      <table id="t_qual"></table>
    </div>
  </div>

  <div class="cartao">
    <h2>Linhagem: do sistema de origem ao painel</h2>
    <div class="fonte">Exemplo do indicador de sinistralidade · detalhe completo em <code>metadados/linhagem.csv</code></div>
    <div class="fluxo">
      <div class="etapa"><b>Origem SISEG</b><span>TB_SINI.VL_INDE + VL_RESV</span></div>
      <div class="etapa"><b>Bronze</b><span>bronze_tb_sini (cópia fiel)</span></div>
      <div class="etapa"><b>Silver</b><span>silver_sinistro (De x Para)</span></div>
      <div class="etapa"><b>Gold</b><span>fato_sinistro.vl_sinistro_retido</span></div>
      <div class="etapa"><b>Consumo</b><span>pc_sinistralidade → este painel</span></div>
    </div>
  </div>

  <div class="cartao">
    <h2>Dicionário de dados pesquisável</h2>
    <div class="fonte">fonte <code>metadados/dicionario_dados.csv</code> · validado contra o banco antes de cada publicação</div>
    <input id="busca" placeholder="Pesquisar por coluna, tabela, termo de negócio ou regra (ex.: prêmio ganho, RN05, PESSOAL)">
    <div class="rolagem"><table id="t_dic"></table></div>
  </div>
</main>
<footer>Projeto de portfólio · Anderson Joel Portes · gerado por src/gerar_dashboard.py</footer>
<div id="dica"></div>

<script>
const D = __DADOS__;

// ---------- formatação pt-BR ----------
const brl = v => v.toLocaleString("pt-BR", {style: "currency", currency: "BRL", maximumFractionDigits: 0});
const mi  = v => "R$ " + (v / 1e6).toLocaleString("pt-BR", {minimumFractionDigits: 2, maximumFractionDigits: 2}) + " mi";
const pct = (v, c = 1) => (v * 100).toLocaleString("pt-BR", {minimumFractionDigits: c, maximumFractionDigits: c}) + "%";
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

// ---------- dica (tooltip) ----------
const dica = document.getElementById("dica");
function comDica(el, texto) {
  el.addEventListener("mousemove", e => {
    dica.textContent = texto; dica.style.opacity = 1;
    dica.style.left = Math.min(e.clientX + 12, innerWidth - dica.offsetWidth - 8) + "px";
    dica.style.top = (e.clientY + 14) + "px";
  });
  el.addEventListener("mouseleave", () => dica.style.opacity = 0);
}

// ---------- cabeçalho e KPIs ----------
const k = D.kpi;
document.getElementById("sub").textContent =
  `Data base ${k.dt_base.split("-").reverse().join("/")} · ${k.qt_apolices.toLocaleString("pt-BR")} apólices · 5 produtos`;

const cartao = (rotulo, valor, nota) =>
  `<div class="cartao"><div class="rotulo">${rotulo}</div><div class="valor">${valor}</div><div class="nota">${nota}</div></div>`;
document.getElementById("kpis").innerHTML =
  cartao("Prêmio emitido", mi(k.vl_premio_emitido), "RN01 · original + endossos") +
  cartao("Prêmio ganho retido", mi(k.vl_premio_ganho_retido), "RN02 + RN05 · pro rata die") +
  cartao("Sinistro retido", mi(k.vl_sinistro_retido), "RN06 · pago + reserva") +
  cartao("Sinistralidade", pct(k.pc_sinistralidade), "sinistro ÷ prêmio ganho") +
  cartao("Comissão", mi(k.vl_comissao), "RN04 · estorna no cancelamento");

const g = D.governanca;
const q = D.qualidade, nOk = q.filter(x => ["OK","TRATADO"].includes(x.st_resultado)).length,
      nAl = q.filter(x => x.st_resultado === "ALERTA").length, nEr = q.filter(x => x.st_resultado === "ERRO").length;
document.getElementById("gov").innerHTML =
  cartao("Colunas documentadas", pct(g.cobertura, 0), `${g.colunas} de ${g.colunas} · portão aprovado`) +
  cartao("Glossário de negócio", g.termos + " termos", "apólice, endosso, sinistro, cosseguro…") +
  cartao("Catálogo de regras", g.regras + " regras", `RN01 a RN0${g.regras} · ${g.de_para} campos no De x Para`) +
  cartao("Validações de qualidade", `${nOk} OK · ${nAl} alertas`, `${nEr} erros · alertas enviados aos donos do dado`);

// ---------- barras horizontais ----------
function barras(id, linhas, nome, valor, rotulo, dicaTxt) {
  const max = Math.max(...linhas.map(valor));
  const el = document.getElementById(id);
  linhas.forEach(l => {
    const d = document.createElement("div");
    d.className = "hbar";
    d.innerHTML = `<div class="nome" title="${esc(nome(l))}">${esc(nome(l))}</div>
      <div class="trilho"><div class="barra" style="width:${valor(l) / max * 100}%"></div></div>
      <div class="num">${rotulo(l)}</div>`;
    comDica(d, dicaTxt(l));
    el.appendChild(d);
  });
}
barras("g_sin", D.sinistralidade, l => l.ds_produto, l => l.pc_sinistralidade, l => pct(l.pc_sinistralidade),
  l => `${l.ds_produto}\nSinistralidade: ${pct(l.pc_sinistralidade)}\nSinistro retido: ${brl(l.vl_sinistro_retido)}\nPrêmio ganho retido: ${brl(l.vl_premio_ganho_retido)}\n${l.qt_sinistros} sinistros em ${l.qt_apolices} apólices`);
barras("g_cor", D.corretores, l => `${l.nr_ranking}º ${l.nm_corretor}`, l => l.vl_premio_liquido_final,
  l => pct(l.pc_participacao), l => `${l.nm_corretor}\nPrêmio líquido: ${brl(l.vl_premio_liquido_final)}\nComissão: ${brl(l.vl_comissao)}\nParticipação: ${pct(l.pc_participacao)}\n${l.qt_apolices} apólices`);

// ---------- colunas mensais ----------
const meses = D.mensal, maxM = Math.max(...meses.map(m => m.vl_premio_emitido));
const nomeMes = am => { const [a, m] = am.split("-"); return "jan fev mar abr mai jun jul ago set out nov dez".split(" ")[m - 1] + "/" + a.slice(2); };
meses.forEach(m => {
  const c = document.createElement("div");
  c.style.height = (m.vl_premio_emitido / maxM * 100) + "%";
  const v = m.pc_variacao_mes == null ? "—" : (m.pc_variacao_mes > 0 ? "+" : "") + pct(m.pc_variacao_mes);
  comDica(c, `${nomeMes(m.aa_mes)}\nPrêmio emitido: ${brl(m.vl_premio_emitido)}\nvs mês anterior: ${v}\nAcumulado: ${brl(m.vl_acumulado)}`);
  document.getElementById("g_mes").appendChild(c);
});
document.getElementById("g_mes_eixo").innerHTML =
  [0, Math.floor(meses.length / 2), meses.length - 1].map(i => `<span>${nomeMes(meses[i].aa_mes)}</span>`).join("");

// ---------- tabela de qualidade (status = ícone + texto, nunca só cor) ----------
const ST = {OK: ["var(--ok)", "✓"], TRATADO: ["var(--info)", "↻"], ALERTA: ["var(--alerta)", "!"], ERRO: ["var(--erro)", "✕"]};
document.getElementById("t_qual").innerHTML =
  "<tr><th>Cód.</th><th>Validação</th><th class='n'>Qtd.</th><th>Resultado</th></tr>" +
  q.map(x => `<tr title="${esc(x.ds_acao)}"><td>${x.cd_validacao}</td><td>${esc(x.ds_validacao)}</td>
    <td class="n">${x.qt_problemas}</td><td><span class="status"><i style="background:${ST[x.st_resultado][0]};${x.st_resultado === "ALERTA" ? "color:#0b0b0b" : ""}">${ST[x.st_resultado][1]}</i>${x.st_resultado}</span></td></tr>`).join("");

// ---------- dicionário pesquisável ----------
function desenharDicionario(filtro = "") {
  const f = filtro.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const linhas = D.dicionario.filter(d => Object.values(d).join(" ").normalize("NFD")
                                         .replace(/[̀-ͯ]/g, "").toLowerCase().includes(f));
  document.getElementById("t_dic").innerHTML =
    "<tr><th>Tabela</th><th>Coluna</th><th>Tipo</th><th>Descrição</th><th>Termo</th><th>Regra</th><th>Classificação</th></tr>" +
    linhas.map(d => `<tr><td>${esc(d.tabela)}</td><td><b>${esc(d.coluna)}</b>${d.chave ? ` <span class="tag">${d.chave}</span>` : ""}</td>
      <td>${esc(d.tipo_dado)}</td><td>${esc(d.descricao)}</td><td>${esc(d.termo_glossario)}</td>
      <td>${esc(d.regra)}</td><td><span class="tag ${d.classificacao}">${d.classificacao}</span></td></tr>`).join("");
}
document.getElementById("busca").addEventListener("input", e => desenharDicionario(e.target.value));
desenharDicionario();
</script>
</body>
</html>
"""


def main():
    dados = coletar_dados()
    html = TEMPLATE.replace("__DADOS__", json.dumps(dados, ensure_ascii=False))
    destino = RAIZ / "dashboard" / "index.html"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    print(f"Dashboard gerado: {destino.relative_to(RAIZ)} (abra no navegador)")


if __name__ == "__main__":
    main()
