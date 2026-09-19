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
repasse -- a leitura desses CSVs e pesada (~1-2 min). O primeiro repasse e o
modelo Cox tambem usam essas receitas: as datas sao recalculadas na copia de
trabalho, com a origem partidaria e a equivalencia PATRIOTA/PATRI em 2018.

Gera:
  data/processed/df_cox_survival.parquet (tbl-cox)
  figs/cap4_survival_km_primeiro.png     (fig-km-cs)
  figs/cap4_survival_km_maior.png        (fig-km-maior-cs)
  figs/cap4_fluxo_cumulativo_prop.png    (fig-semana-campanha)
  figs/cap4_fluxo_cumulativo_abs.png     (fig-semana-abs)
  figs/cap4_lift_semanal.png             (fig-lift-semanal; src/2_gold/cap4_lift_semanal.py)
  tese/reports/lift-semanal/             (lift_semanal.csv, reconciliacao.csv)
  tese/reports/fluxo-semanal/            (fluxo_semanal.csv)
  tese/reports/harmonizacao-cap4/        (verificacao, divergencias e pontos KM)

Execute da raiz do repositorio: python tese/scripts/regenerar_figuras_cap4.py
Apenas o lift semanal: python tese/scripts/regenerar_figuras_cap4.py --so-lift
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
    selecionar_receitas_partido,
    recalcular_primeiro_repasse,
    COVS_MODELO,
)

DATA_PATH = ROOT / "data" / "processed"
FIGS = ROOT / "figs"

COM_CRED = "Com credencial eleitoral prévia"
SEM_CRED = "Sem credencial eleitoral prévia"
ROTULOS_CS = {True: COM_CRED, False: SEM_CRED}
CORES = {COM_CRED: "black", SEM_CRED: "lightgrey"}
DASHES = {COM_CRED: "solid", SEM_CRED: "dot"}
GRUPOS = [COM_CRED, SEM_CRED]
ANOS = [2018, 2022]


# ── Dados base ─────────────────────────────────────────────────────────────

def carregar_rrd_survival(receitas=None):
    rrd = pd.read_parquet(DATA_PATH / "rrd_df_novo.parquet")
    rrd["nr_candidato"] = rrd["nr_candidato"].astype(str)
    receitas = carregar_receitas(ANOS) if receitas is None else receitas
    rrd["dias_primeiro_repasse_base"] = rrd["dias_desde_inicio"]
    rrd = recalcular_primeiro_repasse(rrd, receitas)
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
    d["grupo_cs"] = d["candidato_competitivo"].map(ROTULOS_CS)
    return d


def carregar_survival(rrd_df, lookup):
    survival_dfs = {}
    for ano in ANOS:
        d = preparar_survival(rrd_df, ano)
        survival_dfs[ano] = _add_grupo_cs(d, lookup, ano)
    return survival_dfs


def verificar_origem_partidaria(rrd_df, receitas):
    """Confronta primeiro repasse e totais na janela com a base de candidaturas."""
    keys = ["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato"]
    partido = selecionar_receitas_partido(receitas)
    observado = partido.groupby(keys, as_index=False).agg(
        primeira_data=("dt_receita", "min"), total_janela=("vr_receita", "sum")
    )
    inicio = observado["ano_eleicao"].map({a: JANELAS[a][0] for a in ANOS})
    observado["dias_recalculados"] = (observado["primeira_data"] - inicio).dt.days
    comparacao = rrd_df.loc[rrd_df["ano_eleicao"].isin(ANOS),
                           keys + ["dias_desde_inicio", "dias_primeiro_repasse_base",
                                   "vr_receita_recursos_partidos"]].merge(
        observado, on=keys, how="left", validate="many_to_one"
    )
    comparacao["primeiro_repasse_confere"] = (
        comparacao["dias_desde_inicio"].eq(comparacao["dias_recalculados"])
        | (comparacao["dias_desde_inicio"].isna() & comparacao["dias_recalculados"].isna())
    )
    comparacao["primeiro_repasse_corrigido"] = ~(
        comparacao["dias_desde_inicio"].eq(comparacao["dias_primeiro_repasse_base"])
        | (comparacao["dias_desde_inicio"].isna() & comparacao["dias_primeiro_repasse_base"].isna())
    )
    comparacao["diferenca_recursos"] = (
        comparacao["total_janela"].fillna(0)
        - comparacao["vr_receita_recursos_partidos"].fillna(0)
    )
    comparacao["total_diverge"] = comparacao["diferenca_recursos"].abs() > 0.01
    # O Cap. 3 usa a prestação de contas inteira. Decompõe o resíduo temporal
    # usando a mesma base de receitas e a mesma chave da construção de seus totais.
    rec_cap3 = pd.read_parquet(DATA_PATH / "receitas.parquet")
    rec_cap3 = selecionar_receitas_partido(rec_cap3)
    rec_cap3 = rec_cap3.loc[rec_cap3["ano_eleicao"].isin(ANOS)
                            & rec_cap3["ds_cargo"].eq("DEPUTADO FEDERAL")].copy()
    inicio = rec_cap3["ano_eleicao"].map({a: JANELAS[a][0] for a in ANOS})
    fim = rec_cap3["ano_eleicao"].map({a: JANELAS[a][1] for a in ANOS})
    fora = rec_cap3.loc[~rec_cap3["dt_receita"].between(inicio, fim)]
    keys_cap3 = ["ano_eleicao", "sg_uf", "nr_candidato"]
    fora = fora.groupby(keys_cap3)["vr_receita"].sum().rename("recursos_fora_janela")
    comparacao = comparacao.merge(fora, on=keys_cap3, how="left", validate="many_to_one")
    comparacao["recursos_fora_janela"] = comparacao["recursos_fora_janela"].fillna(0)
    comparacao["residuo_apos_janela"] = (
        comparacao["diferenca_recursos"] + comparacao["recursos_fora_janela"]
    )
    comparacao["total_reconciliado"] = comparacao["residuo_apos_janela"].abs() <= 0.01
    resumo = comparacao.groupby("ano_eleicao", as_index=False).agg(
        candidaturas=("nr_candidato", "size"),
        primeiro_repasse_confere=("primeiro_repasse_confere", "all"),
        primeiro_repasse_corrigido=("primeiro_repasse_corrigido", "sum"),
        candidaturas_total_divergente=("total_diverge", "sum"),
        diferenca_recursos=("diferenca_recursos", "sum"),
        recursos_fora_janela=("recursos_fora_janela", "sum"),
        total_reconciliado=("total_reconciliado", "all"),
    )
    out_dir = ROOT / "tese" / "reports" / "harmonizacao-cap4"
    out_dir.mkdir(parents=True, exist_ok=True)
    resumo.to_csv(out_dir / "verificacao.csv", index=False)
    comparacao.loc[comparacao["total_diverge"] | comparacao["primeiro_repasse_corrigido"]].to_csv(
        out_dir / "divergencias.csv", index=False
    )
    print(resumo.to_string(index=False))
    if not resumo["primeiro_repasse_confere"].all():
        raise ValueError("Primeiro repasse da base difere da origem partidária; ver harmonizacao-cap4.")
    if not resumo["total_reconciliado"].all():
        raise ValueError("Diferença de recursos não explicada pela janela; ver harmonizacao-cap4.")


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
    resumo = []
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
            for semana in (1, 2):
                resumo.append({"ano_eleicao": int(titulo), "grupo_cs": grupo,
                               "semana": semana, "sobrevivencia": float(kmf.predict(semana))})
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
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.18, yanchor="top"),
        height=440, width=850, template="plotly_white",
        margin=dict(t=90, b=50),
    )
    fig.update_xaxes(title_text="Semana da campanha", dtick=1)
    fig.update_yaxes(title_text="S(t)", range=[0, 1.05], col=1)
    fig.write_image(str(out_path), scale=2)
    out_dir = ROOT / "tese" / "reports" / "harmonizacao-cap4"
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(resumo).to_csv(out_dir / f"{out_path.stem}.csv", index=False)
    print(f"Salvo: {out_path}")


def fig_km_primeiro_repasse(survival_dfs):
    """fig-km-cs: dias ate o primeiro repasse, so por candidato_competitivo."""
    paineis = [(str(ano), _km_painel(survival_dfs[ano], ano)) for ano in ANOS]
    _plot_km(paineis, FIGS / "cap4_survival_km_primeiro.png")


def fig_km_maior_repasse(rrd_df, lookup, receitas=None):
    """fig-km-maior-cs: dias ate o maior repasse, so por candidato_competitivo."""
    df_rec = carregar_receitas(ANOS) if receitas is None else receitas
    df_rec_partido = selecionar_receitas_partido(df_rec)
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
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.15, yanchor="top"),
        height=460, width=850, template="plotly_white",
        margin=dict(t=90, b=50),
    )
    fig.update_xaxes(title_text="Semana da campanha", dtick=1)
    if y_fmt_pct:
        fig.update_yaxes(tickformat=".0%", range=[0, 1.05])
    fig.update_yaxes(title_text=y_title, col=1)
    fig.write_image(str(out_path), scale=2)
    print(f"Salvo: {out_path}")


def fig_fluxo_cumulativo(rrd_df, lookup, receitas=None):
    """fig-semana-campanha e fig-semana-abs: fluxo acumulado por semana,
    so por candidato_competitivo, origem Recursos de partido político em 2018/2022."""
    df_rec = carregar_receitas(ANOS) if receitas is None else receitas
    df_rec_partido = selecionar_receitas_partido(df_rec)
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
    df_rec_cs["grupo_cs"] = df_rec_cs["candidato_competitivo"].map(ROTULOS_CS)
    df_rec_cs = df_rec_cs[df_rec_cs["ano_eleicao"].isin(ANOS)].copy()

    df_cum = calc_cumulative(df_rec_cs, ["ano_eleicao", "grupo_cs"])
    out_dir = ROOT / "tese" / "reports" / "fluxo-semanal"
    out_dir.mkdir(parents=True, exist_ok=True)
    df_cum.to_csv(out_dir / "fluxo_semanal.csv", index=False)

    _plot_fluxo(df_cum, "cum_prop", "Proporção acumulada", True,
                FIGS / "cap4_fluxo_cumulativo_prop.png")
    _plot_fluxo(df_cum, "cum_receita", "R$ acumulado (milhões)", False,
                FIGS / "cap4_fluxo_cumulativo_abs.png")


# ── Figura 4: lift semanal do Top-NECr ──────────────────────────────────────

def fig_lift_semanal(receitas=None):
    """fig-lift-semanal: lift do Cap. 3 (competitivos ex-ante no Top-NECr) recalculado
    a cada semana sobre os recursos acumulados. O IC 95% por bootstrap de listas fica só
    no CSV (lift_ic95_*), fora da figura (decisão do autor em 19/09/2026).
    Grava tese/reports/lift-semanal/{lift_semanal,reconciliacao}.csv."""
    from cap4_lift_semanal import calcular_lift_semanal, reconciliar

    rrd = pd.read_parquet(DATA_PATH / "rrd_df_novo.parquet")
    tabela = calcular_lift_semanal(rrd, receitas=receitas)
    rec = reconciliar(rrd, tabela)

    out_dir = ROOT / "tese" / "reports" / "lift-semanal"
    out_dir.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(out_dir / "lift_semanal.csv", index=False)
    rec.to_csv(out_dir / "reconciliacao.csv", index=False)
    print(rec.round(4).to_string(index=False))
    _plot_lift_semanal(tabela, rec)


def _plot_lift_semanal(tabela, rec):
    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True,
        subplot_titles=[str(a) for a in ANOS], horizontal_spacing=0.06,
    )
    for col, ano in enumerate(ANOS, start=1):
        d = tabela[tabela["ano_eleicao"] == ano].sort_values("semana")
        fig.add_trace(
            go.Scatter(
                x=d["semana"], y=d["lift_competitivos"], mode="lines+markers",
                name="Lift semanal", showlegend=(col == 1),
                line=dict(color="black", width=2.5), marker=dict(size=6),
            ),
            row=1, col=col,
        )
        fig.add_trace(
            go.Scatter(
                x=[d["semana"].min(), d["semana"].max()],
                y=[rec.loc[rec["ano_eleicao"] == ano, "lift_cap3"].iloc[0]] * 2,
                mode="lines", name="Lift agregado (Cap. 3)",
                line=dict(color="grey", width=1.5, dash="dash"),
                showlegend=(col == 1),
            ),
            row=1, col=col,
        )
        fig.add_hline(y=1, line=dict(color="lightgrey", width=1, dash="dot"), row=1, col=col)
    fig.update_layout(
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.2, yanchor="top"),
        height=440, width=850, template="plotly_white", margin=dict(t=100, b=50),
    )
    fig.update_xaxes(title_text="Semana da campanha", dtick=1)
    fig.update_yaxes(title_text="Lift (credenciais prévias no Top-NECr)", range=[0.9, 2.3], col=1)
    out = FIGS / "cap4_lift_semanal.png"
    fig.write_image(str(out), scale=2)
    print(f"Salvo: {out}")


if __name__ == "__main__":
    if "--so-lift" in sys.argv:
        fig_lift_semanal()
        sys.exit(0)

    receitas = carregar_receitas(ANOS)
    rrd_df = carregar_rrd_survival(receitas)
    verificar_origem_partidaria(rrd_df, receitas)
    lookup = cs_lookup(rrd_df)

    survival_dfs = carregar_survival(rrd_df, lookup)
    regenerar_cox_survival(survival_dfs)
    fig_km_primeiro_repasse(survival_dfs)

    fig_km_maior_repasse(rrd_df, lookup, receitas)
    fig_fluxo_cumulativo(rrd_df, lookup, receitas)
    fig_lift_semanal(receitas)
