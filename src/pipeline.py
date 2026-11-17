"""
ETAPAS 2 a 6 — PIPELINE: origem -> bronze -> silver -> gold -> indicadores -> validações
======================================================================================

Arquitetura em camadas (a mesma "Medallion" usada no Databricks):

    BRONZE  cópia fiel do sistema de origem, tudo como texto (nada se perde)
    SILVER  De x Para aplicado: nomes padronizados, tipos, deduplicação
    GOLD    modelo dimensional com as regras de negócio de seguros
    + views de indicadores e tabela de qualidade

Usamos SQLite (já vem com o Python) para o projeto rodar em qualquer
máquina sem instalar nada. O SQL é padrão ANSI e migra para Databricks
SQL / Athena com ajustes mínimos (principalmente funções de data).

Uso: python src/pipeline.py
"""

import csv
import sqlite3
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA_ORIGEM = RAIZ / "data" / "origem"
BANCO = RAIZ / "data" / "seguros.db"
PASTA_SQL = RAIZ / "sql"


def carregar_bronze(con):
    """ETAPA 2 — copia cada CSV do sistema de origem para uma tabela bronze_<nome>."""
    print("\n[BRONZE] Carregando tabelas de origem (sem nenhuma transformação)")
    for arquivo in sorted(PASTA_ORIGEM.glob("TB_*.csv")):
        tabela = f"bronze_{arquivo.stem.lower()}"
        with open(arquivo, encoding="utf-8") as f:
            leitor = csv.reader(f, delimiter=";")
            colunas = next(leitor)
            linhas = list(leitor)
        con.execute(f"DROP TABLE IF EXISTS {tabela}")
        con.execute(f"CREATE TABLE {tabela} ({', '.join(c + ' TEXT' for c in colunas)})")
        con.executemany(
            f"INSERT INTO {tabela} VALUES ({', '.join('?' * len(colunas))})", linhas
        )
        print(f"  {tabela:16} {len(linhas):>4} linhas")


def executar_sql(con):
    """ETAPAS 3 a 6 — executa os scripts da pasta sql/ na ordem do nome (01, 02, 03...)."""
    for script in sorted(PASTA_SQL.glob("0*.sql")):
        print(f"\n[SQL] {script.name}")
        con.executescript(script.read_text(encoding="utf-8"))


def mostrar_qualidade(con):
    """Imprime o resultado das validações e devolve True se não houver ERRO."""
    print("\n[QUALIDADE] Resultado das validações")
    sem_erro = True
    for cod, desc, qtd, status in con.execute(
        "SELECT cd_validacao, ds_validacao, qt_problemas, st_resultado "
        "FROM qualidade_resultado ORDER BY cd_validacao"
    ):
        print(f"  {cod} {status:8} {qtd:>3}  {desc}")
        sem_erro &= status != "ERRO"
    return sem_erro


def main():
    if not PASTA_ORIGEM.exists() or not any(PASTA_ORIGEM.glob("TB_*.csv")):
        sys.exit("Rode antes: python src/gerar_dados_origem.py")

    BANCO.unlink(missing_ok=True)          # sempre reconstrói do zero (reprodutível)
    con = sqlite3.connect(BANCO)
    carregar_bronze(con)
    executar_sql(con)
    con.commit()

    ok = mostrar_qualidade(con)
    print("\n[INDICADORES] Sinistralidade por produto")
    for prod, sin, rank in con.execute(
        "SELECT ds_produto, pc_sinistralidade, nr_ranking_sinistralidade "
        "FROM vw_sinistralidade_produto ORDER BY nr_ranking_sinistralidade"
    ):
        print(f"  {rank}. {prod:20} {sin:6.1%}")
    con.close()

    if not ok:
        sys.exit("\nExistem validações com ERRO: dados NÃO podem ser promovidos.")
    print(f"\nPipeline concluído. Banco gerado em {BANCO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
