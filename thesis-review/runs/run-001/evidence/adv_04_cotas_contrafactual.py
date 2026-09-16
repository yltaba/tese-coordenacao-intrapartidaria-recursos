"""adv_04 — 'Estimativa conservadora' por cotas (I-3-005, l. 179).

A estratificação de STA (sta_lift_por_sexo.csv) mantém o núcleo calculado com homens e mulheres
e só separa os grupos-alvo. Outra operacionalização de 'retirar as cotas do cálculo' é refazer
o Top-NECr (NECr, k, pesos) em listas só de homens: o núcleo passa a ser o que o partido escolhe
entre as candidaturas não cobertas pela reserva de 30 % do FEFC.
Reporta cobertura, precisão e lift dessas listas masculinas vs. agregado original.
Execute da raiz: python thesis-review/runs/run-001/evidence/adv_04_cotas_contrafactual.py
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


def metricas(d):
    d = d.copy()
    ws = np.zeros(len(d)); ks = np.zeros(len(d), int)
    for _, idx in d.groupby(grp).indices.items():
        R = d.R.to_numpy()[idx]; t = R.sum()
        k = int(np.floor(1 / ((R / t) ** 2).sum() + 0.5)) if t > 0 else 0
        ws[idx] = pesos(R, k); ks[idx] = k
    d["w"] = ws; d["k"] = ks; d["C"] = d.groupby(grp).R.transform("size")
    out = []
    for y, g in d.groupby("ano_eleicao"):
        for alvo in ["comp", "eleito"]:
            a = g.assign(h=g.w * g[alvo]).groupby(["sg_uf", "lista"]).agg(G=(alvo, "sum"), H=("h", "sum"), k=("k", "first"), C=("C", "first"))
            A0 = (a.G * a.k / a.C).sum()
            out.append(dict(ano=y, alvo=alvo, G=int(a.G.sum()), sum_k=int(a.k.sum()), cobertura=round(a.H.sum() / a.G.sum(), 4),
                            precisao=round(a.H.sum() / a.k.sum(), 4), lift=round(a.H.sum() / A0, 3)))
    return pd.DataFrame(out)


orig = metricas(rrd).assign(universo="todas (original)")
homens = metricas(rrd[rrd.mulher == 0]).assign(universo="só homens, Top-NECr refeito")
tab = pd.concat([orig, homens])
print(tab.to_string(index=False))
tab.to_csv(Path(__file__).parent / "adv_04_metricas.csv", index=False)
# parcela do FEFC/recursos partidários às mulheres
for y, g in rrd.groupby("ano_eleicao"):
    print(f"{y}: parcela dos recursos partidários a mulheres = {g.loc[g.mulher == 1, 'R'].sum() / g.R.sum():.3f}; "
          f"parcela de mulheres entre candidaturas = {g.mulher.mean():.3f}")
