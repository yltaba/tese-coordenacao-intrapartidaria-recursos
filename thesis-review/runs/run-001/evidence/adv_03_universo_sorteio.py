"""adv_03 — Universo do sorteio de referência (I-3-003).

 (a) Decomposição exata: lift_todas = lift_recebedores x lift_receber, em que
     lift_receber = A0_rec / A0_todas mede quanto o grupo-alvo está sobrerrepresentado entre os
     recebedores (a decisão 'financiar x não financiar'). As duas margens são decisões do partido.
 (b) Perfil das candidaturas com R = 0: sexo, votos, competitivos, eleitos — testa a objeção de
     que o sorteio entre todas as C_l é inflado por candidaturas 'de preenchimento' de cota.
 (c) Nulo intermediário: sorteio entre candidaturas com R >= piso (R$ 1.000 e R$ 10.000),
     para ver se a queda do lift vem da margem zero ou de repasses simbólicos.
Execute da raiz: python thesis-review/runs/run-001/evidence/adv_03_universo_sorteio.py
"""
from pathlib import Path
import unicodedata
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / "data/processed"
ALIAS = {"PCDOB": "PC DO B", "PP**": "PP", "SD": "SOLIDARIEDADE", "PTDOB": "PT DO B"}


def nrm(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").upper().strip()


rrd = pd.read_parquet(P / "rrd_df_novo.parquet")
rrd = rrd[rrd.ano_eleicao.isin([2018, 2022])].copy()
rrd["lista"] = rrd.sg_partido.map(lambda s: ALIAS.get(nrm(s), nrm(s)))
rrd["R"] = rrd.vr_receita_recursos_partidos.fillna(0.0)
maj = ["n_eleicoes_prefeito", "n_eleicoes_deputado_estadual", "n_eleicoes_deputado_federal", "n_eleicoes_governador", "n_eleicoes_senador"]
rrd["comp"] = ((rrd[maj].fillna(0).sum(axis=1) > 0) | rrd.alcancou_10pct_qe_hist.fillna(False).astype(bool)).astype(float)
grp = ["ano_eleicao", "sg_uf", "lista"]


def pesos(R, k):
    if k <= 0:
        return np.zeros(len(R))
    q = np.sort(R)[::-1][k - 1]
    above, tied = R > q, R == q
    return above.astype(float) + tied * ((k - above.sum()) / tied.sum())


ws = np.zeros(len(rrd)); ks = np.zeros(len(rrd), int)
for _, idx in rrd.groupby(grp).indices.items():
    R = rrd.R.to_numpy()[idx]; t = R.sum()
    k = int(np.floor(1 / ((R / t) ** 2).sum() + 0.5)) if t > 0 else 0
    ws[idx] = pesos(R, k); ks[idx] = k
rrd["w"] = ws; rrd["k"] = ks
rrd["C"] = rrd.groupby(grp).R.transform("size")
rrd = rrd.merge(pd.read_csv(P / "quociente_eleitoral.csv", sep=";").rename(columns={"qe": "qe_csv"}), on=["ano_eleicao", "sg_uf"], how="left")

print("(a) Decomposição lift_todas = lift_rec x lift_receber")
for y in [2018, 2022]:
    g = rrd[rrd.ano_eleicao == y]
    for alvo in ["comp", "eleito"]:
        out = {}
        for nome, piso in [("todas", None), ("R>0", 0.0), ("R>=1mil", 1000.0), ("R>=10mil", 10000.0)]:
            elig = np.ones(len(g), bool) if piso is None else (g.R > piso).to_numpy() if piso == 0 else (g.R >= piso).to_numpy()
            gg = g.assign(e=elig, ge=g[alvo] * elig, h=g.w * g[alvo])
            a = gg.groupby(["sg_uf", "lista"]).agg(H=("h", "sum"), Ge=("ge", "sum"), nel=("e", "sum"), k=("k", "first"))
            # núcleo cabe no universo elegível? (k <= ne)
            viol = int((a.k > a.nel).sum())
            A0 = (a.Ge * a.k / a.nel.where(a.nel > 0)).fillna(0).sum()
            # listas com k > ne: esperado limitado a Ge (sorteio esgota o universo)
            A0c = np.where(a.k > a.nel, a.Ge, a.Ge * a.k / a.nel.where(a.nel > 0)).astype(float)
            A0c = np.nan_to_num(A0c).sum()
            out[nome] = (a.H.sum() / A0c, viol)
        lt, lr = out["todas"][0], out["R>0"][0]
        print(f"  {y} {alvo:6s}: lift todas={lt:.3f} | rec(R>0)={lr:.3f} | lift_receber={lt/lr:.3f} | "
              f"R>=1mil={out['R>=1mil'][0]:.3f} (listas k>universo: {out['R>=1mil'][1]}) | R>=10mil={out['R>=10mil'][0]:.3f} (listas k>universo: {out['R>=10mil'][1]})")

print("\n(b) Perfil das candidaturas com R = 0 x R > 0")
rrd["pct_qe"] = rrd.qt_votos_nominais / rrd.qe_csv
for y in [2018, 2022]:
    g = rrd[rrd.ano_eleicao == y]
    t = g.assign(zero=g.R <= 0).groupby("zero").agg(n=("R", "size"), mulher=("mulher", "mean"), comp=("comp", "mean"), eleito=("eleito", "mean"),
                                                   votos_mediana=("qt_votos_nominais", "median"), pct_qe_mediana=("pct_qe", "median"),
                                                   abaixo_1pct_qe=("pct_qe", lambda s: (s < 0.01).mean()))
    print(f"  {y}:\n{t.round(4).to_string()}")
    z = g[g.R <= 0]
    print(f"    R=0: mulheres = {int(z.mulher.sum())} de {len(z)} ({100*z.mulher.mean():.1f} %); competitivos = {int(z.comp.sum())}; eleitos = {int(z.eleito.sum())}; "
          f"R=0 em listas sem recursos = {int((z.k == 0).sum())}")
