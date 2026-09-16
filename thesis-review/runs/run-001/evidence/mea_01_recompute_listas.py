"""mea_01 — Recomputa NECr, k e cobertura (eleitos e competitivos) para listas
escolhidas a partir de data/processed/rrd_df_novo.parquet, com implementação
independente (sem importar src/), e confronta com df_cobertura_top_necr_lista.parquet.

Listas: (1) empate exato na fronteira k; (2) sem recursos partidários;
(3) E > k (mais eleitos que posições no núcleo). Também: casos-limite
(lista com 1 candidato, k = C, k > recebedores) e contagem de empates.

Execute da raiz: python thesis-review/runs/run-001/evidence/mea_01_recompute_listas.py
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


rrd["sg_partido_norm"] = rrd.sg_partido.map(norm)
rrd["R"] = rrd.vr_receita_recursos_partidos.fillna(0.0)
# competitivo (definição do código: cap3_cs_features.gerar_features)
maj = ["n_eleicoes_prefeito", "n_eleicoes_deputado_estadual", "n_eleicoes_deputado_federal",
       "n_eleicoes_governador", "n_eleicoes_senador"]
rrd["incumbente"] = rrd[maj].fillna(0).sum(axis=1) > 0
rrd["comp"] = rrd.incumbente | rrd.alcancou_10pct_qe_hist.fillna(False).astype(bool)
rrd["comp_known"] = rrd[maj].notna().all(axis=1) & rrd.alcancou_10pct_qe_hist.notna()


def pesos(R, k):
    """w_il conforme 03-formulas-propostas.qmd eq-w."""
    R = np.asarray(R, float)
    if k <= 0:
        return np.zeros(len(R))
    q = np.sort(R)[::-1][k - 1]
    above = R > q
    tied = R == q
    a, m = above.sum(), tied.sum()
    return above.astype(float) + tied * ((k - a) / m)


rows = []
for (ano, uf, p), g in rrd.groupby(["ano_eleicao", "sg_uf", "sg_partido_norm"], sort=True):
    R = g.R.to_numpy()
    C = len(g)
    tot = R.sum()
    if tot > 0:
        s = R / tot
        necr = 1 / (s ** 2).sum()
        k = int(np.floor(necr + 0.5))
    else:
        necr, k = np.nan, 0
    w = pesos(R, k)
    E = int(g.eleito.sum())
    H_e = float(w @ g.eleito.to_numpy(float))
    q = np.sort(R)[::-1][k - 1] if k > 0 else np.nan
    empate_fronteira = bool(k > 0 and ((R == q).sum() > 1) and ((R > q).sum() < k))
    rows.append(dict(ano=ano, uf=uf, partido=p, C=C, recebedores=int((R > 0).sum()), R_l=tot, NECr=necr, k=k,
                     soma_w=w.sum(), E=E, H_eleitos=H_e, esperado_eleitos=E * k / C,
                     G_comp=int(g.comp.sum()), H_comp=float(w @ g.comp.to_numpy(float)),
                     empate_fronteira=empate_fronteira, q=q,
                     n_no_bloco=int((R == q).sum()) if k > 0 else 0,
                     E_maior_k=E > k, k_igual_C=(k == C and k > 0), k_maior_recebedores=k > (R > 0).sum()))
L = pd.DataFrame(rows)
L.to_csv(OUT / "mea_01_listas_recomputadas.csv", index=False)

# --- confronto com o artefato canônico ---------------------------------
can = pd.read_parquet(ROOT / "data/processed/df_cobertura_top_necr_lista.parquet")
m = L.merge(can, left_on=["ano", "uf", "partido"], right_on=["ano_eleicao", "sg_uf", "sg_partido_norm"], how="outer", indicator=True)
print("merge:", m._merge.value_counts().to_dict())
assert (m._merge == "both").all()
print("NECr igual:", np.allclose(m.NECr_x.fillna(-1), m.NECr_y.fillna(-1)))
print("k igual:", (m.k == m.k_arredondado).all())
print("H_eleitos igual:", np.allclose(m.H_eleitos, m.eleitos_top_arredondado))
print("esperado igual:", np.allclose(m.esperado_eleitos, m.eleitos_esperados_aleatorio_arredondado))
print("C igual:", (m.C == m.n_candidatos).all(), "| E igual:", (m.E == m.n_eleitos).all())

# --- agregados nacionais ------------------------------------------------
print("\nAgregados nacionais (recomputados):")
for ano, g in L.groupby("ano"):
    print(f" {ano}: listas={len(g)} sem_rec={(g.R_l<=0).sum()} sumk={g.k.sum()} H_e={g.H_eleitos.sum():.4f} "
          f"cob_e={g.H_eleitos.sum()/g.E.sum():.4f} prec_e={g.H_eleitos.sum()/g.k.sum():.4f} "
          f"A0={g.esperado_eleitos.sum():.4f} lift_e={g.H_eleitos.sum()/g.esperado_eleitos.sum():.4f} "
          f"| empates na fronteira={g.empate_fronteira.sum()} E>k={g.E_maior_k.sum()} k==C={g.k_igual_C.sum()} "
          f"k>recebedores={g.k_maior_recebedores.sum()} C==1={(g.C==1).sum()} "
          f"eleitos em listas sem rec={g.loc[g.R_l<=0,'E'].sum()}")

# --- três listas escolhidas -------------------------------------------
sel = {}
sel["empate_fronteira"] = L[L.empate_fronteira & (L.E > 0)].sort_values("C").iloc[-1]
sel["sem_recursos"] = L[(L.R_l <= 0) & (L.E > 0)].iloc[0]
sel["E_maior_k"] = L[L.E_maior_k].sort_values("E").iloc[-1]
for nome, r in sel.items():
    g = rrd[(rrd.ano_eleicao == r.ano) & (rrd.sg_uf == r.uf) & (rrd.sg_partido_norm == r.partido)]
    g = g.sort_values("R", ascending=False)
    w = pesos(g.R.to_numpy(), int(r.k))
    tab = g[["nm_candidato", "R", "eleito", "comp"]].assign(w=w)
    print(f"\n=== {nome}: {r.ano} {r.uf} {r.partido} | C={r.C} recebedores={r.recebedores} R_l={r.R_l:,.2f} "
          f"NECr={r.NECr:.4f} k={r.k} sum_w={r.soma_w:.3f} E={r.E} H_eleitos={r.H_eleitos:.4f} "
          f"esperado={r.esperado_eleitos:.4f} G_comp={r.G_comp} H_comp={r.H_comp:.4f}")
    print(tab.head(max(int(r.k) + 3, 8)).to_string(index=False))
    can_r = can[(can.ano_eleicao == r.ano) & (can.sg_uf == r.uf) & (can.sg_partido_norm == r.partido)].iloc[0]
    print(f" canônico: NECr={can_r.NECr} k={can_r.k_arredondado} eleitos_top={can_r.eleitos_top_arredondado} "
          f"esperado={can_r.eleitos_esperados_aleatorio_arredondado}")

# --- empates: quantos empates em zero, quantos em valor positivo -------
print("\nEmpates na fronteira por valor de q:")
e = L[L.empate_fronteira]
print(e.groupby(["ano", e.q.eq(0).rename("q_zero")]).size())
print("Listas com C==1 por ano:", L[L.C == 1].groupby("ano").size().to_dict())
print("Listas com k==C (financiadas) por ano:", L[L.k_igual_C].groupby("ano").size().to_dict())
print("Listas com E>k por ano:", L[L.E_maior_k].groupby("ano").size().to_dict(), " eleitos nelas:", L[L.E_maior_k].groupby("ano").E.sum().to_dict())
print("Eleitos com R=0 (dentro de listas financiadas ou não) por ano:", rrd[(rrd.eleito == 1) & (rrd.R <= 0)].groupby("ano_eleicao").size().to_dict())
print("Competitivos com R=0 por ano:", rrd[(rrd.comp) & (rrd.R <= 0)].groupby("ano_eleicao").size().to_dict())
print("Candidaturas com R=0 por ano:", rrd[rrd.R <= 0].groupby("ano_eleicao").size().to_dict())
print("Candidaturas com R=0 em listas financiadas:", L.groupby("ano").apply(lambda g: (g.C - g.recebedores)[g.R_l > 0].sum()).to_dict())
print("Perfil competitivo não observado por ano:", (~rrd.comp_known).groupby(rrd.ano_eleicao).sum().to_dict())
print("Competitivos por ano (candidato_competitivo):", rrd.groupby("ano_eleicao").comp.sum().to_dict())
print("Eleitos com votos=0? ", ((rrd.eleito == 1) & (rrd.qt_votos_nominais == 0)).sum(), " | Recebedores com 0 votos:", ((rrd.R > 0) & (rrd.qt_votos_nominais == 0)).groupby(rrd.ano_eleicao).sum().to_dict())
