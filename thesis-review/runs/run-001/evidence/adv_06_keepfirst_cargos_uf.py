"""adv_06 — O defeito keep-first (gerar_rrd.py:61-63) também atinge cargos estaduais?
Governador/vice e senador/suplentes compartilham número em (ano, UF). Conta vitórias de
Governador, Senador, Dep. Federal, Dep. Estadual/Distrital (1998-2020) cujo CPF pelo merge do
pipeline difere do CPF obtido com a chave (ano, UF, cargo, nr), e quantas candidaturas de
2018/2022 ganham ou perdem uma vitória estadual por isso.
Execute da raiz: python thesis-review/runs/run-001/evidence/adv_06_keepfirst_cargos_uf.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / "data/processed"
TXT_ELEITOS = ["ELEITO", "ELEITO POR MÉDIA", "MÉDIA", "ELEITO POR QP"]
UF = ["GOVERNADOR", "SENADOR", "DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "DEPUTADO DISTRITAL"]

res = pd.read_parquet(P / "resultados.parquet", columns=["ano_eleicao", "sg_uf", "ds_cargo", "nr_candidato", "ds_sit_tot_turno"])
res["cargo"] = res.ds_cargo.str.upper()
res = res[res.cargo.isin(UF) & res.ds_sit_tot_turno.isin(TXT_ELEITOS)].copy()
res["nr"] = res.nr_candidato.astype(str)
cand = pd.read_parquet(P / "candidatos.parquet", columns=["ano_eleicao", "sg_uf", "ds_cargo", "nr_candidato", "nr_cpf_candidato"])
cand["cargo"] = cand.ds_cargo.str.upper()
cand["nr"] = cand.nr_candidato.astype(str)
kf = cand.drop_duplicates(["ano_eleicao", "sg_uf", "nr"], keep="first")[["ano_eleicao", "sg_uf", "nr", "nr_cpf_candidato"]].rename(columns={"nr_cpf_candidato": "cpf_kf"})
ok = cand[cand.cargo.isin(UF)].drop_duplicates(["ano_eleicao", "sg_uf", "cargo", "nr"])[["ano_eleicao", "sg_uf", "cargo", "nr", "nr_cpf_candidato"]].rename(columns={"nr_cpf_candidato": "cpf_ok"})
m = res.merge(kf, on=["ano_eleicao", "sg_uf", "nr"], how="left").merge(ok, on=["ano_eleicao", "sg_uf", "cargo", "nr"], how="left")
m["difere"] = m.cpf_kf.astype(str) != m.cpf_ok.astype(str)
print("vitórias estaduais com CPF keep-first diferente do CPF por cargo:")
print(m.groupby("cargo").difere.agg(["sum", "size"]).to_string())
rrd = pd.read_parquet(P / "rrd_df_novo.parquet", columns=["ano_eleicao", "nr_cpf_candidato"])
for y, lim in [(2018, 2016), (2022, 2020)]:
    mm = m[m.ano_eleicao <= lim]
    ganha = set(mm.loc[mm.difere, "cpf_kf"].astype(str)) - set(mm.cpf_ok.astype(str))
    perde = set(mm.loc[mm.difere, "cpf_ok"].astype(str)) - set(mm.cpf_kf.astype(str))
    cpfs = set(rrd.loc[rrd.ano_eleicao == y, "nr_cpf_candidato"].astype(str))
    print(f"{y}: candidaturas que recebem vitória estadual indevida = {len(ganha & cpfs)}; que perdem vitória estadual = {len(perde & cpfs)}")
