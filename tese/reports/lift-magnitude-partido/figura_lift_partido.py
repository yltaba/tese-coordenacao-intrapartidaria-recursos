"""Teste de figura: lift do Top-NECr por partido (alvo principal: competitivos
prévios), agregado 2018+2022.

Dot plot horizontal, partidos ordenados por lift decrescente. Cor = confiança
(reliável vs. denominador esperado pequeno); tamanho do marcador = volume de
informação (E esperado). Linha de referência em lift = 1 (nível do acaso).

Ainda em teste — filtros/composição podem mudar antes de entrar no capítulo.

Uso:
    python figura_lift_partido.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FONTE = HERE / "lift_por_partido.csv"
DESTINO = HERE / "figuras" / "lift_partido_competitivos.png"

# Paleta (tese/reports/lift-magnitude-partido — validada via skill dataviz)
COR_ACENTO = "#2a78d6"       # confiável (denominador_pequeno == False)
COR_CINZA = "#b3b1a8"        # denominador pequeno (de-ênfase)
COR_TEXTO_PRIMARIO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_TEXTO_MUTED = "#898781"
COR_GRADE = "#e1e0d9"
COR_BASELINE = "#c3c2b7"
COR_ANEL = "#fcfcfb"         # surface ring ao redor dos marcadores


def carregar() -> pd.DataFrame:
    t = pd.read_csv(FONTE, encoding="utf-8")
    sub = t[(t["ano_eleicao"] == "2018+2022") & (t["alvo"] == "competitivos")].copy()
    sub = sub.dropna(subset=["lift"])
    return sub.sort_values("lift", ascending=True).reset_index(drop=True)


def plotar(sub: pd.DataFrame) -> None:
    n = len(sub)
    fig_h = max(6.0, 0.26 * n)
    fig, ax = plt.subplots(figsize=(7.5, fig_h), dpi=200)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    y = np.arange(n)
    cores = np.where(sub["denominador_pequeno"], COR_CINZA, COR_ACENTO)
    # Tamanho por área (sqrt do E esperado), piso para permanecer visível (>= 8px de diâmetro).
    tamanhos = 18 + 55 * np.sqrt(sub["E_esperado"].clip(lower=0) / sub["E_esperado"].max())

    ax.hlines(y, xmin=0, xmax=sub["lift"], colors=COR_GRADE, linewidth=1, zorder=1)
    ax.scatter(
        sub["lift"], y, s=tamanhos, c=cores, edgecolors=COR_ANEL, linewidths=1.2, zorder=3,
    )
    ax.axvline(1, color=COR_BASELINE, linewidth=1.5, zorder=2)
    ax.text(
        1, n - 0.3, " lift = 1 (nível do acaso)", color=COR_TEXTO_SECUNDARIO,
        fontsize=8, va="bottom", ha="left",
    )

    ax.set_yticks(y)
    ax.set_yticklabels(sub["sg_partido_norm"], fontsize=8, color=COR_TEXTO_PRIMARIO)
    ax.set_xlabel("Lift (competitivos prévios, 2018+2022)", fontsize=9, color=COR_TEXTO_SECUNDARIO)
    ax.set_xlim(left=0)

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COR_BASELINE)
    ax.tick_params(axis="x", colors=COR_TEXTO_MUTED, labelsize=8)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=COR_GRADE, linewidth=1, zorder=0)
    ax.set_axisbelow(True)

    # Legenda mínima: cor (confiabilidade) — tamanho fica só descrito na legenda da figura.
    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", markersize=8,
                   markerfacecolor=COR_ACENTO, markeredgecolor=COR_ANEL, label="E esperado ≥ 5 e ≥ 5 listas"),
        plt.Line2D([0], [0], marker="o", linestyle="", markersize=8,
                   markerfacecolor=COR_CINZA, markeredgecolor=COR_ANEL, label="Denominador pequeno (E < 5 ou < 5 listas)"),
    ]
    ax.legend(
        handles=handles, loc="lower right", frameon=False, fontsize=7.5,
        labelcolor=COR_TEXTO_SECUNDARIO,
    )

    ax.set_title(
        "Lift do Top-NECr por partido — competitivos prévios (2018+2022)",
        fontsize=10.5, color=COR_TEXTO_PRIMARIO, loc="left", pad=12,
    )

    fig.tight_layout()
    DESTINO.parent.mkdir(exist_ok=True)
    fig.savefig(DESTINO, facecolor=fig.get_facecolor())
    print(f"Figura salva em: {DESTINO}")


def main() -> None:
    sub = carregar()
    plotar(sub)


if __name__ == "__main__":
    main()
