"""Regressão fracionária do Cap. 3 (sec-premio-credenciais): teste contínuo da priorização.

Pergunta: sem impor corte algum para definir um núcleo, as credenciais eleitorais prévias estão
associadas a uma parcela maior dos recursos partidários **da própria lista**?

Especificação (18/09/2026, substitui o GLM Binomial agrupado de 16-17/09):
logit fracionário **condicional** — quase-verossimilhança da família de Papke & Wooldridge (1996)
com a média modelada como softmax dentro da lista,

    E[s_il | X, l] = exp(x_il'b) / sum_{j in l} exp(x_jl'b),   s_il = R_il / R_l,

maximizando sum_l sum_i s_il log p_il. O efeito fixo de lista se cancela no softmax: tudo o que é
constante na lista (tamanho C_l, magnitude, partido, UF, R_l) é controlado por construção e não é
estimado — por isso ln(magnitude) saiu dos regressores. A comparação é intralista, como no Top-NECr.
Equivale a Poisson (PPML) de s_il com EF de lista; sem problema de parâmetros incidentais.
Estimado por Newton; EP clusterizados por lista (sanduíche sobre escores somados por lista, com
correção L/(L-1)).

Massa remanescente (19/09/2026, I-3-001/STA-3-001 do run-002): s_il = R_il / R_l usa o R_l da lista
completa (mesmo denominador do NECr/Top-NECr), mas as exclusões da amostra (CPF "-4", raça/cor não
declarada, votos t-1 ausentes) deixam listas em que as parcelas retidas somam m_l = sum_i s_il < 1 (2 listas em 2018,
12 em 2022). O estimando é mantido — a parcela original — e, como no PPML com EF de lista, a média
perfilada passa a ser m_l * p_il (o EF absorve m_l; p_il continua o softmax entre as retidas).
b não muda (o gradiente já era sum (s - m p) x), mas a Hessiana, os escores do sanduíche e os AMEs
agora usam m_l * p_il. Até 18/09/2026 o código assumia m_l = 1, o que só afetava EP e AMEs.
Sensibilidade: renormalizar as parcelas entre as retidas (s/m_l) — em sensibilidade_massa.csv.

Por que mudou: o GLM anterior juntava todas as listas; como a parcela média numa lista é 1/C_l,
parte da variação era tamanho de lista, e ln(magnitude) funcionava como aproximação disso (AME de
-10 pp em 2018, que vai a ~0 quando ln(C_l) entra). Ver notes/tecnico/cap3-plano-regressao-intralista.md.

Efeitos reportados:
  - AME (pp de parcela intralista): contínuas/contagens = média de b*p(1-p) (efeito sobre a própria
    parcela, colegas de lista fixos); binárias (mulher, negra, competitivo) = variação discreta 0->1
    recalculando o softmax da lista (também qe_sem_vitoria). EP pelo método delta (Jacobiano numérico).
  - Razão de parcelas exp(b) (medida principal, na figura desde 18/09/2026): p_i/p_j =
    exp((x_i - x_j)'b) para dois colegas de lista — exata, não depende do tamanho da lista.
    Não é odds ratio. Contagens: por vitória adicional (multiplicativa). Votos t-1: por +10 p.p.
    (colunas razao_rep* em coeficientes.csv).

Modelos:
  R2 (figura, decomposição): contagens de vitórias por cargo + prop_votos_nominais_lag +
    qe_sem_vitoria (critério 10% QE da flag, entre quem não tem vitória acima de vereador;
    acrescentado 18/09/2026) + mulher + negra. Com isso todo componente da flag tem um termo.
  R1 (CSV): candidato_competitivo (mesma flag do Top-NECr) + mulher + negra.
  R1 x magnitude (só CSV): R1 com credencial x grupo de magnitude (grupos da tbl-cap3-01);
    a magnitude sozinha não é identificada, só a interação. Em razão exp(b).

Amostra: candidaturas de listas com R_l > 0 e C_l > 1 (listas de uma candidatura não têm
comparação intralista e não contribuem para a verossimilhança condicional); exclui CPF "-4" e
candidaturas sem raça/cor declarada (`negra` NaN) ou sem `prop_votos_nominais_lag` (4 em 2018).

Testou-se em 16/09 um proxy de "já disputou eleição antes, mesmo sem vencer" — não significativo
no GLM agrupado (p=0,80 em 2018; 0,09 em 2022), por isso não entrou; não foi retestado aqui.

Gera:
  tese/reports/regressao-fracionaria/coeficientes.csv  (b, EP, z, p, exp(b) e IC por modelo/variável/ano)
  tese/reports/regressao-fracionaria/ames.csv           (AME, EP, IC95%, p por modelo/variável/ano)
  tese/reports/regressao-fracionaria/interacao_magnitude.csv (razão da credencial por magnitude)
  tese/reports/regressao-fracionaria/amostra.csv       (candidaturas/listas antes e depois dos filtros)
  tese/reports/regressao-fracionaria/sensibilidade_massa.csv (b e EP com parcelas renormalizadas entre as retidas)
  figs/cap3_regressao_fracionaria.png                   (forest plot das razões exp(b) do R2, escala log, 2018 vs 2022)

Execute da raiz do repositório: python tese/scripts/regressao_fracionaria_cap3.py
"""
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
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

# Ordem e rótulos pt-BR (reordenado em 17/09/2026: eleições por cargo em ordem
# hierárquica Governador > Senador > Deputado Federal > Deputado Estadual > Prefeito >
# Vereador).
COVARS = [
    ("n_eleicoes_governador", "Nº Eleições Governador"),
    ("n_eleicoes_senador", "Nº Eleições Senador"),
    ("n_eleicoes_deputado_federal", "Nº Eleições Deputado Federal"),
    ("n_eleicoes_deputado_estadual", "Nº Eleições Deputado Estadual"),
    ("n_eleicoes_prefeito", "Nº Eleições Prefeito"),
    ("n_eleicoes_vereador", "Nº Eleições Vereador"),
    ("prop_votos_nominais_lag", "Proporção de votos nominais intralista t-1"),
    ("qe_sem_vitoria", "≥10% do QE em eleição anterior, sem vitória acima de vereador"),
]
# Controles estruturais, plotados junto aos AMEs de credenciais mas separados por uma linha
# pontilhada: mulher/negra são pisos legais de repasse (acrescentados em 16/09/2026).
# Ln Magnitude do distrito saiu em 18/09/2026: é constante na lista e fica absorvida pelo
# efeito fixo do logit condicional.
CONTROLES = [
    ("mulher", "Mulher"),
    ("negra", "Negra"),
]
N_ELEICOES_COLS = [c for c, _ in COVARS if c.startswith("n_eleicoes")]
BINARIAS = {"mulher", "negra", "competitivo", "qe_sem_vitoria"}
# Incremento em que a razão é reportada quando +1 não é realista: (fator sobre b, rótulo).
ESCALA_RAZAO = {"prop_votos_nominais_lag": (0.1, "+10 p.p.")}

MODELOS = {
    "R2": COVARS + CONTROLES,
    "R1": [("competitivo", "Credencial eleitoral prévia (flag do Top-NECr)")] + CONTROLES,
}


def montar_base(ano: int) -> tuple[pd.DataFrame, dict]:
    """Candidaturas de listas financiadas (R_l > 0) e com C_l > 1 no ano, com
    y = prop_vr_receita_candidato = R_il / R_l e as covariáveis dos modelos."""
    raw = pd.read_parquet(ROOT / "data" / "processed" / "rrd_df_novo.parquet")
    raw = raw[raw["ano_eleicao"] == ano].copy()
    df = gerar_features(raw)
    amostra = {"ano_eleicao": ano}

    r_lista = df.groupby(["sg_uf", "sg_partido"])["vr_receita_recursos_partidos"].transform("sum")
    df = df[r_lista > 0].copy()
    df = df[df["nr_cpf_candidato"] != "-4"].copy()
    for col in N_ELEICOES_COLS:
        df[col] = df[col].fillna(0)
    df["competitivo"] = df["candidato_competitivo"].astype(float)
    # Critério (ii) da flag competitivo isolado: só muda a classificação de quem não tem
    # vitória acima de vereador (incumbente). Metade desses casos já venceu para vereador,
    # o que entra no modelo pela contagem própria — por isso o rótulo não diz "nunca eleitos".
    df["qe_sem_vitoria"] = (
        df["alcancou_10pct_qe_hist"].fillna(False).astype(bool) & ~df["incumbente"].astype(bool)
    ).astype(float)

    # mulher/negra: NaN só quando ds_cor_raca/ds_genero não foi declarado ao TSE —
    # poucas candidaturas, excluídas em vez de imputadas.
    cols_modelo = ["prop_vr_receita_candidato"] + sorted({c for m in MODELOS.values() for c, _ in m})
    df = df.dropna(subset=cols_modelo)
    df["lista_id"] = df["sg_uf"].astype(str) + "_" + df["sg_partido"].astype(str)
    amostra["candidaturas_listas_financiadas"] = len(df)
    amostra["listas_financiadas"] = df["lista_id"].nunique()

    # Sem colega de lista não há comparação intralista (contribuição nula à verossimilhança).
    df["C_l"] = df.groupby("lista_id")["lista_id"].transform("size")
    df = df[df["C_l"] > 1].copy()
    amostra["candidaturas_modelo"] = len(df)
    amostra["listas_modelo"] = df["lista_id"].nunique()
    amostra["listas_com_variacao_competitivo"] = int(
        (df.groupby("lista_id")["competitivo"].nunique() > 1).sum()
    )
    # Massa remanescente m_l: parte de R_l que ficou nas candidaturas retidas.
    massa = df.groupby("lista_id")["prop_vr_receita_candidato"].sum()
    if (massa <= 0).any():
        raise ValueError("lista sem recursos entre as candidaturas retidas (m_l = 0)")
    amostra["listas_massa_incompleta"] = int((massa < 1 - 1e-9).sum())
    amostra["massa_minima"] = float(massa.min())
    return df, amostra


def _centrar_lista(eta: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Subtrai a média da lista (não altera o softmax; evita overflow)."""
    return eta - (np.bincount(g, eta) / np.bincount(g))[g]


def _softmax_lista(eta: np.ndarray, g: np.ndarray) -> np.ndarray:
    """p_il = exp(eta_il) / sum_{j in l} exp(eta_jl)."""
    e = np.exp(_centrar_lista(eta, g))
    return e / np.bincount(g, e)[g]


def _media_lista(v: np.ndarray, p: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Média de cada coluna de v ponderada por p dentro da lista, devolvida por linha."""
    L = g.max() + 1
    return np.column_stack([np.bincount(g, p * v[:, k], minlength=L) for k in range(v.shape[1])])[g]


def logit_condicional_fracionario(s: np.ndarray, X: np.ndarray, g: np.ndarray,
                                  max_iter: int = 100, tol: float = 1e-10):
    """Maximiza sum_l sum_i s_il log p_il (p = softmax na lista) por Newton.
    Média perfilada m_l * p_il, com m_l = sum_{i in l} s_il (= 1 em lista completa).
    g: código inteiro da lista (0..L-1). Retorna b, V (cluster por lista), p, iterações."""
    L, K = g.max() + 1, X.shape[1]
    m = np.bincount(g, s, minlength=L)[g]
    # Regressor constante em todas as listas (ex.: C_l, magnitude) cai no softmax e não é
    # identificado; sem esta checagem o Newton "estima" ruído de ponto flutuante.
    desvio = X - np.column_stack([np.bincount(g, X[:, k]) / np.bincount(g) for k in range(K)])[g]
    if np.any(np.abs(desvio).max(axis=0) < 1e-10):
        raise ValueError("regressor sem variação dentro de nenhuma lista (não identificado)")
    b = np.zeros(K)
    for it in range(1, max_iter + 1):
        p = _softmax_lista(X @ b, g)
        Xc = X - _media_lista(X, p, g)
        grad = Xc.T @ s  # = sum (s - m p) x, pois p soma 1 e s soma m na lista
        H = (Xc * (m * p)[:, None]).T @ Xc
        passo = np.linalg.solve(H, grad)
        b = b + passo
        if np.max(np.abs(passo)) < tol:
            break
    else:
        raise RuntimeError(f"Newton não convergiu em {max_iter} iterações")
    p = _softmax_lista(X @ b, g)
    Xc = X - _media_lista(X, p, g)
    H = (Xc * (m * p)[:, None]).T @ Xc
    escores = np.column_stack([np.bincount(g, (s - m * p) * X[:, k], minlength=L) for k in range(K)])
    H_inv = np.linalg.inv(H)
    V = H_inv @ (escores.T @ escores) @ H_inv * L / (L - 1)
    return b, V, p, it


def _ame_vec(b: np.ndarray, X: np.ndarray, g: np.ndarray, binarias: np.ndarray,
             m: np.ndarray) -> np.ndarray:
    """AME sobre a própria parcela (escala original R_il/R_l, média m_l p), colegas de lista
    fixos. Contínuas: média de b_k m p(1-p). Binárias: média de m [p(x_k=1) - p(x_k=0)]."""
    eta = _centrar_lista(X @ b, g)
    e = np.exp(eta)
    soma = np.bincount(g, e)[g]
    p = e / soma
    outros = soma - e
    out = np.empty(len(b))
    for k in range(len(b)):
        if binarias[k]:
            e1 = np.exp(eta + b[k] * (1 - X[:, k]))
            e0 = np.exp(eta - b[k] * X[:, k])
            out[k] = np.mean(m * (e1 / (e1 + outros) - e0 / (e0 + outros)))
        else:
            out[k] = b[k] * np.mean(m * p * (1 - p))
    return out


def _jacobiano_numerico(b, X, g, binarias, m, eps: float = 1e-5) -> np.ndarray:
    """Jacobiano d(AME)/d(b) por diferenças finitas centradas (método delta)."""
    G = np.zeros((len(b), len(b)))
    for k in range(len(b)):
        h = eps * max(1.0, abs(b[k]))
        bp, bm = b.copy(), b.copy()
        bp[k] += h
        bm[k] -= h
        G[:, k] = (_ame_vec(bp, X, g, binarias, m) - _ame_vec(bm, X, g, binarias, m)) / (2 * h)
    return G


def estimar(df: pd.DataFrame, ano: int, modelo: str) -> dict:
    variaveis = MODELOS[modelo]
    nomes = [c for c, _ in variaveis]
    y = df["prop_vr_receita_candidato"].to_numpy(dtype=float)
    X = df[nomes].to_numpy(dtype=float)
    _, g = np.unique(df["lista_id"].to_numpy(), return_inverse=True)
    binarias = np.array([c in BINARIAS for c in nomes])

    b, V, p, n_iter = logit_condicional_fracionario(y, X, g)
    ep = np.sqrt(np.diag(V))
    erro_soma = np.max(np.abs(np.bincount(g, p) - 1))
    assert erro_soma < 1e-8, f"parcelas previstas não somam 1 na lista (erro {erro_soma})"

    m = np.bincount(g, y)[g]
    ames = _ame_vec(b, X, g, binarias, m)
    G = _jacobiano_numerico(b, X, g, binarias, m)
    se_ames = np.sqrt(np.diag(G @ V @ G.T))

    base = {"modelo": modelo, "ano_eleicao": ano, "n_candidaturas": len(df),
            "n_listas": g.max() + 1}
    z_b = b / ep
    tab_coef = pd.DataFrame({
        "variavel": nomes, "rotulo": [lbl for _, lbl in variaveis],
        "beta": b, "ep": ep, "z": z_b, "p": 2 * (1 - norm.cdf(np.abs(z_b))),
        "razao": np.exp(b), "razao_ic_inf": np.exp(b - 1.96 * ep),
        "razao_ic_sup": np.exp(b + 1.96 * ep),
    }).assign(**base)
    # Razão na unidade reportada (figura/texto): igual a `razao`, exceto onde ESCALA_RAZAO
    # redefine o incremento (votos t-1: +10 p.p. em vez de 0 -> 100% da lista).
    esc = np.array([ESCALA_RAZAO.get(c, (1.0, ""))[0] for c in nomes])
    tab_coef["incremento"] = [ESCALA_RAZAO.get(c, (1.0, "+1"))[1] or "+1" for c in nomes]
    tab_coef["razao_rep"] = np.exp(esc * b)
    tab_coef["razao_rep_ic_inf"] = np.exp(esc * (b - 1.96 * ep))
    tab_coef["razao_rep_ic_sup"] = np.exp(esc * (b + 1.96 * ep))
    z = ames / se_ames
    tab_ame = pd.DataFrame({
        "variavel": nomes, "rotulo": [lbl for _, lbl in variaveis],
        "tipo_ame": np.where(binarias, "discreto_0_1", "derivada"),
        "ame": ames, "ep": se_ames,
        "ic_inf": ames - 1.96 * se_ames, "ic_sup": ames + 1.96 * se_ames,
        "z": z, "p": 2 * (1 - norm.cdf(np.abs(z))),
    }).assign(**base)

    print(f"\n=== {ano} {modelo}: N={len(df)}, listas={g.max() + 1}, "
          f"Newton={n_iter} it., erro soma={erro_soma:.1e} ===")
    print(tab_coef[["rotulo", "beta", "ep", "p", "razao"]].to_string(index=False))
    print(tab_ame[["rotulo", "tipo_ame", "ame", "ep", "p"]].to_string(index=False))
    return {"coef": tab_coef, "ame": tab_ame}


def sensibilidade_massa(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """R1 e R2 com parcelas renormalizadas entre as candidaturas retidas (s_il / m_l): estimando
    alternativo em que a comparação é só entre remanescentes. Compara b e EP com a principal."""
    s = df["prop_vr_receita_candidato"].to_numpy(dtype=float)
    _, g = np.unique(df["lista_id"].to_numpy(), return_inverse=True)
    s_ren = s / np.bincount(g, s)[g]
    linhas = []
    for modelo, variaveis in MODELOS.items():
        nomes = [c for c, _ in variaveis]
        X = df[nomes].to_numpy(dtype=float)
        b0, V0, _, _ = logit_condicional_fracionario(s, X, g)
        b1, V1, _, _ = logit_condicional_fracionario(s_ren, X, g)
        linhas.append(pd.DataFrame({
            "ano_eleicao": ano, "modelo": modelo, "variavel": nomes,
            "beta_principal": b0, "ep_principal": np.sqrt(np.diag(V0)),
            "beta_renormalizado": b1, "ep_renormalizado": np.sqrt(np.diag(V1)),
            "razao_principal": np.exp(b0), "razao_renormalizado": np.exp(b1),
        }))
    return pd.concat(linhas, ignore_index=True)


GRUPOS_MAG = [("Pequeno", 0, 12, "Pequeno (8–12)"), ("Médio", 13, 31, "Médio (16–31)"),
              ("Grande", 32, 70, "Grande (39–70)")]


def estimar_interacao_magnitude(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """R1 com interação credencial x grupo de magnitude (mesmos grupos da tbl-cap3-01).
    A magnitude é constante na lista e não entra sozinha; só a interação é identificada.
    Reporta a razão exp(b) da credencial em cada grupo e, à parte, o teste da interação
    contínua credencial x ln(magnitude) centrada."""
    _, g = np.unique(df["lista_id"].to_numpy(), return_inverse=True)
    s = df["prop_vr_receita_candidato"].to_numpy(dtype=float)
    grupo = pd.Series(pd.NA, index=df.index, dtype="object")
    for nome, lo, hi, _ in GRUPOS_MAG:
        grupo[(df["qt_vaga"] >= lo) & (df["qt_vaga"] <= hi)] = nome
    comp = df["competitivo"].to_numpy(dtype=float)
    X = np.column_stack([comp, comp * (grupo == "Médio"), comp * (grupo == "Grande"),
                         df["mulher"], df["negra"]]).astype(float)
    b, V, _, _ = logit_condicional_fracionario(s, X, g)

    linhas = []
    for idx, (nome, _, _, rotulo) in enumerate(GRUPOS_MAG):
        c = np.zeros(len(b))
        c[0] = 1
        if idx > 0:
            c[idx] = 1
        bb, ep = c @ b, np.sqrt(c @ V @ c)
        linhas.append({"grupo_magnitude": nome, "rotulo": rotulo, "beta": bb, "ep": ep,
                       "razao": np.exp(bb), "razao_ic_inf": np.exp(bb - 1.96 * ep),
                       "razao_ic_sup": np.exp(bb + 1.96 * ep),
                       "n_candidaturas": int((grupo == nome).sum())})
    tab = pd.DataFrame(linhas)

    ln_mag = np.log(df["qt_vaga"].to_numpy(dtype=float))
    Xc = np.column_stack([comp, comp * (ln_mag - ln_mag.mean()), df["mulher"], df["negra"]])
    bc, Vc, _, _ = logit_condicional_fracionario(s, Xc.astype(float), g)
    tab["beta_interacao_ln_mag"] = bc[1]
    tab["ep_interacao_ln_mag"] = np.sqrt(Vc[1, 1])
    tab["p_interacao_ln_mag"] = 2 * (1 - norm.cdf(abs(bc[1] / np.sqrt(Vc[1, 1]))))
    tab["ano_eleicao"] = ano

    print(f"\n=== {ano} R1 x magnitude ===")
    print(tab[["rotulo", "razao", "razao_ic_inf", "razao_ic_sup", "n_candidaturas"]].to_string(index=False))
    print(f"interação contínua credencial x ln(magnitude): b={bc[1]:.3f} "
          f"(EP {np.sqrt(Vc[1, 1]):.3f}, p={tab['p_interacao_ln_mag'].iloc[0]:.2g})")
    return tab


def fmt(x, d=2):
    return f"{x:,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def fig_razoes(coef_por_ano: dict) -> None:
    """Forest plot das razões de parcelas exp(b) do R2 por variável, escala log com referência
    em 1, 2018 (círculo preto) vs 2022 (losango cinza), no mesmo layout de
    tese/scripts/regenerar_figuras_cap3.py. Credenciais eleitorais (COVARS) no topo, controles
    estruturais (CONTROLES) embaixo, separados por linha pontilhada. Votos t-1 em +10 p.p.
    (ESCALA_RAZAO). Até 18/09/2026 a figura mostrava AMEs (ainda em ames.csv)."""
    variaveis = [lbl for _, lbl in COVARS] + [lbl for _, lbl in CONTROLES]
    sufixo = {lbl: f" ({ESCALA_RAZAO[c][1]})" for c, lbl in COVARS + CONTROLES if c in ESCALA_RAZAO}
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
        tab = coef_por_ano[ano].set_index("rotulo").loc[variaveis]
        y = y_pos + offsets[ano]
        ax.errorbar(
            tab["razao_rep"], y,
            xerr=[tab["razao_rep"] - tab["razao_rep_ic_inf"],
                  tab["razao_rep_ic_sup"] - tab["razao_rep"]],
            fmt=marcadores[ano], color=cores[ano], ecolor=cores[ano],
            capsize=3, markersize=7, linewidth=1.2, label=str(ano),
        )
        dy = 10 if ano == 2018 else -15
        for yi, val in zip(y, tab["razao_rep"]):
            ax.annotate(fmt(val), (val, yi), textcoords="offset points",
                        xytext=(0, dy), ha="center", fontsize=8, color=cores[ano])

    ax.axvline(1, color="#666666", linestyle="--", linewidth=0.8)
    ax.set_xscale("log")
    ticks = [0.5, 1, 2, 4, 8]
    ax.set_xticks(ticks)
    ax.set_xticklabels([fmt(t, 1) if t < 1 else str(t) for t in ticks])
    ax.minorticks_off()
    y_separador = (y_controles.max() + y_covars.min()) / 2
    ax.axhline(y_separador, color="#cccccc", linestyle=":", linewidth=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([textwrap.fill(v + sufixo.get(v, ""), 45) for v in variaveis])
    ax.set_xlabel("Razão de parcelas exp(β) (escala log)")
    ax.set_ylabel("Variável")
    ax.legend(title="Eleições", loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    out = FIGS / "cap3_regressao_fracionaria.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"\nFigura salva em {out}")


def main():
    coef_r2, interacoes = {}, {}
    coefs, ames, amostras, sens = [], [], [], []
    for ano in YEARS:
        df, amostra = montar_base(ano)
        amostras.append(amostra)
        for modelo in MODELOS:
            r = estimar(df, ano, modelo)
            coefs.append(r["coef"])
            ames.append(r["ame"])
            if modelo == "R2":
                coef_r2[ano] = r["coef"]
        interacoes[ano] = estimar_interacao_magnitude(df, ano)
        sens.append(sensibilidade_massa(df, ano))

    pd.concat(coefs, ignore_index=True).to_csv(REPORTS / "coeficientes.csv", index=False)
    pd.concat(ames, ignore_index=True).to_csv(REPORTS / "ames.csv", index=False)
    pd.concat(interacoes.values(), ignore_index=True).to_csv(
        REPORTS / "interacao_magnitude.csv", index=False)
    pd.DataFrame(amostras).to_csv(REPORTS / "amostra.csv", index=False)
    pd.concat(sens, ignore_index=True).to_csv(REPORTS / "sensibilidade_massa.csv", index=False)
    print(f"\nTabelas salvas em {REPORTS}")

    fig_razoes(coef_r2)


if __name__ == "__main__":
    main()
