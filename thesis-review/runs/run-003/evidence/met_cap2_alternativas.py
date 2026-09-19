"""methodology-reviewer, run-003 (Cap. 2). Checagens das explicações alternativas
que o Argumento do Cap. 2 deixa em aberto. Só lê data/processed; não escreve nada fora de evidence/."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "src/2_gold")
from cap3_cs_features import gerar_features

pd.set_option("display.width", 200)
rrd = gerar_features(pd.read_parquet("data/processed/rrd_df_novo.parquet"))
rrd = rrd[rrd.ano_eleicao.isin([2018, 2022])].copy()
rec = pd.read_parquet("data/processed/receitas.parquet")
rec = rec[rec.ano_eleicao.isin([2018, 2022]) & (rec.ds_cargo == "DEPUTADO FEDERAL")]

print("=== A. Receitas de candidatos a DF por origem (% do total) ===")
t = rec.groupby(["ano_eleicao", "ds_origem_receita"]).vr_receita.sum().unstack(0)
print((100 * t / t.sum()).round(2).sort_values(2022, ascending=False).head(8))

print("\n=== B. 'Recursos de partido político' por fonte (% do total da origem) ===")
p = rec[rec.ds_origem_receita.str.startswith("Recursos de partido")]
t = p.groupby(["ano_eleicao", "ds_fonte_receita"]).vr_receita.sum().unstack(0)
print((100 * t / t.sum()).round(2))

print("\n=== C. Recursos não partidários (vr_receita_outros) por credencial ===")
rrd["R"] = rrd.vr_receita_recursos_partidos.fillna(0)
rrd["O"] = rrd.vr_receita_outros.fillna(0)
rrd["comp"] = rrd.candidato_competitivo.astype(bool)
g = rrd.groupby(["ano_eleicao", "comp"]).agg(n=("R", "size"), R=("R", "sum"), O=("O", "sum"),
                                              med_O=("O", "median"), pct_O_pos=("O", lambda x: (x > 0).mean()))
g["O_sobre_total"] = g.O / (g.O + g.R)
print(g.round(3))
# substituição dentro da lista: correlação entre parcela partidária e parcela de 'outros' na lista
rrd["lista"] = rrd.ano_eleicao.astype(str) + "_" + rrd.sg_uf + "_" + rrd.sg_partido
for c in ["R", "O"]:
    tot = rrd.groupby("lista")[c].transform("sum")
    rrd["s" + c] = np.where(tot > 0, rrd[c] / tot, np.nan)
for ano in [2018, 2022]:
    d = rrd[(rrd.ano_eleicao == ano)].dropna(subset=["sR", "sO"])
    d = d[d.groupby("lista").sR.transform("size") > 1]
    # correlação intralista (desvios da média da lista)
    x = d.sR - d.groupby("lista").sR.transform("mean")
    y = d.sO - d.groupby("lista").sO.transform("mean")
    print(ano, "corr intralista sR x sO =", round(np.corrcoef(x, y)[0, 1], 3), "n =", len(d))

print("\n=== D. Candidaturas com R_il = 0 em listas financiadas; lift com e sem elas ===")
def topk_hits(df):
    s = df.R.values
    tot = s.sum()
    if tot <= 0:
        return pd.Series(dict(H=0.0, k=0, C=len(df), G=df.comp.sum(), Cpos=(s > 0).sum(), Gpos=df.comp[s > 0].sum()))
    sh = s / tot
    k = int(np.floor(1 / np.sum(sh ** 2) + 0.5))
    order = np.argsort(-s, kind="mergesort")
    ss, cc = s[order], df.comp.values[order].astype(float)
    H, rest, i = 0.0, k, 0
    while i < len(ss) and rest > 0:
        j = i
        while j < len(ss) and ss[j] == ss[i]:
            j += 1
        b = j - i
        take = min(rest, b)
        H += take * cc[i:j].mean()
        rest -= take
        i = j
    return pd.Series(dict(H=H, k=k, C=len(df), G=df.comp.sum(), Cpos=(s > 0).sum(), Gpos=df.comp[s > 0].sum()))

L = rrd.groupby(["ano_eleicao", "lista"]).apply(topk_hits).reset_index()
L = L[L.k > 0]
for ano, d in L.groupby("ano_eleicao"):
    E_all = (d.G * d.k / d.C).sum()
    E_pos = (d.Gpos * d.k / d.Cpos).sum()
    zero = (d.C - d.Cpos).sum()
    print(ano, f"listas={len(d)} cand={int(d.C.sum())} cand_R0={int(zero)} ({100*zero/d.C.sum():.1f}%) "
          f"comp_R0={int((d.G-d.Gpos).sum())} H={d.H.sum():.1f} lift_todos={d.H.sum()/E_all:.3f} "
          f"lift_so_R>0={d.H.sum()/E_pos:.3f} cobertura={d.H.sum()/d.G.sum():.3f}")

print("\n=== E. Parcela de não-competitivos com R>0 que recebe menos que 1/C (quase-simbólico) ===")
rrd["C"] = rrd.groupby("lista").R.transform("size")
d = rrd[rrd.groupby("lista").R.transform("sum") > 0]
for ano, x in d.groupby("ano_eleicao"):
    nc = x[~x.comp]
    print(ano, "não-comp: R=0:", round((nc.R == 0).mean(), 3), "| s<1/(2C):", round((nc.sR < 0.5 / nc.C).mean(), 3),
          "| comp: R=0:", round((x[x.comp].R == 0).mean(), 3))

print("\n=== F. Cotas: parcela dos recursos partidários (DF) destinada a mulheres; credenciais por grupo ===")
for ano, x in rrd.groupby("ano_eleicao"):
    fin = x[x.groupby("lista").R.transform("sum") > 0]
    print(ano, "mulheres: % candidaturas =", round(100 * x.mulher.mean(), 1),
          "| % recursos partidários =", round(100 * x.loc[x.mulher == 1, "R"].sum() / x.R.sum(), 1),
          "| % com credencial (M/H) =", round(100 * x[x.mulher == 1].comp.mean(), 1), round(100 * x[x.mulher == 0].comp.mean(), 1))
    by = x.groupby("sg_partido").apply(lambda g: g.loc[g.mulher == 1, "R"].sum() / g.R.sum() if g.R.sum() > 0 else np.nan, include_groups=False).dropna()
    print("   partidos com % mulheres dos recursos DF entre 28% e 35%:", int(((by >= .28) & (by <= .35)).sum()), "de", len(by),
          "| mediana =", round(100 * by.median(), 1))

print("\n=== G. Composição do grupo com credencial: vitória acima de vereador vs só votação (10% QE) ===")
cols = ["n_eleicoes_prefeito", "n_eleicoes_deputado_estadual", "n_eleicoes_deputado_federal", "n_eleicoes_governador", "n_eleicoes_senador"]
rrd["vit"] = rrd[cols].fillna(0).sum(axis=1) > 0
rrd["depfed"] = rrd["n_eleicoes_deputado_federal"].fillna(0) > 0
for ano, x in rrd[rrd.comp].groupby("ano_eleicao"):
    print(ano, "credenciados =", len(x), "| com vitória acima de vereador =", int(x.vit.sum()),
          "| já eleito dep. federal =", int(x.depfed.sum()), "| só votação >=10% QE =", int((~x.vit).sum()))

print("\n=== H. Lift observado vs teto mecânico (H<=min(G,k)) por magnitude ===")
mag = rrd.groupby("lista").qt_vaga.first()
L["qt_vaga"] = L.lista.map(mag)
L["faixa"] = pd.cut(L.qt_vaga, [0, 12, 31, 70], labels=["Pequeno", "Médio", "Grande"])
L["E"] = L.G * L.k / L.C
L["Hmax"] = np.minimum(L.G, L.k)
out = L.groupby(["ano_eleicao", "faixa"], observed=True).agg(listas=("H", "size"), H=("H", "sum"), E=("E", "sum"), Hmax=("Hmax", "sum"), C=("C", "mean"))
out["lift"] = out.H / out.E
out["lift_teto"] = out.Hmax / out.E
out["lift/teto"] = out.lift / out.lift_teto
print(out.round(3))
