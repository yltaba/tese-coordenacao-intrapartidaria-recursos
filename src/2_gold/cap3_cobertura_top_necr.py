"""Cobertura dos eleitos e dos competitivos prévios pelo núcleo Top-NECr.

Para cada lista partido x UF x ano, calcula o NECr a partir dos recursos
partidários, ordena os candidatos por esses recursos e verifica quantos
eleitos e quantos candidatos competitivos prévios (ex-ante) estão entre os
Top-k, com k derivado do NECr. O resultado eleitoral não define o ranking
nem o tamanho do núcleo.

Regra principal: k = arredondamento convencional de NECr (0,5 para cima).
Robustez: piso e teto. Empates no corte são contabilizados fracionariamente.
Eleitos/competitivos em listas sem recursos partidários permanecem no
denominador nacional.

`candidato_competitivo` é sempre a versão EX-ANTE (incumbente OU >=10% do QE
em disputa anterior) — a mesma definição de cap3_cs_features.gerar_features.
NUNCA usar `candidato_forte_cs` (ex-post) aqui.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cap3_cs_features import PROCESSED_DATA_PATH, carregar_rrd  # noqa: E402
from cap3_taa_features import _preparar, acertos_fracionarios  # noqa: E402


N_ELEICOES_COLS = [
    "n_eleicoes_prefeito",
    "n_eleicoes_deputado_estadual",
    "n_eleicoes_deputado_federal",
    "n_eleicoes_governador",
    "n_eleicoes_senador",
]


def calcular_cobertura_top_necr(rrd: pd.DataFrame | None = None):
    if rrd is None:
        rrd = carregar_rrd()
    df = _preparar(rrd)
    df = df[df["ano_eleicao"].isin([2018, 2022])].copy()

    # candidato_competitivo (ex-ante) — ver docstring do módulo.
    incumbente = df[N_ELEICOES_COLS].fillna(0).sum(axis=1) > 0
    df["candidato_competitivo"] = incumbente | df["alcancou_10pct_qe_hist"].fillna(False)

    linhas = []
    for (ano, uf, partido), g in df.groupby(
        ["ano_eleicao", "sg_uf", "sg_partido_norm"], sort=True
    ):
        recursos = g["vr_receita_recursos_partidos"].to_numpy(dtype=float)
        eleitos = g["eleito"].to_numpy(dtype=int)
        competitivos = g["candidato_competitivo"].to_numpy(dtype=int)
        total_recursos = recursos.sum()
        n_eleitos = int(eleitos.sum())
        n_com_recursos = int((recursos > 0).sum())

        if total_recursos > 0:
            shares = recursos / total_recursos
            necr = 1.0 / np.square(shares).sum()
            ks = {
                "piso": max(1, int(np.floor(necr))),
                "arredondado": max(1, int(np.floor(necr + 0.5))),
                "teto": max(1, int(np.ceil(necr))),
            }
        else:
            necr = np.nan
            ks = {"piso": 0, "arredondado": 0, "teto": 0}

        # Bloco original (não alterar nomes/ordem: consumido por
        # tese/reports/resultados-capitulo-3/ e pelo texto já auditado).
        reg = {
            "ano_eleicao": int(ano),
            "sg_uf": uf,
            "sg_partido_norm": partido,
            "n_eleitos": n_eleitos,
            "n_candidatos": len(g),
            "n_com_recursos": n_com_recursos,
            "total_recursos_partidarios": total_recursos,
            "NECr": necr,
        }
        for regra, k in ks.items():
            reg[f"k_{regra}"] = k
            reg[f"eleitos_top_{regra}"] = (
                acertos_fracionarios(recursos, eleitos, k) if k > 0 else 0.0
            )
            reg[f"eleitos_esperados_aleatorio_{regra}"] = n_eleitos * k / len(g)

        # Extensão (aditiva): magnitude, partido de exibição e alvo
        # competitivos prévios (ex-ante), para desagregação por magnitude/partido.
        n_competitivos = int(competitivos.sum())
        reg["sg_partido"] = g["sg_partido"].iloc[0]
        reg["qt_vaga"] = int(g["qt_vaga"].iloc[0])
        reg["dm_cat"] = g["dm_cat"].iloc[0]
        reg["n_competitivos"] = n_competitivos
        for regra, k in ks.items():
            reg[f"competitivos_top_{regra}"] = (
                acertos_fracionarios(recursos, competitivos, k) if k > 0 else 0.0
            )
            reg[f"competitivos_esperados_aleatorio_{regra}"] = (
                n_competitivos * k / len(g)
            )
        linhas.append(reg)

    listas = pd.DataFrame(linhas)
    resumos = []
    for ano, g in listas.groupby("ano_eleicao"):
        total_eleitos = int(g["n_eleitos"].sum())
        total_competitivos = int(g["n_competitivos"].sum())
        sem_recursos_eleitos = int(
            g.loc[g["total_recursos_partidarios"] <= 0, "n_eleitos"].sum()
        )
        sem_recursos_competitivos = int(
            g.loc[g["total_recursos_partidarios"] <= 0, "n_competitivos"].sum()
        )
        for regra in ["piso", "arredondado", "teto"]:
            cobertos = g[f"eleitos_top_{regra}"].sum()
            esperado = g[f"eleitos_esperados_aleatorio_{regra}"].sum()
            cobertos_comp = g[f"competitivos_top_{regra}"].sum()
            esperado_comp = g[f"competitivos_esperados_aleatorio_{regra}"].sum()
            resumos.append(
                {
                    # Bloco original (nomes/ordem preservados).
                    "ano_eleicao": int(ano),
                    "regra_k": regra,
                    "eleitos_total": total_eleitos,
                    "eleitos_top_necr": cobertos,
                    "cobertura": cobertos / total_eleitos,
                    "eleitos_esperados_aleatorio": esperado,
                    "cobertura_aleatoria": esperado / total_eleitos,
                    "n_posicoes_top_necr": int(g[f"k_{regra}"].sum()),
                    "n_candidatos": int(g["n_candidatos"].sum()),
                    "eleitos_em_listas_sem_recursos": sem_recursos_eleitos,
                    # Extensão (aditiva): lift explícito (eleitos) e bloco
                    # paralelo completo para competitivos prévios (ex-ante).
                    "lift": cobertos / esperado,
                    "competitivos_total": total_competitivos,
                    "competitivos_top_necr": cobertos_comp,
                    "cobertura_competitivos": cobertos_comp / total_competitivos,
                    "competitivos_esperados_aleatorio": esperado_comp,
                    "cobertura_aleatoria_competitivos": esperado_comp
                    / total_competitivos,
                    "lift_competitivos": cobertos_comp / esperado_comp,
                    "competitivos_em_listas_sem_recursos": sem_recursos_competitivos,
                }
            )
    return listas, pd.DataFrame(resumos)


def main():
    listas, resumo = calcular_cobertura_top_necr()
    destino_listas = PROCESSED_DATA_PATH / "df_cobertura_top_necr_lista.parquet"
    destino_resumo = PROCESSED_DATA_PATH / "df_cobertura_top_necr_resumo.csv"
    listas.to_parquet(destino_listas, index=False)
    resumo.to_csv(destino_resumo, index=False)

    exibir = resumo[
        [
            "ano_eleicao",
            "regra_k",
            "eleitos_total",
            "eleitos_top_necr",
            "cobertura",
            "lift",
            "competitivos_total",
            "competitivos_top_necr",
            "cobertura_competitivos",
            "lift_competitivos",
        ]
    ].copy()
    for c in ["eleitos_top_necr", "competitivos_top_necr", "lift", "lift_competitivos"]:
        exibir[c] = exibir[c].round(3)
    exibir["cobertura_pct"] = (100 * exibir.pop("cobertura")).round(2)
    exibir["cobertura_competitivos_pct"] = (
        100 * exibir.pop("cobertura_competitivos")
    ).round(2)
    print(exibir.to_string(index=False))
    print(f"\nListas: {destino_listas}")
    print(f"Resumo: {destino_resumo}")


if __name__ == "__main__":
    main()
