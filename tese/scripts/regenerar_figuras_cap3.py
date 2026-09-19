"""Gera diretamente de rrd_df_novo.parquet as 5 figuras do Cap. 3 que dependem de
candidato_competitivo (e por isso mudaram com as correções I-3-002/I-3-001 de 2026-09-14):

  figs/cap3_fig_amplitude_barras.png
  figs/cap3_fig_concentracao_barras.png
  figs/cap3_fig_top_necr.png               (credenciais prévias; Resultados)
  figs/cap3_fig_top_necr_eleicao.png       (eleitos; Robustez)
  figs/cap3_fig_topx_competitividade.png   (Robustez)
  figs/cap3_fig_topx_eleicao.png           (Robustez)
  figs/cap3_fig_lift_partido.png           (lift por partido e ano, com teto e bancada; Robustez)

Os números da figura por partido ficam em
tese/reports/lift-magnitude-partido/lift_por_partido_ano.csv.

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
    fund["R"] = 100 * fund.NECr / fund.C
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    labels = ["Mediana", "Média"]
    y = np.arange(len(labels))
    for ano in YEARS:
        g = fund[fund.ano_eleicao == ano]["R"]
        vals = [g.median(), g.mean()]
        offset = 0.19 if ano == 2018 else -0.19
        bars = ax.barh(y + offset, vals, height=0.36, color=PRETO if ano == 2018 else CINZA, label=str(ano))
        for b, v in zip(bars, vals):
            ax.text(v + 100 * 0.02, b.get_y() + b.get_height() / 2, fmt(v) + "%", va="center", fontsize=9)
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 100)
    ax.set_title("NECr/C (%)")
    ax.spines[["right", "top"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False)
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


# ---------------------------------------------------------------------------
# 6) Lift do Top-NECr por partido e ano, com teto mecânico e bancada eleita
# ---------------------------------------------------------------------------

ALVOS_PARTIDO = {"competitividade": "F", "eleicao": "E"}


def lift_por_partido(listas):
    """Lift por (ano, partido) e alvo, na mesma razão de somas do lift nacional.

    Além de H e E = Σ G·k/C, traz o teto do lift (Hmax = Σ min(k, G): o núcleo não comporta
    mais acertos que min(k, G)), o lift normalizado (H−E)/(Hmax−E) e o DP do lift sob a
    hipótese nula hipergeométrica. Listas sem recursos (k = 0) não entram em H nem em E, mas
    seus eleitos contam na bancada."""
    d = listas.copy()
    k, C = d["k_arredondado"], d["C"]
    linhas = []
    for alvo, G_col in ALVOS_PARTIDO.items():
        G = d[G_col]
        p = G / C
        d[f"E_{alvo}"] = G * k / C
        d[f"Hmax_{alvo}"] = np.minimum(k, G)
        d[f"var_{alvo}"] = np.where(C > 1, k * p * (1 - p) * (C - k) / (C - 1).clip(lower=1), 0.0)
    for (ano, partido), g in d.groupby(["ano_eleicao", "sg_partido_norm"]):
        financiada = g["Recursos"] > 0
        base = dict(
            ano_eleicao=int(ano), sg_partido_norm=partido, n_listas=len(g),
            n_listas_financiadas=int(financiada.sum()),
            bancada=int(g["E"].sum()), bancada_listas_financiadas=int(g.loc[financiada, "E"].sum()),
        )
        for alvo in ALVOS_PARTIDO:
            H = g[f"H_{alvo}_topnecr"].sum()
            E = g[f"E_{alvo}"].sum()
            Hmax = g[f"Hmax_{alvo}"].sum()
            linhas.append(dict(
                base, alvo=alvo, H_observado=H, E_esperado=E, H_maximo=Hmax,
                lift=H / E if E > 0 else np.nan,
                teto_lift=Hmax / E if E > 0 else np.nan,
                lift_normalizado=(H - E) / (Hmax - E) if Hmax - E > 1e-9 else np.nan,
                dp_nulo_lift=np.sqrt(g[f"var_{alvo}"].sum()) / E if E > 0 else np.nan,
                denominador_pequeno=bool(E < 5),
            ))
    return pd.DataFrame(linhas)


def fig_lift_partido(tab, out_path):
    """Painéis 2018 | 2022; partidos com ≥1 eleito, ordenados pela bancada. Segmento cinza de
    1 até o teto do lift de eleitos; círculo = lift de eleitos (área ∝ bancada); losango vazado
    = lift de credenciais prévias. Cada marcador fica cinza quando o E do seu alvo é < 5."""
    wide = tab.pivot_table(
        index=["ano_eleicao", "sg_partido_norm", "bancada"], columns="alvo",
        values=["lift", "teto_lift", "E_esperado"],
    ).reset_index()
    wide.columns = ["_".join(c).strip("_") for c in wide.columns]
    wide = wide[wide["bancada"] > 0]

    n_por_ano = wide.groupby("ano_eleicao").size()
    n_max = n_por_ano.max()
    # Mesma altura de linha nos dois painéis, alinhados pelo topo: o de 2022 (menos partidos)
    # ocupa só as primeiras linhas da grade.
    fig = plt.figure(figsize=(12.5, 0.27 * n_max + 2.0))
    gs = fig.add_gridspec(n_max, 2, wspace=0.45)
    axes = [fig.add_subplot(gs[: n_por_ano[ano], i]) for i, ano in enumerate(YEARS)]
    area = lambda b: 14 + 3.2 * b  # noqa: E731 — área do marcador ∝ bancada
    COR_SEG, COR_PEQ = "#d9d9d9", "#b0b0b0"

    for ax, ano in zip(axes, YEARS):
        g = wide[wide.ano_eleicao == ano].sort_values(["bancada", "sg_partido_norm"], ascending=[True, False])
        y = np.arange(len(g))
        cor_ele = np.where(g["E_esperado_eleicao"] < 5, COR_PEQ, PRETO)
        cor_comp = np.where(g["E_esperado_competitividade"] < 5, COR_PEQ, PRETO)

        ax.hlines(y, 1, g["teto_lift_eleicao"], color=COR_SEG, lw=3, zorder=1)
        ax.scatter(g["teto_lift_eleicao"], y, marker="|", s=90, color="#8c8c8c", lw=1.5, zorder=2)
        ax.scatter(g["lift_eleicao"], y, s=area(g["bancada"]), color=cor_ele,
                   edgecolor="white", lw=1, alpha=0.9, zorder=3)
        # Losango por cima do círculo, para não sumir nas bancadas grandes.
        ax.scatter(g["lift_competitividade"], y, marker="D", s=26, facecolor="white",
                   edgecolor=cor_comp, lw=1.2, zorder=4)
        ax.axvline(1, color="#999999", lw=1, ls=":", zorder=0)

        ax.set_yticks(y)
        ax.set_yticklabels([f"{p} ({b})" for p, b in zip(g["sg_partido_norm"], g["bancada"])], fontsize=8.5)
        ax.set_ylim(-0.7, len(g) - 0.3)
        ax.set_title(str(ano), loc="left", fontsize=11)
        ax.set_xlim(-0.2, 10)
        ax.set_xticks(range(0, 11))
        ax.set_xlabel("Lift (observado / referência aleatória)")
        ax.grid(axis="x", color="#e6eaed")
        ax.set_axisbelow(True)
        ax.spines[["right", "top", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)

    handles = [
        plt.Line2D([], [], marker="o", ls="", color=PRETO, ms=9, label="Lift de eleitos (área ∝ bancada)"),
        plt.Line2D([], [], marker="D", ls="", mfc="white", mec=PRETO, ms=6, label="Lift de credenciais prévias"),
        plt.Line2D([], [], color=COR_SEG, lw=3, marker="|", mec="#8c8c8c", ms=10,
                   label="Faixa de 1 ao teto do lift de eleitos"),
        plt.Line2D([], [], marker="o", ls="", color=COR_PEQ, ms=9, label="Cinza: esperado ao acaso < 5"),
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False, fontsize=9)
    fig.subplots_adjust(left=0.13, right=0.98, top=0.96, bottom=0.1)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"[fig_lift_partido] {out_path}")


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
    tab_partido = lift_por_partido(listas)
    tab_partido.to_csv(ROOT / "tese/reports/lift-magnitude-partido/lift_por_partido_ano.csv",
                       index=False, encoding="utf-8")
    fig_lift_partido(tab_partido, FIGS / "cap3_fig_lift_partido.png")


if __name__ == "__main__":
    main()
