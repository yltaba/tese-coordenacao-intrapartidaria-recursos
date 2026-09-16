"""
cap4_plot_fortes_vagas.py
Análogo 2 de Cheibub & Sin (2020): número de candidatos fortes vs. vagas conquistadas
por lista — análise do excesso. Produz dois gráficos de barras 100% empilhadas:
  (a) usando definição de candidato forte (cap4_fig_fortes_vagas_pct.png)
  (b) usando NECr no lugar de candidatos fortes  (cap4_fig_nec_vagas_pct.png)
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from cap3_cs_features import FIGS_PATH, carregar_rrd, gerar_features

pio.renderers.default = "png"
FIGS_PATH.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Categorias e classificadores
# ---------------------------------------------------------------------------

CAT_ORDER_FORTES = [
    "Fortes <= Vagas + 1",
    "Fortes >= Vagas + 2",
]

CAT_ORDER_NEC = [
    "NEC <= Vagas + 1",
    "NEC >= Vagas + 2",
]

DM_ORDER = ["8–12", "16–31", "39–70", "Total"]


def _classificar_excesso_fortes(exc: int) -> str:
    return "Fortes <= Vagas + 1" if exc <= 1 else "Fortes >= Vagas + 2"


def _classificar_excesso_nec(exc: float) -> str:
    return "NEC <= Vagas + 1" if exc <= 1 else "NEC >= Vagas + 2"


# ---------------------------------------------------------------------------
# Preparação de listas
# ---------------------------------------------------------------------------


def gerar_listas_tab4(rrd: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega rrd ao nível de lista (partido × uf × ano) para listas com ≥1 vaga.
    Inclui contagem de candidatos fortes pelas duas definições (QE oficial e nominal).
    """
    dm_bins   = [0, 12, 31, 70]
    dm_labels = ["8–12", "16–31", "39–70"]

    listas = (
        rrd[rrd["n_seats"] > 0]
        .groupby(["ano_eleicao", "sg_uf", "sg_partido"], group_keys=False)
        .apply(
            lambda g: pd.Series({
                "n_seats":       g["n_seats"].iloc[0],
                "n_cands":       len(g),
                "n_fortes":      int(g["candidato_forte_cs"].sum()),
                "n_fortes_nom":  int(g["candidato_forte_cs_nom"].sum()),
                "qt_vaga":       g["qt_vaga"].iloc[0],
                "tipo_partido":  g["tipo_partido"].iloc[0],
            }),
            include_groups=False,
        )
        .reset_index()
    )

    listas["dm_grupo"] = pd.cut(listas["qt_vaga"], bins=dm_bins, labels=dm_labels)
    listas["excesso"]  = listas["n_fortes"] - listas["n_seats"]
    listas["tipo_lista"] = pd.Categorical(
        listas["excesso"].apply(_classificar_excesso_fortes),
        categories=CAT_ORDER_FORTES, ordered=True,
    )
    return listas


def gerar_listas_nec(rrd: pd.DataFrame, listas: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula NECr por lista e classifica o excesso (NECr_arredondado - vagas).
    Retorna listas enriquecidas com nec_recursos, excesso_nec e tipo_lista_nec.
    """
    rrd_com_rec = rrd[rrd["vr_receita_recursos_partidos"] > 0].copy()

    total_por_lista = (
        rrd_com_rec
        .groupby(["ano_eleicao", "sg_uf", "sg_partido"])["vr_receita_recursos_partidos"]
        .sum()
        .rename("total_recursos_lista")
        .reset_index()
    )
    rrd_com_rec = rrd_com_rec.merge(total_por_lista, on=["ano_eleicao", "sg_uf", "sg_partido"])
    rrd_com_rec["s_i_sq"] = (
        rrd_com_rec["vr_receita_recursos_partidos"] / rrd_com_rec["total_recursos_lista"]
    ) ** 2

    nec = (
        rrd_com_rec
        .groupby(["ano_eleicao", "sg_uf", "sg_partido"])
        .agg(sum_si_sq=("s_i_sq", "sum"))
        .reset_index()
    )
    nec["nec_recursos"] = 1.0 / nec["sum_si_sq"]

    listas_nec = listas.merge(
        nec[["ano_eleicao", "sg_uf", "sg_partido", "nec_recursos"]],
        on=["ano_eleicao", "sg_uf", "sg_partido"],
        how="inner",
    )
    listas_nec["excesso_nec"] = listas_nec["nec_recursos"].round() - listas_nec["n_seats"]
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
    """
    Calcula proporções por (ano, dm_grupo, categoria) e adiciona linha 'Total' por ano.

    Retorna DataFrame com colunas: ano_eleicao, dm_label, <cat_col>, pct, n, is_total.
    dm_label é Categorical na ordem DM_ORDER = ["8–12", "16–31", "39–70", "Total"].
    """
    # --- por magnitude ---
    por_dm = (
        df.groupby([ano_col, dm_col, cat_col], observed=True)
        .size().reset_index(name="n")
    )
    por_dm["total"] = por_dm.groupby([ano_col, dm_col], observed=True)["n"].transform("sum")
    por_dm["pct"]   = por_dm["n"] / por_dm["total"] * 100
    por_dm = por_dm.rename(columns={dm_col: "dm_label"})
    por_dm["is_total"] = False

    # --- por Total ---
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
    width: int = 900,
    height: int = 480,
) -> go.Figure:
    """
    Cria gráfico de barras 100% empilhadas com um painel (facet) por ano.

    Barras da coluna 'Total' usam cores de `cores_total` (mais claras/neutras) e
    recebem uma borda escura fina para sinalizar que são agregados — não magnitudes
    individuais.
    """
    anos = sorted(prop["ano_eleicao"].unique())
    fig = make_subplots(
        rows=1,
        cols=len(anos),
        subplot_titles=[str(a) for a in anos],
        shared_yaxes=True,
        horizontal_spacing=0.05,
    )

    for col_idx, ano in enumerate(anos, start=1):
        df_ano = prop[prop["ano_eleicao"] == ano]

        for cat in cat_order:
            df_t = (
                df_ano[df_ano[cat_col] == cat]
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
                    showlegend=(col_idx == 1),
                    legendgroup=cat,
                ),
                row=1,
                col=col_idx,
            )

    fig.update_layout(
        barmode="stack",
        bargap=0.35,
        legend_title=legend_title,
        template="plotly_white",
        width=width,
        height=height,
        margin=dict(t=60, b=50),
    )
    # Eixo y: só mostra título no painel esquerdo (shared_yaxes=True)
    fig.update_yaxes(range=[0, 105], ticksuffix="%")
    fig.update_yaxes(title_text="Proporção de listas (%)", col=1)
    # Eixo x: rótulo igual em todos os painéis
    fig.update_xaxes(title_text="Magnitude do distrito")

    return fig


# ---------------------------------------------------------------------------
# Figuras públicas
# ---------------------------------------------------------------------------


def plot_fortes_vagas_pct(listas: pd.DataFrame) -> go.Figure:
    """Barras 100% empilhadas: excesso de candidatos fortes (C&S) por ano e magnitude."""
    cores = {
        "Fortes <= Vagas + 1": "#1f4e79",
        "Fortes >= Vagas + 2": "#c55a11",
    }
    # Total: mesma matiz, mas mais clara — sinaliza coluna agregada
    cores_total = {
        "Fortes <= Vagas + 1": "#648aad",
        "Fortes >= Vagas + 2": "#e89d6b",
    }
    prop = _proporcoes(listas, "tipo_lista")
    return _stacked_bar_facet(
        prop, "tipo_lista", CAT_ORDER_FORTES, cores, cores_total,
        legend_title="Tipo de lista",
    )


def plot_nec_vagas_pct(listas_nec: pd.DataFrame) -> go.Figure:
    """Barras 100% empilhadas: excesso de NECr por ano e magnitude."""
    cores = {
        "NEC <= Vagas + 1": "#1f4e79",
        "NEC >= Vagas + 2": "#c55a11",
    }
    cores_total = {
        "NEC <= Vagas + 1": "#6fa3d4",
        "NEC >= Vagas + 2": "#e89d6b",
    }
    prop = _proporcoes(listas_nec, "tipo_lista_nec")
    return _stacked_bar_facet(
        prop, "tipo_lista_nec", CAT_ORDER_NEC, cores, cores_total,
        legend_title="Categoria",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    rrd = gerar_features(carregar_rrd())
    listas = gerar_listas_tab4(rrd)
    listas_nec = gerar_listas_nec(rrd, listas)

    ate_m1 = listas["excesso"].le(1).mean()
    ate_m0 = listas["excesso"].le(0).mean()
    print(f"Fortes ≤ Vagas+1: {ate_m1:.1%}  |  Fortes ≤ Vagas: {ate_m0:.1%}")

    sobrep = rrd[rrd["n_seats"] > 0].copy()
    sobrep["top_n"] = sobrep["rank_recursos"] <= sobrep["n_seats"]
    print(f"% top-N que são fortes: {sobrep[sobrep['top_n']]['candidato_forte_cs'].mean():.1%}")
    for ano in [2018, 2022]:
        sub = sobrep[sobrep["ano_eleicao"] == ano]
        print(f"  {ano} | top-N que são fortes: {sub[sub['top_n']]['candidato_forte_cs'].mean():.1%}")

    fig_fortes = plot_fortes_vagas_pct(listas)
    out_fortes = FIGS_PATH / "cap3_fig_fortes_vagas_pct.png"
    fig_fortes.write_image(out_fortes, scale=2)
    print(f"\nFigura salva em {out_fortes}")

    fig_nec = plot_nec_vagas_pct(listas_nec)
    out_nec = FIGS_PATH / "cap3_fig_nec_vagas_pct.png"
    fig_nec.write_image(out_nec, scale=2)
    print(f"Figura salva em {out_nec}")


if __name__ == "__main__":
    main()