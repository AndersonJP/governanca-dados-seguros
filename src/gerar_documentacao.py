"""
ETAPA 8 — DOCUMENTAÇÃO COMO CÓDIGO: uma fonte, vários destinos
===============================================================

A "biblioteca de dados" vive nos CSVs da pasta metadados/ (fonte única da
verdade, versionada no Git). Este script publica essa mesma informação em:

    docs/*.md                          -> leitura direta no GitHub
    confluence/paginas/*.xhtml         -> formato nativo do Confluence (API REST)
    confluence/word/*.docx             -> importação manual no Confluence
                                          (Criar página > Mais ações > Importar > Word)
    sql/databricks/unity_catalog_comments.sql
                                       -> comentários e tags no Databricks Unity Catalog

Assim, ninguém mantém a mesma definição em 4 lugares: alterou o CSV,
roda o script e tudo fica igual. Isso é "nomenclatura unificada" na prática.

Uso: python src/gerar_documentacao.py
"""

import csv
import html
import json
import sqlite3
import unicodedata
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
META = RAIZ / "metadados"
DOCS = RAIZ / "docs"
CONF = RAIZ / "confluence"
TITULO_ESPACO = "Governança de Dados — Seguros"


def ler_csv(nome):
    with open(META / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def slug(titulo):
    """'05 De x Para (origem -> modelo)' -> '05_de_x_para_origem_modelo' (nome de arquivo sem acento)."""
    t = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode().lower()
    t = "".join(c if c.isalnum() else "_" for c in t)
    while "__" in t:
        t = t.replace("__", "_")
    return t.strip("_")


def carregar():
    """Lê todos os metadados + o resultado das validações de qualidade (se o pipeline já rodou)."""
    m = {n: ler_csv(f"{n}.csv") for n in
         ("tabelas", "dicionario_dados", "glossario", "regras_negocio", "de_para", "linhagem")}
    banco = RAIZ / "data" / "seguros.db"
    m["qualidade"] = []
    if banco.exists():
        con = sqlite3.connect(banco)
        con.row_factory = sqlite3.Row
        m["qualidade"] = [dict(r) for r in con.execute(
            "SELECT * FROM qualidade_resultado ORDER BY cd_validacao")]
    return m


# ---------------------------------------------------------------------------
# Conteúdo de cada página: (título, introdução, lista de seções)
# Cada seção = (subtítulo, cabeçalho da tabela, linhas). Isso alimenta os
# três formatos (Markdown, Confluence XHTML e Word) com o MESMO conteúdo.
# ---------------------------------------------------------------------------
def montar_paginas(m):
    paginas = []

    paginas.append(("01 Visão geral",
        "Biblioteca de dados dos produtos de seguro: o que existe, o que significa, de onde vem "
        "e quem é o dono. Fonte única da verdade: pasta metadados/ no Git.",
        [("Tabelas documentadas", ["Tabela", "Camada", "Descrição", "Grão", "Dono"],
          [[t["tabela"], t["camada"], t["descricao"], t["grao"], t["dono_dado"]] for t in m["tabelas"]]),
         ("Números da documentação", ["Item", "Quantidade"],
          [["Tabelas", len(m["tabelas"])], ["Colunas no dicionário", len(m["dicionario_dados"])],
           ["Termos no glossário", len(m["glossario"])], ["Regras de negócio", len(m["regras_negocio"])],
           ["Mapeamentos De x Para", len(m["de_para"])]])]))

    paginas.append(("02 Glossário de negócio",
        "Termos de seguros explicados em linguagem simples para Atuária, Sinistros e Comercial.",
        [("Termos", ["Termo", "Definição", "Exemplo", "Área", "Campos relacionados"],
          [[g["termo"], g["definicao_negocio"], g["exemplo"], g["area_principal"],
            g["campos_relacionados"]] for g in m["glossario"]])]))

    paginas.append(("03 Catálogo de regras de negócio",
        "Regras oficiais de cálculo. O código RNxx aparece no SQL e no dicionário, ligando regra, campo e cálculo.",
        [(f"{r['id']} — {r['nome']}", ["Item", "Conteúdo"],
          [["Descrição", r["descricao"]], ["Fórmula", r["formula"]],
           ["Campos resultantes", r["campos_resultado"]], ["Área dona", r["area_dona"]],
           ["Versão", r["versao"]], ["Status", r["status"]], ["Vigente desde", r["vigente_desde"]]])
         for r in m["regras_negocio"]]))

    por_tabela = defaultdict(list)
    for d in m["dicionario_dados"]:
        por_tabela[d["tabela"]].append(d)
    paginas.append(("04 Dicionário de dados",
        "Todas as colunas das camadas Silver, Gold e Consumo: tipo, chaves, significado, "
        "classificação (LGPD) e dono. Validado automaticamente contra o banco a cada mudança.",
        [(f"{tab} ({linhas[0]['camada']})",
          ["Coluna", "Tipo", "Chave", "Referência", "Descrição", "Termo", "Regra", "Classificação", "Status"],
          [[d["coluna"], d["tipo_dado"], d["chave"], d["referencia"], d["descricao"],
            d["termo_glossario"], d["regra"], d["classificacao"], d["status"]] for d in linhas])
         for tab, linhas in por_tabela.items()]))

    paginas.append(("05 De x Para (origem -> modelo)",
        "Mapeamento campo a campo do sistema de emissão SISEG para a camada Silver.",
        [("Mapeamento", ["Tabela origem", "Coluna origem", "Tabela destino", "Coluna destino",
                         "Tipo destino", "Transformação"],
          [[d["tabela_origem"], d["coluna_origem"], d["tabela_destino"], d["coluna_destino"],
            d["tipo_destino"], d["transformacao"]] for d in m["de_para"]])]))

    paginas.append(("06 Linhagem de dados",
        "Caminho do dado desde o sistema de origem até o dashboard e o relatório regulatório. "
        "Exemplo: TB_SINI.VL_INDE + VL_RESV -> silver_sinistro -> fato_sinistro.vl_sinistro_retido "
        "-> vw_sinistralidade_produto.pc_sinistralidade -> Dashboard.",
        [("Fluxo tabela a tabela", ["Origem", "Destino", "Camada do destino", "O que acontece"],
          [[l["origem"], l["destino"], l["tipo_destino"], l["descricao"]] for l in m["linhagem"]])]))

    if m["qualidade"]:
        paginas.append(("07 Qualidade de dados",
            "Resultado da última execução das validações (sql/04_validacoes.sql).",
            [("Validações", ["Código", "Validação", "Tabela", "Registros", "Resultado", "Ação"],
              [[q["cd_validacao"], q["ds_validacao"], q["nm_tabela"], q["qt_problemas"],
                q["st_resultado"], q["ds_acao"]] for q in m["qualidade"]])]))
    return paginas


# ---------------------------------------------------------------------------
# Destino 1: Markdown (GitHub)
# ---------------------------------------------------------------------------
def gerar_markdown(paginas):
    DOCS.mkdir(exist_ok=True)
    for titulo, intro, secoes in paginas:
        linhas = [f"# {titulo[3:]}", "", f"> {intro}", "",
                  "_Arquivo gerado por `src/gerar_documentacao.py` — edite os CSVs em `metadados/`._", ""]
        for sub, cab, rows in secoes:
            linhas += [f"## {sub}", "", "| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
            linhas += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows]
            linhas.append("")
        (DOCS / f"{slug(titulo)}.md").write_text("\n".join(linhas), encoding="utf-8")


# ---------------------------------------------------------------------------
# Destino 2: Confluence Storage Format (XHTML) — publicado via API REST
# ---------------------------------------------------------------------------
CORES_STATUS = {"APROVADO": "Green", "OK": "Green", "TRATADO": "Blue", "ALERTA": "Yellow",
                "ERRO": "Red", "PESSOAL": "Red", "CONFIDENCIAL": "Yellow",
                "INTERNA": "Blue", "PUBLICA": "Grey"}


def celula_confluence(valor):
    """Valores de status viram 'lozenges' coloridos do Confluence (macro status)."""
    v = str(valor)
    if v in CORES_STATUS:
        return (f'<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">'
                f'{CORES_STATUS[v]}</ac:parameter><ac:parameter ac:name="title">{v}'
                f'</ac:parameter></ac:structured-macro>')
    return html.escape(v)


def gerar_confluence_xhtml(paginas):
    pasta = CONF / "paginas"
    pasta.mkdir(parents=True, exist_ok=True)
    manifesto = []
    for titulo, intro, secoes in paginas:
        x = ['<ac:structured-macro ac:name="info"><ac:rich-text-body><p>'
             f'{html.escape(intro)}</p></ac:rich-text-body></ac:structured-macro>',
             '<ac:structured-macro ac:name="toc"><ac:parameter ac:name="maxLevel">2'
             '</ac:parameter></ac:structured-macro>']
        for sub, cab, rows in secoes:
            x.append(f"<h2>{html.escape(sub)}</h2><table><tbody>")
            x.append("<tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in cab) + "</tr>")
            for r in rows:
                x.append("<tr>" + "".join(f"<td>{celula_confluence(c)}</td>" for c in r) + "</tr>")
            x.append("</tbody></table>")
        x.append("<p><em>Gerado automaticamente a partir do repositório Git (pasta metadados/). "
                 "Não edite aqui: altere o CSV e publique novamente.</em></p>")
        (pasta / f"{slug(titulo)}.xhtml").write_text("\n".join(x), encoding="utf-8")
        manifesto.append({"arquivo": f"{slug(titulo)}.xhtml", "titulo": titulo[3:]})
    # manifesto.json: ordem e títulos das páginas, lido por confluence/publicar_confluence.py
    (pasta / "manifesto.json").write_text(
        json.dumps({"pagina_pai": TITULO_ESPACO, "paginas": manifesto}, ensure_ascii=False, indent=2),
        encoding="utf-8")


# ---------------------------------------------------------------------------
# Destino 3: Word (.docx) — importação manual no Confluence Cloud
# ---------------------------------------------------------------------------
def gerar_word(paginas):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor
    except ImportError:
        print("  (python-docx não instalado: pulando .docx — pip install python-docx)")
        return
    pasta = CONF / "word"
    pasta.mkdir(parents=True, exist_ok=True)
    for titulo, intro, secoes in paginas:
        doc = Document()
        doc.styles["Normal"].font.name = "Calibri"
        doc.styles["Normal"].font.size = Pt(10)
        doc.add_heading(titulo[3:], level=1)
        p = doc.add_paragraph(intro)
        p.runs[0].italic = True
        for sub, cab, rows in secoes:
            doc.add_heading(sub, level=2)
            t = doc.add_table(rows=1, cols=len(cab))
            t.style = "Light Grid Accent 1"
            for i, c in enumerate(cab):
                t.rows[0].cells[i].text = c
            for r in rows:
                cells = t.add_row().cells
                for i, c in enumerate(r):
                    cells[i].text = str(c)
        rodape = doc.add_paragraph("Gerado a partir do repositório Git (pasta metadados/).")
        rodape.runs[0].font.color.rgb = RGBColor(0x80, 0x80, 0x80)
        doc.save(pasta / f"{slug(titulo)}.docx")


# ---------------------------------------------------------------------------
# Destino 4: Databricks Unity Catalog — o dicionário vira metadado no catálogo
# ---------------------------------------------------------------------------
def gerar_unity_catalog(m):
    esquema = {"SILVER": "silver", "GOLD": "gold"}
    sql = ["-- Gerado por src/gerar_documentacao.py a partir de metadados/.",
           "-- Rode no Databricks SQL para publicar descrições e tags no Unity Catalog.",
           "-- (Views da camada CONSUMO recebem comentários no próprio CREATE VIEW.)", ""]
    for t in m["tabelas"]:
        if t["camada"] not in esquema:
            continue
        nome = f"seguros.{esquema[t['camada']]}.{t['tabela']}"
        desc = t["descricao"].replace("'", "''")
        sql += [f"-- {t['tabela']}",
                f"COMMENT ON TABLE {nome} IS '{desc} Grão: {t['grao']}.';",
                f"ALTER TABLE {nome} SET TAGS ('dono_dado' = '{t['dono_dado']}', 'camada' = '{t['camada']}');"]
        for d in m["dicionario_dados"]:
            if d["tabela"] != t["tabela"]:
                continue
            desc = d["descricao"].replace("'", "''")
            sql.append(f"ALTER TABLE {nome} ALTER COLUMN {d['coluna']} COMMENT '{desc}';")
            tags = f"'classificacao' = '{d['classificacao']}'"
            if d["regra"]:
                tags += f", 'regra_negocio' = '{d['regra']}'"
            sql.append(f"ALTER TABLE {nome} ALTER COLUMN {d['coluna']} SET TAGS ({tags});")
        sql.append("")
    destino = RAIZ / "sql" / "databricks"
    destino.mkdir(exist_ok=True)
    (destino / "unity_catalog_comments.sql").write_text("\n".join(sql), encoding="utf-8")


def main():
    m = carregar()
    paginas = montar_paginas(m)
    gerar_markdown(paginas)
    gerar_confluence_xhtml(paginas)
    gerar_word(paginas)
    gerar_unity_catalog(m)
    print(f"Documentação gerada: {len(paginas)} páginas em docs/, confluence/paginas/ e "
          "confluence/word/ + sql/databricks/unity_catalog_comments.sql")


if __name__ == "__main__":
    main()
