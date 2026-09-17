"""Gera diretamente de rrd_df_novo.parquet as 5 figuras do Cap. 3 que dependem de
candidato_competitivo (e por isso mudaram com as correções I-3-002/I-3-001 de 2026-09-14):

  figs/cap3_fig_amplitude_barras.png
  figs/cap3_fig_concentracao_barras.png
  figs/cap3_fig_top_necr.png               (credenciais prévias; Resultados)
  figs/cap3_fig_top_necr_eleicao.png       (eleitos; Robustez)
  figs/cap3_fig_topx_competitividade.png   (Robustez)
  figs/cap3_fig_topx_eleicao.png           (Robustez)

Recomputa direto da base (mesma fórmula do capítulo, @eq-indicadores). É o único gerador das
figuras de Top-NECr e Top-X% do Cap. 3; a cadeia anterior (alternativas-top-necr ->
sensibilidade-top-x -> relatorio-consolidado-capitulo-3) foi removida em 16/09/2026.

Execute da raiz do repositório: python tese/scripts/regenerar_figuras_cap3.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "2_gold"))
from cap3_cs_features import gerar_features  # noqa: E402
from cap3_taa_features import _preparar, acertos_fracionarios  # noqa: E402

FIGS = ROOT / "figs"

PRETO, CINZA = "#222222", "#a6a6a6"
TAUS = [50, 60, 70, 80, 90, 95]
YEARS = [2018, 2022]
# Sem título geral nas imagens: o título vem da legenda da figura no .qmd.
REF_ALEATORIA = "Referência aleatória"


def carregar_listas():
    """Painel lista-nível (ano, UF, partido) com C, F (competitivo), E (eleito), NECr,
    k_arredondado e k por limiar Top-X%, calculado diretamente das candidaturas."""
    raw = pd.read_parquet(ROOT / "data/processed/rrd_df_novo.parquet")
    raw = raw[raw.ano_eleicao.isin(YEARS)].copy()
    df = _preparar(gerar_features(raw))

    linhas = []
    for (ano, uf, partido), g in df.groupby(["ano_eleicao", "sg_uf", "sg_partido_norm"]):
        recursos = g["vr_receita_recursos_partidos"].to_numpy(dtype=float)
        competitivo = g["candidato_competitivo"].to_numpy(dtype=float)
        eleito = g["eleito"].to_numpy(dtype=float)
        total = recursos.sum()
        C = len(g)

        if total > 0:
            necr = 1.0 / np.square(recursos / total).sum()
            k_arred = max(1, int(np.floor(necr + 0.5)))
            ordem = np.argsort(-recursos)
            cum = np.cumsum((recursos / total)[ordem])
        else:
            necr = np.nan
            k_arred = 0
            cum = np.zeros(C)

        reg = dict(
            ano_eleicao=ano, sg_uf=uf, sg_partido_norm=partido, C=C,
            F=competitivo.sum(), E=eleito.sum(), Recursos=total, NECr=necr,
            k_arredondado=k_arred,
            H_competitividade_topnecr=acertos_fracionarios(recursos, competitivo, k_arred) if k_arred else 0.0,
            H_eleicao_topnecr=acertos_fracionarios(recursos, eleito, k_arred) if k_arred else 0.0,
        )
        for tau in TAUS:
            if total > 0:
                k_tau = min(int(np.searchsorted(cum, tau / 100)) + 1, C)
            else:
                k_tau = 0
            reg[f"k_{tau}"] = k_tau
            reg[f"H_competitividade_{tau}"] = acertos_fracionarios(recursos, competitivo, k_tau) if k_tau else 0.0
            reg[f"H_eleicao_{tau}"] = acertos_fracionarios(recursos, eleito, k_tau) if k_tau else 0.0
        linhas.append(reg)

    return pd.DataFrame(linhas)


def nacional(listas, outcome, regra_col, h_col):
    """Cobertura/precisão/lift nacionais para um outcome ('competitividade'|'eleicao') e uma
    coluna de posições (k_arredondado ou k_{tau})."""
    alvo = "F" if outcome == "competitividade" else "E"
    out = {}
    for ano in YEARS:
        g = listas[listas.ano_eleicao == ano]
        sAlvo, sH, sK, sC = g[alvo].sum(), g[h_col].sum(), g[regra_col].sum(), g.C.sum()
        esperado = (g[alvo] * g[regra_col] / g.C).sum()
        out[ano] = dict(
            cobertura=100 * sH / sAlvo, cobertura_acaso=100 * esperado / sAlvo,
            precisao=100 * sH / sK if sK else np.nan, precisao_acaso=100 * esperado / sK if sK else np.nan,
            lift=sH / esperado if esperado else np.nan,
        )
    return out


def fmt(x, d=2):
    return f"{x:,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")


# ---------------------------------------------------------------------------
# 1) Amplitude e 2) Concentração — barras horizontais agrupadas
# ---------------------------------------------------------------------------

def fig_amplitude(listas):
    fund = listas[listas.Recursos > 0]
    metrics = [("C", "Candidaturas\ntotais"), ("F", "Candidaturas\ncompetitivas"), ("NECr", "NECr")]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4))
    for ax, (stat, titulo) in zip(axes, [("mean", "Média"), ("median", "Mediana")]):
        labels = [lbl for _, lbl in metrics]
        y = np.arange(len(labels))
        for i, ano in enumerate(YEARS):
            g = fund[fund.ano_eleicao == ano]
            vals = [getattr(g[m], stat)() for m, _ in metrics]
            offset = (i - 0.5) * 0.38
            bars = ax.barh(y + offset, vals, height=0.36, color=PRETO if ano == 2018 else CINZA, label=str(ano))
            for b, v in zip(bars, vals):
                ax.text(v + 0.15, b.get_y() + b.get_height() / 2, fmt(v), va="center", fontsize=9)
        ax.set_yticks(y, labels)
        ax.set_xlim(0, 17)
        ax.set_title(titulo)
        ax.set_xlabel("Candidaturas por nominata")
        ax.spines[["right", "top"]].set_visible(False)
        ax.invert_yaxis()
    axes[0].legend(loc="lower right", frameon=False)
    fig.tight_layout()
    out = FIGS / "cap3_fig_amplitude_barras.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"[fig_amplitude] {out}")


def fig_concentracao(listas):
    fund = listas[listas.Recursos > 0].copy()
    fund["Q"] = fund.C / fund.NECr
    fund["R"] = 100 * fund.NECr / fund.C
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    specs = [("Q", "C/NECr", 0, 5, ""), ("R", "NECr/C (%)", 0, 100, "%")]
    for ax, (col, titulo, xmin, xmax, suf) in zip(axes, specs):
        labels = ["Mediana", "Média"]
        y = np.arange(len(labels))
        for i, ano in enumerate(YEARS):
            g = fund[fund.ano_eleicao == ano][col]
            vals = [g.median(), g.mean()]
            offset = (i - 0.5) * 0.38
            bars = ax.barh(y + offset, vals, height=0.36, color=PRETO if ano == 2018 else CINZA, label=str(ano))
            for b, v in zip(bars, vals):
                ax.text(v + xmax * 0.02, b.get_y() + b.get_height() / 2, fmt(v) + suf, va="center", fontsize=9)
        ax.set_yticks(y, labels)
        ax.set_xlim(xmin, xmax)
        ax.set_title(titulo)
        ax.spines[["right", "top"]].set_visible(False)
    axes[0].legend(loc="lower right", frameon=False)
    fig.tight_layout()
    out = FIGS / "cap3_fig_concentracao_barras.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"[fig_concentracao] {out}")


# ---------------------------------------------------------------------------
# 3) Top-NECr: cobertura, precisão e lift — competitivos e eleitos, 2018 x 2022
# ---------------------------------------------------------------------------

def fig_top_necr(listas, outcome, out_path):
    """Uma linha (cobertura, precisão, lift) para um perfil. Credenciais prévias vão para
    Resultados (03-top-necr.png); eleitos, para Robustez (03-top-necr-eleicao.png)."""
    metricas = {"cobertura": "Cobertura (%)", "precisao": "Precisão (%)", "lift": "Lift (observado / referência)"}
    ymax = {"cobertura": 100, "precisao": 45, "lift": 3.4}
    nac = nacional(listas, outcome, "k_arredondado", f"H_{outcome}_topnecr")
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.6))
    for ax, (metric, label) in zip(axes, metricas.items()):
        for serie, cor, estilo, marker_fc in [("observado", PRETO, "-o", None), ("acaso", "#999999", ":o", "white")]:
            if metric == "lift":
                y = np.ones(2) if serie == "acaso" else [nac[a]["lift"] for a in YEARS]
            else:
                y = [nac[a][metric if serie == "observado" else metric + "_acaso"] for a in YEARS]
            ax.plot(YEARS, y, estilo, color=cor, lw=2, ms=6,
                    label="Top-NECr" if serie == "observado" else REF_ALEATORIA,
                    markerfacecolor=marker_fc or cor)
            for ano, v in zip(YEARS, y):
                ax.annotate(fmt(v, 2 if metric == "lift" else 1), (ano, v),
                            xytext=(0, -16 if serie == "acaso" else 9), textcoords="offset points",
                            ha="center", color=cor, fontsize=10)
        ax.set(title=label, xlim=(2017.3, 2022.7), ylim=(0, ymax[metric]), xticks=YEARS)
        ax.grid(axis="y", color="#e6eaed")
        ax.spines[["right", "top"]].set_visible(False)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", bbox_to_anchor=(0.5, 0.01), ncol=2, frameon=False)
    fig.tight_layout(rect=[0.01, 0.1, 0.99, 1], w_pad=2)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"[fig_top_necr:{outcome}] {out_path}")
    for ano in YEARS:
        print("   ", ano, {m: round(v, 3) for m, v in nac[ano].items()})


# ---------------------------------------------------------------------------
# 4) e 5) Sensibilidade Top-X%: competitivos e eleitos, 6 limiares x 3 indicadores x 2 anos
# ---------------------------------------------------------------------------

def fig_topx(listas, outcome, out_path):
    metricas = {"cobertura": "Cobertura (%)", "precisao": "Precisão (%)", "lift": "Lift (observado / referência)"}
    ymax = {"cobertura": 100, "precisao": 60, "lift": 4.0}
    h_topnecr_col = f"H_{outcome}_topnecr"
    nac_topnecr = nacional(listas, outcome, "k_arredondado", h_topnecr_col)

    fig, axes = plt.subplots(2, 3, figsize=(13.6, 8.4))
    handles_labels = None
    for row, ano in enumerate(YEARS):
        for col, (metric, label) in enumerate(metricas.items()):
            ax = axes[row, col]
            obs, aca = [], []
            for tau in TAUS:
                nac = nacional(listas, outcome, f"k_{tau}", f"H_{outcome}_{tau}")
                obs.append(nac[ano][metric])
                aca.append(nac[ano][metric if metric == "lift" else metric + "_acaso"] if metric != "lift" else 1.0)
            ax.plot(TAUS, obs, "-o", color=PRETO, lw=2, ms=5, label="Observado")
            ax.plot(TAUS, aca, ":o", color="#999999", lw=2, ms=5, markerfacecolor="white", label=REF_ALEATORIA)
            idx80 = TAUS.index(80)
            ax.plot(TAUS[idx80], obs[idx80], "o", color=PRETO, ms=10, zorder=5)
            ref = nac_topnecr[ano]["lift"] if metric == "lift" else nac_topnecr[ano][metric]
            ax.axhline(ref, color="#666666", lw=1.2, ls="--")
            if metric == "lift":
                ax.axhline(1, color="#bbbbbb", lw=1, ls=":")
            ax.set(title=f"{ano} · {label}", xlim=(48, 97), ylim=(0, ymax[metric]), xticks=TAUS)
            ax.set_xlabel("Limiar de recursos acumulados" if row == 1 else None)
            ax.grid(axis="y", color="#e6eaed")
            ax.spines[["right", "top"]].set_visible(False)
            if handles_labels is None and row == 0 and col == 0:
                handles_labels = ax.get_legend_handles_labels()
    fig.legend(*handles_labels, loc="lower center", bbox_to_anchor=(0.5, 0.01), ncol=2, frameon=False)
    fig.tight_layout(rect=[0.01, 0.06, 0.99, 1], h_pad=3, w_pad=2)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"[fig_topx:{outcome}] {out_path}")


def main():
    listas = carregar_listas()
    print(f"{len(listas)} nominatas (2018+2022)")
    fig_amplitude(listas)
    fig_concentracao(listas)
    # Resultados: só credenciais eleitorais prévias. Robustez: eleitos e Top-X%.
    fig_top_necr(listas, "competitividade", FIGS / "cap3_fig_top_necr.png")
    fig_top_necr(listas, "eleicao", FIGS / "cap3_fig_top_necr_eleicao.png")
    fig_topx(listas, "competitividade", FIGS / "cap3_fig_topx_competitividade.png")
    fig_topx(listas, "eleicao", FIGS / "cap3_fig_topx_eleicao.png")


if __name__ == "__main__":
    main()
