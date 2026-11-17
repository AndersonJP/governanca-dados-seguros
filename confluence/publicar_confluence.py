"""
Publica as páginas de confluence/paginas/ no Confluence Cloud via API REST.
==========================================================================

Duas formas de levar a documentação para o Confluence:

  A) MANUAL (sem configurar nada) — arquivos .docx da pasta confluence/word/
     Confluence Cloud: Criar página > Mais ações (...) > Modelos e importação
     > aba Importar > Documento do Word (.docx). Aceita até 30 arquivos por vez;
     cada arquivo vira uma página.

  B) AUTOMÁTICA (este script) — usa o formato nativo do Confluence (XHTML
     "storage format"), com tabelas, sumário e etiquetas de status coloridas.
     Cria a página pai e as filhas; se já existirem, atualiza (nova versão).

Configuração (variáveis de ambiente):
    CONFLUENCE_URL    ex.: https://suaempresa.atlassian.net/wiki
    CONFLUENCE_EMAIL  e-mail da conta Atlassian
    CONFLUENCE_TOKEN  token de API (id.atlassian.com > Segurança > Tokens de API)
    CONFLUENCE_SPACE  chave do espaço, ex.: DADOS

Uso:
    python confluence/publicar_confluence.py --simular   (só mostra o que faria)
    python confluence/publicar_confluence.py
"""

import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PASTA = Path(__file__).resolve().parent / "paginas"


def chamar_api(metodo, caminho, corpo=None):
    url = os.environ["CONFLUENCE_URL"].rstrip("/") + caminho
    credencial = f"{os.environ['CONFLUENCE_EMAIL']}:{os.environ['CONFLUENCE_TOKEN']}"
    req = urllib.request.Request(url, method=metodo, data=json.dumps(corpo).encode() if corpo else None)
    req.add_header("Authorization", "Basic " + base64.b64encode(credencial.encode()).decode())
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read() or "{}")


def buscar_pagina(espaco, titulo):
    q = urllib.parse.urlencode({"spaceKey": espaco, "title": titulo, "expand": "version"})
    res = chamar_api("GET", f"/rest/api/content?{q}")["results"]
    return res[0] if res else None


def publicar(espaco, titulo, xhtml, pai_id=None):
    """Cria a página ou, se já existir, publica uma nova versão (histórico preservado)."""
    corpo = {"type": "page", "title": titulo, "space": {"key": espaco},
             "body": {"storage": {"value": xhtml, "representation": "storage"}}}
    if pai_id:
        corpo["ancestors"] = [{"id": pai_id}]
    existente = buscar_pagina(espaco, titulo)
    if existente:
        corpo["version"] = {"number": existente["version"]["number"] + 1}
        return chamar_api("PUT", f"/rest/api/content/{existente['id']}", corpo)["id"]
    return chamar_api("POST", "/rest/api/content", corpo)["id"]


def main():
    manifesto = json.loads((PASTA / "manifesto.json").read_text(encoding="utf-8"))
    simular = "--simular" in sys.argv

    if simular:
        print(f"[simulação] página pai: {manifesto['pagina_pai']}")
        for p in manifesto["paginas"]:
            print(f"[simulação]   └─ {p['titulo']}  ({p['arquivo']})")
        return

    faltando = [v for v in ("CONFLUENCE_URL", "CONFLUENCE_EMAIL", "CONFLUENCE_TOKEN",
                            "CONFLUENCE_SPACE") if not os.environ.get(v)]
    if faltando:
        sys.exit(f"Defina as variáveis de ambiente: {', '.join(faltando)}")

    espaco = os.environ["CONFLUENCE_SPACE"]
    indice = "<p>Documentação gerada a partir do repositório Git.</p>" \
             '<ac:structured-macro ac:name="children" />'
    pai = publicar(espaco, manifesto["pagina_pai"], indice)
    for p in manifesto["paginas"]:
        xhtml = (PASTA / p["arquivo"]).read_text(encoding="utf-8")
        publicar(espaco, p["titulo"], xhtml, pai)
        print(f"Publicado: {p['titulo']}")


if __name__ == "__main__":
    main()
