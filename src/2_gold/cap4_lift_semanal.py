"""Lift do Top-NECr semana a semana (Cap. 4).

Em cada semana w da campanha, os recursos partidários de cada candidatura são
substituídos pelo valor ACUMULADO até w (origem "Recursos de partido político", mesma regra
de semana do fluxo cumulativo do Cap. 4) e a medida do Cap. 3 é recalculada por
inteiro: NECr(w), k(w) = floor(NECr(w) + 0,5), Top-NECr(w) com empates
fracionários, e lift = competitivos no Top-NECr(w) / referência hipergeométrica
(competitivos·k/C somados nas listas). Reaproveita
cap3_cobertura_top_necr.calcular_cobertura_top_necr; nada da regra é
reimplementado aqui.

`candidato_competitivo` é a versão ex-ante (ver cap3_cobertura_top_necr).

Listas sem recurso acumulado em w (R_l(w) = 0) têm k = 0 e não entram no
numerador nem na referência: o lift é condicional às listas já financiadas.
A cobertura (denominador = todos os competitivos) é incondicional.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cap3_cobertura_top_necr import calcular_cobertura_top_necr  # noqa: E402
from cap3_survival_features import (  # noqa: E402
    DURACAO,
    JANELAS,
    carregar_receitas,
    selecionar_receitas_partido,
)

ANOS = [2018, 2022]
REGRA = "arredondado"
CHAVE = ["sg_uf", "sg_partido", "nr_candidato"]


def receitas_partido_por_semana(receitas=None) -> pd.DataFrame:
    df = carregar_receitas(ANOS) if receitas is None else receitas
    df = selecionar_receitas_partido(df)
    df = df[df["ano_eleicao"].isin(ANOS)].copy()
    inicio = df["ano_eleicao"].map({a: JANELAS[a][0] for a in ANOS})
    df["semana"] = ((df["dt_receita"] - inicio).dt.days // 7) + 1
    return (
        df.groupby(["ano_eleicao", "semana"] + CHAVE, as_index=False)["vr_receita"].sum()
    )


def _rrd_acumulado(rrd: pd.DataFrame, rec: pd.DataFrame, ano: int, w: int) -> pd.DataFrame:
    """rrd de `ano` com vr_receita_recursos_partidos = acumulado das semanas <= w."""
    acum = (
        rec[(rec["ano_eleicao"] == ano) & (rec["semana"] <= w)]
        .groupby(CHAVE, as_index=False)["vr_receita"].sum()
    )
    d = rrd[rrd["ano_eleicao"] == ano].drop(columns="vr_receita_recursos_partidos").copy()
    d["nr_candidato"] = d["nr_candidato"].astype(str)
    d = d.merge(acum, on=CHAVE, how="left")
    d["vr_receita_recursos_partidos"] = d["vr_receita"].fillna(0.0)
    return d.drop(columns="vr_receita")


def _razoes(listas: pd.DataFrame) -> dict:
    ativo = listas["total_recursos_partidarios"] > 0
    top = listas.loc[ativo, f"competitivos_top_{REGRA}"].sum()
    esp = listas.loc[ativo, f"competitivos_esperados_aleatorio_{REGRA}"].sum()
    n_comp = listas["n_competitivos"].sum()
    k = listas.loc[ativo, f"k_{REGRA}"].sum()
    return {
        "lift": top / esp if esp > 0 else np.nan,
        "cobertura": top / n_comp,
        "precisao": top / k if k > 0 else np.nan,
        "cobertura_aleatoria": esp / n_comp,
        "n_posicoes_top": int(k),
    }


def _bootstrap_lift(listas: pd.DataFrame, n_boot: int, rng) -> tuple[float, float]:
    ativo = listas[listas["total_recursos_partidarios"] > 0]
    top = ativo[f"competitivos_top_{REGRA}"].to_numpy()
    esp = ativo[f"competitivos_esperados_aleatorio_{REGRA}"].to_numpy()
    n = len(ativo)
    if n == 0:
        return np.nan, np.nan
    idx = rng.integers(0, n, size=(n_boot, n))
    lifts = top[idx].sum(axis=1) / esp[idx].sum(axis=1)
    return tuple(np.nanpercentile(lifts, [2.5, 97.5]))


def calcular_lift_semanal(rrd: pd.DataFrame, n_boot: int = 1000, seed: int = 42,
                          receitas=None) -> pd.DataFrame:
    rec = receitas_partido_por_semana(receitas)
    rng = np.random.default_rng(seed)
    total_final = (
        rec.groupby("ano_eleicao")["vr_receita"].sum().to_dict()
    )
    linhas = []
    for ano in ANOS:
        max_semana = int(np.ceil(DURACAO[ano] / 7))
        for w in range(1, max_semana + 1):
            d = _rrd_acumulado(rrd, rec, ano, w)
            listas, _ = calcular_cobertura_top_necr(d)
            r = _razoes(listas)
            lo, hi = _bootstrap_lift(listas, n_boot, rng)
            acum_w = rec[(rec["ano_eleicao"] == ano) & (rec["semana"] <= w)]["vr_receita"].sum()
            linhas.append(
                {
                    "ano_eleicao": ano,
                    "semana": w,
                    "lift_competitivos": r["lift"],
                    "lift_ic95_inf": lo,
                    "lift_ic95_sup": hi,
                    "cobertura_competitivos": r["cobertura"],
                    "cobertura_aleatoria": r["cobertura_aleatoria"],
                    "precisao_competitivos": r["precisao"],
                    "n_posicoes_top": r["n_posicoes_top"],
                    "listas_total": len(listas),
                    "listas_financiadas": int((listas["total_recursos_partidarios"] > 0).sum()),
                    "prop_recursos_acumulados": acum_w / total_final[ano],
                }
            )
            print(f"{ano} semana {w}: lift={r['lift']:.3f} [{lo:.3f}; {hi:.3f}]")
    return pd.DataFrame(linhas)


def reconciliar(rrd: pd.DataFrame, tabela: pd.DataFrame) -> pd.DataFrame:
    """Última semana × Cap. 3 (vr_receita_recursos_partidos total)."""
    _, resumo = calcular_cobertura_top_necr(rrd)
    resumo = resumo[resumo["regra_k"] == REGRA].set_index("ano_eleicao")
    ultima = tabela.sort_values("semana").groupby("ano_eleicao").tail(1).set_index("ano_eleicao")
    out = pd.DataFrame(
        {
            "lift_ultima_semana": ultima["lift_competitivos"],
            "lift_cap3": resumo["lift_competitivos"],
            "cobertura_ultima_semana": ultima["cobertura_competitivos"],
            "cobertura_cap3": resumo["cobertura_competitivos"],
        }
    )
    out["dif_lift"] = out["lift_ultima_semana"] - out["lift_cap3"]
    return out.reset_index()
