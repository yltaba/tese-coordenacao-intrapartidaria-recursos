"""
cap3_survival_features.py
Constantes e funções compartilhadas para a análise de sobrevivência do Capítulo 4
(timing do primeiro repasse de recursos partidários).

Importado por:
  notebooks/3_modelos_duracao.ipynb
  notebooks/3_fluxo_cumulativo.ipynb
"""
import numpy as np
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE     = Path(__file__).resolve()
RAW_PATH  = _HERE.parents[2] / "data" / "raw" / "finanças"
DATA_PATH = _HERE.parents[2] / "data" / "processed"

# ── Janelas de campanha ────────────────────────────────────────────────────────
JANELAS = {
    2014: (pd.Timestamp("2014-07-06"),  pd.Timestamp("2014-10-05")),
    2018: (pd.Timestamp("2018-08-16"),  pd.Timestamp("2018-10-07")),
    2022: (pd.Timestamp("2022-08-16"),  pd.Timestamp("2022-10-02")),
}
DURACAO = {ano: (fim - inicio).days for ano, (inicio, fim) in JANELAS.items()}
# 2014: 91 dias (pré-FEFC) | 2018: 52 dias | 2022: 47 dias

FONTES_PARTIDO = {"FP", "PJ_ROTEADO", "FEFC"}

ARQUIVOS_RECEITAS = {
    2014: RAW_PATH / "receitas_candidatos_2014_brasil.txt",
    2018: RAW_PATH / "receitas_candidatos_2018_BRASIL.csv",
    2022: RAW_PATH / "receitas_candidatos_2022_BRASIL.csv",
}

# Covariáveis do modelo de sobrevivência
COVS_MODELO = [
    "n_eleicoes_deputado_federal",
    "n_eleicoes_deputado_estadual",
    "n_eleicoes_vereador",
    "n_eleicoes_prefeito",
    "n_eleicoes_governador",
    "n_eleicoes_senador",
    "prop_votos_nominais_lag",
    "log_qt_vaga",
    "mulher",   # dummy gênero feminino; NaN = não divulgado
    "negra",    # dummy preta ou parda (TSE); NaN = não divulgado
]

_RENAME_2014 = {
    "cargo":            "ds_cargo",
    "fonte recurso":    "ds_fonte_receita",
    "valor receita":    "vr_receita",
    "data da receita":  "dt_receita",   # formato "DD/MM/YYYYHH:MM:SS" sem espaço
    "uf":               "sg_uf",
    "sigla  partido":   "sg_partido",   # dois espaços no original
    "numero candidato": "nr_candidato",
}

_N_ELEICOES_COLS_CS = [
    "n_eleicoes_prefeito",
    "n_eleicoes_deputado_estadual",
    "n_eleicoes_deputado_federal",
    "n_eleicoes_governador",
    "n_eleicoes_senador",
]


# ── Carregamento de dados transacionais ───────────────────────────────────────

def ler_tab_receitas(path_arquivo):
    return pd.read_csv(path_arquivo, sep=";", encoding="latin-1", low_memory=False)


def tratar_df_receita(df, ano):
    """Normaliza um CSV de receitas TSE e classifica a fonte de recurso.

    fonte_tipo:
      2014: FP | PJ_ROTEADO | PJ_DIRETO | PF | PROPRIO | OUTROS_CAND | OUTROS
      2018/2022: FEFC | FP | PF | PROPRIO | OUTROS_CAND | FINANCIAMENTO_COLETIVO | OUTROS

    Para análises de coordenação partidária, filtrar por FONTES_PARTIDO.
    """
    df.columns = df.columns.str.lower()

    rename = {k: v for k, v in _RENAME_2014.items() if k in df.columns}
    if rename:
        df = df.rename(columns=rename)

    df["ds_cargo"]         = df["ds_cargo"].str.strip().str.title()
    df["ds_fonte_receita"] = df["ds_fonte_receita"].str.upper()
    df = df.loc[df["ds_cargo"] == "Deputado Federal"].copy()

    if ano == 2014:
        tipo = df["tipo receita"].str.strip()
        df["fonte_tipo"] = np.select(
            [
                (tipo == "Recursos de partido político") & (df["ds_fonte_receita"] == "FUNDO PARTIDARIO"),
                (tipo == "Recursos de partido político"),
                tipo == "Recursos de pessoas jurídicas",
                tipo == "Recursos de pessoas físicas",
                tipo == "Recursos próprios",
                tipo == "Recursos de outros candidatos/comitês",
            ],
            ["FP", "PJ_ROTEADO", "PJ_DIRETO", "PF", "PROPRIO", "OUTROS_CAND"],
            default="OUTROS",
        )
        df["dt_receita"] = pd.to_datetime(df["dt_receita"].str[:10], format="%d/%m/%Y")
    else:
        origem = df["ds_origem_receita"].str.strip()
        df["fonte_tipo"] = np.select(
            [
                df["ds_fonte_receita"] == "FUNDO ESPECIAL",
                df["ds_fonte_receita"] == "FUNDO PARTIDARIO",
                origem == "Recursos de pessoas físicas",
                origem == "Recursos próprios",
                origem == "Recursos de outros candidatos",
                origem == "Recursos de Financiamento Coletivo",
            ],
            ["FEFC", "FP", "PF", "PROPRIO", "OUTROS_CAND", "FINANCIAMENTO_COLETIVO"],
            default="OUTROS",
        )
        df["dt_receita"] = pd.to_datetime(df["dt_receita"], dayfirst=True)

    df["vr_receita"] = df["vr_receita"].astype(str).str.replace(",", ".").astype(float)
    df["ano_eleicao"] = ano

    inicio, fim = JANELAS[ano]
    df = df.loc[(df["dt_receita"] >= inicio) & (df["dt_receita"] <= fim)].copy()

    df = df.groupby(
        ["ano_eleicao", "dt_receita", "sg_uf", "sg_partido", "nr_candidato", "fonte_tipo"],
        as_index=False,
    )["vr_receita"].sum()
    return df


def carregar_receitas():
    """Retorna dados transacionais consolidados para Dep. Federal (2014/2018/2022).

    Para análises de coordenação, filtrar a coluna `fonte_tipo` por FONTES_PARTIDO.
    """
    partes = [
        tratar_df_receita(ler_tab_receitas(p), ano)
        for ano, p in ARQUIVOS_RECEITAS.items()
    ]
    df = pd.concat(partes, ignore_index=True)
    df["nr_candidato"] = df["nr_candidato"].astype(str)
    return df


# ── Feature engineering ───────────────────────────────────────────────────────

def gerar_features_survival(rrd: pd.DataFrame) -> pd.DataFrame:
    """Adiciona variáveis derivadas usadas nos modelos de sobrevivência.

    Colunas adicionadas:
      incumbente            — vitória prévia em qualquer cargo exceto Vereador
      candidato_competitivo — incumbente OR alcancou_10pct_qe_hist (ex-ante, sem resultado atual)
      partido_uf            — chave de cluster para SE clusterizados
      repasse_semana1       — dias_primeira_receita <= 7
      exp_deputado_federal  — categoria de experiência como Dep. Federal (pd.cut)
    """
    rrd = rrd.copy()

    rrd["incumbente"] = rrd[_N_ELEICOES_COLS_CS].fillna(0).sum(axis=1) > 0
    rrd["candidato_competitivo"] = (
        rrd["incumbente"] | rrd["alcancou_10pct_qe_hist"].fillna(False)
    )
    rrd["partido_uf"] = rrd["sg_partido"] + "_" + rrd["sg_uf"]

    dias = rrd["dias_primeira_receita"] if "dias_primeira_receita" in rrd.columns else rrd["dias_desde_inicio"]
    rrd["repasse_semana1"] = (dias <= 7).astype(int)

    rrd["exp_deputado_federal"] = pd.cut(
        rrd["n_eleicoes_deputado_federal"].fillna(0).astype(int),
        bins=[-0.1, 0, 1, 100],
        labels=["Sem experiencia", "1 mandato", "2+ mandatos"],
    )

    return rrd


# ── Preparação do dataset de sobrevivência ────────────────────────────────────

def preparar_survival(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Filtra e prepara o dataset de sobrevivência para um ano.

    Colunas de saída: nr_candidato, sg_uf, sg_partido, partido_uf,
                      duration, event, eleito, COVS_MODELO.
    """
    d = df.loc[df["ano_eleicao"] == ano].copy()
    dur_max = DURACAO[ano]
    d["duration"] = d["dias_desde_inicio"].fillna(dur_max).clip(upper=dur_max)
    d["event"]    = d["dias_desde_inicio"].notna().astype(int)
    for c in COVS_MODELO:
        if c.startswith("n_eleicoes"):
            d[c] = d[c].fillna(0).astype(float)
    d["log_qt_vaga"] = np.log(d["qt_vaga"])
    cols = [
        "nr_candidato", "sg_uf", "sg_partido", "partido_uf",
        "duration", "event", "eleito",
    ] + COVS_MODELO
    # dropna exclui NaN residuais em prop_votos_nominais_lag (CPF="-4", ~1 caso/ano)
    return d[cols].dropna(subset=COVS_MODELO + ["duration", "event"])


# ── Dias até o maior repasse ──────────────────────────────────────────────────

def calcular_dias_maior_receita(df_rec_partido: pd.DataFrame) -> pd.DataFrame:
    """Para cada candidato, retorna os dias desde o início da campanha até o
    maior repasse partidário diário (soma de FONTES_PARTIDO no mesmo dia).

    Colunas de saída: ano_eleicao, sg_uf, sg_partido, nr_candidato,
                      dias_maior_receita, vr_maior_receita.
    """
    daily = (
        df_rec_partido
        .groupby(["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato", "dt_receita"])
        ["vr_receita"].sum()
        .reset_index()
    )
    idx_max = (
        daily.groupby(["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato"])
        ["vr_receita"].idxmax()
    )
    maior = daily.loc[idx_max].copy()
    maior["dias_maior_receita"] = maior.apply(
        lambda r: (r["dt_receita"] - JANELAS[r["ano_eleicao"]][0]).days, axis=1
    )
    return (
        maior[["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato",
               "dias_maior_receita", "vr_receita"]]
        .rename(columns={"vr_receita": "vr_maior_receita"})
    )


def preparar_survival_maior(
    df_rrd: pd.DataFrame,
    df_maior: pd.DataFrame,
    ano: int,
) -> pd.DataFrame:
    """Survival dataset usando dias até o maior repasse (robustez ao preparar_survival).

    Mesmo conjunto de covariáveis; duration = dias_maior_receita.
    Censura = candidato sem nenhum repasse partidário.
    """
    d = df_rrd.loc[df_rrd["ano_eleicao"] == ano].copy()
    dur_max = DURACAO[ano]

    d = d.merge(
        df_maior.loc[
            df_maior["ano_eleicao"] == ano,
            ["sg_uf", "sg_partido", "nr_candidato", "dias_maior_receita"],
        ],
        on=["sg_uf", "sg_partido", "nr_candidato"],
        how="left",
    )
    d["duration"] = d["dias_maior_receita"].fillna(dur_max).clip(upper=dur_max)
    d["event"]    = d["dias_maior_receita"].notna().astype(int)
    for c in COVS_MODELO:
        if c.startswith("n_eleicoes"):
            d[c] = d[c].fillna(0).astype(float)
    d["log_qt_vaga"] = np.log(d["qt_vaga"])
    cols = [
        "nr_candidato", "sg_uf", "sg_partido", "partido_uf",
        "duration", "event", "eleito",
    ] + COVS_MODELO
    return d[cols].dropna(subset=COVS_MODELO + ["duration", "event"])


# ── Fluxo cumulativo ──────────────────────────────────────────────────────────

def calc_cumulative(df: pd.DataFrame, group_cols: list) -> pd.DataFrame:
    """Calcula o fluxo cumulativo de receita por semana para cada grupo.

    Requer que `df` tenha as colunas `semana`, `ano_eleicao` e `vr_receita`.
    Retorna: group_cols + [semana, vr_receita, cum_receita, cum_prop].
    """
    max_semana = {ano: int(np.ceil(dur / 7)) for ano, dur in DURACAO.items()}

    agg = (
        df.groupby(group_cols + ["semana"], observed=True)["vr_receita"]
        .sum().reset_index().sort_values(group_cols + ["semana"])
    )
    keys = agg[group_cols].drop_duplicates()
    expanded_rows = []
    for _, row in keys.iterrows():
        mask = pd.Series(True, index=agg.index)
        for col in group_cols:
            mask &= agg[col] == row[col]
        ano = row["ano_eleicao"]
        semanas_completas = pd.DataFrame({"semana": range(1, max_semana[ano] + 1)})
        grupo_df = (
            agg[mask][["semana", "vr_receita"]]
            .merge(semanas_completas, on="semana", how="right")
            .fillna(0)
        )
        for col in group_cols:
            grupo_df[col] = row[col]
        expanded_rows.append(grupo_df)

    agg_full = (
        pd.concat(expanded_rows, ignore_index=True)
        .sort_values(group_cols + ["semana"])
    )
    agg_full["cum_receita"] = agg_full.groupby(group_cols, observed=True)["vr_receita"].cumsum()
    totais = agg_full.groupby(group_cols, observed=True)["vr_receita"].transform("sum")
    agg_full["cum_prop"] = agg_full["cum_receita"] / totais
    return agg_full
