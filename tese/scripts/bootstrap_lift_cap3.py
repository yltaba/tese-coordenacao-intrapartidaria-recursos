"""Intervalos bootstrap para cobertura, precisão e lift do Top-NECr (Cap. 3).

Reamostra unidades com reposição dentro de cada eleição e recalcula as razões
de somas nacionais (cobertura = ΣH/ΣG, precisão = ΣH/Σk, lift = ΣH/ΣE), por
eleição e por grupo de magnitude. Duas unidades de reamostragem:

- lista (partido × UF), a mesma do bootstrap semanal do Cap. 4
  (src/2_gold/cap4_lift_semanal.py);
- partido (sg_partido_norm), porque o repasse é decidido pela organização
  partidária acima da lista (mesma sensibilidade de STA-3-002).

Todas as quantidades de um mesmo sorteio (nacional e por magnitude) vêm dos
mesmos índices, de modo que as diferenças entre magnitudes dentro de uma
eleição são pareadas. Entre eleições os sorteios são independentes.

Regra de k: arredondado. Reaproveita cap3_cobertura_top_necr; nada da medida
é reimplementado aqui.

Saídas em tese/reports/bootstrap-lift-cap3/:
- ic_metricas.csv    cobertura, precisão e lift com IC 95% (percentil)
- ic_diferencas.csv  2018 − 2022 e Grande − Pequeno, com IC 95%
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "2_gold"))

from cap3_cobertura_top_necr import calcular_cobertura_top_necr  # noqa: E402

RRD = ROOT / "data" / "processed" / "rrd_df_novo.parquet"
OUT = ROOT / "tese" / "reports" / "bootstrap-lift-cap3"
REGRA = "arredondado"
ANOS = [2018, 2022]
ALVOS = {"competitivos": "n_competitivos", "eleitos": "n_eleitos"}
GRUPOS = ["Total", "Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)"]
UNIDADES = {"lista": None, "partido": "sg_partido_norm"}
N_BOOT = 2000
SEED = 42


def _somas(listas: pd.DataFrame, alvo: str) -> pd.DataFrame:
    """H, E, G, k por lista; listas sem recurso entram só em G."""
    ativo = listas["total_recursos_partidarios"] > 0
    return pd.DataFrame(
        {
            "H": listas[f"{alvo}_top_{REGRA}"].where(ativo, 0.0),
            "E": listas[f"{alvo}_esperados_aleatorio_{REGRA}"].where(ativo, 0.0),
            "G": listas[ALVOS[alvo]].astype(float),
            "k": listas[f"k_{REGRA}"].where(ativo, 0).astype(float),
        }
    )


def _metricas(H, E, G, k):
    return {"cobertura": H / G, "precisao": H / k, "lift": H / E}


def _cubo(listas: pd.DataFrame, alvo: str, unidade: str | None) -> np.ndarray:
    """Array unidades × grupos × (H, E, G, k)."""
    s = _somas(listas, alvo)
    s["grupo"] = listas["dm_cat"].to_numpy()
    s["unidade"] = np.arange(len(listas)) if unidade is None else listas[unidade].to_numpy()
    cubo = []
    for g in GRUPOS:
        sub = s if g == "Total" else s[s["grupo"] == g]
        agg = sub.groupby("unidade")[["H", "E", "G", "k"]].sum()
        cubo.append(agg.reindex(s["unidade"].unique(), fill_value=0.0).to_numpy())
    return np.stack(cubo, axis=1)


def main() -> None:
    rrd = pd.read_parquet(RRD)
    listas, resumo = calcular_cobertura_top_necr(rrd)
    rng = np.random.default_rng(SEED)

    linhas, sorteios = [], {}
    for nome_u, col_u in UNIDADES.items():
        for alvo in ALVOS:
            for ano in ANOS:
                cubo = _cubo(listas[listas["ano_eleicao"] == ano], alvo, col_u)
                n = cubo.shape[0]
                pontual = _metricas(*cubo.sum(axis=0).T)
                idx = rng.integers(0, n, size=(N_BOOT, n))
                boot = _metricas(*cubo[idx].sum(axis=1).transpose(2, 0, 1))
                sorteios[(nome_u, alvo, ano)] = boot
                for gi, g in enumerate(GRUPOS):
                    for m in ("cobertura", "precisao", "lift"):
                        lo, hi = np.nanpercentile(boot[m][:, gi], [2.5, 97.5])
                        linhas.append(
                            {
                                "unidade_reamostragem": nome_u,
                                "n_unidades": n,
                                "alvo": alvo,
                                "ano_eleicao": ano,
                                "magnitude": g,
                                "metrica": m,
                                "estimativa": pontual[m][gi],
                                "ic95_inf": lo,
                                "ic95_sup": hi,
                            }
                        )
    metr = pd.DataFrame(linhas)

    difs = []
    for nome_u in UNIDADES:
        for alvo in ALVOS:
            a, b = sorteios[(nome_u, alvo, 2018)], sorteios[(nome_u, alvo, 2022)]
            for gi, g in enumerate(GRUPOS):
                d = a["lift"][:, gi] - b["lift"][:, gi]
                p = metr.query(
                    "unidade_reamostragem == @nome_u and alvo == @alvo and magnitude == @g and metrica == 'lift'"
                ).set_index("ano_eleicao")["estimativa"]
                difs.append(
                    {
                        "unidade_reamostragem": nome_u, "alvo": alvo,
                        "comparacao": f"2018 − 2022 ({g})",
                        "estimativa": p[2018] - p[2022],
                        "ic95_inf": np.percentile(d, 2.5), "ic95_sup": np.percentile(d, 97.5),
                    }
                )
            for ano in ANOS:
                boot = sorteios[(nome_u, alvo, ano)]["lift"]
                d = boot[:, GRUPOS.index("Grande (39–70)")] - boot[:, GRUPOS.index("Pequeno (8–12)")]
                p = metr.query(
                    "unidade_reamostragem == @nome_u and alvo == @alvo and ano_eleicao == @ano and metrica == 'lift'"
                ).set_index("magnitude")["estimativa"]
                difs.append(
                    {
                        "unidade_reamostragem": nome_u, "alvo": alvo,
                        "comparacao": f"Grande − Pequeno ({ano})",
                        "estimativa": p["Grande (39–70)"] - p["Pequeno (8–12)"],
                        "ic95_inf": np.percentile(d, 2.5), "ic95_sup": np.percentile(d, 97.5),
                    }
                )
    difs = pd.DataFrame(difs)

    # Conferência com o Cap. 3 (lift nacional, regra arredondado) e com
    # lift_por_magnitude.csv (fonte de tbl-cap3-01/tbl-cap3-02).
    ref = resumo[resumo["regra_k"] == REGRA].set_index("ano_eleicao")
    tot = metr.query("unidade_reamostragem == 'lista' and magnitude == 'Total' and metrica == 'lift'")
    for _, r in tot.iterrows():
        col = "lift" if r["alvo"] == "eleitos" else "lift_competitivos"
        esperado = ref.loc[r["ano_eleicao"], col]
        assert abs(r["estimativa"] - esperado) < 1e-9, (r["alvo"], r["ano_eleicao"], r["estimativa"], esperado)

    mag = pd.read_csv(ROOT / "tese" / "reports" / "lift-magnitude-partido" / "lift_por_magnitude.csv")
    mag = mag[mag["ano_eleicao"].isin(["2018", "2022"])].astype({"ano_eleicao": int})
    for _, r in mag.iterrows():
        est = metr.query(
            "unidade_reamostragem == 'lista' and alvo == @r.alvo and ano_eleicao == @r.ano_eleicao "
            "and magnitude == @r.dm_cat and metrica == 'lift'"
        )["estimativa"].item()
        assert abs(est - r["lift"]) < 1e-9, (r["alvo"], r["ano_eleicao"], r["dm_cat"], est, r["lift"])

    OUT.mkdir(parents=True, exist_ok=True)
    metr.to_csv(OUT / "ic_metricas.csv", index=False)
    difs.to_csv(OUT / "ic_diferencas.csv", index=False)
    print(metr.query("metrica == 'lift'").round(3).to_string(index=False))
    print(difs.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
