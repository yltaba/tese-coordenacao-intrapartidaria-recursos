"""
cap4_plot_necr_eficiencia.py
Análogo 1 de Cheibub & Sin (2020): eficiência da lista medida pelo NECr (Número Efetivo de
Candidatos em recursos) dividido pelas vagas conquistadas, por tipo de partido e magnitude.

Saída: figs/cap4_fig_nep_eficiencia_ano.png
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

from cap3_cs_features import FIGS_PATH, carregar_rrd, gerar_features

pio.renderers.default = "png"
FIGS_PATH.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------

def calcular_nec_por_lista(rrd: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula NECr = 1 / Σ(sᵢ²) por lista, onde sᵢ é o share de cada candidato
    nos recursos totais da lista. Inclui apenas candidatos com recursos > 0.
    Retorna DataFrame com colunas: ano_eleicao, sg_uf, sg_partido, nec_recursos,
    n_seats, tipo_partido, dm_cat, nec_eficiencia (= nec_recursos / n_seats).
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

    nec_lista = (
        rrd_com_rec
        .groupby(["ano_eleicao", "sg_uf", "sg_partido"])
        .agg(sum_si_sq=("s_i_sq", "sum"))
        .reset_index()
    )
    nec_lista["nec_recursos"] = 1.0 / nec_lista["sum_si_sq"]

    # Juntar metadados da lista
    list_meta = (
        rrd.groupby(["ano_eleicao", "sg_uf", "sg_partido"], observed=True)
        .agg(
            n_seats=("eleito", "sum"),
            tipo_partido=("tipo_partido", "first"),
            dm_cat=("dm_cat", "first"),
        )
        .reset_index()
    )
    nec_lista = nec_lista.merge(list_meta, on=["ano_eleicao", "sg_uf", "sg_partido"], how="left")
    nec_lista = nec_lista[nec_lista["n_seats"] >= 1].copy()
    nec_lista["nec_eficiencia"] = nec_lista["nec_recursos"] / nec_lista["n_seats"]
    return nec_lista


def resumir_nec_eficiencia(nec_lista: pd.DataFrame) -> pd.DataFrame:
    """Médias de nec_eficiencia por (ano, tipo_partido, dm_cat) + totais por ano."""
    dm_order = ["Todos", "Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)"]

    por_dm = (
        nec_lista
        .groupby(["ano_eleicao", "tipo_partido", "dm_cat"], observed=True)
        .agg(media=("nec_eficiencia", "mean"), n=("nec_eficiencia", "count"))
        .reset_index()
    )
    por_total = (
        nec_lista
        .groupby(["ano_eleicao", "tipo_partido"], observed=True)
        .agg(media=("nec_eficiencia", "mean"), n=("nec_eficiencia", "count"))
        .reset_index()
        .assign(dm_cat="Todos")
    )
    resumo = pd.concat([por_total, por_dm], ignore_index=True)
    resumo["dm_cat"] = pd.Categorical(resumo["dm_cat"], categories=dm_order, ordered=True)
    return resumo.sort_values(["ano_eleicao", "tipo_partido", "dm_cat"])


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def plot_nec_eficiencia(resumo: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras agrupadas: NECr/vagas por tipo de partido e magnitude,
    um painel por ano eleitoral.
    """
    tipo_ordem = ["Competitivo", "Menos competitivo"]
    cores = {"Competitivo": "#1f4e79", "Menos competitivo": "#c55a11"}
    anos = sorted(resumo["ano_eleicao"].unique())

    fig = make_subplots(
        rows=1, cols=len(anos),
        subplot_titles=[str(a) for a in anos],
        shared_yaxes=True,
    )

    for col_idx, ano in enumerate(anos, start=1):
        df_ano = resumo[resumo["ano_eleicao"] == ano]
        for tipo in tipo_ordem:
            df_t = df_ano[df_ano["tipo_partido"] == tipo].sort_values("dm_cat")
            fig.add_trace(
                go.Bar(
                    name=tipo,
                    x=df_t["dm_cat"].astype(str),
                    y=df_t["media"],
                    marker_color=cores[tipo],
                    text=df_t["media"].round(2),
                    textposition="outside",
                    showlegend=(col_idx == 1),
                    legendgroup=tipo,
                ),
                row=1, col=col_idx,
            )

    fig.update_layout(
        yaxis_title="NECr / vagas (média)",
        barmode="group",
        legend_title="Tipo de partido",
        width=1000,
        height=500,
        template="plotly_white",
    )
    return fig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    rrd = gerar_features(carregar_rrd())
    nec_lista = calcular_nec_por_lista(rrd)
    resumo = resumir_nec_eficiencia(nec_lista)

    print("NECr / vagas — estatísticas por ano:")
    print(nec_lista.groupby("ano_eleicao")["nec_eficiencia"].describe().round(3))
    print()
    print(resumo.to_string(index=False))

    fig = plot_nec_eficiencia(resumo)
    out = FIGS_PATH / "cap4_fig_nep_eficiencia_ano.png"
    fig.write_image(out, scale=2)
    print(f"\nFigura salva em {out}")


if __name__ == "__main__":
    main()
