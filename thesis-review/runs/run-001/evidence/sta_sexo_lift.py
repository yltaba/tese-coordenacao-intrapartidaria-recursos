"""statistics-reviewer, run-001. Lift/precisao do Top-NECr restritos por sexo, para checar a
afirmacao de que as cotas tornam os indicadores 'uma estimativa conservadora da priorizacao'.
Dentro de cada lista, C, k, G e H sao restritos ao subgrupo; A0 = k_s * G_s / C_s."""
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
SRC = next(p for p in [ROOT / "tese/reports/sensibilidade-top-x/candidaturas.parquet",
                       ROOT / "tese/sensibilidade-top-x/candidaturas.parquet"] if p.exists())
d = pd.read_parquet(SRC)
rrd = pd.read_parquet(ROOT / "data/processed/rrd_df_novo.parquet",
                      columns=["ano_eleicao", "sg_uf", "nr_candidato", "mulher"])
rrd = rrd[rrd.ano_eleicao.isin([2018, 2022])].copy()
rrd["nr_candidato"] = pd.to_numeric(rrd.nr_candidato).astype("int64")
rrd["ano_eleicao"] = rrd.ano_eleicao.astype("int64")
d = d.merge(rrd, on=["ano_eleicao", "sg_uf", "nr_candidato"], how="left", validate="one_to_one")

rows = []
for tg, col in {"competitividade": "competitivo_previo", "eleicao": "eleito"}.items():
    for ano, df in d.groupby("ano_eleicao"):
        for grupo, mask in [("todos", pd.Series(True, index=df.index)), ("homens", df.mulher.eq(0)), ("mulheres", df.mulher.eq(1))]:
            s = df[mask]
            g = s[col].astype(float)
            valid = g.notna()
            w = s.top_necr.astype(float).where(valid, 0.0)
            t = pd.DataFrame({"l": s.sg_uf + "|" + s.sg_partido_norm, "C": valid.astype(float), "k": w,
                              "G": g.fillna(0), "H": w * g.fillna(0)})
            a = t.groupby("l").sum()
            a["A0"] = (a.k * a.G / a.C.replace(0, np.nan)).fillna(0)
            rows.append(dict(desfecho=tg, ano=ano, grupo=grupo, candidaturas=int(a.C.sum()), sumG=a.G.sum(), sumk=a.k.sum(),
                             sumH=a.H.sum(), A0=a.A0.sum(), cobertura=a.H.sum() / a.G.sum(), precisao=a.H.sum() / a.k.sum(),
                             lift=a.H.sum() / a.A0.sum()))
out = pd.DataFrame(rows)
out.to_csv(OUT / "sta_lift_por_sexo.csv", index=False)
print(out.round(4).to_string(index=False))
