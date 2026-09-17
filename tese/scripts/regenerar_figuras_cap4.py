"""Gera as figuras do Cap. 4 (timing dos repasses partidarios) sem o corte por
tipo de partido (competitivo / menos competitivo). Ate 17/09/2026 as figuras do
capitulo cruzavam candidato competitivo x tipo de partido; o corte por tipo de
partido era exploratorio e foi removido -- as figuras abaixo distinguem apenas
candidato competitivo x nao-competitivo.

Substitui o pipeline que antes vivia em notebooks/3_modelos_duracao_v2.ipynb e
notebooks/3_fluxo_cumulativo.ipynb (nao versionados; recuperados manualmente em
2026-09-17). A partir de agora este script e a fonte de verdade, versionada,
para as figuras e para data/processed/df_cox_survival.parquet -- o .qmd so LE
esse parquet (nao ajusta o modelo), entao ele precisa ser regenerado por este
script sempre que rrd_df_novo.parquet mudar. Ate 17/09/2026 o parquet estava
desatualizado: foi gerado em 19/06/2026, antes das correcoes de 14/09/2026 em
rrd_df_novo.parquet (as mesmas que motivaram regenerar_figuras_cap3.py).

Requer os CSVs brutos de receitas em data/raw/financas/ (ver ARQUIVOS_RECEITAS em
cap3_survival_features.py) para as figuras de fluxo cumulativo e a de maior
repasse -- a leitura desses CSVs e pesada (~1-2 min). O modelo Cox e as figuras
de primeiro repasse NAO precisam disso (usam so rrd_df_novo.parquet).

Gera:
  data/processed/df_cox_survival.parquet (tbl-cox)
  figs/cap4_survival_km_primeiro.png     (fig-km-cs)
  figs/cap4_survival_km_maior.png        (fig-km-maior-cs)
  figs/cap4_fluxo_cumulativo_prop.png    (fig-semana-campanha)
  figs/cap4_fluxo_cumulativo_abs.png     (fig-semana-abs)

Execute da raiz do repositorio: python tese/scripts/regenerar_figuras_cap4.py
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from lifelines import KaplanMeierFitter, CoxPHFitter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "2_gold"))
from cap3_survival_features import (  # noqa: E402
    gerar_features_survival,
    preparar_survival,
    calcular_dias_maior_receita,
    preparar_survival_maior,
    carregar_receitas,
    calc_cumulative,
    JANELAS,
    DURACAO,
    FONTES_PARTIDO,
    COVS_MODELO,
)

DATA_PATH = ROOT / "data" / "processed"
FIGS = ROOT / "figs"

CORES = {"Candidato competitivo": "black", "Candidato não-competitivo": "lightgrey"}
DASHES = {"Candidato competitivo": "solid", "Candidato não-competitivo": "dot"}
GRUPOS = ["Candidato competitivo", "Candidato não-competitivo"]
ANOS = [2018, 2022]


# ── Dados base ─────────────────────────────────────────────────────────────

def carregar_rrd_survival():
    rrd = pd.read_parquet(DATA_PATH / "rrd_df_novo.parquet")
    rrd["nr_candidato"] = rrd["nr_candidato"].astype(str)
    rrd["dias_primeira_receita"] = rrd["dias_desde_inicio"]
    return gerar_features_survival(rrd)


def cs_lookup(rrd_df):
    return rrd_df[
        ["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato", "candidato_competitivo"]
    ].drop_duplicates()


def _add_grupo_cs(df, lookup, ano):
    chave = lookup.loc[
        lookup["ano_eleicao"] == ano,
        ["sg_uf", "sg_partido", "nr_candidato", "candidato_competitivo"],
    ]
    d = df.merge(chave, on=["sg_uf", "sg_partido", "nr_candidato"], how="left")
    d["candidato_competitivo"] = d["candidato_competitivo"].fillna(False)
    d["grupo_cs"] = d["candidato_competitivo"].map(
        {True: "Candidato competitivo", False: "Candidato não-competitivo"}
    )
    return d


def carregar_survival(rrd_df, lookup):
    survival_dfs = {}
    for ano in ANOS:
        d = preparar_survival(rrd_df, ano)
        survival_dfs[ano] = _add_grupo_cs(d, lookup, ano)
    return survival_dfs


# ── Modelo Cox PH (tbl-cox) ──────────────────────────────────────────────────

def regenerar_cox_survival(survival_dfs):
    """Ajusta o Cox PH por ano (2018, 2022) e regrava data/processed/df_cox_survival.parquet.

    survival_dfs vem de carregar_survival(); a coluna grupo_cs (candidato_competitivo)
    nao entra no modelo -- so as COVS_MODELO, como no notebook original."""
    linhas = []
    for ano, d in survival_dfs.items():
        cph = CoxPHFitter()
        cph.fit(
            d[COVS_MODELO + ["duration", "event", "partido_uf"]],
            duration_col="duration", event_col="event", cluster_col="partido_uf",
        )
        s = cph.summary.reset_index().rename(columns={"covariate": "variavel"})
        s["ano"] = ano
        linhas.append(s[["variavel", "ano", "exp(coef)", "exp(coef) lower 95%",
                          "exp(coef) upper 95%", "p"]])
        print(f"Cox PH {ano}: C-index = {cph.concordance_index_:.4f}")

    df_cox = pd.concat(linhas, ignore_index=True)
    out = DATA_PATH / "df_cox_survival.parquet"
    df_cox.to_parquet(out, index=False)
    print(f"Salvo: {out}")


# ── Figura 1: KM primeiro repasse ───────────────────────────────────────────

def _km_painel(d, ano):
    d = d.copy()
    d["duration_semana"] = (d["duration"] / 7).clip(upper=DURACAO[ano] / 7)
    return d


def _plot_km(paineis, out_path):
    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True,
        subplot_titles=[p[0] for p in paineis],
        horizontal_spacing=0.06,
    )
    for col, (titulo, d) in enumerate(paineis, start=1):
        for grupo in GRUPOS:
            mask = d["grupo_cs"] == grupo
            kmf = KaplanMeierFitter()
            kmf.fit(d.loc[mask, "duration_semana"], event_observed=d.loc[mask, "event"], label=grupo)
            sf = kmf.survival_function_
            fig.add_trace(
                go.Scatter(
                    x=kmf.timeline, y=sf[grupo].values,
                    mode="lines", name=grupo,
                    showlegend=(col == 1),
                    line=dict(color=CORES[grupo], width=2.5, dash=DASHES[grupo]),
                ),
                row=1, col=col,
            )
    fig.update_layout(
        legend=dict(title="Candidato (ex-ante)", orientation="h", x=0.5, xanchor="center",
                    y=1.18, yanchor="top"),
        height=440, width=850, template="plotly_white",
        margin=dict(t=90, b=50),
    )
    fig.update_xaxes(title_text="Semana da campanha", dtick=1)
    fig.update_yaxes(title_text="S(t)", range=[0, 1.05], col=1)
    fig.write_image(str(out_path), scale=2)
    print(f"Salvo: {out_path}")


def fig_km_primeiro_repasse(survival_dfs):
    """fig-km-cs: dias ate o primeiro repasse, so por candidato_competitivo."""
    paineis = [(str(ano), _km_painel(survival_dfs[ano], ano)) for ano in ANOS]
    _plot_km(paineis, FIGS / "cap4_survival_km_primeiro.png")


def fig_km_maior_repasse(rrd_df, lookup):
    """fig-km-maior-cs: dias ate o maior repasse, so por candidato_competitivo."""
    df_rec = carregar_receitas()
    df_rec_partido = df_rec[df_rec["fonte_tipo"].isin(FONTES_PARTIDO)].copy()
    df_maior = calcular_dias_maior_receita(df_rec_partido)

    paineis = []
    for ano in ANOS:
        d = preparar_survival_maior(rrd_df, df_maior, ano)
        d = _add_grupo_cs(d, lookup, ano)
        paineis.append((str(ano), _km_painel(d, ano)))
    _plot_km(paineis, FIGS / "cap4_survival_km_maior.png")


# ── Figuras 2 e 3: fluxo cumulativo ─────────────────────────────────────────

def _plot_fluxo(df_cum, value_col, y_title, y_fmt_pct, out_path):
    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=(y_fmt_pct),
        subplot_titles=[str(a) for a in ANOS],
        horizontal_spacing=0.08,
    )
    for col, ano in enumerate(ANOS, start=1):
        for grupo in GRUPOS:
            d = df_cum[
                (df_cum["ano_eleicao"] == ano) & (df_cum["grupo_cs"] == grupo)
            ].sort_values("semana")
            if d.empty:
                continue
            y = d[value_col] / 1e6 if value_col == "cum_receita" else d[value_col]
            fig.add_trace(
                go.Scatter(
                    x=d["semana"], y=y,
                    mode="lines+markers", name=grupo,
                    showlegend=(col == 1),
                    line=dict(color=CORES[grupo], dash=DASHES[grupo], width=2),
                    marker=dict(size=6),
                ),
                row=1, col=col,
            )
    fig.update_layout(
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.15, yanchor="top",
                    title="Candidato (ex-ante)"),
        height=460, width=850, template="plotly_white",
        margin=dict(t=90, b=50),
    )
    fig.update_xaxes(title_text="Semana da campanha", dtick=1)
    if y_fmt_pct:
        fig.update_yaxes(tickformat=".0%", range=[0, 1.05])
    fig.update_yaxes(title_text=y_title, col=1)
    fig.write_image(str(out_path), scale=2)
    print(f"Salvo: {out_path}")


def fig_fluxo_cumulativo(rrd_df, lookup):
    """fig-semana-campanha e fig-semana-abs: fluxo acumulado por semana,
    so por candidato_competitivo, restrito a receitas de partido (FEFC+FP) em 2018/2022."""
    df_rec = carregar_receitas()
    df_rec_partido = df_rec[df_rec["fonte_tipo"].isin(FONTES_PARTIDO)].copy()
    df_rec_partido["dias_campanha"] = df_rec_partido.apply(
        lambda r: (r["dt_receita"] - JANELAS[r["ano_eleicao"]][0]).days, axis=1
    )
    df_rec_partido["semana"] = (df_rec_partido["dias_campanha"] // 7) + 1

    # _add_grupo_cs espera um ano fixo; aqui o ano varia por linha, então
    # mesclamos direto pela chave completa (ano, uf, partido, candidato).
    df_rec_cs = df_rec_partido.merge(
        lookup, on=["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato"], how="left"
    )
    df_rec_cs["candidato_competitivo"] = df_rec_cs["candidato_competitivo"].fillna(False)
    df_rec_cs["grupo_cs"] = df_rec_cs["candidato_competitivo"].map(
        {True: "Candidato competitivo", False: "Candidato não-competitivo"}
    )
    df_rec_cs = df_rec_cs[df_rec_cs["ano_eleicao"].isin(ANOS)].copy()

    df_cum = calc_cumulative(df_rec_cs, ["ano_eleicao", "grupo_cs"])

    _plot_fluxo(df_cum, "cum_prop", "Proporção acumulada", True,
                FIGS / "cap4_fluxo_cumulativo_prop.png")
    _plot_fluxo(df_cum, "cum_receita", "R$ acumulado (milhões)", False,
                FIGS / "cap4_fluxo_cumulativo_abs.png")


if __name__ == "__main__":
    rrd_df = carregar_rrd_survival()
    lookup = cs_lookup(rrd_df)

    survival_dfs = carregar_survival(rrd_df, lookup)
    regenerar_cox_survival(survival_dfs)
    fig_km_primeiro_repasse(survival_dfs)

    raw_dir = ROOT / "data" / "raw"
    if not raw_dir.exists():
        print(
            "\nAVISO: data/raw/ nao existe neste ambiente -- nao foi possivel gerar "
            "cap4_survival_km_maior.png, cap4_fluxo_cumulativo_prop.png e "
            "cap4_fluxo_cumulativo_abs.png."
        )
    else:
        fig_km_maior_repasse(rrd_df, lookup)
        fig_fluxo_cumulativo(rrd_df, lookup)
