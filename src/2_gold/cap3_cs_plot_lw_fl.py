"""
cap4_plot_lw_fl.py
Análogo 3 de Cheibub & Sin (2020): descontinuidade na fronteira eleito/não-eleito.
Compara recursos e timing entre pares de posições adjacentes (NNLW, NLW, LW, FL, SL, TL),
calculando diferenças ao nível da lista para evitar média de médias.

Saídas:
  figs/cap4_fig4a_diffs_recursos.png  — share de recursos (prop_vr_receita_candidato)
  figs/cap4_fig4b_diffs_timing.png    — timing (dias_desde_inicio)
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

from cap3_cs_features import FIGS_PATH, carregar_rrd, gerar_features

pio.renderers.default = "png"
FIGS_PATH.mkdir(exist_ok=True)

# Pares de posições adjacentes: (pos_a, pos_b, rótulo)
# diff = pos_a − pos_b  →  positivo significa pos_a recebe mais / antes
PARES = [
    (-2, -1, "NNLW–NLW"),
    (-1,  0, "NLW–LW"),
    ( 0,  1, "LW–FL"),
    ( 1,  2, "FL–SL"),
    ( 2,  3, "SL–TL"),
]
PAR_ORDER = ["NNLW–NLW", "NLW–LW", "LW–FL", "FL–SL", "SL–TL"]
DM_CATS   = ["Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)"]
CORES_DM  = {
    "Pequeno (8–12)": "#1f4e79",
    "Médio (16–31)":  "#2e75b6",
    "Grande (39–70)": "#9dc3e6",
}


# ---------------------------------------------------------------------------
# Preparação
# ---------------------------------------------------------------------------

def filtrar_posicoes(rrd: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra listas válidas (n_seats ≥ 2 e n_cands ≥ n_seats + 3, garantindo
    as 6 posições NNLW–TL) e retorna apenas candidatos nas posições de interesse.
    """
    mask = (
        (rrd["n_seats"] >= 2) &
        (rrd["n_cands"] >= rrd["n_seats"] + 3) &
        rrd["pos_relativa"].isin([-2, -1, 0, 1, 2, 3])
    )
    return rrd[mask].copy()


def calc_diffs_por_lista(df_pos: pd.DataFrame, var_col: str) -> pd.DataFrame:
    """
    Calcula, para cada par de posições adjacentes, a diferença média (pos_a − pos_b)
    ao nível da lista. Reporta por magnitude distrital e total.
    """
    lista_id_cols = ["ano_eleicao", "sg_uf", "sg_partido"]

    pivot = df_pos.pivot_table(
        index=lista_id_cols + ["dm_cat"],
        columns="pos_relativa",
        values=var_col,
        aggfunc="mean",
        observed=True,
    ).reset_index()

    anos = sorted(pivot["ano_eleicao"].unique())
    resultados = []
    for pos_a, pos_b, label in PARES:
        if pos_a not in pivot.columns or pos_b not in pivot.columns:
            continue
        diff = pivot[pos_a] - pivot[pos_b]

        for ano_val in list(anos) + ["Todos"]:
            mask = (pivot["ano_eleicao"] == ano_val) if ano_val != "Todos" else pd.Series(True, index=pivot.index)

            for dm in DM_CATS:
                vals = diff[mask & (pivot["dm_cat"] == dm)].dropna()
                if len(vals):
                    resultados.append({"ano_eleicao": ano_val, "par": label, "dm_cat": dm, "diff_media": vals.mean(), "n_listas": len(vals)})

            vals_all = diff[mask].dropna()
            resultados.append({"ano_eleicao": ano_val, "par": label, "dm_cat": "Todos", "diff_media": vals_all.mean(), "n_listas": len(vals_all)})

    return pd.DataFrame(resultados)


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def _base_bar_fig(diffs: pd.DataFrame, var_label: str) -> go.Figure:
    """Cria figura de barras agrupadas por magnitude, um painel por ano eleitoral."""
    anos = sorted(a for a in diffs["ano_eleicao"].unique() if a != "Todos")
    fig = make_subplots(
        rows=1, cols=len(anos),
        subplot_titles=[str(a) for a in anos],
        shared_yaxes=True,
    )
    for col_idx, ano in enumerate(anos, start=1):
        df_ano = diffs[(diffs["ano_eleicao"] == ano) & (diffs["dm_cat"] != "Todos")]
        for dm in DM_CATS:
            df_dm = df_ano[df_ano["dm_cat"] == dm].copy()
            df_dm["par"] = pd.Categorical(df_dm["par"], categories=PAR_ORDER, ordered=True)
            df_dm = df_dm.sort_values("par")
            fig.add_trace(
                go.Bar(
                    name=dm.split(" (")[0],
                    x=df_dm["par"],
                    y=df_dm["diff_media"],
                    marker_color=CORES_DM[dm],
                    showlegend=(col_idx == 1),
                    legendgroup=dm,
                ),
                row=1, col=col_idx,
            )
        fig.update_xaxes(title_text="Par de candidatos", row=1, col=col_idx)
    fig.update_layout(
        barmode="group",
        legend_title="Magnitude",
        yaxis_title=var_label,
        width=1500, height=500,
        template="plotly_white",
    )
    return fig


def plot_diffs_recursos(diffs: pd.DataFrame) -> go.Figure:
    """
    Barras agrupadas: diferença média no share de recursos (LW−FL positivo = LW recebe mais).
    Realça LW–FL (fronteira eleito/não-eleito). Um painel por ano.
    """
    fig = _base_bar_fig(diffs, "Diferença média no share de recursos")
    anos = sorted(a for a in diffs["ano_eleicao"].unique() if a != "Todos")
    y_min = min(0.0, diffs.loc[diffs["ano_eleicao"] != "Todos", "diff_media"].min()) * 1.2
    y_max = max(0.0, diffs.loc[diffs["ano_eleicao"] != "Todos", "diff_media"].max()) * 1.2
    for col_idx in range(1, len(anos) + 1):
        fig.add_shape(
            type="rect",
            x0=1.5, x1=2.5,
            y0=y_min, y1=y_max,
            fillcolor="rgba(255,200,0,0.15)",
            line_width=0,
            row=1, col=col_idx,
        )
    fig.update_layout(
        title=(
            "Diferença média de recursos entre pares de candidatos na mesma lista<br>"
            "<sup>Share de recursos do partido. Posições definidas por rank de votos. "
            "Região sombreada = fronteira eleito/não-eleito (LW–FL).</sup>"
        ),
    )
    return fig


def plot_diffs_timing(diffs: pd.DataFrame) -> go.Figure:
    """
    Barras agrupadas: diferença média em dias até o primeiro repasse (NLW−LW positivo = LW recebe antes).
    Realça LW–FL. Um painel por ano.
    """
    fig = _base_bar_fig(diffs, "Diferença média (dias)")
    anos = sorted(a for a in diffs["ano_eleicao"].unique() if a != "Todos")
    y_min = diffs.loc[diffs["ano_eleicao"] != "Todos", "diff_media"].min() * 1.2
    y_max = diffs.loc[diffs["ano_eleicao"] != "Todos", "diff_media"].max() * 1.2
    for col_idx in range(1, len(anos) + 1):
        fig.add_shape(
            type="rect",
            x0=1.5, x1=2.5,
            y0=y_min, y1=y_max,
            fillcolor="rgba(255,200,0,0.15)",
            line_width=0,
            row=1, col=col_idx,
        )
    return fig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    rrd = gerar_features(carregar_rrd())
    df_pos = filtrar_posicoes(rrd)

    print(f"Observações por posição ({len(df_pos):,} total):")
    print(df_pos.groupby("pos_relativa").size().to_string())
    print()

    diffs_rec = calc_diffs_por_lista(df_pos, "prop_vr_receita_candidato")
    print("Diferenças de recursos por par (total e por magnitude) — todos os anos:")
    print(
        diffs_rec[diffs_rec["ano_eleicao"] == "Todos"]
        .pivot(index="par", columns="dm_cat", values="diff_media")
        .reindex(PAR_ORDER)
        .round(4)
        .to_string()
    )
    print()

    df_pos["dias_desde_inicio_inv"] = -df_pos["dias_desde_inicio"]
    diffs_tim = calc_diffs_por_lista(df_pos, "dias_desde_inicio_inv")

    print("Diferenças de timing (dias) por par (total e por magnitude) — todos os anos:")
    print(
        diffs_tim[diffs_tim["ano_eleicao"] == "Todos"]
        .pivot(index="par", columns="dm_cat", values="diff_media")
        .reindex(PAR_ORDER)
        .round(2)
        .to_string()
    )

    fig_rec = plot_diffs_recursos(diffs_rec)
    out_rec = FIGS_PATH / "cap4_fig4a_diffs_recursos_ano.png"
    fig_rec.write_image(out_rec, scale=2)
    print(f"\nFigura salva em {out_rec}")

    fig_tim = plot_diffs_timing(diffs_tim)
    out_tim = FIGS_PATH / "cap4_fig4b_diffs_timing_ano.png"
    fig_tim.write_image(out_tim, scale=2)
    print(f"Figura salva em {out_tim}")


if __name__ == "__main__":
    main()
