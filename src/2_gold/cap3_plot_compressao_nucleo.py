"""
cap3_plot_compressao_nucleo.py
Figura B — barras parte-e-todo: a barra inteira é a nominata formal (mediana de
candidatos) e o segmento escuro é o núcleo efetivamente financiado (NECr
mediano), por magnitude do distrito e eleição (versão gráfica de
@tbl-compressao-necr-mag).

A compressão N/NECr aparece como a fração preenchida da barra; o rótulo ao fim
de cada barra dá os dois valores e o percentual NECr/N (calculado sobre as
medianas plotadas).

Insumo: data/processed/df_calibracao_lista.parquet
Saída:  figs/cap3_fig_compressao_nucleo.png
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from cap3_cs_features import FIGS_PATH, PROCESSED_DATA_PATH

pio.renderers.default = "png"
FIGS_PATH.mkdir(exist_ok=True)

CORES = {2018: "#2471A3", 2022: "#CB4335"}
CORES_CLARAS = {2018: "rgba(36, 113, 163, 0.22)", 2022: "rgba(203, 67, 53, 0.22)"}
ORDEM = ["Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)", "Total"]


def preparar_dados() -> pd.DataFrame:
    pan = pd.read_parquet(PROCESSED_DATA_PATH / "df_calibracao_lista.parquet")
    pan = pan[pan["ano_eleicao"].isin([2018, 2022])].copy()
    pan["magnitude"] = pan["dm_cat"].astype(str)

    def resumo(g):
        return pd.Series({
            "listas": len(g),
            "cands_med": g["n_cands"].median(),
            "necr_med": g["NECr"].median(),
        })

    por_dm = (
        pan.groupby(["ano_eleicao", "magnitude"])
        .apply(resumo, include_groups=False)
        .reset_index()
    )
    total = (
        pan.groupby("ano_eleicao")
        .apply(resumo, include_groups=False)
        .reset_index()
        .assign(magnitude="Total")
    )
    df = pd.concat([por_dm, total], ignore_index=True)
    df["magnitude"] = pd.Categorical(df["magnitude"], categories=ORDEM, ordered=True)
    return df.sort_values(["magnitude", "ano_eleicao"]).reset_index(drop=True)


def plot(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    # duas barras por magnitude (2018 acima, 2022 abaixo), Pequeno no topo
    y_pos = {}
    for i, mag in enumerate(ORDEM):
        base = (len(ORDEM) - 1 - i) * 2.2
        y_pos[(mag, 2018)] = base + 0.46
        y_pos[(mag, 2022)] = base - 0.46

    fmt = lambda v: f"{v:.1f}".replace(".", ",")

    for _, row in df.iterrows():
        mag, ano = row["magnitude"], row["ano_eleicao"]
        y = y_pos[(mag, ano)]
        necr, n = row["necr_med"], row["cands_med"]
        pct = necr / n

        # segmento escuro = NECr (núcleo financiado)
        fig.add_trace(go.Bar(
            x=[necr], y=[y],
            orientation="h",
            width=0.72,
            marker=dict(color=CORES[ano], line=dict(color="white", width=2)),
            showlegend=False,
            hoverinfo="skip",
        ))
        # segmento claro = demais candidaturas da nominata
        fig.add_trace(go.Bar(
            x=[n - necr], y=[y],
            base=[necr],
            orientation="h",
            width=0.72,
            marker=dict(color=CORES_CLARAS[ano], line=dict(color="white", width=2)),
            showlegend=False,
            hoverinfo="skip",
        ))
        # rótulo ao fim da barra: NECr de N (percentual)
        fig.add_annotation(
            x=n, y=y,
            text=f"<b>{fmt(necr)}</b> de {n:.0f}  ({pct:.0%})",
            showarrow=False,
            xanchor="left", xshift=8,
            font=dict(size=12, color="#39454e"),
        )
        # rótulo do ano, à esquerda da barra
        fig.add_annotation(
            x=0, y=y,
            text=str(ano),
            showarrow=False,
            xanchor="right", xshift=-8,
            font=dict(size=11, color=CORES[ano]),
        )

    # legenda de segmentos (traces fantasma, em cinza neutro)
    fig.add_trace(go.Bar(
        x=[None], y=[None], orientation="h",
        name="NECr (núcleo efetivamente financiado)",
        marker=dict(color="#5c6b76"),
    ))
    fig.add_trace(go.Bar(
        x=[None], y=[None], orientation="h",
        name="Demais candidaturas da nominata",
        marker=dict(color="rgba(92, 107, 118, 0.22)"),
    ))

    ticks = {mag: (y_pos[(mag, 2018)] + y_pos[(mag, 2022)]) / 2 for mag in ORDEM}
    fig.update_layout(
        template="plotly_white",
        barmode="overlay",
        width=950,
        height=560,
        margin=dict(l=150, r=110, t=50, b=70),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.09),
        xaxis=dict(
            title="Candidatos por lista (mediana)",
            range=[0, 46],
            showgrid=True,
            gridcolor="#e8eaec",
            zeroline=False,
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=[ticks[m] for m in ORDEM],
            ticktext=[f"<b>{m}</b>" if m == "Total" else m for m in ORDEM],
            showgrid=False,
            zeroline=False,
            range=[-1.3, (len(ORDEM) - 1) * 2.2 + 1.3],
        ),
    )
    return fig


def main():
    df = preparar_dados()
    print(df.round(2).to_string(index=False))
    fig = plot(df)
    out = FIGS_PATH / "cap3_fig_compressao_nucleo.png"
    fig.write_image(out, scale=2)
    print(f"\nFigura salva em {out}")


if __name__ == "__main__":
    main()
