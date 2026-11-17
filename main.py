"""
Executa o projeto inteiro, de ponta a ponta, com um único comando:

    python main.py

Ordem (cada etapa é um script independente em src/, com comentários próprios):
    1. gerar_dados_origem.py    sistema de origem fictício (CSV)
    2-6. pipeline.py             bronze -> silver (De x Para) -> gold (regras) -> indicadores -> qualidade
    7. validar_documentacao.py  portão de governança: documentação x realidade do banco
    8. gerar_documentacao.py    Markdown, Confluence (XHTML + Word) e Unity Catalog
    9. gerar_dashboard.py       dashboard HTML
"""

import subprocess
import sys

ETAPAS = [
    ("1    Gerar dados do sistema de origem", "src/gerar_dados_origem.py"),
    ("2-6  Pipeline bronze > silver > gold + qualidade", "src/pipeline.py"),
    ("7    Portão de governança (documentação x banco)", "src/validar_documentacao.py"),
    ("8    Publicar documentação (docs, Confluence, Unity Catalog)", "src/gerar_documentacao.py"),
    ("9    Gerar dashboard HTML", "src/gerar_dashboard.py"),
]

for titulo, script in ETAPAS:
    print(f"\n{'=' * 70}\nETAPA {titulo}\n{'=' * 70}")
    if subprocess.run([sys.executable, script]).returncode != 0:
        sys.exit(f"\nParado na etapa: {titulo}")

print("\nTudo pronto! Abra dashboard/index.html no navegador.")
