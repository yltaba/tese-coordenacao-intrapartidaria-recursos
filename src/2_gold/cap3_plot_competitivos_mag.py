"""
cap3_plot_competitivos_mag.py
Figura A — dot plot conectado: % de candidaturas competitivas por magnitude
do distrito, 2018 → 2022 (versão gráfica de @tbl-competitivos-mag).

Saída: figs/cap3_fig_competitivos_mag.png
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from cap3_cs_features import FIGS_PATH, carregar_rrd, gerar_features

pio.renderers.default = "png"
FIGS_PATH.mkdir(exist_ok=True)

CORES = {2018: "#2471A3", 2022: "#CB4335"}
ORDEM = ["Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)", "Total"]


def preparar_dados() -> pd.DataFrame:
    rrd = gerar_features(carregar_rrd())
    rrd = rrd[rrd["ano_eleicao"].isin([2018, 2022])]

    por_dm = (
        rrd.groupby(["ano_eleicao", "dm_cat"], observed=True)
        .agg(n_comp=("candidato_competitivo", "sum"), n_cands=("candidato_competitivo", "size"))
        .reset_index()
        .rename(columns={"dm_cat": "magnitude"})
    )
    total = (
        rrd.groupby("ano_eleicao")
        .agg(n_comp=("candidato_competitivo", "sum"), n_cands=("candidato_competitivo", "size"))
        .reset_index()
        .assign(magnitude="Total")
    )
    df = pd.concat([por_dm, total], ignore_index=True)
    df["pct"] = 100 * df["n_comp"] / df["n_cands"]
    df["magnitude"] = pd.Categorical(df["magnitude"], categories=ORDEM, ordered=True)
    return df.sort_values(["magnitude", "ano_eleicao"]).reset_index(drop=True)


def plot(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    # eixo y invertido: Pequeno no topo, Total embaixo
    y_pos = {mag: len(ORDEM) - 1 - i for i, mag in enumerate(ORDEM)}

    # segmentos conectores (por trás dos pontos)
    for mag in ORDEM:
        sub = df[df["magnitude"] == mag].set_index("ano_eleicao")["pct"]
        fig.add_trace(go.Scatter(
            x=[sub[2018], sub[2022]],
            y=[y_pos[mag], y_pos[mag]],
            mode="lines",
            line=dict(color="#9aa4ab", width=2),
            showlegend=False,
            hoverinfo="skip",
        ))

    # pontos por ano + rótulos diretos, afastados na direção da variação
    for ano in [2018, 2022]:
        sub = df[df["ano_eleicao"] == ano]
        posicoes = []
        for _, row in sub.iterrows():
            outro = df[(df["magnitude"] == row["magnitude"]) & (df["ano_eleicao"] != ano)]["pct"].iloc[0]
            posicoes.append("middle left" if row["pct"] <= outro else "middle right")
        fig.add_trace(go.Scatter(
            x=sub["pct"],
            y=[y_pos[m] for m in sub["magnitude"]],
            mode="markers+text",
            name=str(ano),
            marker=dict(color=CORES[ano], size=13, line=dict(color="white", width=2)),
            text=[f"{v:.1f}".replace(".", ",") for v in sub["pct"]],
            textposition=posicoes,
            textfont=dict(size=12, color=CORES[ano]),
            cliponaxis=False,
        ))

    fig.update_layout(
        template="plotly_white",
        width=850,
        height=420,
        margin=dict(l=140, r=60, t=40, b=70),
        legend=dict(title="Eleição", orientation="h", x=0.5, xanchor="center", y=1.12),
        xaxis=dict(
            title="Candidaturas competitivas na nominata (%)",
            range=[0, 20],
            ticksuffix="%",
            showgrid=True,
            gridcolor="#e8eaec",
            zeroline=False,
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=[y_pos[m] for m in ORDEM],
            ticktext=[f"<b>{m}</b>" if m == "Total" else m for m in ORDEM],
            showgrid=False,
            zeroline=False,
            range=[-0.6, len(ORDEM) - 0.4],
        ),
    )
    return fig


def main():
    df = preparar_dados()
    print(df.to_string(index=False))
    fig = plot(df)
    out = FIGS_PATH / "cap3_fig_competitivos_mag.png"
    fig.write_image(out, scale=2)
    print(f"\nFigura salva em {out}")


if __name__ == "__main__":
    main()
