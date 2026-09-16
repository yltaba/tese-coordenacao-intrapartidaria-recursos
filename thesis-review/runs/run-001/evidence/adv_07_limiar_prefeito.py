"""adv_07 — Quão exigente é o critério '>= 10% do QE' aplicado a Prefeito (gerar_rrd.py:686-692,
qt_vaga = 1 => 10% dos votos válidos do município)? Compara com Dep. Federal (10% do QE).
Execute da raiz: python thesis-review/runs/run-001/evidence/adv_07_limiar_prefeito.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / "data/processed"
res = pd.read_parquet(P / "resultados.parquet", columns=["ano_eleicao", "nr_turno", "sg_uf", "cd_municipio", "ds_cargo", "nr_candidato", "ds_sit_tot_turno", "qt_votos_nominais"])
res["cargo"] = res.ds_cargo.str.upper()
vv = pd.read_parquet(P / "votos_validos_partido.parquet")
vv["cargo"] = vv.ds_cargo.str.upper()

p = res[(res.cargo == "PREFEITO") & (res.nr_turno == 1) & res.ano_eleicao.isin([2012, 2016, 2020])].copy()
vm = vv[vv.cargo == "PREFEITO"].groupby(["ano_eleicao", "cd_municipio"], as_index=False).votos_validos.sum()
p["cd_municipio"] = p.cd_municipio.astype(str); vm["cd_municipio"] = vm.cd_municipio.astype(str)
p = p.merge(vm, on=["ano_eleicao", "cd_municipio"], how="left")
p["pct"] = p.qt_votos_nominais / p.votos_validos
p["n_cand_mun"] = p.groupby(["ano_eleicao", "cd_municipio"]).nr_candidato.transform("size")
print("Prefeito, 1º turno: parcela de candidaturas com >= 10% dos votos válidos")
print(p.groupby("ano_eleicao").apply(lambda g: pd.Series({"candidaturas": len(g), "pct>=10%": round((g.pct >= 0.10).mean(), 3),
                                                        "nao_eleitos_com_pct>=10%": int(((g.pct >= 0.10) & ~g.ds_sit_tot_turno.eq("ELEITO")).sum()),
                                                        "mediana_candidatos_por_municipio": g.groupby("cd_municipio").size().median()}), include_groups=False).to_string())

d = res[(res.cargo == "DEPUTADO FEDERAL") & res.ano_eleicao.isin([2010, 2014, 2018])].copy()
qe = pd.read_csv(P / "quociente_eleitoral.csv", sep=";")
d = d.merge(qe, on=["ano_eleicao", "sg_uf"], how="left")
d["pct"] = d.qt_votos_nominais / d.qe
print("\nDep. Federal: parcela de candidaturas com >= 10% do QE")
print(d.groupby("ano_eleicao").apply(lambda g: pd.Series({"candidaturas": len(g), "pct>=10%QE": round((g.pct >= 0.10).mean(), 3)}), include_groups=False).to_string())
