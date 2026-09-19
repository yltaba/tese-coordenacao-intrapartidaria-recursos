"""adversarial-reviewer, run-003 (Cap. 2). Tenta derrubar I-2-001/I-2-002 e checa uma omissão.
Só lê data/processed; não escreve nada fora de evidence/.
Rodar da raiz do repositório:  python thesis-review/runs/run-003/evidence/adv_rivais_cap2.py

A. "Força do candidato" (I-2-001/I-2-012): a correlação intralista +0,41/+0,34 entre parcela partidária
   e parcela não partidária sobrevive dentro dos estratos de credencial e após residualizar pelas
   credenciais/votação prévia? Se some, a correlação não é evidência de rival distinto da sinalização.
B. Dispersão (I-2-002): quanto a alocação observada se afasta da divisão igualitária (NECr/C) e o que a
   regra "igualitária" daria de lift (=1 por construção).
C. Marginais × credenciados (I-2-002): parcela normalizada (s*C) por quintil da proporção de votos
   nominais intralista na eleição anterior (quem disputou DF antes). Foco em marginais prevê U invertido;
   concentração em credenciados/puxadores prevê monotonia. Também só entre incumbentes (DF eleitos antes).
D. Captura (I-2-001): entre incumbentes, a parcela cresce com a votação anterior? Captura por posição
   prevê perfil plano; sinal de voto prevê gradiente.
E. Mulheres (omissão): Cap. 2 L151 (Janusz et al.: mulheres recebem menos mesmo controlando experiência)
   × Cap. 3 L171 (mulher: razão 1,44/1,32 intralista). Razão bruta e por estrato de credencial.
"""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "src/2_gold")
from cap3_cs_features import gerar_features  # noqa: E402

pd.set_option("display.width", 200)
d = gerar_features(pd.read_parquet("data/processed/rrd_df_novo.parquet"))
d = d[d.ano_eleicao.isin([2018, 2022])].copy()
d["R"] = d.vr_receita_recursos_partidos.fillna(0)
d["O"] = d.vr_receita_outros.fillna(0)
d["comp"] = d.candidato_competitivo.astype(bool)
d["lista"] = d.ano_eleicao.astype(str) + "_" + d.sg_uf + "_" + d.sg_partido
d["C"] = d.groupby("lista").R.transform("size")
for c in ["R", "O"]:
    tot = d.groupby("lista")[c].transform("sum")
    d["s" + c] = np.where(tot > 0, d[c] / tot, np.nan)
d["sRn"] = d.sR * d.C  # parcela normalizada: 1 = divisão igualitária

def demean(v, g):
    return v - v.groupby(g).transform("mean")

print("=== A. Correlação intralista sR x sO: total, por estrato de credencial e residualizada ===")
for ano in [2018, 2022]:
    x = d[(d.ano_eleicao == ano)].dropna(subset=["sR", "sO"]).copy()
    x = x[x.groupby("lista").sR.transform("size") > 1]
    tot = np.corrcoef(demean(x.sR, x.lista), demean(x.sO, x.lista))[0, 1]
    out = [f"{ano} total={tot:.3f} (n={len(x)})"]
    for flag, lab in [(True, "credenciados"), (False, "sem credencial")]:
        y = x[x.comp == flag]
        y = y[y.groupby("lista").sR.transform("size") > 1]
        r = np.corrcoef(demean(y.sR, y.lista), demean(y.sO, y.lista))[0, 1]
        out.append(f"{lab}={r:.3f} (n={len(y)})")
    # residualização intralista por credenciais (contagens por cargo, 10% QE, votos t-1, mulher, negra)
    Z = x[["n_eleicoes_deputado_federal", "n_eleicoes_deputado_estadual", "n_eleicoes_prefeito",
           "n_eleicoes_vereador", "n_eleicoes_governador", "n_eleicoes_senador",
           "alcancou_10pct_qe_hist", "mulher", "negra"]].astype(float).fillna(0)
    Z["votlag"] = x.prop_votos_nominais_lag.fillna(0).astype(float)
    Z["comp"] = x.comp.astype(float)
    Zd = Z.apply(lambda col: demean(col, x.lista)).values
    ry = demean(x.sR, x.lista).values
    rx = demean(x.sO, x.lista).values
    bR, *_ = np.linalg.lstsq(Zd, ry, rcond=None)
    bO, *_ = np.linalg.lstsq(Zd, rx, rcond=None)
    rp = np.corrcoef(ry - Zd @ bR, rx - Zd @ bO)[0, 1]
    out.append(f"parcial|credenciais={rp:.3f}")
    print(" | ".join(out))

print("\n=== B. Distância da divisão igualitária (listas financiadas, C>1) ===")
L = d[d.groupby("lista").R.transform("sum") > 0].groupby(["ano_eleicao", "lista"]).agg(
    C=("R", "size"), necr=("sR", lambda s: 1 / np.sum(s ** 2)))
L = L[L.C > 1]
L["necr_C"] = L.necr / L.C
print(L.groupby("ano_eleicao").necr_C.describe(percentiles=[.1, .25, .5, .75, .9]).round(3))
print("% listas com NECr/C >= 0,9 (quase igualitárias):",
      (L.groupby("ano_eleicao").necr_C.apply(lambda v: round(100 * (v >= 0.9).mean(), 1))).to_dict())

print("\n=== C. Parcela normalizada (s*C) por quintil da proporção de votos intralista t-1 ===")
f = d[(d.groupby("lista").R.transform("sum") > 0) & d.prop_votos_nominais_lag.notna()
      & (d.prop_votos_nominais_lag > 0)].copy()
for ano, x in f.groupby("ano_eleicao"):
    x = x.copy()
    x["q"] = pd.qcut(x.prop_votos_nominais_lag, 5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])
    t = x.groupby("q", observed=True).agg(n=("sRn", "size"), votlag_med=("prop_votos_nominais_lag", "median"),
                                          sRn_media=("sRn", "mean"), sRn_mediana=("sRn", "median"),
                                          pct_comp=("comp", "mean"))
    print(ano, "(todos com votação DF anterior)")
    print(t.round(3))
    inc = x[x.n_eleicoes_deputado_federal.fillna(0) > 0].copy()
    inc["q"] = pd.qcut(inc.prop_votos_nominais_lag, 4, labels=["Q1", "Q2", "Q3", "Q4"])
    t2 = inc.groupby("q", observed=True).agg(n=("sRn", "size"), votlag_med=("prop_votos_nominais_lag", "median"),
                                             sRn_media=("sRn", "mean"), sRn_mediana=("sRn", "median"))
    print(ano, "(só quem já venceu para DF antes; quartis de votos t-1)")
    print(t2.round(3))
    # D. correlação de Spearman entre votos t-1 e parcela normalizada entre ex-eleitos DF
    print(ano, "Spearman(votlag, s*C) entre ex-eleitos DF =",
          round(inc[["prop_votos_nominais_lag", "sRn"]].corr(method="spearman").iloc[0, 1], 3),
          "| só incumbente==1:",
          round(inc[inc.incumbente == 1][["prop_votos_nominais_lag", "sRn"]].corr(method="spearman").iloc[0, 1], 3)
          if "incumbente" in inc and (inc.incumbente == 1).sum() > 10 else "n/d")

print("\n=== E. Mulheres × homens: parcela normalizada (s*C) média, listas financiadas ===")
g = d[d.groupby("lista").R.transform("sum") > 0]
for ano, x in g.groupby("ano_eleicao"):
    row = [f"{ano}"]
    m, h = x[x.mulher == 1], x[x.mulher == 0]
    row.append(f"bruto M/H={m.sRn.mean() / h.sRn.mean():.2f} (R$ médio M/H={m.R.mean() / h.R.mean():.2f})")
    for flag, lab in [(True, "credenciados"), (False, "sem credencial")]:
        mm, hh = m[m.comp == flag], h[h.comp == flag]
        row.append(f"{lab} M/H={mm.sRn.mean() / hh.sRn.mean():.2f} (nM={len(mm)}, nH={len(hh)})")
    print(" | ".join(row))

print("\n=== C2. Igual a C/D, com prop_votos_nominais_lag_candidato (merge UF+CPF, cobre trocas de partido) ===")
f = d[(d.groupby("lista").R.transform("sum") > 0) & (d.prop_votos_nominais_lag_candidato > 0)].copy()
for ano, x in f.groupby("ano_eleicao"):
    x = x.copy()
    x["q"] = pd.qcut(x.prop_votos_nominais_lag_candidato, 5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])
    print(ano, "(todos com votação DF anterior)")
    print(x.groupby("q", observed=True).agg(n=("sRn", "size"), votlag_med=("prop_votos_nominais_lag_candidato", "median"),
          sRn_media=("sRn", "mean"), sRn_mediana=("sRn", "median"), pct_comp=("comp", "mean")).round(3))
    inc = x[x.n_eleicoes_deputado_federal.fillna(0) > 0].copy()
    inc["q"] = pd.qcut(inc.prop_votos_nominais_lag_candidato, 4, labels=["Q1", "Q2", "Q3", "Q4"])
    print(ano, "(ex-eleitos DF; quartis de votos t-1)")
    print(inc.groupby("q", observed=True).agg(n=("sRn", "size"), votlag_med=("prop_votos_nominais_lag_candidato", "median"),
          sRn_media=("sRn", "mean"), sRn_mediana=("sRn", "median")).round(3))
    print(ano, "Spearman(votlag_cand, s*C) ex-eleitos DF =",
          round(inc[["prop_votos_nominais_lag_candidato", "sRn"]].corr(method="spearman").iloc[0, 1], 3),
          "| sem credencial OU credenciado só por votação (sem vitória DF) =",
          round(x[~x.comp.astype(bool) | (x.alcancou_10pct_qe_hist.fillna(0) > 0) & (x.n_eleicoes_deputado_federal.fillna(0) == 0)]
                [["prop_votos_nominais_lag_candidato", "sRn"]].corr(method="spearman").iloc[0, 1], 3))
