"""statistics-reviewer, run-001, Cap. 3.
Recomputa a partir de tese/sensibilidade-top-x/candidaturas.parquet (pesos Top-NECr e Top-X%,
competitivo_previo, eleito) e data/processed/rrd_df_novo.parquet (sexo):
  1. razoes de somas nacionais (conferencia com 15_cobertura_nacional.csv / resumo_nacional.csv);
  2. nulo por permutacao dentro da lista (2.000 replicas), dois universos (todos / so recebedores);
  3. bootstrap por lista e por partido (2.000 replicas) para lift, cobertura, precisao e diferencas;
  4. media das razoes por lista vs razao das somas; peso das listas degeneradas (k = C);
  5. contribuicao das maiores listas; 6. nucleo por sexo; 7. gradiente acumulado vs marginal.
Saidas: sta_*.csv e sta_resultados.json nesta pasta.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
SEED = 20260914
B_PERM = 2000
B_BOOT = 2000
LK = ["ano_eleicao", "sg_uf", "sg_partido_norm"]

# A pasta tese/sensibilidade-top-x foi movida para tese/reports/ durante o run-001.
SRC = next(p for p in [ROOT / "tese/reports/sensibilidade-top-x/candidaturas.parquet",
                       ROOT / "tese/sensibilidade-top-x/candidaturas.parquet"] if p.exists())
print("fonte:", SRC.relative_to(ROOT))
d = pd.read_parquet(SRC)
rrd = pd.read_parquet(ROOT / "data/processed/rrd_df_novo.parquet",
                      columns=["ano_eleicao", "sg_uf", "nr_candidato", "mulher", "negra"])
rrd = rrd[rrd.ano_eleicao.isin([2018, 2022])].copy()
rrd["nr_candidato"] = pd.to_numeric(rrd.nr_candidato).astype("int64")
rrd["ano_eleicao"] = rrd.ano_eleicao.astype("int64")
d = d.merge(rrd, on=["ano_eleicao", "sg_uf", "nr_candidato"], how="left", validate="one_to_one")
assert d.groupby("ano_eleicao").size().to_dict() == {2018: 7630, 2022: 9675}

RULES = ["top_necr", "top_50", "top_60", "top_70", "top_80", "top_90", "top_95"]
TARGETS = {"competitividade": "competitivo_previo", "eleicao": "eleito"}


def por_lista(df, rule, target):
    """Agregados por lista restritos a candidaturas com perfil observado (convencao da nota formal)."""
    g = df[target].astype(float)
    valid = g.notna()
    w = df[rule].astype(float).where(valid, 0.0)
    rec = (df.vr_receita_recursos_partidos > 0)
    t = pd.DataFrame({"ano": df.ano_eleicao, "uf": df.sg_uf, "partido": df.sg_partido_norm,
                      "C": valid.astype(float), "k": w, "G": g.fillna(0),
                      "H": w * g.fillna(0),
                      "Crec": (valid & rec).astype(float), "Grec": (g.fillna(0) * rec)})
    a = t.groupby(["ano", "uf", "partido"]).sum()
    a["A0"] = (a.k * a.G / a.C.replace(0, np.nan)).fillna(0.0)
    # nulo so entre recebedores: o nucleo e sempre composto de recebedores (k <= n_rec)
    a["A0rec"] = (a.k * a.Grec / a.Crec.replace(0, np.nan)).fillna(0.0)
    return a.reset_index()


def nacional(a):
    H, G, k, A0, A0r = a.H.sum(), a.G.sum(), a.k.sum(), a.A0.sum(), a.A0rec.sum()
    return dict(sumH=H, sumG=G, sumk=k, A0=A0, A0rec=A0r, cobertura=H / G, precisao=H / k,
                lift=H / A0, lift_rec=H / A0r, cob_acaso=A0 / G, prec_acaso=A0 / k)


# ---------- 1. razoes de somas ----------
tab = []
lists = {}
for rule in RULES:
    for tg, col in TARGETS.items():
        for ano, df in d.groupby("ano_eleicao"):
            a = por_lista(df, rule, col)
            lists[(rule, tg, ano)] = a
            tab.append(dict(regra=rule, desfecho=tg, ano=ano, **nacional(a)))
tab = pd.DataFrame(tab)
tab.to_csv(OUT / "sta_razoes_de_somas.csv", index=False)
print(tab[tab.regra.eq("top_necr")].round(4).to_string(index=False))

# ---------- 2. nulo por permutacao dentro da lista (preserva vetor de recursos e pesos w) ----------
rng = np.random.default_rng(SEED)
perm_rows = []
for tg, col in TARGETS.items():
    for ano, df in d.groupby("ano_eleicao"):
        sims_all = np.zeros(B_PERM)
        sims_rec = np.zeros(B_PERM)
        for _, g in df.groupby(LK):
            w = g.top_necr.to_numpy(float)
            y = g[col].to_numpy(float)
            ok = ~np.isnan(y)
            w = w[ok]
            y = y[ok]
            if w.sum() == 0 or y.sum() == 0:
                continue
            Y = rng.permuted(np.tile(y, (B_PERM, 1)), axis=1)
            sims_all += Y @ w
            rec = (g.vr_receita_recursos_partidos.to_numpy(float)[ok] > 0)
            yr = y[rec]
            wr = w[rec]
            if yr.sum() == 0:
                continue
            Yr = rng.permuted(np.tile(yr, (B_PERM, 1)), axis=1)
            sims_rec += Yr @ wr
        n = nacional(lists[("top_necr", tg, ano)])
        obs = n["sumH"]
        for uni, sims, A0 in [("todos", sims_all, n["A0"]), ("recebedores", sims_rec, n["A0rec"])]:
            perm_rows.append(dict(desfecho=tg, ano=ano, universo=uni, observado=obs, esperado_analitico=A0,
                                  media_perm=sims.mean(), sd_perm=sims.std(ddof=1),
                                  p2_5=np.quantile(sims, .025), p97_5=np.quantile(sims, .975), max_perm=sims.max(),
                                  lift_obs=obs / A0, lift_p2_5=np.quantile(sims, .025) / A0,
                                  lift_p97_5=np.quantile(sims, .975) / A0,
                                  p_valor=(np.sum(sims >= obs) + 1) / (B_PERM + 1), replicas=B_PERM))
perm = pd.DataFrame(perm_rows)
perm.to_csv(OUT / "sta_permutacao_top_necr.csv", index=False)
print("\nPERMUTACAO\n", perm.round(3).to_string(index=False))


# ---------- 3. bootstrap por lista e por partido ----------
def boot(a_dict, cluster, B, rng):
    """Reamostra clusters (com reposicao) uma vez e aplica a todas as tabelas de a_dict.
    Devolve nome -> array (B,3) de [cobertura, precisao, lift]."""
    base = next(iter(a_dict.values()))
    keys = base[cluster].drop_duplicates().reset_index(drop=True)
    idx = {tuple(r): i for i, r in enumerate(keys.itertuples(index=False))}
    n = len(keys)
    mats = {}
    for name, a in a_dict.items():
        m = np.zeros((n, 4))
        ci_ = np.array([idx[tuple(r)] for r in a[cluster].itertuples(index=False)])
        for j, colname in enumerate(["H", "G", "k", "A0"]):
            np.add.at(m[:, j], ci_, a[colname].to_numpy(float))
        mats[name] = m
    draws = rng.integers(0, n, size=(B, n))
    counts = np.zeros((B, n))
    for b in range(B):
        counts[b] = np.bincount(draws[b], minlength=n)
    out = {}
    for name, m in mats.items():
        S = counts @ m
        out[name] = np.column_stack([S[:, 0] / S[:, 1], S[:, 0] / S[:, 2], S[:, 0] / S[:, 3]])
    return out, n


def ci(x):
    return np.quantile(x, [.025, .975])


boot_rows = []
diff_rows = []
rng = np.random.default_rng(SEED + 1)
store = {}
for cluster_name, cluster in [("lista", ["uf", "partido"]), ("partido", ["partido"])]:
    for ano in [2018, 2022]:
        a_dict = {f"{r}|{t}": lists[(r, t, ano)] for r in ["top_necr", "top_50", "top_80"] for t in TARGETS}
        out, n = boot(a_dict, cluster, B_BOOT, rng)
        for name, arr in out.items():
            r, t = name.split("|")
            pt = nacional(lists[(r, t, ano)])
            for j, met in enumerate(["cobertura", "precisao", "lift"]):
                lo, hi = ci(arr[:, j])
                boot_rows.append(dict(cluster=cluster_name, n_clusters=n, ano=ano, regra=r, desfecho=t, metrica=met,
                                      ponto=pt[met], ic95_inf=lo, ic95_sup=hi, sd_boot=arr[:, j].std(ddof=1)))
        store[(cluster_name, ano)] = out
        for (n1, n2, rot) in [("top_necr|eleicao", "top_necr|competitividade", "lift eleitos - lift competitivos (Top-NECr)"),
                              ("top_50|competitividade", "top_necr|competitividade", "lift Top-50% - lift Top-NECr (competitivos)"),
                              ("top_50|eleicao", "top_necr|eleicao", "lift Top-50% - lift Top-NECr (eleitos)"),
                              ("top_80|competitividade", "top_necr|competitividade", "lift Top-80% - lift Top-NECr (competitivos)")]:
            dlt = out[n1][:, 2] - out[n2][:, 2]
            lo, hi = ci(dlt)
            p1 = nacional(lists[(n1.split("|")[0], n1.split("|")[1], ano)])["lift"]
            p2 = nacional(lists[(n2.split("|")[0], n2.split("|")[1], ano)])["lift"]
            diff_rows.append(dict(cluster=cluster_name, ano=str(ano), comparacao=rot, ponto=p1 - p2, ic95_inf=lo, ic95_sup=hi,
                                  prop_boot_le_0=float(np.mean(dlt <= 0))))
    for name, rot in [("top_necr|competitividade", "lift 2022 - lift 2018 (competitivos, Top-NECr)"),
                      ("top_necr|eleicao", "lift 2022 - lift 2018 (eleitos, Top-NECr)")]:
        dlt = store[(cluster_name, 2022)][name][:, 2] - store[(cluster_name, 2018)][name][:, 2]
        lo, hi = ci(dlt)
        r, t = name.split("|")
        pt = nacional(lists[(r, t, 2022)])["lift"] - nacional(lists[(r, t, 2018)])["lift"]
        diff_rows.append(dict(cluster=cluster_name, ano="2022-2018", comparacao=rot, ponto=pt, ic95_inf=lo, ic95_sup=hi,
                              prop_boot_le_0=float(np.mean(dlt <= 0))))
    for met, j in [("cobertura", 0), ("precisao", 1)]:
        for name in ["top_necr|competitividade", "top_necr|eleicao"]:
            dlt = store[(cluster_name, 2022)][name][:, j] - store[(cluster_name, 2018)][name][:, j]
            lo, hi = ci(dlt)
            r, t = name.split("|")
            pt = nacional(lists[(r, t, 2022)])[met] - nacional(lists[(r, t, 2018)])[met]
            diff_rows.append(dict(cluster=cluster_name, ano="2022-2018", comparacao=f"{met} 2022 - 2018 ({t}, Top-NECr)",
                                  ponto=pt, ic95_inf=lo, ic95_sup=hi, prop_boot_le_0=float(np.mean(dlt <= 0))))
bootdf = pd.DataFrame(boot_rows)
diffdf = pd.DataFrame(diff_rows)
bootdf.to_csv(OUT / "sta_bootstrap_ic.csv", index=False)
diffdf.to_csv(OUT / "sta_bootstrap_diferencas.csv", index=False)
print("\nBOOTSTRAP IC\n", bootdf.round(4).to_string(index=False))
print("\nDIFERENCAS\n", diffdf.round(4).to_string(index=False))

# ---------- 4. media das razoes vs razao das somas; listas degeneradas ----------
mr_rows = []
for tg in TARGETS:
    for ano in [2018, 2022]:
        a = lists[("top_necr", tg, ano)]
        fin = a[a.k > 0]
        deg = fin[fin.k >= fin.C - 1e-9]
        nond = fin[fin.k < fin.C - 1e-9]
        withG = a[a.G > 0]
        lift_lista = withG[withG.A0 > 0]
        mr_rows.append(dict(
            desfecho=tg, ano=ano, listas=len(a), financiadas=len(fin), degeneradas_k_igual_C=len(deg),
            share_k_degeneradas=deg.k.sum() / fin.k.sum(), share_G_degeneradas=deg.G.sum() / a.G.sum(),
            share_A0_degeneradas=deg.A0.sum() / a.A0.sum(), share_H_degeneradas=deg.H.sum() / a.H.sum(),
            lift_razao_somas=a.H.sum() / a.A0.sum(),
            lift_so_nao_degeneradas=nond.H.sum() / nond.A0.sum(),
            cobertura_razao_somas=a.H.sum() / a.G.sum(),
            cobertura_media_listas_G_pos=(withG.H / withG.G).mean(),
            cobertura_mediana_listas_G_pos=(withG.H / withG.G).median(),
            precisao_razao_somas=a.H.sum() / a.k.sum(),
            precisao_media_listas_k_pos=(fin.H / fin.k).mean(),
            lift_media_listas_A0_pos=(lift_lista.H / lift_lista.A0).mean(),
            lift_mediana_listas_A0_pos=(lift_lista.H / lift_lista.A0).median(),
            listas_com_G_pos=len(withG),
            listas_G_pos_e_0_k_C=int(((withG.k > 0) & (withG.k < withG.C - 1e-9)).sum()),
            listas_G_pos_cobertura_100=int((withG.H >= withG.G - 1e-9).sum())))
mr = pd.DataFrame(mr_rows)
mr.to_csv(OUT / "sta_media_razoes_vs_razao_somas.csv", index=False)
print("\nMEDIA DAS RAZOES / DEGENERADAS\n", mr.round(4).T.to_string())

# ---------- 5. contribuicao das maiores listas ----------
cr = []
for tg in TARGETS:
    for ano in [2018, 2022]:
        a = lists[("top_necr", tg, ano)].sort_values("G", ascending=False)
        top = a.head(int(np.ceil(0.10 * len(a))))
        cr.append(dict(desfecho=tg, ano=ano, listas_top10pct=len(top), share_G=top.G.sum() / a.G.sum(),
                       share_H=top.H.sum() / a.H.sum(), share_A0=top.A0.sum() / a.A0.sum(), share_k=top.k.sum() / a.k.sum(),
                       lift_top10pct=top.H.sum() / top.A0.sum(),
                       lift_resto=(a.H.sum() - top.H.sum()) / (a.A0.sum() - top.A0.sum()),
                       ufs_top10pct=", ".join(top.uf.value_counts().head(4).index)))
cr = pd.DataFrame(cr)
cr.to_csv(OUT / "sta_contribuicao_listas_grandes.csv", index=False)
print("\nCONTRIBUICAO 10% MAIORES LISTAS (por G_l)\n", cr.round(3).to_string(index=False))

# ---------- 6. nucleo por sexo (claim das cotas) ----------
sx = []
for ano, df in d.groupby("ano_eleicao"):
    for sexo, m in [("mulheres", df.mulher.eq(1)), ("homens", df.mulher.eq(0))]:
        s = df[m]
        v = s.competitivo_previo.notna()
        sx.append(dict(ano=ano, grupo=sexo, candidaturas=len(s), competitivos_pct=100 * s.competitivo_previo.mean(),
                       posicoes_nucleo=s.top_necr.sum(), share_posicoes_nucleo=s.top_necr.sum() / df.top_necr.sum(),
                       precisao_comp_no_grupo=100 * (s.top_necr * s.competitivo_previo.fillna(0)).sum() / s.top_necr[v].sum(),
                       precisao_eleitos_no_grupo=100 * (s.top_necr * s.eleito).sum() / s.top_necr.sum()))
sx = pd.DataFrame(sx)
sx.to_csv(OUT / "sta_nucleo_por_sexo.csv", index=False)
print("\nNUCLEO POR SEXO\n", sx.round(2).to_string(index=False))

# ---------- 7. gradiente Top-X%: lift acumulado vs lift marginal ----------
gr = []
for tg, col in TARGETS.items():
    for ano, df in d.groupby("ano_eleicao"):
        prev = None
        prev_rule = "0"
        for rule in ["top_50", "top_60", "top_70", "top_80", "top_90", "top_95"]:
            a = lists[(rule, tg, ano)]
            n = nacional(a)
            if prev is not None:
                dH = a.H.sum() - prev.H.sum()
                dA = a.A0.sum() - prev.A0.sum()
                dk = a.k.sum() - prev.k.sum()
                gr.append(dict(desfecho=tg, ano=ano, faixa=f"{prev_rule}->{rule}", lift_acumulado=n["lift"],
                               lift_marginal_faixa=dH / dA, densidade_marginal=dH / dk, precisao_acumulada=n["precisao"]))
            else:
                gr.append(dict(desfecho=tg, ano=ano, faixa=f"0->{rule}", lift_acumulado=n["lift"],
                               lift_marginal_faixa=n["lift"], densidade_marginal=n["precisao"], precisao_acumulada=n["precisao"]))
            prev = a
            prev_rule = rule
gr = pd.DataFrame(gr)
gr.to_csv(OUT / "sta_gradiente_marginal.csv", index=False)
print("\nGRADIENTE MARGINAL\n", gr.round(3).to_string(index=False))

json.dump({"seed": SEED, "replicas_permutacao": B_PERM, "replicas_bootstrap": B_BOOT,
           "fonte": "tese/sensibilidade-top-x/candidaturas.parquet + data/processed/rrd_df_novo.parquet",
           "razoes_top_necr": tab[tab.regra.eq("top_necr")].to_dict("records"),
           "permutacao": perm.to_dict("records"), "diferencas": diffdf.to_dict("records")},
          open(OUT / "sta_resultados.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
print("\nOK")
