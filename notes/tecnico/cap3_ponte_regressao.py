"""Apoio a notes/tecnico/cap3-regressao-como-teste.md. Não gera nada para a tese.

Pergunta: a regressão fracionária (sec-premio-credenciais) testa a mesma hipótese que o
lift do Top-NECr? Compara, nas mesmas candidaturas (listas com R_l > 0):
  M0  especificação do capítulo (reprodução de regressao_fracionaria_cap3.py)
  M1  M0 com ln(C_l) (tamanho da lista) no lugar de ln(magnitude)
  M2  fracionária com a flag binária do capítulo (candidato_competitivo) + mulher/negra + ln(C_l)
  M3  M2 com efeitos fixos de lista (comparação intralista, como o lift)
  M4  MPL com EF de lista: pertença (fracionária) ao Top-NECr ~ competitivo + mulher + negra
e decompõe a flag binária em (vitória prévia) x (só 10% QE) e o papel de vereador.
Rodar da raiz: python notes/tecnico/cap3_ponte_regressao.py
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "2_gold"))
from cap3_cs_features import gerar_features  # noqa: E402

LISTA = ["ano_eleicao", "sg_uf", "sg_partido"]


def pertenca_top(r: pd.Series, k: int) -> np.ndarray:
    """Pertença ao Top-NECr por candidatura, com empate na fronteira fracionário
    (mesma regra de acertos_fracionarios)."""
    v = r.to_numpy(float)
    out = np.zeros(len(v))
    if k <= 0:
        return out
    ordem = np.argsort(-v, kind="mergesort")
    restantes, i = min(k, len(v)), 0
    while i < len(v) and restantes > 0:
        j = i
        while j < len(v) and v[ordem[j]] == v[ordem[i]]:
            j += 1
        bloco = j - i
        w = 1.0 if bloco <= restantes else restantes / bloco
        out[ordem[i:j]] = w
        restantes -= min(bloco, restantes)
        i = j
    return out


def base(ano):
    raw = pd.read_parquet(ROOT / "data/processed/rrd_df_novo.parquet")
    df = gerar_features(raw[raw["ano_eleicao"] == ano].copy())
    g = df.groupby(LISTA)["vr_receita_recursos_partidos"]
    df["R_l"] = g.transform("sum")
    df = df[(df["R_l"] > 0) & (df["nr_cpf_candidato"] != "-4")].copy()
    df["C_l"] = df.groupby(LISTA)["sg_uf"].transform("size")
    df["s"] = df["vr_receita_recursos_partidos"].fillna(0) / df["R_l"]
    necr = df.groupby(LISTA)["s"].transform(lambda x: 1 / (x**2).sum())
    df["k"] = np.floor(necr + 0.5).astype(int)
    df["top"] = 0.0
    for _, idx in df.groupby(LISTA).groups.items():
        sub = df.loc[idx]
        df.loc[idx, "top"] = pertenca_top(sub["vr_receita_recursos_partidos"].fillna(0), int(sub["k"].iloc[0]))
    df["comp"] = df["candidato_competitivo"].astype(float)
    df["ln_C"] = np.log(df["C_l"])
    df["ln_qt_vaga"] = np.log(df["qt_vaga"])
    for c in [c for c in df.columns if c.startswith("n_eleicoes")]:
        df[c] = df[c].fillna(0)
    df["lista_id"] = df["sg_uf"] + "_" + df["sg_partido"]
    return df


def ame(res, X, nome):
    mu = res.predict(X)
    return res.params[nome] * np.mean(mu * (1 - mu)), res.bse[nome] * np.mean(mu * (1 - mu))


def frac(df, covs, fe=False):
    d = df.dropna(subset=["s"] + covs)
    X = d[covs].astype(float)
    if fe:
        X = pd.concat([X, pd.get_dummies(d["lista_id"], drop_first=True, dtype=float)], axis=1)
    X = sm.add_constant(X, has_constant="add")
    res = sm.GLM(d["s"], X, family=sm.families.Binomial()).fit(
        cov_type="cluster", cov_kwds={"groups": d["lista_id"]})
    return res, X, len(d)


CRED = ["n_eleicoes_governador", "n_eleicoes_senador", "n_eleicoes_deputado_federal",
        "n_eleicoes_deputado_estadual", "n_eleicoes_prefeito", "n_eleicoes_vereador",
        "prop_votos_nominais_lag"]

for ano in [2018, 2022]:
    df = base(ano)
    print(f"\n================ {ano} ================")
    print(f"candidaturas em listas financiadas: {len(df)}; listas: {df['lista_id'].nunique()}")
    print(f"NaN em prop_votos_nominais_lag: {df['prop_votos_nominais_lag'].isna().sum()}; "
          f"NaN em negra: {df['negra'].isna().sum()}")
    vit = df["incumbente"]
    qe = df["alcancou_10pct_qe_hist"].fillna(False).astype(bool)
    print(f"competitivos: {int(df['comp'].sum())} | por vitória: {int(vit.sum())} | "
          f"só 10% QE (sem vitória): {int((qe & ~vit).sum())}")
    ver = (df["n_eleicoes_vereador"] > 0) & ~df["candidato_competitivo"]
    print(f"vereadores eleitos não classificados como competitivos: {int(ver.sum())}")

    # Médias intralista: share relativo à divisão igual (s*C_l) e pertença ao topo
    df["s_rel"] = df["s"] * df["C_l"]
    grp = {"competitivo": df["candidato_competitivo"],
           "  vitória prévia": vit, "  só 10% QE": qe & ~vit,
           "não comp.: vereador eleito": ver,
           "não comp.: sem nada": ~df["candidato_competitivo"] & ~ver}
    print("\ngrupo | n | média s·C_l (1 = divisão igual) | P(Top-NECr)")
    for nome, m in grp.items():
        print(f"{nome:30s} {int(m.sum()):6d}  {df.loc[m,'s_rel'].mean():6.2f}  {df.loc[m,'top'].mean():.3f}")
    p1, p0 = df.loc[df.comp == 1, "top"].mean(), df.loc[df.comp == 0, "top"].mean()
    print(f"P(top|comp)={p1:.3f}  P(top|não)={p0:.3f}  razão={p1/p0:.2f}")
    H, E = (df["top"] * df["comp"]).sum(), (df.groupby("lista_id").apply(
        lambda x: x["comp"].sum() * x["k"].iloc[0] / len(x), include_groups=False)).sum()
    print(f"lift (checagem) = {H/E:.3f}")

    ctrl = ["mulher", "negra"]
    r0, X0, n0 = frac(df, CRED + ["ln_qt_vaga"] + ctrl)
    r1, X1, n1 = frac(df, CRED + ["ln_C"] + ctrl)
    r1b, X1b, _ = frac(df, CRED + ["ln_qt_vaga", "ln_C"] + ctrl)
    print(f"\nM0 (capítulo)  N={n0}  AME dep.fed={ame(r0,X0,'n_eleicoes_deputado_federal')[0]*100:.2f} pp"
          f"  AME ln_mag={ame(r0,X0,'ln_qt_vaga')[0]*100:.2f}  deviance={r0.deviance:.1f}")
    print(f"M1 (ln C_l)    AME dep.fed={ame(r1,X1,'n_eleicoes_deputado_federal')[0]*100:.2f} pp"
          f"  AME ln_C={ame(r1,X1,'ln_C')[0]*100:.2f}  deviance={r1.deviance:.1f}")
    print(f"M1b (ambos)    AME ln_mag={ame(r1b,X1b,'ln_qt_vaga')[0]*100:.2f}  AME ln_C={ame(r1b,X1b,'ln_C')[0]*100:.2f}")
    for nm in CRED:
        print(f"   {nm:32s} M0 {ame(r0,X0,nm)[0]*100:6.2f}   M1 {ame(r1,X1,nm)[0]*100:6.2f}")

    r2, X2, n2 = frac(df, ["comp", "ln_C"] + ctrl)
    a, se = ame(r2, X2, "comp")
    print(f"\nM2 fracionária, flag binária: AME comp = {a*100:.2f} pp (EP {se*100:.2f}); "
          f"mulher {ame(r2,X2,'mulher')[0]*100:.2f}; negra {ame(r2,X2,'negra')[0]*100:.2f}")
    r3, X3, n3 = frac(df, ["comp"] + ctrl, fe=True)
    a, se = ame(r3, X3, "comp")
    print(f"M3 fracionária + EF lista:    AME comp = {a*100:.2f} pp (EP {se*100:.2f}); "
          f"mulher {ame(r3,X3,'mulher')[0]*100:.2f}; negra {ame(r3,X3,'negra')[0]*100:.2f}")

    d = df.dropna(subset=["negra"]).copy()
    cols = ["top", "comp", "mulher", "negra"]
    dm = d[cols] - d.groupby("lista_id")[cols].transform("mean")
    m4 = sm.OLS(dm["top"], dm[["comp", "mulher", "negra"]]).fit(
        cov_type="cluster", cov_kwds={"groups": d["lista_id"]})
    print(f"M4 MPL Top-NECr + EF lista:   comp {m4.params['comp']:.3f} (EP {m4.bse['comp']:.3f}); "
          f"mulher {m4.params['mulher']:.3f}; negra {m4.params['negra']:.3f}; "
          f"média P(top)={d['top'].mean():.3f}")


# --- Complemento: zeros na VD e contraparte regressiva da tbl-cap3-01 (lift por magnitude)
print("\n\n===== complemento =====")
for ano in [2018, 2022]:
    df = base(ano).dropna(subset=["negra"])
    print(f"\n{ano}: share = 0 em {(df['s'] == 0).mean():.1%} das candidaturas; "
          f"C_l médio {df.groupby('lista_id')['C_l'].first().mean():.1f}, "
          f"1/C_l médio por candidatura {(1/df['C_l']).mean():.3f}")
    df["grupo_mag"] = pd.cut(df["qt_vaga"], [0, 12, 31, 70], labels=["Pequeno", "Médio", "Grande"])
    for gm, d in df.groupby("grupo_mag", observed=True):
        cols = ["top", "comp", "mulher", "negra"]
        dm = d[cols] - d.groupby("lista_id")[cols].transform("mean")
        m = sm.OLS(dm["top"], dm[["comp", "mulher", "negra"]]).fit(
            cov_type="cluster", cov_kwds={"groups": d["lista_id"]})
        p1, p0 = d.loc[d.comp == 1, "top"].mean(), d.loc[d.comp == 0, "top"].mean()
        print(f"  {gm:8s} n={len(d):5d}  MPL-EF comp={m.params['comp']:.3f} (EP {m.bse['comp']:.3f})"
              f"  P(top|comp)={p1:.3f} P(top|não)={p0:.3f}")
