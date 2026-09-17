"""Recalcula a regressão fracionária de "prêmio" às credenciais eleitorais prévias
(Cap. 3, seção reinserida em 16/09/2026) com a base rrd_df_novo.parquet corrigida.

A especificação replica a versão apresentada em revisoes/2026-09-12_..., que não tinha
código versionado no repositório: GLM família Binomial / link logit (Papke & Wooldridge
1996) da fração de recursos partidários que cada candidatura recebe dentro de sua lista,
com erros-padrão clusterizados por lista (partido x UF) e modelos separados por eleição
(2018 e 2022). AMEs calculados analiticamente (AME_j = beta_j * mean[mu(1-mu)]) com
Jacobiano numérico para o método delta sobre a matriz de covariância clusterizada.

Acrescenta `mulher` e `negra` como controles estruturais (17/09/2026): ~80% da amostra
não tem nenhuma vitória prévia, mas esse grupo não recebe zero recursos — em média,
mulheres sem histórico recebem mais que homens sem histórico, consistente com o piso de
30% do FEFC para candidaturas femininas (desde 2018) e o repasse proporcional a
candidaturas negras (desde 2022), já discutidos na seção @sec-discussao-cap3. No modelo,
`mulher` é positivo e robusto nos dois anos; `negra` é negativo e significativo em 2018
(antes da obrigatoriedade do repasse proporcional) e cai a ~0 e não-significativo em 2022
(primeira eleição sob a regra) — indício de efeito nivelador da regra, não conclusivo.
Testou-se também um proxy de "já disputou eleição antes, mesmo sem vencer" (candidaturas
anteriores sem vitória, via CPF em resultados.parquet) — não significativo em 2018
(p=0,80) e apenas marginal em 2022 (p=0,09), por isso não entrou no modelo final.

Amostra: candidaturas de listas com recursos partidários (R_l > 0), excluindo as poucas
candidaturas com CPF inválido ("-4", sem histórico eleitoral linkável — 3 casos na base
inteira, nenhum em 2018/2022) e as candidaturas sem raça/cor declarada (`negra` NaN).

Gera:
  tese/reports/regressao-fracionaria/coeficientes.csv  (beta, EP, z, p por variável/ano)
  tese/reports/regressao-fracionaria/ames.csv           (AME, EP, IC95%, p por variável/ano)
  figs/cap3_regressao_fracionaria.png                   (forest plot dos AMEs, 2018 vs 2022)

Execute da raiz do repositório: python tese/scripts/regressao_fracionaria_cap3.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.special import expit
from scipy.stats import norm

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "2_gold"))
from cap3_cs_features import gerar_features  # noqa: E402

REPORTS = ROOT / "tese" / "reports" / "regressao-fracionaria"
FIGS = ROOT / "figs"
REPORTS.mkdir(parents=True, exist_ok=True)

YEARS = [2018, 2022]
PRETO, CINZA = "#222222", "#a6a6a6"

# Ordem e rótulos pt-BR iguais aos da figura de 12/09/2026 (revisoes/...).
COVARS = [
    ("ln_qt_vaga", "Ln Magnitude do distrito"),
    ("n_eleicoes_deputado_estadual", "Nº Eleições Deputado Estadual"),
    ("n_eleicoes_deputado_federal", "Nº Eleições Deputado Federal"),
    ("n_eleicoes_governador", "Nº Eleições Governador"),
    ("n_eleicoes_prefeito", "Nº Eleições Prefeito"),
    ("n_eleicoes_senador", "Nº Eleições Senador"),
    ("n_eleicoes_vereador", "Nº Eleições Vereador"),
    ("prop_votos_nominais_lag", "Proporção de votos nominais intralista t-1"),
]
# Controles estruturais (pisos legais de repasse), acrescentados em 16/09/2026 — ver
# docstring do módulo. Plotados junto aos AMEs de credenciais, mas conceitualmente
# separados: não são credenciais eleitorais, são obrigações legais de alocação.
CONTROLES = [
    ("mulher", "Mulher"),
    ("negra", "Negra"),
]
N_ELEICOES_COLS = [c for c, _ in COVARS if c.startswith("n_eleicoes")]
TODAS_COVARS = COVARS + CONTROLES


def montar_base(ano: int) -> pd.DataFrame:
    """Candidaturas de listas financiadas (R_l > 0) do ano, com y (share de recursos
    partidários na lista) e as covariáveis do modelo. Exclui CPF '-4' (sem histórico)."""
    raw = pd.read_parquet(ROOT / "data" / "processed" / "rrd_df_novo.parquet")
    raw = raw[raw["ano_eleicao"] == ano].copy()
    df = gerar_features(raw)  # prop_vr_receita_candidato = R_il / R_l (share na lista)

    r_lista = df.groupby(["ano_eleicao", "sg_uf", "sg_partido"])[
        "vr_receita_recursos_partidos"
    ].transform("sum")
    df = df[r_lista > 0].copy()

    df = df[df["nr_cpf_candidato"] != "-4"].copy()

    df["ln_qt_vaga"] = np.log(df["qt_vaga"])
    for col in N_ELEICOES_COLS:
        df[col] = df[col].fillna(0)

    # mulher/negra: NaN só quando ds_cor_raca/ds_genero não foi declarado ao TSE
    # (cap3_cs_features via gerar_rrd.py) — poucas candidaturas, excluídas do modelo
    # em vez de imputadas (ver cols_modelo abaixo).
    cols_modelo = ["prop_vr_receita_candidato"] + [c for c, _ in TODAS_COVARS]
    df = df.dropna(subset=cols_modelo)

    df["lista_id"] = df["sg_uf"].astype(str) + "_" + df["sg_partido"].astype(str)
    return df


def _mu(beta: np.ndarray, X: np.ndarray) -> np.ndarray:
    return expit(X @ beta)


def _ame_vec(beta: np.ndarray, X: np.ndarray, idx_covars: np.ndarray) -> np.ndarray:
    """AME_j = beta_j * mean_i[mu_i(1-mu_i)] para as colunas não-constantes de X."""
    mu = _mu(beta, X)
    mean_w = np.mean(mu * (1 - mu))
    return beta[idx_covars] * mean_w


def _jacobiano_numerico(beta: np.ndarray, X: np.ndarray, idx_covars: np.ndarray,
                         eps: float = 1e-5) -> np.ndarray:
    """Jacobiano d(AME)/d(beta) por diferenças finitas centradas (método delta)."""
    n_covars = len(idx_covars)
    n_params = len(beta)
    G = np.zeros((n_covars, n_params))
    for k in range(n_params):
        step = eps * max(1.0, abs(beta[k]))
        beta_p, beta_m = beta.copy(), beta.copy()
        beta_p[k] += step
        beta_m[k] -= step
        ame_p = _ame_vec(beta_p, X, idx_covars)
        ame_m = _ame_vec(beta_m, X, idx_covars)
        G[:, k] = (ame_p - ame_m) / (2 * step)
    return G


def estimar(ano: int) -> dict:
    df = montar_base(ano)

    y = df["prop_vr_receita_candidato"].to_numpy(dtype=float)
    X_df = sm.add_constant(df[[c for c, _ in TODAS_COVARS]], has_constant="add")
    X = X_df.to_numpy(dtype=float)
    groups = df["lista_id"].to_numpy()

    modelo = sm.GLM(y, X, family=sm.families.Binomial())
    resultado = modelo.fit(cov_type="cluster", cov_kwds={"groups": groups})

    beta = resultado.params
    cov_beta = resultado.cov_params()
    idx_covars = np.arange(1, len(beta))  # exclui a constante (posição 0)

    ames = _ame_vec(beta, X, idx_covars)
    G = _jacobiano_numerico(beta, X, idx_covars)
    var_ames = G @ cov_beta @ G.T
    se_ames = np.sqrt(np.diag(var_ames))

    z = ames / se_ames
    p = 2 * (1 - norm.cdf(np.abs(z)))
    ic_inf = ames - 1.96 * se_ames
    ic_sup = ames + 1.96 * se_ames

    n_listas = df["lista_id"].nunique()
    n_cand = len(df)

    tab_coef = pd.DataFrame({
        "variavel": ["const"] + [c for c, _ in TODAS_COVARS],
        "beta": beta,
        "ep": resultado.bse,
        "z": resultado.tvalues,
        "p": resultado.pvalues,
    })
    tab_coef["ano_eleicao"] = ano
    tab_coef["n_candidaturas"] = n_cand
    tab_coef["n_listas"] = n_listas

    tab_ame = pd.DataFrame({
        "variavel": [c for c, _ in TODAS_COVARS],
        "rotulo": [lbl for _, lbl in TODAS_COVARS],
        "ame": ames,
        "ep": se_ames,
        "ic_inf": ic_inf,
        "ic_sup": ic_sup,
        "z": z,
        "p": p,
    })
    tab_ame["ano_eleicao"] = ano
    tab_ame["n_candidaturas"] = n_cand
    tab_ame["n_listas"] = n_listas

    print(f"\n=== {ano}: N candidaturas={n_cand}, N listas financiadas={n_listas} ===")
    print(resultado.summary())
    print("\nAMEs:")
    print(tab_ame[["rotulo", "ame", "ep", "p"]].to_string(index=False))

    return {"resultado": resultado, "coef": tab_coef, "ame": tab_ame, "df": df}


def fmt(x, d=2):
    return f"{x:,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def fig_ames(ames_por_ano: dict) -> None:
    """Forest plot dos AMEs por variável, 2018 (círculo preto) vs 2022 (losango cinza),
    no mesmo layout de tese/scripts/regenerar_figuras_cap3.py. Credenciais eleitorais
    (COVARS) no topo, controles estruturais (CONTROLES) embaixo, com um espaço e uma
    linha pontilhada horizontal separando os dois blocos."""
    variaveis = [lbl for _, lbl in COVARS] + [lbl for _, lbl in CONTROLES]
    gap = 1  # linhas em branco entre os dois blocos
    n_covars, n_controles = len(COVARS), len(CONTROLES)
    y_controles = np.arange(n_controles)[::-1]
    y_covars = np.arange(n_covars)[::-1] + n_controles + gap
    y_pos = np.concatenate([y_covars, y_controles])

    fig, ax = plt.subplots(figsize=(9, 6.8))
    offsets = {2018: 0.12, 2022: -0.12}
    marcadores = {2018: "o", 2022: "D"}
    cores = {2018: PRETO, 2022: CINZA}

    for ano in YEARS:
        tab = ames_por_ano[ano].set_index("rotulo").loc[variaveis]
        y = y_pos + offsets[ano]
        ax.errorbar(
            tab["ame"], y,
            xerr=[tab["ame"] - tab["ic_inf"], tab["ic_sup"] - tab["ame"]],
            fmt=marcadores[ano], color=cores[ano], ecolor=cores[ano],
            capsize=3, markersize=7, linewidth=1.2, label=str(ano),
        )
        dy = 10 if ano == 2018 else -15
        for yi, val in zip(y, tab["ame"]):
            ax.annotate(fmt(val), (val, yi), textcoords="offset points",
                        xytext=(0, dy), ha="center", fontsize=8, color=cores[ano])

    ax.axvline(0, color="#666666", linestyle="--", linewidth=0.8)
    y_separador = (y_controles.max() + y_covars.min()) / 2
    ax.axhline(y_separador, color="#cccccc", linestyle=":", linewidth=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(variaveis)
    ax.set_xlabel("AME")
    ax.set_ylabel("Variável")
    ax.legend(title="Eleições", loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    out = FIGS / "cap3_regressao_fracionaria.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"\nFigura salva em {out}")


def main():
    ames_por_ano = {}
    coefs = []
    ames = []
    for ano in YEARS:
        r = estimar(ano)
        ames_por_ano[ano] = r["ame"]
        coefs.append(r["coef"])
        ames.append(r["ame"])

    pd.concat(coefs, ignore_index=True).to_csv(REPORTS / "coeficientes.csv", index=False)
    pd.concat(ames, ignore_index=True).to_csv(REPORTS / "ames.csv", index=False)
    print(f"\nTabelas salvas em {REPORTS}")

    fig_ames(ames_por_ano)


if __name__ == "__main__":
    main()
