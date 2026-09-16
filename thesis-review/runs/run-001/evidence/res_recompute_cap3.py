"""res_recompute_cap3.py -- results-reviewer, run-001, Cap. 3.
Recomputa a partir de data/processed/rrd_df_novo.parquet os numeros do capitulo
que nao tem artefato direto e confere os que tem. Replica cap3_cs_features
(candidato_competitivo) e cap3_taa_features (normalizacao de sigla, empates
fracionarios). Saida: res_recompute_cap3.out.
"""
import unicodedata
import numpy as np
import pandas as pd

ROOT = "C:/Users/yuri_taba/Desktop/recursos-campanha-local"
rrd = pd.read_parquet(f"{ROOT}/data/processed/rrd_df_novo.parquet")
rrd = rrd[rrd.ano_eleicao.isin([2018, 2022])].copy()

ALIAS = {"PCDOB": "PC DO B", "PP**": "PP", "SD": "SOLIDARIEDADE", "PTDOB": "PT DO B"}


def to_ascii(s):
    if not isinstance(s, str):
        return str(s).upper().strip()
    try:
        s = s.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").upper().strip()


rrd["partido_norm"] = rrd.sg_partido.map(lambda s: ALIAS.get(to_ascii(s), to_ascii(s)))
rrd["R"] = rrd.vr_receita_recursos_partidos.fillna(0).astype(float)

ncols = ["n_eleicoes_prefeito", "n_eleicoes_deputado_estadual", "n_eleicoes_deputado_federal",
         "n_eleicoes_governador", "n_eleicoes_senador"]
rrd["incumbente"] = rrd[ncols].fillna(0).sum(axis=1) > 0
rrd["comp"] = rrd.incumbente | rrd.alcancou_10pct_qe_hist.fillna(False).astype(bool)
rrd["comp_na"] = rrd.alcancou_10pct_qe_hist.isna() & ~rrd.incumbente


def acertos_frac(score, g, k):
    s = np.asarray(score, float)
    e = np.asarray(g, float)
    if k <= 0:
        return 0.0
    chave = np.where(np.isnan(-s), np.inf, -s)
    o = np.argsort(chave, kind="mergesort")
    chave, e = chave[o], e[o]
    k = min(int(k), len(chave))
    ac, rest, i = 0.0, k, 0
    while i < len(chave) and rest > 0:
        j = i
        while j < len(chave) and chave[j] == chave[i]:
            j += 1
        b = j - i
        if b <= rest:
            ac += e[i:j].sum()
            rest -= b
        else:
            ac += rest * e[i:j].mean()
            rest = 0
        i = j
    return ac


key = ["ano_eleicao", "sg_uf", "partido_norm"]
print("=" * 70)
print("1. UNIVERSOS (linhas 25, 27, 115)")
for ano, d in rrd.groupby("ano_eleicao"):
    L = d.groupby(["sg_uf", "partido_norm"])
    Rl = L.R.sum()
    sem = (Rl <= 0).rename("sem_rec").reset_index()
    el_sem = d.merge(sem, on=["sg_uf", "partido_norm"]).query("sem_rec").eleito.sum()
    print(f"{ano}: candidaturas={len(d)} competitivas={int(d.comp.sum())} ({100 * d.comp.mean():.2f}%) "
          f"perfil_NA={int(d.comp_na.sum())} listas={L.ngroups} sem_recursos={int(sem['sem_rec'].sum())} "
          f"eleitos={int(d.eleito.sum())} eleitos_em_listas_sem_recursos={int(el_sem)}")
n18 = (rrd.ano_eleicao == 2018).sum()
n22 = (rrd.ano_eleicao == 2022).sum()
c18 = rrd.query("ano_eleicao==2018").comp.sum()
c22 = rrd.query("ano_eleicao==2022").comp.sum()
print(f"crescimento candidaturas 2018->2022: {100 * (n22 / n18 - 1):.1f}%  competitivas: {100 * (c22 / c18 - 1):.1f}%")

print("=" * 70)
print("2. DESCRITIVOS POR LISTA (linhas 117, 121, 127, 131, 175, 181)")
lst = rrd.groupby(key).agg(
    C=("R", "size"), F=("comp", "sum"), R=("R", "sum"), E=("eleito", "sum"),
    ssq=("R", lambda x: ((x / x.sum()) ** 2).sum() if x.sum() > 0 else np.nan),
).reset_index()
lst["NECr"] = 1 / lst.ssq
lst["k"] = np.where(lst.R > 0, np.floor(lst.NECr + 0.5), 0).astype(int)
lst["C_NECr"] = lst.C / lst.NECr
lst["NECr_C"] = 100 * lst.NECr / lst.C
for ano, d in lst.groupby("ano_eleicao"):
    f = d[d.R > 0]
    print(f"{ano} todas ({len(d)}): C med={d.C.median():.2f} mean={d.C.mean():.2f} | "
          f"F med={d.F.median():.2f} mean={d.F.mean():.3f}")
    print(f"{ano} financiadas ({len(f)}): C med={f.C.median():.2f} mean={f.C.mean():.2f} | "
          f"F med={f.F.median():.2f} mean={f.F.mean():.3f} | NECr med={f.NECr.median():.3f} mean={f.NECr.mean():.3f} | "
          f"C/NECr med={f.C_NECr.median():.3f} mean={f.C_NECr.mean():.3f} | "
          f"NECr/C pct med={f.NECr_C.median():.2f} mean={f.NECr_C.mean():.2f} | sum k={f.k.sum()} k/513={f.k.sum() / 513:.2f}")
f18 = lst.query("ano_eleicao==2018 and R>0")
f22 = lst.query("ano_eleicao==2022 and R>0")
a18 = lst.query("ano_eleicao==2018")
a22 = lst.query("ano_eleicao==2022")
print(f"'listas dobraram' (l.181): financiadas razao medianas C={f22.C.median() / f18.C.median():.2f}, "
      f"razao medias={f22.C.mean() / f18.C.mean():.2f}; todas: medianas={a22.C.median() / a18.C.median():.2f}, "
      f"medias={a22.C.mean() / a18.C.mean():.2f}")

print("=" * 70)
print("3. TOP-NECr NACIONAL (linhas 139-147; fig 03)")
rrd = rrd.merge(lst[key + ["k", "C"]], on=key)
alvos = [
    ("competitivos (perfil NA excluido)", "comp", ~rrd.comp_na),
    ("competitivos (NA=False)", "comp", pd.Series(True, index=rrd.index)),
    ("eleitos", "eleito", pd.Series(True, index=rrd.index)),
]
for alvo, col, mask in alvos:
    for ano in (2018, 2022):
        d = rrd[(rrd.ano_eleicao == ano) & mask]
        H = G = K = A0 = 0.0
        for _, g in d.groupby(["sg_uf", "partido_norm"]):
            k = int(g.k.iloc[0])
            Cl = len(g)
            kk = min(k, Cl)
            H += acertos_frac(g.R, g[col], kk)
            G += g[col].sum()
            K += kk
            A0 += g[col].sum() * kk / Cl
        print(f"{alvo} {ano}: sumG={G:.0f} sumk={K:.0f} sumH={H:.2f} A0={A0:.2f} "
              f"cobertura={100 * H / G:.2f}% precisao={100 * H / K:.2f}% "
              f"cob_acaso={100 * A0 / G:.2f}% prec_acaso={100 * A0 / K:.2f}% lift={H / A0:.3f}")

print("=" * 70)
print("4. PLACEHOLDER l.179: competitivas por genero (universo de candidaturas)")
for ano, d in rrd.groupby("ano_eleicao"):
    t = d.groupby("ds_genero").comp.agg(["mean", "sum", "size"])
    t["pct"] = 100 * t["mean"]
    print(ano)
    print(t.round(2).to_string())

print("=" * 70)
print("5. DISCUSSAO l.173/177: lifts Top-X% (sensibilidade-top-x/resumo_nacional.csv)")
# Nota: durante o run-001 (2026-09-14 17:01) os relatorios foram movidos de tese/ para tese/reports/.
import glob
cands = (glob.glob(f"{ROOT}/tese/sensibilidade-top-x/resumo_nacional.csv")
         + glob.glob(f"{ROOT}/tese/reports/sensibilidade-top-x/resumo_nacional.csv"))
print("fonte:", cands[0])
rn = pd.read_csv(cands[0], encoding="utf-8-sig")
rn = rn[rn.regra.str.startswith("top_")].copy()
piv = rn.pivot_table(index=["desfecho", "ano_eleicao"], columns="regra", values="lift").round(2)
print(piv.to_string())
sel = rn[rn.regra != "top_necr"]
print(f"lifts Top-X% em [1,8; 2,0]: {((sel.lift >= 1.8) & (sel.lift <= 2.0)).sum()} de {len(sel)}; "
      f"em [1,7; 2,1]: {((sel.lift >= 1.7) & (sel.lift <= 2.1)).sum()} de {len(sel)}; "
      f"min={sel.lift.min():.2f} max={sel.lift.max():.2f}")
for lim in ("top_50", "top_80"):
    t = rn[rn.regra == lim].set_index(["desfecho", "ano_eleicao"])[["cobertura", "precisao", "lift"]].copy()
    t["cobertura"] = 100 * t.cobertura
    t["precisao"] = 100 * t.precisao
    print(lim)
    print(t.round(2).to_string())
for (des, ano), g in rn[rn.regra != "top_necr"].sort_values("limiar").groupby(["desfecho", "ano_eleicao"]):
    print(f"{des} {ano}: cobertura nao-decrescente={bool((g.cobertura.diff().dropna() >= 0).all())} "
          f"precisao nao-crescente={bool((g.precisao.diff().dropna() <= 0).all())} "
          f"lift nao-crescente={bool((g.lift.diff().dropna() <= 0).all())} "
          f"precisao>fora em todos={bool((g.precisao > g.proporcao_perfil_fora).all())}")
ce = rn[rn.desfecho == "eleicao"].sort_values(["ano_eleicao", "limiar"]).cobertura.values
cc = rn[rn.desfecho == "competitividade"].sort_values(["ano_eleicao", "limiar"]).cobertura.values
print("cobertura eleitos > cobertura competitivos em todos os limiares (l.165):", bool((ce > cc).all()))
