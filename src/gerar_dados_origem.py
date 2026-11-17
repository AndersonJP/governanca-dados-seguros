"""
ETAPA 1 — Gerar os dados do SISTEMA DE ORIGEM (simulado)
=========================================================

Por que existe?
    Numa seguradora, os dados nascem em sistemas legados de emissão e sinistro,
    com nomes de colunas "crípticos" (NR_APOL, VL_PRM_LIQ, PC_COSS_CED...).
    O trabalho do Analista de Dados/Governança é justamente "escavar" essas
    tabelas, entender o que cada campo significa e documentar.

O que este script faz?
    Gera 5 tabelas CSV fictícias, imitando o sistema de emissão "SISEG":
        TB_PROD  -> produtos (Vida, Odonto, Residencial...)
        TB_CORR  -> corretores e % de comissão
        TB_APOL  -> apólices (contrato do seguro)
        TB_ENDS  -> endossos (alterações da apólice: aumento, redução, cancelamento)
        TB_SINI  -> sinistros (ocorrências indenizáveis)

    De propósito, inserimos alguns PROBLEMAS REAIS de qualidade, para que as
    validações (sql/04_validacoes.sql) tenham o que encontrar:
        - apólices duplicadas por reprocessamento de carga (mesmo NR_APOL, DT_CARGA diferente)
        - sinistros com data de ocorrência FORA da vigência da apólice
        - endosso "órfão" (aponta para uma apólice que não existe)

Dados 100% sintéticos — nenhuma informação real de clientes.
Uso: python src/gerar_dados_origem.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # semente fixa: qualquer pessoa que rodar gera exatamente os mesmos dados

PASTA_ORIGEM = Path(__file__).resolve().parents[1] / "data" / "origem"
DATA_BASE = date(2026, 10, 31)  # "data de fechamento" usada para calcular prêmio ganho


def salvar_csv(nome, cabecalho, linhas):
    """Grava uma tabela de origem em CSV (separador ';', padrão comum em sistemas brasileiros)."""
    PASTA_ORIGEM.mkdir(parents=True, exist_ok=True)
    with open(PASTA_ORIGEM / f"{nome}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cabecalho)
        w.writerows(linhas)
    print(f"  {nome:8} -> {len(linhas):>4} linhas")


def main():
    print("Gerando dados do sistema de origem SISEG (fictício)...")

    # ---------------- TB_PROD: produtos ----------------
    # (codigo, descrição, faixa de prêmio anual, prob. de sinistro, severidade média)
    produtos = [
        (101, "VIDA EM GRUPO",       (900, 4000),  0.10, 13500),
        (102, "ACIDENTES PESSOAIS",  (300, 1500),  0.08, 5000),
        (103, "ODONTO EMPRESARIAL",  (1200, 6000), 0.90, 2800),
        (104, "RESIDENCIAL",         (400, 1800),  0.15, 3700),
        (105, "PREVIDENCIA RISCO",   (1500, 7000), 0.05, 30000),
    ]
    salvar_csv("TB_PROD", ["CD_PROD", "DS_PROD"], [(p[0], p[1]) for p in produtos])

    # ---------------- TB_CORR: corretores ----------------
    nomes = ["ALFA CORRETORA", "BETA SEGUROS", "GAMA PROTECAO", "DELTA BROKER",
             "EPSILON CORRETAGEM", "ZETA ASSESSORIA", "ETA SEGUROS", "TETA CORRETORA",
             "IOTA PARTNERS", "KAPPA SEGUROS"]
    corretores = [(201 + i, n, random.choice([0.10, 0.12, 0.15, 0.18, 0.20]))
                  for i, n in enumerate(nomes)]
    salvar_csv("TB_CORR", ["CD_CORR", "NM_CORR", "PC_COMS"], corretores)

    # ---------------- TB_APOL: apólices ----------------
    apolices = []
    for i in range(1200):
        prod = random.choice(produtos)
        ini = date(2025, 1, 1) + timedelta(days=random.randint(0, 637))  # até set/2026
        fim = ini + timedelta(days=365)
        premio = round(random.uniform(*prod[2]), 2)
        # ~15% das apólices são canceladas em algum momento da vigência
        status, dt_canc = "A", ""
        if random.random() < 0.15:
            dt_c = ini + timedelta(days=random.randint(30, 300))
            if dt_c <= DATA_BASE:
                status, dt_canc = "C", dt_c.isoformat()
        # ~20% das apólices têm cosseguro cedido (parte do risco dividido com outra seguradora)
        pc_coss = random.choice([0.20, 0.30, 0.40]) if random.random() < 0.20 else 0.0
        apolices.append([
            f"AP{100000 + i}", prod[0], random.choice(corretores)[0],
            f"SEG{random.randint(1000, 9999)}", ini.isoformat(), fim.isoformat(),
            premio, status, dt_canc, pc_coss, "2026-11-01",
        ])

    # PROBLEMA PROPOSITAL 1: 8 apólices recarregadas (duplicadas) num reprocessamento
    for ap in random.sample(apolices, 12):
        dup = ap.copy()
        dup[-1] = "2026-11-02"  # DT_CARGA mais recente -> deve prevalecer na deduplicação
        apolices.append(dup)

    salvar_csv("TB_APOL",
               ["NR_APOL", "CD_PROD", "CD_CORR", "CD_SEGD", "DT_INI_VIG", "DT_FIM_VIG",
                "VL_PRM_LIQ", "ST_APOL", "DT_CANC", "PC_COSS_CED", "DT_CARGA"],
               apolices)

    # ---------------- TB_ENDS: endossos ----------------
    unicas = {a[0]: a for a in apolices}  # visão sem duplicatas para gerar filhos
    endossos, n = [], 1
    for ap in unicas.values():
        ini = date.fromisoformat(ap[4])
        # endosso de aumento/redução de capital (~25% das apólices)
        if random.random() < 0.25:
            tp = random.choice(["AUM", "RED"])
            valor = round(ap[6] * random.uniform(0.05, 0.25) * (1 if tp == "AUM" else -1), 2)
            emis = min(ini + timedelta(days=random.randint(10, 200)), DATA_BASE)
            endossos.append([f"EN{n:06d}", ap[0], tp, emis.isoformat(), valor]); n += 1
        # endosso de cancelamento: devolve ao cliente o prêmio NÃO decorrido
        # (o valor é calculado na camada gold pela regra RN03; aqui fica 0 como no legado)
        if ap[7] == "C":
            endossos.append([f"EN{n:06d}", ap[0], "CAN", ap[8], 0]); n += 1

    # PROBLEMA PROPOSITAL 2: endosso apontando para apólice inexistente
    endossos.append([f"EN{n:06d}", "AP999999", "AUM", "2026-05-10", 150.00])
    salvar_csv("TB_ENDS", ["NR_ENDS", "NR_APOL", "TP_ENDS", "DT_EMIS", "VL_PRM_ENDS"], endossos)

    # ---------------- TB_SINI: sinistros ----------------
    prod_por_cod = {p[0]: p for p in produtos}
    sinistros, n = [], 1
    for ap in unicas.values():
        prod = prod_por_cod[ap[1]]
        ini, fim = date.fromisoformat(ap[4]), date.fromisoformat(ap[5])
        limite = min(fim, DATA_BASE, date.fromisoformat(ap[8]) if ap[8] else fim)
        dias = (limite - ini).days
        if dias <= 0:
            continue
        # quanto mais tempo exposto ao risco, maior a chance de sinistro
        if random.random() < prod[3] * dias / 365:
            ocor = ini + timedelta(days=random.randint(0, dias - 1))
            aviso = min(ocor + timedelta(days=random.randint(1, 40)), DATA_BASE)
            valor = round(random.expovariate(1 / prod[4]), 2)
            pago = aviso + timedelta(days=30) <= DATA_BASE and random.random() < 0.7
            # pago -> indenização paga; aberto -> fica como reserva (provisão)
            sinistros.append([f"SN{n:06d}", ap[0], ocor.isoformat(), aviso.isoformat(),
                              valor if pago else 0, 0 if pago else valor,
                              "PAGO" if pago else "ABERTO"]); n += 1

    # PROBLEMA PROPOSITAL 3: sinistros com ocorrência ANTES do início de vigência
    for ap in random.sample(list(unicas.values()), 3):
        ocor = date.fromisoformat(ap[4]) - timedelta(days=random.randint(5, 60))
        sinistros.append([f"SN{n:06d}", ap[0], ocor.isoformat(),
                          (ocor + timedelta(days=10)).isoformat(), 0, 1800.00, "ABERTO"]); n += 1

    salvar_csv("TB_SINI",
               ["NR_SINI", "NR_APOL", "DT_OCOR", "DT_AVIS", "VL_INDE", "VL_RESV", "ST_SINI"],
               sinistros)
    print("Pronto! Arquivos em data/origem/")


if __name__ == "__main__":
    main()
