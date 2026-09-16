"""
cap3_plot_compressao_dumbbell.py
Figura B — dumbbell: da nominata formal (mediana de candidatos) ao núcleo
financiado (NECr mediano), por magnitude do distrito e eleição
(versão gráfica de @tbl-compressao-necr-mag).

Ponto aberto = candidatos na nominata; ponto cheio = NECr; o segmento entre
eles é a compressão. A anotação ×N é a razão de compressão N/NECr
(mediana calculada lista a lista).

Insumo: data/processed/df_calibracao_lista.parquet
Saída:  figs/cap3_fig_compressao_dumbbell.png
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from cap3_cs_features import FIGS_PATH, PROCESSED_DATA_PATH

pio.renderers.default = "png"
FIGS_PATH.mkdir(exist_ok=True)

CORES = {2018: "#2471A3", 2022: "#CB4335"}
ORDEM = ["Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)", "Total"]


def preparar_dados() -> pd.DataFrame:
    pan = pd.read_parquet(PROCESSED_DATA_PATH / "df_calibracao_lista.parquet")
    pan = pan[pan["ano_eleicao"].isin([2018, 2022])].copy()
    pan["razao"] = pan["n_cands"] / pan["NECr"]
    # rótulos do painel usam en-dash; harmoniza com ORDEM
    pan["magnitude"] = pan["dm_cat"].astype(str)

    def resumo(g):
        return pd.Series({
            "listas": len(g),
            "cands_med": g["n_cands"].median(),
            "necr_med": g["NECr"].median(),
            "razao_med": g["razao"].median(),
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

    # duas linhas por magnitude (2018 acima, 2022 abaixo), Pequeno no topo
    y_pos = {}
    for i, mag in enumerate(ORDEM):
        base = (len(ORDEM) - 1 - i) * 2.2
        y_pos[(mag, 2018)] = base + 0.42
        y_pos[(mag, 2022)] = base - 0.42

    fmt = lambda v: f"{v:.1f}".replace(".", ",")

    for _, row in df.iterrows():
        mag, ano = row["magnitude"], row["ano_eleicao"]
        y = y_pos[(mag, ano)]
        cor = CORES[ano]

        # segmento NECr -> candidatos
        fig.add_trace(go.Scatter(
            x=[row["necr_med"], row["cands_med"]],
            y=[y, y],
            mode="lines",
            line=dict(color=cor, width=2.5),
            opacity=0.75,
            showlegend=False,
            hoverinfo="skip",
        ))
        # ponto cheio = NECr
        fig.add_trace(go.Scatter(
            x=[row["necr_med"]], y=[y],
            mode="markers",
            marker=dict(color=cor, size=12, line=dict(color="white", width=2)),
            showlegend=False,
            hovertemplate=f"{mag} · {ano}<br>NECr mediano: {fmt(row['necr_med'])}<extra></extra>",
        ))
        # ponto aberto = candidatos na nominata
        fig.add_trace(go.Scatter(
            x=[row["cands_med"]], y=[y],
            mode="markers",
            marker=dict(color="white", size=12, line=dict(color=cor, width=2.5)),
            showlegend=False,
            hovertemplate=f"{mag} · {ano}<br>Candidatos (mediana): {fmt(row['cands_med'])}<extra></extra>",
        ))
        # anotação da razão de compressão, à direita do ponto aberto
        fig.add_annotation(
            x=row["cands_med"], y=y,
            text=f"×{fmt(row['razao_med'])}",
            showarrow=False,
            xanchor="left", xshift=14,
            font=dict(size=12, color="#5c6b76"),
        )
        # rótulo do ano, à esquerda do ponto cheio
        fig.add_annotation(
            x=row["necr_med"], y=y,
            text=str(ano),
            showarrow=False,
            xanchor="right", xshift=-14,
            font=dict(size=11, color=cor),
        )

    # legenda de formas (traces fantasma)
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers", name="NECr (núcleo financiado)",
        marker=dict(color="#5c6b76", size=12, line=dict(color="white", width=2)),
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers", name="Candidatos na nominata",
        marker=dict(color="white", size=12, line=dict(color="#5c6b76", width=2.5)),
    ))

    ticks = {mag: (y_pos[(mag, 2018)] + y_pos[(mag, 2022)]) / 2 for mag in ORDEM}
    fig.update_layout(
        template="plotly_white",
        width=950,
        height=560,
        margin=dict(l=150, r=70, t=50, b=70),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.09),
        xaxis=dict(
            title="Candidatos por lista (mediana)",
            range=[0, 44],
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
            range=[-1.2, (len(ORDEM) - 1) * 2.2 + 1.2],
        ),
    )
    return fig


def main():
    df = preparar_dados()
    print(df.round(2).to_string(index=False))
    fig = plot(df)
    out = FIGS_PATH / "cap3_fig_compressao_dumbbell.png"
    fig.write_image(out, scale=2)
    print(f"\nFigura salva em {out}")


if __name__ == "__main__":
    main()
