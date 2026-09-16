"""Lift do Top-NECr por partido (item 4).

Lê base_lista_congelada.parquet e agrega por sg_partido_norm x alvo (eleitos,
competitivos prévios) x ano (2018, 2022 e agregado), regra de k = arredondado.
Ordena por lift decrescente dentro de cada (ano, alvo) e sinaliza partidos
com denominador esperado pequeno (E < 5 ou < 5 listas) — candidatos a
outlier por pouca informação, não por focalização real.

Também calcula a persistência do ranking de lift entre 2018 e 2022 usando a
família partidária (familia_partidaria.py), restrita a famílias com E >= 5
nos dois anos, via correlação de Spearman.

Uso:
    python resultados_partido.py
"""
import json
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

BASE_PATH = HERE / "base_lista_congelada.parquet"
DESTINO_TABELA = HERE / "lift_por_partido.csv"
DESTINO_PERSISTENCIA = HERE / "persistencia_ranking_partido.json"

REGRA = "arredondado"
ALVOS = ["eleitos", "competitivos"]
LIMIAR_E_PEQUENO = 5
LIMIAR_N_LISTAS_PEQUENO = 5


def agregar_por_partido(sub: pd.DataFrame, ano_label, chave: str) -> pd.DataFrame:
    linhas = []
    for partido, g in sub.groupby(chave):
        for alvo in ALVOS:
            h_col = f"{alvo}_top_{REGRA}"
            e_col = f"{alvo}_esperados_aleatorio_{REGRA}"
            H = g[h_col].sum()
            E = g[e_col].sum()
            linhas.append(
                {
                    "ano_eleicao": ano_label,
                    chave: partido,
                    "alvo": alvo,
                    "n_listas": len(g),
                    "H_observado": H,
                    "E_esperado": E,
                    "lift": H / E if E > 0 else float("nan"),
                    "denominador_pequeno": (
                        E < LIMIAR_E_PEQUENO or len(g) < LIMIAR_N_LISTAS_PEQUENO
                    ),
                }
            )
    out = pd.DataFrame(linhas)
    out = out.sort_values(["alvo", "lift"], ascending=[True, False]).reset_index(drop=True)
    return out


def calcular_persistencia(base: pd.DataFrame) -> dict:
    """Spearman entre o rank de lift por família partidária em 2018 e 2022,
    restrito a famílias com E >= LIMIAR_E_PEQUENO nos dois anos."""
    resultado = {}
    for alvo in ALVOS:
        h_col = f"{alvo}_top_{REGRA}"
        e_col = f"{alvo}_esperados_aleatorio_{REGRA}"
        tab = (
            base.groupby(["ano_eleicao", "familia_partidaria"])
            .agg(H=(h_col, "sum"), E=(e_col, "sum"), n=(h_col, "size"))
            .reset_index()
        )
        tab["lift"] = tab["H"] / tab["E"]
        piv_lift = tab.pivot(index="familia_partidaria", columns="ano_eleicao", values="lift")
        piv_E = tab.pivot(index="familia_partidaria", columns="ano_eleicao", values="E")
        comum = piv_lift.dropna(subset=[2018, 2022])
        comum = comum[(piv_E.loc[comum.index, 2018] >= LIMIAR_E_PEQUENO) & (piv_E.loc[comum.index, 2022] >= LIMIAR_E_PEQUENO)]
        if len(comum) >= 3:
            rho, p = spearmanr(comum[2018], comum[2022])
        else:
            rho, p = float("nan"), float("nan")
        resultado[alvo] = {
            "n_familias_comparadas": int(len(comum)),
            "spearman_rho": None if pd.isna(rho) else float(rho),
            "spearman_p": None if pd.isna(p) else float(p),
            "familias": sorted(comum.index.tolist()),
        }
    return resultado


def main() -> None:
    base = pd.read_parquet(BASE_PATH)

    partes = [
        agregar_por_partido(base[base["ano_eleicao"] == ano], ano, "sg_partido_norm")
        for ano in [2018, 2022]
    ]
    partes.append(agregar_por_partido(base, "2018+2022", "sg_partido_norm"))
    tabela = pd.concat(partes, ignore_index=True)
    tabela.to_csv(DESTINO_TABELA, index=False, encoding="utf-8")

    persistencia = calcular_persistencia(base)
    DESTINO_PERSISTENCIA.write_text(
        json.dumps(persistencia, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("Top 10 por lift, eleitos, agregado 2018+2022:")
    print(
        tabela[(tabela["alvo"] == "eleitos") & (tabela["ano_eleicao"] == "2018+2022")]
        .head(10)
        .to_string(index=False)
    )
    print("\nPersistência de ranking (Spearman, por família partidária):")
    print(json.dumps(persistencia, indent=2, ensure_ascii=False))
    print(f"\nTabela: {DESTINO_TABELA}")
    print(f"Persistência: {DESTINO_PERSISTENCIA}")


if __name__ == "__main__":
    main()
