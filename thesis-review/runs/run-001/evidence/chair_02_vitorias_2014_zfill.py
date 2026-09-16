"""Chair, pass 2: vitórias estaduais/federais de 2014 perdidas pela falta de zfill (ADV-3-001).
Ligação independente por (ano, UF, cargo, nr), única para cargos estaduais/federais; CPF normalizado com zfill(11).
Conta candidaturas 2018/2022 da base não competitivas que têm vitória em 2014 (Gov, Sen, DF, DE, DD)."""
import pandas as pd
P = "data/processed/"
cand = pd.read_parquet(P + "candidatos.parquet", columns=["ano_eleicao","sg_uf","ds_cargo","nr_candidato","nr_cpf_candidato","ds_situacao_candidatura"])
res = pd.read_parquet(P + "resultados.parquet", columns=["ano_eleicao","sg_uf","ds_cargo","nr_candidato","ds_sit_tot_turno"])
rrd = pd.read_parquet(P + "rrd_df_novo.parquet")
CARG = ["GOVERNADOR","SENADOR","DEPUTADO FEDERAL","DEPUTADO ESTADUAL","DEPUTADO DISTRITAL"]
TXT = ["ELEITO","ELEITO POR QP","ELEITO POR MÉDIA","MÉDIA"]
for d in (cand, res): d["ds_cargo"] = d["ds_cargo"].str.upper()
r = res[(res.ano_eleicao==2014) & res.ds_cargo.isin(CARG) & res.ds_sit_tot_turno.isin(TXT)][["sg_uf","ds_cargo","nr_candidato"]].drop_duplicates()
c = cand[(cand.ano_eleicao==2014) & cand.ds_cargo.isin(CARG)].copy()
c["apto"] = c.ds_situacao_candidatura.eq("APTO")
c = c.sort_values("apto", ascending=False).drop_duplicates(["sg_uf","ds_cargo","nr_candidato"])
w = r.merge(c, on=["sg_uf","ds_cargo","nr_candidato"], how="left")
print("vitórias 2014 (cargos estaduais/federais):", len(w), "| sem CPF ligado:", int(w.nr_cpf_candidato.isna().sum()),
      "| CPF < 11 díg.:", int((w.nr_cpf_candidato.str.len()<11).sum()))
w["cpf11"] = w.nr_cpf_candidato.str.zfill(11)
cols = ["n_eleicoes_prefeito","n_eleicoes_deputado_estadual","n_eleicoes_deputado_federal","n_eleicoes_governador","n_eleicoes_senador"]
rrd["comp"] = (rrd[cols].fillna(0).sum(axis=1)>0) | rrd.alcancou_10pct_qe_hist.fillna(False)
for ano in (2018, 2022):
    b = rrd[rrd.ano_eleicao==ano]
    x = b[b.nr_cpf_candidato.isin(set(w.cpf11))]
    print(ano, "| candidaturas com vitória em 2014:", len(x), "| não competitivas na base:", int((~x.comp).sum()),
          "| destas CPF iniciado em 0:", int((~x.comp & x.nr_cpf_candidato.str.startswith("0")).sum()),
          "| no núcleo (R>0):", int((~x.comp & (x.vr_receita_recursos_partidos.fillna(0)>0)).sum()))
