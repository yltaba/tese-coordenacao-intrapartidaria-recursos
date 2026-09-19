"""Piloto do logit fracionário condicional (EF de lista) — apoio a notes/tecnico/cap3-plano-regressao-intralista.md.
Rodar da raiz: python notes/tecnico/cap3_piloto_logit_condicional.py"""
import numpy as np, pandas as pd
from scipy.stats import norm
src = open("notes/tecnico/cap3_ponte_regressao.py", encoding="utf-8").read().split("CRED = [")[0]
ns = {"__file__": "notes/tecnico/cap3_ponte_regressao.py"}; exec(src, ns)
CRED = ["n_eleicoes_governador","n_eleicoes_senador","n_eleicoes_deputado_federal",
        "n_eleicoes_deputado_estadual","n_eleicoes_prefeito","n_eleicoes_vereador","prop_votos_nominais_lag"]

def cond_logit_frac(s, X, g, it=50):
    """max sum_l sum_i s_il log softmax_l(X b). EF de lista eliminado; EP cluster por lista."""
    codes, g = np.unique(g, return_inverse=True); L = len(codes)
    b = np.zeros(X.shape[1])
    for _ in range(it):
        eta = X @ b; eta -= np.bincount(g, eta)[g] / np.bincount(g)[g]
        e = np.exp(eta); p = e / np.bincount(g, e)[g]
        xbar = np.vstack([np.bincount(g, p * X[:, j]) for j in range(X.shape[1])]).T[g]
        Xc = X - xbar
        grad = Xc.T @ s  # sum (s-p) x == sum s (x - xbar)
        H = (Xc * p[:, None]).T @ Xc
        step = np.linalg.solve(H, grad); b += step
        if np.max(np.abs(step)) < 1e-10: break
    sc = np.vstack([np.bincount(g, ((s - p)[:, None] * X)[:, j], minlength=L) for j in range(X.shape[1])]).T
    Hi = np.linalg.inv(H); V = Hi @ (sc.T @ sc) @ Hi * L / (L - 1)
    return b, np.sqrt(np.diag(V)), p

for ano in [2018, 2022]:
    df = ns["base"](ano).dropna(subset=CRED + ["mulher", "negra"])
    df = df[df["C_l"] > 1]
    for nome, covs in [("contagens (spec atual)", CRED + ["mulher", "negra"]), ("flag binária", ["comp", "mulher", "negra"])]:
        b, se, p = cond_logit_frac(df["s"].to_numpy(float), df[covs].to_numpy(float), df["lista_id"].to_numpy())
        w = np.mean(p * (1 - p))
        print(f"\n{ano} [{nome}] N={len(df)} listas={df['lista_id'].nunique()}")
        for c, bi, si in zip(covs, b, se):
            print(f"  {c:30s} b={bi:6.3f} (EP {si:.3f}) p={2*(1-norm.cdf(abs(bi/si))):.3f}  exp(b)={np.exp(bi):5.2f}  AME~{bi*w*100:5.2f} pp")
