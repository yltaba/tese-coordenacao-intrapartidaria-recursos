"""Chair, pass 2: verificação independente, por amostragem, de ADV-3-001 e ADV-3-002.

Não reusa código do adversarial. Lê só data/processed/.
(a) Comprimento dos CPFs por ano em candidatos.parquet.
(b) Parcela das candidaturas 2018/2022 da base com CPF iniciado em '0'.
(c) Amostra nominal de 5 deputados federais eleitos em 2014 citados em ADV-3-001:
    CPF em 2014 (candidatos), CPF na base 2018, n_eleicoes_deputado_federal e flag competitiva.
(d) Contagem independente: candidaturas 2018 da base cujo CPF (11 díg.) só aparece em 2014
    na forma sem zeros à esquerda; quantas delas foram eleitas dep. federal em 2014.
(e) ADV-3-002: chaves (ano, UF, nr) de Dep. Federal com >1 CPF; amostra de 3 casos citados.
"""
import pandas as pd
import numpy as np

P = "data/processed/"
cand = pd.read_parquet(P + "candidatos.parquet")
rrd = pd.read_parquet(P + "rrd_df_novo.parquet")
res = pd.read_parquet(P + "resultados.parquet",
                      columns=["ano_eleicao", "nr_turno", "sg_uf", "ds_cargo", "nr_candidato",
                               "nm_candidato", "ds_sit_tot_turno", "qt_votos_nominais"])

print("(a) comprimento de nr_cpf_candidato por ano (parcela)")
cand["len"] = cand["nr_cpf_candidato"].str.len()
tab = pd.crosstab(cand["ano_eleicao"], cand["len"], normalize="index").round(3)
print(tab.to_string())

rrd = rrd[rrd["ano_eleicao"].isin([2018, 2022])].copy()
print("\n(b) parcela da base com CPF iniciado em '0'")
print(rrd.groupby("ano_eleicao")["nr_cpf_candidato"].apply(lambda s: round(s.str.startswith("0").mean(), 3)).to_string())

cols_n = ["n_eleicoes_prefeito", "n_eleicoes_deputado_estadual", "n_eleicoes_deputado_federal",
          "n_eleicoes_governador", "n_eleicoes_senador"]
rrd["comp"] = (rrd[cols_n].fillna(0).sum(axis=1) > 0) | rrd["alcancou_10pct_qe_hist"].fillna(False)

print("\n(c) amostra nominal (5 casos de ADV-3-001)")
nomes = ["MARX BELTR", "NILTO IGNACIO TATTO", "VITOR LIPPI", "ALIEL MACHADO", "NEWTON CARDOSO J"]
c14 = cand[(cand["ano_eleicao"] == 2014) & (cand["ds_cargo"].str.upper() == "DEPUTADO FEDERAL")]
r14 = res[(res["ano_eleicao"] == 2014) & (res["ds_cargo"].str.upper() == "DEPUTADO FEDERAL")]
for n in nomes:
    a = c14[c14["nm_candidato"].str.upper().str.contains(n, na=False)]
    b = rrd[(rrd["ano_eleicao"] == 2018) & rrd["nm_candidato"].str.upper().str.contains(n, na=False)]
    e = r14[r14["nm_candidato"].str.upper().str.contains(n, na=False)]["ds_sit_tot_turno"].unique().tolist()
    print(f"- {n}: 2014 cpf={a['nr_cpf_candidato'].tolist()} sit2014={e} | 2018 cpf={b['nr_cpf_candidato'].tolist()} "
          f"n_dep_fed={b['n_eleicoes_deputado_federal'].tolist()} 10pct_hist={b['alcancou_10pct_qe_hist'].tolist()} comp={b['comp'].tolist()}")

print("\n(d) contagem independente, 2018")
cpf14_raw = set(cand.loc[cand["ano_eleicao"] == 2014, "nr_cpf_candidato"])
cpf12_raw = set(cand.loc[cand["ano_eleicao"] == 2012, "nr_cpf_candidato"])
b18 = rrd[rrd["ano_eleicao"] == 2018].copy()
b18["strip"] = b18["nr_cpf_candidato"].str.lstrip("0")
b18["em14_so_sem_zero"] = b18["strip"].isin(cpf14_raw) & ~b18["nr_cpf_candidato"].isin(cpf14_raw) & b18["nr_cpf_candidato"].str.startswith("0")
b18["em12_so_sem_zero"] = b18["strip"].isin(cpf12_raw) & ~b18["nr_cpf_candidato"].isin(cpf12_raw) & b18["nr_cpf_candidato"].str.startswith("0")
print("candidaturas 2018 que concorreram em 2014 com CPF gravado sem zeros:", int(b18["em14_so_sem_zero"].sum()))
print("candidaturas 2018 que concorreram em 2012 com CPF gravado sem zeros:", int(b18["em12_so_sem_zero"].sum()))
# eleitos dep. federal 2014, ligando por (UF, nr) apenas dentro de Dep. Federal (chave única por cargo)
TXT = ["ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA", "MÉDIA"]
el14 = r14[r14["ds_sit_tot_turno"].isin(TXT)][["sg_uf", "nr_candidato"]].drop_duplicates()
el14 = el14.merge(c14[["sg_uf", "nr_candidato", "nr_cpf_candidato"]].drop_duplicates(["sg_uf", "nr_candidato"]),
                  on=["sg_uf", "nr_candidato"], how="left")
el14["cpf11"] = el14["nr_cpf_candidato"].str.zfill(11)
print("eleitos dep. federal 2014:", len(el14), "| com CPF < 11 díg.:", int((el14["nr_cpf_candidato"].str.len() < 11).sum()))
x = b18[b18["nr_cpf_candidato"].isin(set(el14["cpf11"]))]
print("candidaturas 2018 de eleitos dep. fed. 2014:", len(x), "| n_eleicoes_deputado_federal == 0:",
      int((x["n_eleicoes_deputado_federal"].fillna(0) == 0).sum()), "| não competitivas:", int((~x["comp"]).sum()),
      "| dessas com CPF iniciado em 0:", int((~x["comp"] & x["nr_cpf_candidato"].str.startswith("0")).sum()))

print("\n(e) ADV-3-002: chave (ano, UF, nr) de Dep. Federal com >1 CPF")
cdf = cand[(cand["ds_cargo"].str.upper() == "DEPUTADO FEDERAL") & cand["ano_eleicao"].isin([2018, 2022])]
g = cdf.groupby(["ano_eleicao", "sg_uf", "nr_candidato"])["nr_cpf_candidato"].nunique()
print((g > 1).groupby("ano_eleicao").sum().to_string())
for ano, uf, nr in [(2022, "AM", "4444"), (2022, "DF", "4545"), (2022, "CE", "1251")]:
    k = cand[(cand["ano_eleicao"] == ano) & (cand["sg_uf"] == uf) & (cand["nr_candidato"] == nr)]
    print(f"- {ano} {uf} {nr} registros em candidatos.parquet (ordem do arquivo):")
    print(k[["ds_cargo", "nm_candidato", "nr_cpf_candidato", "ds_situacao_candidatura", "st_candidato_inserido_urna", "ds_genero"]].to_string(index=False))
    b = rrd[(rrd["ano_eleicao"] == ano) & (rrd["sg_uf"] == uf) & (rrd["nr_candidato"] == nr)]
    print("  base:", b[["nm_candidato", "nr_cpf_candidato", "ds_genero", "qt_votos_nominais", "n_eleicoes_deputado_federal", "comp"]].to_dict("records"))
