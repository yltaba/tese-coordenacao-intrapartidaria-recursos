"""
cap3_cs_plot_necr_eficiencia_bancada.py
NECr / bancada — variante ex-ante com denominador Mp.

Layout 1 × 2: 2018 | 2022, com desagregação apenas por magnitude.
Para 2014 usa vr_receita_total; para 2018/2022 usa vr_receita_recursos_partidos.

Saída: figs/cap3_fig_nep_eficiencia_ano_bancada.png
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

from cap3_cs_features import FIGS_PATH, PROCESSED_DATA_PATH, carregar_rrd, gerar_features

pio.renderers.default = "png"
FIGS_PATH.mkdir(exist_ok=True)

# (rótulo do painel, ano_eleicao, coluna de recurso no rrd)
PANELS = [
    ("2018", 2018, "vr_receita_recursos_partidos"),
    ("2022", 2022, "vr_receita_recursos_partidos"),
]


# ---------------------------------------------------------------------------
# Bancada
# ---------------------------------------------------------------------------

def carregar_bancada() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DATA_PATH / "bancada_partido_uf.csv")
    mapa = {"PP**": "PP", "PCdoB": "PC do B", "PTdoB": "PT do B", "SD": "SOLIDARIEDADE"}
    df["sg_partido"] = df["sg_partido"].map(lambda x: mapa.get(x, x))
    return df[["ano_eleicao", "sg_partido", "sg_uf", "n_deputados"]]


# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------

def calcular_nec_lista_painel(
    rrd_ano: pd.DataFrame,
    bancada_ano: pd.DataFrame,
    rec_col: str,
    painel: str,
) -> pd.DataFrame:
    """NECr / bancada para um único painel (ano × definição de recurso)."""
    rrd_com_rec = rrd_ano[rrd_ano[rec_col] > 0].copy()

    total_por_lista = (
        rrd_com_rec
        .groupby(["sg_uf", "sg_partido"])[rec_col]
        .sum().rename("total_recursos_lista").reset_index()
    )
    rrd_com_rec = rrd_com_rec.merge(total_por_lista, on=["sg_uf", "sg_partido"])
    rrd_com_rec["s_i_sq"] = (rrd_com_rec[rec_col] / rrd_com_rec["total_recursos_lista"]) ** 2

    nec = (
        rrd_com_rec.groupby(["sg_uf", "sg_partido"])
        .agg(sum_si_sq=("s_i_sq", "sum")).reset_index()
    )
    nec["nec_recursos"] = 1.0 / nec["sum_si_sq"]

    list_meta = (
        rrd_ano.groupby(["sg_uf", "sg_partido"], observed=True)
        .agg(
            n_seats=("eleito", "sum"),
            dm_cat=("dm_cat", "first"),
        )
        .reset_index()
    )
    nec = nec.merge(list_meta, on=["sg_uf", "sg_partido"], how="left")
    nec = nec.merge(bancada_ano, on=["sg_partido", "sg_uf"], how="left")
    nec["n_deputados"] = nec["n_deputados"].fillna(0).astype(int)
    nec = nec[nec["n_deputados"] >= 1].copy()
    nec["nec_eficiencia"] = nec["nec_recursos"] / nec["n_deputados"]
    nec["painel"] = painel
    return nec


def resumir(nec_all: pd.DataFrame) -> pd.DataFrame:
    dm_order = ["Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)"]
    painel_order = [p for p, _, _ in PANELS]

    resumo = (
        nec_all.groupby(["painel", "dm_cat"], observed=True)
        .agg(media=("nec_eficiencia", "mean"), n=("nec_eficiencia", "count"))
        .reset_index()
    )
    resumo["dm_cat"] = pd.Categorical(resumo["dm_cat"], categories=dm_order, ordered=True)
    resumo["painel"] = pd.Categorical(resumo["painel"], categories=painel_order, ordered=True)
    return resumo.sort_values(["painel", "dm_cat"])


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def plot_nec_eficiencia(resumo: pd.DataFrame, n_por_painel: dict) -> go.Figure:
    """Layout 1 × 2: 2018 | 2022, com uma barra por faixa de magnitude."""
    paineis = resumo["painel"].cat.categories.tolist()

    subtitles = [f"{p}  (N={n_por_painel.get(p, '?')})" for p in paineis]

    fig = make_subplots(
        rows=1, cols=len(paineis),
        subplot_titles=subtitles,
        shared_yaxes=True,
        horizontal_spacing=0.06,
    )

    y_max = resumo["media"].max()

    for col_idx, painel in enumerate(paineis, start=1):
        df_p = resumo[resumo["painel"] == painel]
        df_p = df_p.sort_values("dm_cat")
        fig.add_trace(
            go.Bar(
                x=df_p["dm_cat"].astype(str),
                y=df_p["media"],
                marker_color="#1f4e79",
                text=df_p["media"].round(2),
                textposition="outside",
                showlegend=False,
            ),
            row=1, col=col_idx,
        )

    fig.update_yaxes(range=[0, y_max * 1.2])
    fig.update_yaxes(title_text="NECr / bancada (média)", col=1)
    fig.update_layout(
        width=1100,
        height=500,
        template="plotly_white",
        margin=dict(t=80, b=60),
    )
    return fig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    rrd = gerar_features(carregar_rrd())
    bancada = carregar_bancada()

    print("Bancada por ano:", bancada.groupby("ano_eleicao")["n_deputados"].sum().to_dict())

    partes = []
    for painel, ano, rec_col in PANELS:
        rrd_ano = rrd[rrd["ano_eleicao"] == ano].copy()
        bancada_ano = bancada[bancada["ano_eleicao"] == ano][
            ["sg_partido", "sg_uf", "n_deputados"]
        ].copy()
        df_p = calcular_nec_lista_painel(rrd_ano, bancada_ano, rec_col, painel)
        partes.append(df_p)

    nec_all = pd.concat(partes, ignore_index=True)
    n_por_painel = nec_all.groupby("painel").size().to_dict()

    print("\nNECr / bancada — N de listas e estatísticas por painel:")
    print(nec_all.groupby("painel")["nec_eficiencia"].describe().round(3))

    resumo = resumir(nec_all)
    print()
    print(resumo.to_string(index=False))

    fig = plot_nec_eficiencia(resumo, n_por_painel)
    out = FIGS_PATH / "cap3_fig_nep_eficiencia_ano_bancada.png"
    fig.write_image(out, scale=2)
    print(f"\nFigura salva em {out}")


if __name__ == "__main__":
    main()
