"""Base congelada por lista para o lift do Top-NECr por magnitude e partido.

Lê data/processed/df_cobertura_top_necr_lista.parquet (gerado por
src/2_gold/cap3_cobertura_top_necr.py, que já traz H_l/E_l para os alvos
eleitos e candidato_competitivo, além de qt_vaga/dm_cat/sg_partido), junta a
família partidária (familia_partidaria.py) e grava uma cópia local congelada
— os itens 3-6 desta pasta consomem só este arquivo, sem recalcular nada.

Uso:
    python construir_base.py
"""
import hashlib
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROCESSED = ROOT / "data" / "processed"

sys.path.insert(0, str(HERE))
from familia_partidaria import familia  # noqa: E402

FONTE = PROCESSED / "df_cobertura_top_necr_lista.parquet"
DESTINO = HERE / "base_lista_congelada.parquet"

REGRA_K = "arredondado"  # regra principal do capítulo (k = NECr arredondado)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def construir() -> pd.DataFrame:
    df = pd.read_parquet(FONTE)
    df["familia_partidaria"] = df["sg_partido_norm"].map(familia)

    for regra in ["piso", "arredondado", "teto"]:
        for prefixo in ["eleitos", "competitivos"]:
            h = df[f"{prefixo}_top_{regra}"]
            e = df[f"{prefixo}_esperados_aleatorio_{regra}"]
            df[f"lift_lista_{prefixo}_{regra}"] = h / e

    cols = [
        "ano_eleicao",
        "sg_uf",
        "sg_partido_norm",
        "sg_partido",
        "familia_partidaria",
        "qt_vaga",
        "dm_cat",
        "n_candidatos",
        "n_com_recursos",
        "total_recursos_partidarios",
        "NECr",
        "n_eleitos",
        "n_competitivos",
    ]
    for regra in ["piso", "arredondado", "teto"]:
        cols += [f"k_{regra}"]
        for prefixo in ["eleitos", "competitivos"]:
            cols += [
                f"{prefixo}_top_{regra}",
                f"{prefixo}_esperados_aleatorio_{regra}",
                f"lift_lista_{prefixo}_{regra}",
            ]
    return df[cols]


def main() -> None:
    base = construir()
    base.to_parquet(DESTINO, index=False)
    print(f"Base congelada: {DESTINO} ({len(base)} listas)")
    print(f"Fonte: {FONTE}")
    print(f"  sha256: {sha256(FONTE)}")
    print(f"Regra de k principal para as tabulações seguintes: {REGRA_K}")


if __name__ == "__main__":
    main()
