"""mea_03 — Convenções não declaradas e benchmark:
 (a) referência aleatória com universo = todas as candidaturas (C_l, como o código) vs
     universo = recebedores de recursos positivos (alternativa do 03-formulas-propostas);
 (b) candidaturas com pertencimento fracionário (0 < w < 1) e listas com empate na fronteira;
 (c) piso/teto (existem em df_cobertura_top_necr_resumo.csv, não no capítulo);
 (d) competitivos por sexo (claim da l. 179 sobre cotas) e sexo dentro do núcleo;
 (e) métricas de competitivos com C_l/k_l integrais (fórmula do texto) vs válidos (código).
Execute da raiz: python thesis-review/runs/run-001/evidence/mea_03_benchmark_e_convencoes.py
"""
from pathlib import Path
import unicodedata
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
rrd = pd.read_parquet(ROOT / "data/processed/rrd_df_novo.parquet")
rrd = rrd[rrd.ano_eleicao.isin([2018, 2022])].copy()
ALIAS = {"PCDOB": "PC DO B", "PP**": "PP", "SD": "SOLIDARIEDADE", "PTDOB": "PT DO B"}


def norm(s):
    try:
        s = s.encode("latin-1").decode("utf-8")
    except Exception:
        pass
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").upper().strip()
    return ALIAS.get(s, s)


rrd["lista"] = rrd.sg_partido.map(norm)
rrd["R"] = rrd.vr_receita_recursos_partidos.fillna(0.0)
maj = ["n_eleicoes_prefeito", "n_eleicoes_deputado_estadual", "n_eleicoes_deputado_federal", "n_eleicoes_governador", "n_eleicoes_senador"]
rrd["comp"] = ((rrd[maj].fillna(0).sum(axis=1) > 0) | rrd.alcancou_10pct_qe_hist.fillna(False).astype(bool)).astype(float)
rrd["known"] = (rrd[maj].notna().all(axis=1) & rrd.alcancou_10pct_qe_hist.notna())
rrd.loc[~rrd.known, "comp"] = np.nan


def pesos(R, k):
    R = np.asarray(R, float)
    if k <= 0:
        return np.zeros(len(R))
    q = np.sort(R)[::-1][k - 1]
    above, tied = R > q, R == q
    return above.astype(float) + tied * ((k - above.sum()) / tied.sum())


ws = np.zeros(len(rrd)); ks = np.zeros(len(rrd), int)
for _, idx in rrd.groupby(["ano_eleicao", "sg_uf", "lista"]).indices.items():
    R = rrd.R.to_numpy()[idx]
    tot = R.sum()
    k = int(np.floor(1 / ((R / tot) ** 2).sum() + 0.5)) if tot > 0 else 0
    ws[idx] = pesos(R, k); ks[idx] = k
rrd["w"] = ws; rrd["k"] = ks
rrd["C"] = rrd.groupby(["ano_eleicao", "sg_uf", "lista"]).R.transform("size")
rrd["rec"] = (rrd.R > 0)
rrd["n_rec"] = rrd.groupby(["ano_eleicao", "sg_uf", "lista"]).rec.transform("sum")

for y, g in rrd.groupby("ano_eleicao"):
    print(f"\n===== {y} =====")
    L = g.groupby(["sg_uf", "lista"]).agg(C=("R", "size"), k=("k", "first"), n_rec=("rec", "sum"), E=("eleito", "sum"),
                                          E_rec=("eleito", lambda s: int(s[g.loc[s.index, "rec"]].sum())),
                                          H_e=("eleito", lambda s: float((s * g.loc[s.index, "w"]).sum())),
                                          G_c=("comp", "sum"), G_c_rec=("comp", lambda s: float(s[g.loc[s.index, "rec"]].sum())),
                                          H_c=("comp", lambda s: float((s.fillna(0) * g.loc[s.index, "w"]).sum())),
                                          n_valid=("known", "sum"), k_valid=("w", lambda s: float(s[g.loc[s.index, "known"]].sum())))
    # (a) benchmark
    A0_all_e = (L.E * L.k / L.C).sum()
    A0_rec_e = (L.E_rec * L.k / L.n_rec.where(L.n_rec > 0)).fillna(0).sum()
    A0_all_c = (L.G_c * L.k / L.n_valid.where(L.n_valid > 0)).fillna(0).sum()
    A0_rec_c = (L.G_c_rec * L.k / L.n_rec.where(L.n_rec > 0)).fillna(0).sum()
    print(f"(a) ELEITOS: H={L.H_e.sum():.3f} | A0 todas C={A0_all_e:.3f} lift={L.H_e.sum()/A0_all_e:.3f} | A0 recebedores={A0_rec_e:.3f} lift={L.H_e.sum()/A0_rec_e:.3f}")
    print(f"    eleitos com R=0: {int(L.E.sum()-L.E_rec.sum())} de {int(L.E.sum())}; candidaturas com R=0: {int((L.C-L.n_rec).sum())} de {int(L.C.sum())}")
    print(f"(a) COMPETITIVOS: H={L.H_c.sum():.3f} | A0 todas={A0_all_c:.3f} lift={L.H_c.sum()/A0_all_c:.3f} | A0 recebedores={A0_rec_c:.3f} lift={L.H_c.sum()/A0_rec_c:.3f}")
    print(f"    competitivos com R=0: {int(L.G_c.sum()-L.G_c_rec.sum())} de {int(L.G_c.sum())}")
    # cobertura máxima alcançável
    print(f"    cobertura máxima possível (só recebedores podem estar no núcleo): eleitos {L.E_rec.sum()/L.E.sum():.4f}, competitivos {L.G_c_rec.sum()/L.G_c.sum():.4f}")
    # (b) fracionários
    frac = g[(g.w > 0) & (g.w < 1)]
    print(f"(b) candidaturas com 0<w<1: {len(frac)} (em {frac.groupby(['sg_uf','lista']).ngroups} listas); eleitas entre elas: {int(frac.eleito.sum())}; competitivas: {int(frac.comp.fillna(0).sum())}; soma dos pesos fracionários: {frac.w.sum():.2f}")
    print(f"    candidaturas com w==1: {int((g.w==1).sum())}; posições k somadas: {int(L.k.sum())}")
    # (e) fórmula do texto (C_l, k_l integrais) vs válidos
    print(f"(e) COMPETITIVOS precisão com sum k integral = {L.H_c.sum()/L.k.sum():.4f} vs válidos = {L.H_c.sum()/L.k_valid.sum():.4f}; "
          f"lift com C_l integral = {L.H_c.sum()/((L.G_c*L.k/L.C).sum()):.4f} vs válidos = {L.H_c.sum()/A0_all_c:.4f}")
    # (d) sexo
    gg = g[g.mulher.notna()]
    t = gg.groupby("mulher").agg(n=("comp", "size"), comp=("comp", "mean"), no_nucleo=("w", "mean"), rec=("rec", "mean"))
    print("(d) por sexo (0=homem,1=mulher): n, % competitivas, peso médio no núcleo, % recebedoras:\n", t.round(4).to_string())
    print(f"    parcela das posições do núcleo ocupadas por mulheres: {gg[gg.mulher==1].w.sum()/gg.w.sum():.4f}; competitivas entre mulheres no núcleo (ponderado): {(gg[gg.mulher==1].w*gg[gg.mulher==1].comp.fillna(0)).sum()/gg[gg.mulher==1].w.sum():.4f}; entre homens no núcleo: {(gg[gg.mulher==0].w*gg[gg.mulher==0].comp.fillna(0)).sum()/gg[gg.mulher==0].w.sum():.4f}")

# (c) piso/teto
print("\n(c) piso/arredondado/teto (df_cobertura_top_necr_resumo.csv):")
r = pd.read_csv(ROOT / "data/processed/df_cobertura_top_necr_resumo.csv")
r["precisao"] = r.eleitos_top_necr / r.n_posicoes_top_necr
r["lift"] = r.eleitos_top_necr / r.eleitos_esperados_aleatorio
print(r[["ano_eleicao", "regra_k", "n_posicoes_top_necr", "cobertura", "precisao", "lift"]].round(4).to_string(index=False))
print("\nmenção a 'piso' ou 'teto' no capítulo:")
txt = (ROOT / "tese/03-medindo-coordenacao-intrapartidaria.qmd").read_text(encoding="utf-8")
print(" piso:", txt.count("piso"), "| teto:", txt.count("teto"), "| lceil:", txt.count("lceil"))
