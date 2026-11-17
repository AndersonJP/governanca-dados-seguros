"""
ETAPA 7 — PORTÃO DE GOVERNANÇA: "nenhum campo vai para produção sem documentação"
=================================================================================

Responde a uma responsabilidade central da vaga:
    "Garantir que novos campos criados pela Engenharia de Dados estejam
     devidamente classificados e documentados ANTES da promoção para produção."

Como funciona?
    Compara a REALIDADE (estrutura das tabelas no banco) com a DOCUMENTAÇÃO
    (arquivos da pasta metadados/). Se algo não bater, o script termina com
    erro — e no GitHub Actions isso BLOQUEIA o merge do Pull Request.

Verificações:
    D0  Toda tabela tem descrição, grão e dono?
    D1  Toda coluna do banco está no dicionário?           (campo novo sem doc)
    D2  Toda coluna do dicionário existe no banco?         (doc desatualizada)
    D3  O tipo documentado é o tipo real?
    D4  A chave primária (PK) documentada é a real?
    D5  A chave estrangeira (FK) documentada é a real?
    D6  Descrição, classificação LGPD e dono preenchidos e status APROVADO?
    D7  O termo citado existe no Glossário? A regra existe no Catálogo de Regras?
    D8  Toda coluna do sistema de origem tem De x Para?

Uso:
    python src/validar_documentacao.py
    python src/validar_documentacao.py --simular-campo-novo   (demonstração para entrevista)
"""

import csv
import json
import sqlite3
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BANCO = RAIZ / "data" / "seguros.db"
META = RAIZ / "metadados"
PREFIXOS_GOVERNADOS = ("silver_", "dim_", "fato_", "vw_")  # camadas que exigem documentação


def ler_csv(nome):
    with open(META / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def estrutura_real(con):
    """Lê do próprio banco: tabelas, colunas, tipos, PKs e FKs (o 'information_schema')."""
    real = {}
    objetos = con.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view')"
    ).fetchall()
    for (tabela,) in objetos:
        if not tabela.startswith(PREFIXOS_GOVERNADOS):
            continue
        fks = {f[3]: f"{f[2]}.{f[4]}" for f in con.execute(f"PRAGMA foreign_key_list({tabela})")}
        for _, coluna, tipo, _, _, pk in con.execute(f"PRAGMA table_info({tabela})"):
            real[(tabela, coluna)] = {"tipo": tipo, "pk": bool(pk), "fk": fks.get(coluna, "")}
    return real


def validar(con):
    real = estrutura_real(con)
    dicionario = {(d["tabela"], d["coluna"]): d for d in ler_csv("dicionario_dados.csv")}
    termos = {g["termo"] for g in ler_csv("glossario.csv")}
    regras = {r["id"] for r in ler_csv("regras_negocio.csv")}
    de_para = {(d["tabela_origem"], d["coluna_origem"]) for d in ler_csv("de_para.csv")}
    problemas = []

    def falha(cod, tabela, coluna, msg):
        problemas.append({"codigo": cod, "tabela": tabela, "coluna": coluna, "problema": msg})

    for chave, info in real.items():
        if chave not in dicionario:
            falha("D1", *chave, "Campo existe no banco mas NÃO está documentado no dicionário")
    for chave, doc in dicionario.items():
        if chave not in real:
            falha("D2", *chave, "Campo documentado não existe mais no banco (documentação desatualizada)")
            continue
        info = real[chave]
        if info["tipo"] and info["tipo"] != doc["tipo_dado"]:          # views não têm tipo declarado
            falha("D3", *chave, f"Tipo documentado {doc['tipo_dado']} difere do real {info['tipo']}")
        if info["pk"] != (doc["chave"] == "PK"):
            falha("D4", *chave, "Chave primária documentada difere da real")
        if info["fk"] != doc["referencia"]:
            falha("D5", *chave, f"FK documentada '{doc['referencia']}' difere da real '{info['fk']}'")
        for campo in ("descricao", "classificacao", "dono_dado"):
            if not doc[campo].strip():
                falha("D6", *chave, f"Campo obrigatório '{campo}' vazio")
        if doc["status"] != "APROVADO":
            falha("D6", *chave, f"Status '{doc['status']}': aguardando aprovação da governança")
        if doc["termo_glossario"] and doc["termo_glossario"] not in termos:
            falha("D7", *chave, f"Termo '{doc['termo_glossario']}' não existe no glossário")
        if doc["regra"] and doc["regra"] not in regras:
            falha("D7", *chave, f"Regra '{doc['regra']}' não existe no catálogo de regras")

    # D0: toda tabela governada tem descrição, grão e dono em metadados/tabelas.csv
    tabelas_doc = {t["tabela"] for t in ler_csv("tabelas.csv")}
    for tabela in sorted({t for t, _ in real} - tabelas_doc):
        falha("D0", tabela, "*", "Tabela sem descrição/grão/dono em tabelas.csv")

    # D8: toda coluna de origem (bronze) precisa ter um destino no De x Para
    for (tabela,) in con.execute("SELECT name FROM sqlite_master WHERE name LIKE 'bronze_%'"):
        origem = tabela.replace("bronze_", "").upper()
        for _, coluna, *_ in con.execute(f"PRAGMA table_info({tabela})"):
            if (origem, coluna) not in de_para:
                falha("D8", origem, coluna, "Coluna de origem sem mapeamento no De x Para")

    return real, dicionario, problemas


def main():
    con = sqlite3.connect(BANCO)

    if "--simular-campo-novo" in sys.argv:
        # DEMONSTRAÇÃO: a Engenharia criou um campo e "esqueceu" de documentar.
        # Fazemos numa cópia em memória para não alterar o banco real.
        memoria = sqlite3.connect(":memory:")
        con.backup(memoria)
        con = memoria
        con.execute("ALTER TABLE fato_premio ADD COLUMN vl_iof REAL")
        print(">> Simulação: Engenharia criou fato_premio.vl_iof sem documentar\n")

    real, dicionario, problemas = validar(con)

    documentadas = sum(1 for c in real if c in dicionario)
    cobertura = documentadas / len(real) if real else 0
    print(f"Colunas governadas no banco : {len(real)}")
    print(f"Colunas documentadas        : {documentadas}  ({cobertura:.0%} de cobertura)")

    # Relatório usado pelo dashboard (só na execução real, não na simulação)
    if "--simular-campo-novo" not in sys.argv:
        relatorio = {"colunas_governadas": len(real), "colunas_documentadas": documentadas,
                     "cobertura": round(cobertura, 4), "problemas": problemas}
        (RAIZ / "data" / "relatorio_governanca.json").write_text(
            json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")

    if problemas:
        print(f"\nREPROVADO — {len(problemas)} problema(s) de documentação:")
        for p in problemas:
            print(f"  [{p['codigo']}] {p['tabela']}.{p['coluna']}: {p['problema']}")
        sys.exit(1)
    print("\nAPROVADO — documentação reflete a realidade das tabelas. Liberado para produção.")


if __name__ == "__main__":
    main()
