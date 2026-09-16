"""
Consolida votacao_partido_munzona_*_BRASIL.csv → votos_validos_partido.parquet

Votos válidos por (ano, uf, cargo) para cargos estaduais e
por (ano, municipio, cargo) para Prefeito.

Os arquivos do TSE têm três layouts de colunas ao longo dos anos:
  - Layout A (2000–2014): QT_VOTOS_NOMINAIS + QT_VOTOS_LEGENDA
  - Layout B (1998, 2018): QT_VOTOS_NOMINAIS_VALIDOS + QT_VOTOS_LEGENDA_VALIDOS
                           (1998 usa -3 como sentinel de n/a → tratar como 0)
  - Layout C (2016–2022): QT_VOTOS_NOMINAIS_VALIDOS + QT_VOTOS_LEGENDA_VALIDOS
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "resultados"
OUTPUT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "processed"

CARGOS_ESTADUAIS = [
    "DEPUTADO FEDERAL",
    "DEPUTADO ESTADUAL",
    "DEPUTADO DISTRITAL",
    "GOVERNADOR",
    "SENADOR",
]
CARGOS_MUNICIPAIS = ["PREFEITO"]
CARGOS_INTERESSE = CARGOS_ESTADUAIS + CARGOS_MUNICIPAIS

# Colunas fixas presentes em todos os anos
COLS_FIXAS = [
    "ANO_ELEICAO",
    "NR_TURNO",
    "NM_TIPO_ELEICAO",
    "SG_UF",
    "CD_MUNICIPIO",
    "DS_CARGO",
]

# Colunas de votos por layout — detectadas dinamicamente após leitura
COL_NOMINAIS_VALIDOS = "qt_votos_nominais_validos"   # layouts B e C
COL_LEGENDA_VALIDOS  = "qt_votos_legenda_validos"    # layouts B e C
COL_NOMINAIS         = "qt_votos_nominais"            # layout A
COL_LEGENDA          = "qt_votos_legenda"             # layout A


def _extrair_componentes_votos(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Retorna (votos_nominais, votos_legenda) tratando os dois layouts de colunas.
    Clipa em 0 para tratar o sentinel -3 presente nos anos antigos (layout B).
    """
    if COL_NOMINAIS_VALIDOS in df.columns and COL_LEGENDA_VALIDOS in df.columns:
        nominais = df[COL_NOMINAIS_VALIDOS].clip(lower=0)
        legenda  = df[COL_LEGENDA_VALIDOS].clip(lower=0)
    else:
        nominais = df[COL_NOMINAIS].clip(lower=0)
        legenda  = df[COL_LEGENDA].clip(lower=0)
    return nominais, legenda


def _ler_ano(raw_path: Path, ano: int) -> pd.DataFrame:
    """Lê um arquivo ano, normaliza colunas e retorna apenas cargos de interesse."""
    arquivo = raw_path / f"votacao_partido_munzona_{ano}_BRASIL.csv"

    # Colunas de votos variam — carregar todas e filtrar depois
    df = pd.read_csv(arquivo, sep=";", encoding="latin1", dtype=str, low_memory=False)
    df.columns = df.columns.str.strip().str.lower()

    # Filtros obrigatórios
    df["nm_tipo_eleicao"] = df["nm_tipo_eleicao"].str.upper().str.strip()
    df["nr_turno"] = pd.to_numeric(df["nr_turno"], errors="coerce")
    df["ano_eleicao"] = pd.to_numeric(df["ano_eleicao"], errors="coerce")
    df["ds_cargo"] = df["ds_cargo"].str.upper().str.strip()

    df = df.loc[
        (df["nm_tipo_eleicao"] == "ELEIÇÃO ORDINÁRIA") & (df["nr_turno"] == 1)
    ].copy()
    df = df.loc[df["ds_cargo"].isin(CARGOS_INTERESSE)].copy()

    if df.empty:
        return df

    # Converter colunas de votos para numérico
    for col in [COL_NOMINAIS_VALIDOS, COL_LEGENDA_VALIDOS, COL_NOMINAIS, COL_LEGENDA]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    nominais, legenda = _extrair_componentes_votos(df)
    df["votos_nominais"] = nominais
    df["votos_validos"]  = nominais + legenda
    df = df[["ano_eleicao", "sg_uf", "cd_municipio", "ds_cargo", "votos_nominais", "votos_validos"]]
    print(f"  {ano}: {len(df):,} linhas após filtros")
    return df


def consolidar_anos(raw_path: Path) -> pd.DataFrame:
    """Lê e concatena todos os anos disponíveis."""
    anos = list(range(1998, 2024, 2))
    partes = []
    for ano in anos:
        arquivo = raw_path / f"votacao_partido_munzona_{ano}_BRASIL.csv"
        if not arquivo.exists():
            print(f"  {ano}: arquivo não encontrado, pulando")
            continue
        df = _ler_ano(raw_path, ano)
        if not df.empty:
            partes.append(df)
    return pd.concat(partes, ignore_index=True)


def _agregar_estadual(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega cargos estaduais por (ano, uf, cargo). Consolida Dep. Distrital em Estadual."""
    est = df[df["ds_cargo"].isin(CARGOS_ESTADUAIS)].copy()
    est["ds_cargo"] = est["ds_cargo"].replace("DEPUTADO DISTRITAL", "DEPUTADO ESTADUAL")
    return (
        est.groupby(["ano_eleicao", "sg_uf", "ds_cargo"], as_index=False)
        [["votos_nominais", "votos_validos"]].sum()
        .assign(cd_municipio=np.nan)
    )


def _agregar_municipal(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega Prefeito por (ano, municipio, cargo)."""
    mun = df[df["ds_cargo"].isin(CARGOS_MUNICIPAIS)].copy()
    return (
        mun.groupby(["ano_eleicao", "cd_municipio", "ds_cargo"], as_index=False)
        [["votos_nominais", "votos_validos"]].sum()
        .assign(sg_uf=np.nan)
    )


def consolidar_e_salvar(raw_path: Path, output_path: Path) -> pd.DataFrame:
    print("Lendo arquivos...")
    df_raw = consolidar_anos(raw_path)

    print("Agregando cargos estaduais...")
    estadual = _agregar_estadual(df_raw)

    print("Agregando Prefeito (nível município)...")
    municipal = _agregar_municipal(df_raw)

    resultado = pd.concat([estadual, municipal], ignore_index=True)
    resultado = resultado[
        ["ano_eleicao", "sg_uf", "cd_municipio", "ds_cargo", "votos_nominais", "votos_validos"]
    ]

    out = output_path / "votos_validos_partido.parquet"
    resultado.to_parquet(out, index=False)
    print(f"\nSalvo em: {out}  ({len(resultado):,} linhas)")
    print(resultado.groupby("ds_cargo")[["votos_nominais", "votos_validos"]].count().rename(
        columns={"votos_nominais": "n_nominais", "votos_validos": "n_validos"}
    ))
    return resultado


def main():
    consolidar_e_salvar(RAW_DATA_PATH, OUTPUT_DATA_PATH)


if __name__ == "__main__":
    main()
