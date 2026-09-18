"""Diagnósticos para o caderno técnico de sec-metricas (Cap. 3).

Recomputa as medidas do núcleo priorizado e testa as decisões não-óbvias:
candidaturas com R=0, listas sem recursos, empates na fronteira, razão de
somas vs. média de razões, e o piso max(1, k).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]  # notes/tecnico/ -> raiz do repositório
sys.path.insert(0, str(RAIZ / "src" / "2_gold"))

from cap3_cs_features import carregar_rrd  # noqa: E402
from cap3_taa_features import _preparar, acertos_fracionarios  # noqa: E402

N_COLS = [
    "n_eleicoes_prefeito",
    "n_eleicoes_deputado_estadual",
    "n_eleicoes_deputado_federal",
    "n_eleicoes_governador",
    "n_eleicoes_senador",
]


def base():
    df = _preparar(carregar_rrd())
    df = df[df["ano_eleicao"].isin([2018, 2022])].copy()
    incumbente = df[N_COLS].fillna(0).sum(axis=1) > 0
    df["comp"] = (
        incumbente | df["alcancou_10pct_qe_hist"].fillna(False)
    ).astype(int)
    return df


def tem_empate_na_fronteira(r, k):
    """True se um bloco de valores idênticos cruza a posição k."""
    if k <= 0 or k >= len(r):
        return False
    s = np.sort(r)[::-1]
    return s[k - 1] == s[k]


def por_lista(df):
    linhas = []
    for (ano, uf, part), g in df.groupby(["ano_eleicao", "sg_uf", "sg_partido_norm"]):
        r = g["vr_receita_recursos_partidos"].to_numpy(float)
        c = g["comp"].to_numpy(int)
        e = g["eleito"].to_numpy(int)
        tot = r.sum()
        C, G = len(r), int(c.sum())
        if tot > 0:
            necr = 1.0 / np.square(r / tot).sum()
            k = max(1, int(np.floor(necr + 0.5)))
            k_bruto = int(np.floor(necr + 0.5))
            H = acertos_fracionarios(r, c, k)
            He = acertos_fracionarios(r, e, k)
        else:
            necr, k, k_bruto, H, He = np.nan, 0, 0, 0.0, 0.0
        linhas.append(
            dict(
                ano=ano, uf=uf, partido=part, C=C, G=G, n_eleitos=int(e.sum()),
                n_com_recursos=int((r > 0).sum()), total=tot, NECr=necr,
                k=k, k_bruto=k_bruto, H=H, H_eleitos=He,
                EH=G * k / C, EH_eleitos=int(e.sum()) * k / C,
                empate_fronteira=tem_empate_na_fronteira(r, k),
                H_fracionario=bool(abs(H - round(H)) > 1e-9),
                qt_vaga=int(g["qt_vaga"].iloc[0]),
            )
        )
    return pd.DataFrame(linhas)


def bloco(titulo):
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)


def exemplo(df, ano, uf, partido):
    g = df[(df.ano_eleicao == ano) & (df.sg_uf == uf) & (df.sg_partido_norm == partido)]
    r = g["vr_receita_recursos_partidos"].to_numpy(float)
    c = g["comp"].to_numpy(int)
    e = g["eleito"].to_numpy(int)
    nome = g["nm_urna_candidato"].to_numpy() if "nm_urna_candidato" in g else None
    o = np.argsort(-r, kind="mergesort")
    r, c, e = r[o], c[o], e[o]
    if nome is not None:
        nome = nome[o]
    s = r / r.sum()
    necr = 1 / np.square(s).sum()
    k = max(1, int(np.floor(necr + 0.5)))
    print(f"\n--- {partido}/{uf} {ano} ---")
    print(f"C_l={len(r)}  G_l={c.sum()}  R_l={r.sum():,.0f}  NECr={necr:.4f}  k_l={k}")
    # pesos w_il replicando a regra fracionária
    w = np.zeros(len(r))
    i, rest = 0, k
    while i < len(r) and rest > 0:
        j = i
        while j < len(r) and r[j] == r[i]:
            j += 1
        n_bloco = j - i
        w[i:j] = 1.0 if n_bloco <= rest else rest / n_bloco
        rest -= min(n_bloco, rest)
        i = j
    print(f"{'pos':>4} {'R_il':>14} {'s_il':>8} {'w_il':>7} {'g_il':>5} {'eleito':>7}")
    for i in range(len(r)):
        print(f"{i+1:>4} {r[i]:>14,.0f} {s[i]:>8.4f} {w[i]:>7.3f} {c[i]:>5} {e[i]:>7}")
    H = float((w * c).sum())
    EH = c.sum() * k / len(r)
    print(f"soma w = {w.sum():.3f} (= k_l)   H_l = {H:.3f}   E[H_l] = {EH:.4f}"
          f"   H/E = {H/EH if EH else float('nan'):.3f}")
    print(f"conferência acertos_fracionarios = {acertos_fracionarios(r, c, k):.3f}")


def main():
    df = base()
    L = por_lista(df)

    bloco("1. AGREGADOS NACIONAIS (regra arredondada)")
    for ano in (2018, 2022):
        a = L[L.ano == ano]
        H, k, G, EH = a.H.sum(), a.k.sum(), a.G.sum(), a.EH.sum()
        print(f"\n{ano}: listas={len(a)}  C={a.C.sum()}  G={G}  sum k={k}")
        print(f"  H={H:.3f}  E[H]={EH:.3f}")
        print(f"  Precisão  = H/sum k = {H/k:.4f}   (aleatória {EH/k:.4f})")
        print(f"  Cobertura = H/sum G = {H/G:.4f}   (aleatória {EH/G:.4f})")
        print(f"  Lift = {H/EH:.4f}  | lift via precisão = {(H/k)/(EH/k):.4f}"
              f"  | lift via cobertura = {(H/G)/(EH/G):.4f}")

    bloco("2. CANDIDATURAS COM R=0 DENTRO DE LISTAS FINANCIADAS")
    for ano in (2018, 2022):
        d = df[df.ano_eleicao == ano]
        fin = L[(L.ano == ano) & (L.total > 0)]
        chaves = set(zip(fin.uf, fin.partido))
        dd = d[[ (u, p) in chaves for u, p in zip(d.sg_uf, d.sg_partido_norm) ]]
        z = dd["vr_receita_recursos_partidos"] == 0
        print(f"\n{ano}: candidatos em listas financiadas={len(dd)}  "
              f"com R=0: {z.sum()} ({100*z.mean():.1f}%)  "
              f"destes competitivos: {dd.loc[z,'comp'].sum()}  eleitos: {dd.loc[z,'eleito'].sum()}")

    print("\n-- Recálculo alternativo: C_l e G_l restritos a quem tem R>0 --")
    linhas = []
    for (ano, uf, part), g in df.groupby(["ano_eleicao", "sg_uf", "sg_partido_norm"]):
        g = g[g["vr_receita_recursos_partidos"] > 0]
        if len(g) == 0:
            continue
        r = g["vr_receita_recursos_partidos"].to_numpy(float)
        c = g["comp"].to_numpy(int)
        necr = 1.0 / np.square(r / r.sum()).sum()
        k = max(1, int(np.floor(necr + 0.5)))
        linhas.append(dict(ano=ano, C=len(r), G=int(c.sum()), k=k,
                           H=acertos_fracionarios(r, c, k),
                           EH=int(c.sum()) * k / len(r)))
    A = pd.DataFrame(linhas)
    for ano in (2018, 2022):
        a = A[A.ano == ano]
        orig = L[(L.ano == ano)]
        print(f"{ano}: lift restrito a R>0 = {a.H.sum()/a.EH.sum():.4f}   "
              f"(original {orig.H.sum()/orig.EH.sum():.4f})   "
              f"cobertura restrita = {a.H.sum()/a.G.sum():.4f}")

    bloco("3. LISTAS SEM NENHUM RECURSO PARTIDÁRIO")
    for ano in (2018, 2022):
        a = L[L.ano == ano]
        sr = a[a.total <= 0]
        cf = a[a.total > 0]
        print(f"\n{ano}: listas sem recursos={len(sr)} de {len(a)}  "
              f"candidatos={sr.C.sum()}  competitivos={sr.G.sum()}  eleitos={sr.n_eleitos.sum()}")
        print(f"  Cobertura com essas listas no denominador: {cf.H.sum()/a.G.sum():.4f}")
        print(f"  Cobertura só entre listas financiadas:     {cf.H.sum()/cf.G.sum():.4f}")
        print(f"  Lift (idêntico nos dois casos):            {cf.H.sum()/cf.EH.sum():.4f}")

    bloco("4. EMPATES NA FRONTEIRA DO CORTE")
    for ano in (2018, 2022):
        a = L[(L.ano == ano) & (L.total > 0)]
        print(f"\n{ano}: listas financiadas={len(a)}  "
              f"com empate cruzando k: {a.empate_fronteira.sum()} ({100*a.empate_fronteira.mean():.1f}%)  "
              f"com H_l fracionário: {a.H_fracionario.sum()}")
        sub = a[a.empate_fronteira]
        print(f"  H nessas listas={sub.H.sum():.2f} de {a.H.sum():.2f} total "
              f"({100*sub.H.sum()/a.H.sum():.1f}%)")
        # quanto do empate é entre candidatos com R=0
        z = a[a.empate_fronteira & (a.k >= a.n_com_recursos)]
        print(f"  destas, empate ocorre na faixa de R=0 (k >= n_com_recursos): {len(z)}")

    bloco("5. RAZÃO DE SOMAS vs. MÉDIA DE RAZÕES")
    for ano in (2018, 2022):
        a = L[(L.ano == ano) & (L.total > 0) & (L.EH > 0)]
        razao_somas = a.H.sum() / a.EH.sum()
        media_razoes = (a.H / a.EH).mean()
        mediana = (a.H / a.EH).median()
        print(f"\n{ano}: razão de somas={razao_somas:.4f}  "
              f"média dos lifts por lista={media_razoes:.4f}  mediana={mediana:.4f}  "
              f"listas com E[H]>0: {len(a)}")
        print(f"  listas com lift<1: {(a.H/a.EH < 1).sum()}  =1: {((a.H/a.EH).round(6)==1).sum()}  "
              f">1: {(a.H/a.EH > 1).sum()}")

    bloco("6. O PISO max(1, k) ALGUMA VEZ ATUA?")
    fin = L[L.total > 0]
    print(f"listas financiadas com floor(NECr+0,5)=0 antes do piso: "
          f"{(fin.k_bruto == 0).sum()}")
    print(f"NECr mínimo observado: {fin.NECr.min():.4f}  k mínimo: {fin.k.min()}")

    bloco("7. EXEMPLOS TRABALHADOS")
    exemplo(df, 2018, "AC", "PSL")
    # lista grande, com empate na fronteira e alto lift
    cand = L[(L.ano == 2022) & (L.empate_fronteira) & (L.C >= 12) & (L.G >= 3)
             & (L.H > L.EH)].sort_values("C", ascending=False)
    print("\nCandidatas a segundo exemplo (2022, empate na fronteira):")
    print(cand[["uf", "partido", "C", "G", "NECr", "k", "H", "EH"]].head(8).to_string(index=False))
    if len(cand):
        exemplo(df, 2022, cand.iloc[0].uf, cand.iloc[0].partido)

    bloco("8. DISTRIBUIÇÃO DE k E DE C")
    for ano in (2018, 2022):
        a = L[(L.ano == ano) & (L.total > 0)]
        print(f"\n{ano}: C mediana={a.C.median():.0f} média={a.C.mean():.2f} | "
              f"NECr mediana={a.NECr.median():.2f} | k mediana={a.k.median():.0f} "
              f"média={a.k.mean():.2f} | k/C mediana={(a.k/a.C).median():.4f}")
        print(f"  listas com k=C (núcleo = lista inteira): {(a.k == a.C).sum()} de {len(a)}")
        print(f"  listas com C=1: {(a.C==1).sum()}   com G=0: {(a.G==0).sum()}")

    bloco("9. EFEITO DAS LISTAS COM k=C SOBRE O LIFT AGREGADO")
    for ano in (2018, 2022):
        a = L[(L.ano == ano) & (L.total > 0)]
        print(f"\n{ano}: lift publicado = {a.H.sum()/a.EH.sum():.4f}")
        for rot, sub in [
            ("k<C (núcleo é subconjunto próprio)", a[a.k < a.C]),
            ("k=C (núcleo = lista inteira)      ", a[a.k == a.C]),
            ("C>=10 e k<C                       ", a[(a.C >= 10) & (a.k < a.C)]),
        ]:
            eh = sub.EH.sum()
            lift = sub.H.sum() / eh if eh else float("nan")
            print(f"  {rot}: n={len(sub):>4}  H={sub.H.sum():>8.2f}  "
                  f"E[H]={eh:>8.2f}  lift={lift:.4f}")
        kc = a[a.k == a.C]
        print(f"  H vindo de listas k=C: {kc.H.sum():.2f} "
              f"({100*kc.H.sum()/a.H.sum():.1f}% do H total)")
        print(f"  NECr/C médio nas listas k=C: {(kc.NECr/kc.C).mean():.3f} "
              f"(em todas as financiadas: {(a.NECr/a.C).mean():.3f})")
        print(f"  distribuição de C nas listas k=C: "
              f"{kc.C.value_counts().sort_index().head(8).to_dict()}")


if __name__ == "__main__":
    main()
