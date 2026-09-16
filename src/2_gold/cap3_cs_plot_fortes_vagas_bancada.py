"""
cap3_cs_plot_fortes_vagas_bancada.py
Análogo 2 de Cheibub & Sin (2020) — variante bancada.

Idêntico a cap3_cs_plot_fortes_vagas.py, mas substitui n_seats (vagas
conquistadas na eleição corrente) por n_deputados (bancada do partido na UF
em 16/08/2018 e 16/08/2022, via API da Câmara) como denominador.

Saídas:
  figs/cap3_fig_fortes_vagas_pct_bancada.png
  figs/cap3_fig_nec_vagas_pct_bancada.png
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from cap3_cs_features import FIGS_PATH, PROCESSED_DATA_PATH, carregar_rrd, gerar_features

pio.renderers.default = "png"
FIGS_PATH.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Bancada
# ---------------------------------------------------------------------------

def carregar_bancada() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DATA_PATH / "bancada_partido_uf.csv")
    mapa = {"PP**": "PP", "PCdoB": "PC do B", "PTdoB": "PT do B", "SD": "SOLIDARIEDADE"}
    df["sg_partido"] = df["sg_partido"].map(lambda x: mapa.get(x, x))
    return df[["ano_eleicao", "sg_partido", "sg_uf", "n_deputados"]]


# ---------------------------------------------------------------------------
# Categorias e classificadores
# ---------------------------------------------------------------------------

CAT_ORDER_FORTES = [
    "Candidatos competitivos <= Mp + 1",
    "Candidatos competitivos >= Mp + 2",
]

CAT_ORDER_NEC = [
    "NECr <= Mp + 1",
    "NECr >= Mp + 2",
]

DM_ORDER = ["8–12", "16–31", "39–70", "Total"]


def _classificar_excesso_fortes(exc: int) -> str:
    return "Candidatos competitivos <= Mp + 1" if exc <= 1 else "Candidatos competitivos >= Mp + 2"


def _classificar_excesso_nec(exc: float) -> str:
    return "NECr <= Mp + 1" if exc <= 1 else "NECr >= Mp + 2"


# ---------------------------------------------------------------------------
# Preparação de listas
# ---------------------------------------------------------------------------


def gerar_listas_tab4(rrd: pd.DataFrame, bancada: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega rrd ao nível de lista (partido × uf × ano).
    Usa n_deputados (bancada) como denominador em vez de n_seats.
    Inclui apenas listas com n_deputados >= 1.
    """
    dm_bins   = [0, 12, 31, 70]
    dm_labels = ["8–12", "16–31", "39–70"]

    listas = (
        rrd.groupby(["ano_eleicao", "sg_uf", "sg_partido"], group_keys=False)
        .apply(
            lambda g: pd.Series({
                "n_seats":       int(g["n_seats"].iloc[0]),
                "n_cands":       len(g),
                "n_fortes":      int(g["candidato_competitivo"].sum()),
                "n_fortes_nom":  int(g["candidato_competitivo_nom"].sum()),
                "qt_vaga":       g["qt_vaga"].iloc[0],
                "tipo_partido":  g["tipo_partido"].iloc[0],
            }),
            include_groups=False,
        )
        .reset_index()
    )

    listas = listas.merge(bancada, on=["ano_eleicao", "sg_partido", "sg_uf"], how="left")
    listas["n_deputados"] = listas["n_deputados"].fillna(0).astype(int)
    listas = listas[listas["n_deputados"] >= 1].copy()

    listas["dm_grupo"] = pd.cut(listas["qt_vaga"], bins=dm_bins, labels=dm_labels)
    listas["excesso"]  = listas["n_fortes"] - listas["n_deputados"]
    listas["tipo_lista"] = pd.Categorical(
        listas["excesso"].apply(_classificar_excesso_fortes),
        categories=CAT_ORDER_FORTES, ordered=True,
    )
    return listas


def _calcular_nec_col(rrd_sub: pd.DataFrame, rec_col: str) -> pd.DataFrame:
    """NECr por lista para uma coluna de recurso específica."""
    rrd_com_rec = rrd_sub[rrd_sub[rec_col] > 0].copy()
    total = (
        rrd_com_rec
        .groupby(["ano_eleicao", "sg_uf", "sg_partido"])[rec_col]
        .sum().rename("total_recursos_lista").reset_index()
    )
    rrd_com_rec = rrd_com_rec.merge(total, on=["ano_eleicao", "sg_uf", "sg_partido"])
    rrd_com_rec["s_i_sq"] = (rrd_com_rec[rec_col] / rrd_com_rec["total_recursos_lista"]) ** 2
    nec = (
        rrd_com_rec.groupby(["ano_eleicao", "sg_uf", "sg_partido"])
        .agg(sum_si_sq=("s_i_sq", "sum")).reset_index()
    )
    nec["nec_recursos"] = 1.0 / nec["sum_si_sq"]
    return nec[["ano_eleicao", "sg_uf", "sg_partido", "nec_recursos"]]


# (rótulo do painel, ano_eleicao, coluna de recurso)
_PANELS_NEC = [
    ("2018", 2018, "vr_receita_recursos_partidos"),
    ("2022", 2022, "vr_receita_recursos_partidos"),
]


def gerar_listas_nec(rrd: pd.DataFrame, listas: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula NECr por lista para 3 painéis (2014 Total + 2018 + 2022)
    e classifica o excesso em relação à bancada.
    """
    partes = []
    for painel, ano, rec_col in _PANELS_NEC:
        rrd_ano = rrd[rrd["ano_eleicao"] == ano]
        listas_ano = listas[listas["ano_eleicao"] == ano]
        nec = _calcular_nec_col(rrd_ano, rec_col)
        merged = listas_ano.merge(
            nec[["sg_uf", "sg_partido", "nec_recursos"]],
            on=["sg_uf", "sg_partido"],
            how="inner",
        ).copy()
        merged["painel"] = painel
        partes.append(merged)

    listas_nec = pd.concat(partes, ignore_index=True)
    painel_order = [p for p, _, _ in _PANELS_NEC]
    listas_nec["painel"] = pd.Categorical(listas_nec["painel"], categories=painel_order, ordered=True)
    listas_nec["excesso_nec"] = listas_nec["nec_recursos"].round() - listas_nec["n_deputados"]
    listas_nec["tipo_lista_nec"] = pd.Categorical(
        listas_nec["excesso_nec"].apply(_classificar_excesso_nec),
        categories=CAT_ORDER_NEC, ordered=True,
    )
    return listas_nec


# ---------------------------------------------------------------------------
# Helper: proporções por (ano × magnitude × categoria) + Total por ano
# ---------------------------------------------------------------------------


def _proporcoes(
    df: pd.DataFrame,
    cat_col: str,
    dm_col: str = "dm_grupo",
    ano_col: str = "ano_eleicao",
) -> pd.DataFrame:
    por_dm = (
        df.groupby([ano_col, dm_col, cat_col], observed=True)
        .size().reset_index(name="n")
    )
    por_dm["total"] = por_dm.groupby([ano_col, dm_col], observed=True)["n"].transform("sum")
    por_dm["pct"]   = por_dm["n"] / por_dm["total"] * 100
    por_dm = por_dm.rename(columns={dm_col: "dm_label"})
    por_dm["is_total"] = False

    por_total = (
        df.groupby([ano_col, cat_col], observed=True)
        .size().reset_index(name="n")
    )
    por_total["total"]    = por_total.groupby([ano_col], observed=True)["n"].transform("sum")
    por_total["pct"]      = por_total["n"] / por_total["total"] * 100
    por_total["dm_label"] = "Total"
    por_total["is_total"] = True

    prop = pd.concat([por_dm, por_total], ignore_index=True)
    prop["dm_label"] = pd.Categorical(prop["dm_label"], categories=DM_ORDER, ordered=True)
    return prop.sort_values([ano_col, "dm_label"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Helper compartilhado: barras 100% empilhadas com facets por ano
# ---------------------------------------------------------------------------


def _stacked_bar_facet(
    prop: pd.DataFrame,
    cat_col: str,
    cat_order: list,
    cores: dict,
    cores_total: dict,
    legend_title: str = "Categoria",
    width: int = 1300,
    height: int = 480,
    facet_col: str = "ano_eleicao",
) -> go.Figure:
    if hasattr(prop[facet_col], "cat"):
        paineis = prop[facet_col].cat.categories.tolist()
    else:
        paineis = sorted(prop[facet_col].unique())

    n = len(paineis)

    # Layout 2×3 para 5 painéis; caso contrário 1×n
    if n > 3:
        n_cols = 3
        n_rows = 2
        specs = [
            [{"type": "xy"}] * n_cols,
            [{"type": "xy"} if i < n - n_cols else None for i in range(n_cols)],
        ]
        pos = {p: (1 + i // n_cols, (i % n_cols) + 1) for i, p in enumerate(paineis)}
        fig = make_subplots(
            rows=n_rows, cols=n_cols,
            subplot_titles=[str(p) for p in paineis],
            specs=specs,
            vertical_spacing=0.18,
            horizontal_spacing=0.06,
        )
        fig_height = height * 2
        fig_width = width
    else:
        n_rows = 1
        pos = {p: (1, i + 1) for i, p in enumerate(paineis)}
        fig = make_subplots(
            rows=1, cols=n,
            subplot_titles=[str(p) for p in paineis],
            shared_yaxes=True,
            horizontal_spacing=0.05,
        )
        fig_height = height
        fig_width = width

    for painel in paineis:
        row, col = pos[painel]
        df_p = prop[prop[facet_col] == painel]

        for cat in cat_order:
            df_t = (
                df_p[df_p[cat_col] == cat]
                .sort_values("dm_label")
                .reset_index(drop=True)
            )
            is_total = df_t["is_total"].tolist()

            fig.add_trace(
                go.Bar(
                    name=cat,
                    x=df_t["dm_label"].astype(str),
                    y=df_t["pct"].round(1),
                    marker=dict(
                        color=[cores_total[cat] if t else cores[cat] for t in is_total],
                        line=dict(
                            color=["#444444" if t else "rgba(0,0,0,0)" for t in is_total],
                            width=[1.5 if t else 0.0 for t in is_total],
                        ),
                    ),
                    text=df_t["pct"].apply(lambda v: f"{v:.1f}%" if v >= 5 else ""),
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="white", size=11),
                    showlegend=bool(painel == paineis[0]),
                    legendgroup=cat,
                ),
                row=row,
                col=col,
            )

    fig.update_layout(
        barmode="stack",
        bargap=0.35,
        legend_title=legend_title,
        template="plotly_white",
        width=fig_width,
        height=fig_height,
        margin=dict(t=60, b=50),
    )
    fig.update_yaxes(range=[0, 105], ticksuffix="%")
    for r in range(1, n_rows + 1):
        fig.update_yaxes(title_text="Proporção de listas (%)", row=r, col=1)
    fig.update_xaxes(title_text="Magnitude do distrito")

    return fig


# ---------------------------------------------------------------------------
# Figuras públicas
# ---------------------------------------------------------------------------


def plot_fortes_vagas_pct(listas: pd.DataFrame) -> go.Figure:
    cores = {
        "Candidatos competitivos <= Mp + 1": "#1f4e79",
        "Candidatos competitivos >= Mp + 2": "#c55a11",
    }
    cores_total = {
        "Candidatos competitivos <= Mp + 1": "#648aad",
        "Candidatos competitivos >= Mp + 2": "#e89d6b",
    }
    prop = _proporcoes(listas, "tipo_lista")
    return _stacked_bar_facet(
        prop, "tipo_lista", CAT_ORDER_FORTES, cores, cores_total,
        legend_title="Tipo de lista",
    )


def plot_nec_vagas_pct(listas_nec: pd.DataFrame) -> go.Figure:
    cores = {
        "NECr <= Mp + 1": "#1f4e79",
        "NECr >= Mp + 2": "#c55a11",
    }
    cores_total = {
        "NECr <= Mp + 1": "#6fa3d4",
        "NECr >= Mp + 2": "#e89d6b",
    }
    prop = _proporcoes(listas_nec, "tipo_lista_nec", ano_col="painel")
    return _stacked_bar_facet(
        prop, "tipo_lista_nec", CAT_ORDER_NEC, cores, cores_total,
        legend_title="Categoria",
        width=1300,
        facet_col="painel",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    rrd = gerar_features(carregar_rrd())
    rrd = rrd[rrd["ano_eleicao"].isin([2018, 2022])].copy()
    bancada = carregar_bancada()

    # Verificação: totais esperados ~508 (2018) e ~513 (2022)
    print("Bancada por ano:", bancada.groupby("ano_eleicao")["n_deputados"].sum().to_dict())

    listas = gerar_listas_tab4(rrd, bancada)
    listas_nec = gerar_listas_nec(rrd, listas)

    ate_m1 = listas["excesso"].le(1).mean()
    ate_m0 = listas["excesso"].le(0).mean()
    print(f"Fortes <= Bancada+1: {ate_m1:.1%}  |  Fortes <= Bancada: {ate_m0:.1%}")

    ate_m1_nec = listas_nec["excesso_nec"].le(1).mean()
    ate_m0_nec = listas_nec["excesso_nec"].le(0).mean()
    print(f"NEC <= Bancada+1:   {ate_m1_nec:.1%}  |  NEC <= Bancada:   {ate_m0_nec:.1%}")

    sobrep = rrd.copy()
    sobrep["top_n"] = sobrep["rank_recursos"] <= sobrep["n_seats"]
    print(f"% top-N que são competitivos: {sobrep[sobrep['top_n']]['candidato_competitivo'].mean():.1%}")
    for ano in [2018, 2022]:
        sub = sobrep[sobrep["ano_eleicao"] == ano]
        print(f"  {ano} | top-N que são competitivos: {sub[sub['top_n']]['candidato_competitivo'].mean():.1%}")

    fig_fortes = plot_fortes_vagas_pct(listas)
    out_fortes = FIGS_PATH / "cap3_fig_fortes_vagas_pct_bancada.png"
    fig_fortes.write_image(out_fortes, scale=2)
    print(f"\nFigura salva em {out_fortes}")

    fig_nec = plot_nec_vagas_pct(listas_nec)
    out_nec = FIGS_PATH / "cap3_fig_nec_vagas_pct_bancada.png"
    fig_nec.write_image(out_nec, scale=2)
    print(f"Figura salva em {out_nec}")


if __name__ == "__main__":
    main()
