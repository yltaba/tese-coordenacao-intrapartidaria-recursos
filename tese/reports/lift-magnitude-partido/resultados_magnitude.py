"""Lift do Top-NECr por magnitude de lista (item 3).

Lê base_lista_congelada.parquet (já validada por verificar.py) e agrega por
faixa de magnitude (dm_cat) x alvo (eleitos, competitivos prévios) x ano
(2018, 2022 e agregado), regra de k = arredondado (principal do capítulo).

Não recalcula H_l/E_l — só soma o que já está na base congelada.

Uso:
    python resultados_magnitude.py
"""
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "base_lista_congelada.parquet"
DESTINO = HERE / "lift_por_magnitude.csv"

REGRA = "arredondado"
ALVOS = ["eleitos", "competitivos"]
ORDEM_MAGNITUDE = ["Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)"]


def agregar(sub: pd.DataFrame, ano_label) -> pd.DataFrame:
    linhas = []
    for dm_cat, g in sub.groupby("dm_cat", observed=True):
        for alvo in ALVOS:
            h_col = f"{alvo}_top_{REGRA}"
            e_col = f"{alvo}_esperados_aleatorio_{REGRA}"
            k_col = f"k_{REGRA}"
            H = g[h_col].sum()
            E = g[e_col].sum()
            linhas.append(
                {
                    "ano_eleicao": ano_label,
                    "dm_cat": dm_cat,
                    "alvo": alvo,
                    "n_listas": len(g),
                    "tamanho_relativo_medio_top_necr": (
                        g[k_col] / g["n_candidatos"]
                    ).mean(),
                    "H_observado": H,
                    "E_esperado": E,
                    "lift": H / E if E > 0 else float("nan"),
                }
            )
    return pd.DataFrame(linhas)


def main() -> None:
    base = pd.read_parquet(BASE_PATH)

    partes = [agregar(base[base["ano_eleicao"] == ano], ano) for ano in [2018, 2022]]
    partes.append(agregar(base, "2018+2022"))
    out = pd.concat(partes, ignore_index=True)

    out["dm_cat"] = pd.Categorical(out["dm_cat"], categories=ORDEM_MAGNITUDE, ordered=True)
    out = out.sort_values(["alvo", "ano_eleicao", "dm_cat"]).reset_index(drop=True)
    out.to_csv(DESTINO, index=False, encoding="utf-8")

    print(out.to_string(index=False))
    print(f"\nSalvo em: {DESTINO}")


if __name__ == "__main__":
    main()
