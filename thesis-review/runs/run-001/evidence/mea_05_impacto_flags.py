"""mea_05 — Impacto das definições alternativas de 'competitivo' (saída de mea_02) sobre
cobertura, precisão e lift do Top-NECr; unidade lista vs coligação/federação;
médias de competitivos por lista financiada (l. 117 e 175 do capítulo).
Execute da raiz (depois de mea_02): python thesis-review/runs/run-001/evidence/mea_05_impacto_flags.py
"""
from pathlib import Path
import unicodedata
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
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


def pesos(R, k):
    R = np.asarray(R, float)
    if k <= 0:
        return np.zeros(len(R))
    q = np.sort(R)[::-1][k - 1]
    above, tied = R > q, R == q
    return above.astype(float) + tied * ((k - above.sum()) / tied.sum())


ws = np.zeros(len(rrd)); ks = np.zeros(len(rrd), int)
for _, idx in rrd.groupby(["ano_eleicao", "sg_uf", "lista"]).indices.items():
    R = rrd.R.to_numpy()[idx]; tot = R.sum()
    k = int(np.floor(1 / ((R / tot) ** 2).sum() + 0.5)) if tot > 0 else 0
    ws[idx] = pesos(R, k); ks[idx] = k
rrd["w"] = ws; rrd["k"] = ks
rrd["C"] = rrd.groupby(["ano_eleicao", "sg_uf", "lista"]).R.transform("size")

flags = pd.concat([pd.read_csv(OUT / f"mea_02_flags_{y}.csv", dtype={"nr_candidato": str}) for y in [2018, 2022]])
flags["nr_candidato"] = flags.nr_candidato.astype(str)
rrd["nr_candidato"] = rrd.nr_candidato.astype(str)
m = rrd.merge(flags[["ano_eleicao", "sg_uf", "nr_candidato", "comp_rrd", "comp_texto", "comp_cod_ok"]],
              on=["ano_eleicao", "sg_uf", "nr_candidato"], how="left", validate="one_to_one")
assert m.comp_rrd.notna().all()

rows = []
for y, g in m.groupby("ano_eleicao"):
    L = g.groupby(["sg_uf", "lista"])
    for flag in ["comp_rrd", "comp_texto", "comp_cod_ok"]:
        G = L[flag].sum(); H = g.assign(h=g.w * g[flag]).groupby(["sg_uf", "lista"]).h.sum()
        k = L.k.first(); C = L.C.first()
        A0 = (G * k / C).sum()
        rows.append(dict(ano=y, flag=flag, G=int(G.sum()), sum_k=int(k.sum()), H=round(H.sum(), 3),
                         cobertura=round(H.sum() / G.sum(), 4), precisao=round(H.sum() / k.sum(), 4),
                         cob_acaso=round(A0 / G.sum(), 4), lift=round(H.sum() / A0, 4)))
tab = pd.DataFrame(rows)
print("Top-NECr x competitivos, por definição da flag:\n", tab.to_string(index=False))
tab.to_csv(OUT / "mea_05_metricas_por_flag.csv", index=False)

# --- médias de competitivos por lista financiada (l. 117 / 175) --------------
print("\nCompetitivos (candidato_competitivo) por lista:")
for y, g in m.groupby("ano_eleicao"):
    L = g.groupby(["sg_uf", "lista"]).agg(F=("comp_rrd", "sum"), R=("R", "sum"), C=("C", "first"))
    fin = L[L.R > 0]
    print(f" {y}: todas as listas: média={L.F.mean():.3f} mediana={L.F.median():.0f} (n={len(L)}) | financiadas: média={fin.F.mean():.3f} mediana={fin.F.median():.0f} (n={len(fin)}) | competitivos em listas sem recursos={int(L[L.R<=0].F.sum())}")

# --- coligações (2018) e federações (2022) ------------------------------------
res = pd.read_parquet(ROOT / "data/processed/resultados.parquet",
                      columns=["ano_eleicao", "sg_uf", "ds_cargo", "sg_partido", "nr_candidato", "ds_composicao_coligacao"])
res = res[res.ano_eleicao.isin([2018, 2022]) & (res.ds_cargo.str.upper() == "DEPUTADO FEDERAL")].copy()
res["lista"] = res.sg_partido.map(norm)
res["comp"] = res.ds_composicao_coligacao.astype(str).map(norm)
res["n_partidos_comp"] = res.comp.str.count("/") + 1
res.loc[res.comp.isin(["#NULO", "#NULO#", "NAN", "NONE", ""]), "n_partidos_comp"] = 1
print("\nComposição da lista no boletim (ds_composicao_coligacao):")
for y, g in res.groupby("ano_eleicao"):
    L = g.groupby(["sg_uf", "lista"]).agg(n_comp=("n_partidos_comp", "max"), comp=("comp", "first"))
    print(f" {y}: listas partido x UF = {len(L)}; em coligação/federação com >1 partido = {(L.n_comp>1).sum()} ({100*(L.n_comp>1).mean():.1f}%); "
          f"candidaturas nessas listas = {int(g[g.n_partidos_comp>1].shape[0])} de {len(g)}")
    print("   exemplos:", L[L.n_comp > 1].comp.head(5).tolist())
