"""Recompute literal historical criterion from upstream processed files (read-only)."""
from pathlib import Path
import sys,json
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'src/1_silver'));sys.path.insert(0,str(ROOT/'src/2_gold'))
import gerar_rrd as build
from cap3_cs_features import gerar_features
rrd=gerar_features(pd.read_parquet(ROOT/'data/processed/rrd_df_novo.parquet'))
c=pd.read_parquet(ROOT/'data/processed/candidatos.parquet')
c.nr_cpf_candidato=build._normalizar_cpf(c.nr_cpf_candidato)
r=pd.read_parquet(ROOT/'data/processed/resultados.parquet')
# Retain literal cargo/year universe before joining (also includes distrital for comparison).
cargos=['PRESIDENTE','GOVERNADOR','SENADOR','DEPUTADO FEDERAL','DEPUTADO ESTADUAL','PREFEITO']
r=r[(r.ano_eleicao>=1998)&(r.ano_eleicao<2022)&r.ds_cargo.str.upper().isin(cargos+['DEPUTADO DISTRITAL'])].copy()
r=build.ligar_cpf(r,c,['nr_cpf_candidato'])
r.ds_cargo=r.ds_cargo.str.upper()
vv=pd.read_parquet(ROOT/'data/processed/votos_validos_partido.parquet')
vv=vv[vv.ds_cargo.isin(['DEPUTADO FEDERAL','DEPUTADO ESTADUAL'])]
vv=vv.groupby(['ano_eleicao','sg_uf','ds_cargo'],as_index=False).votos_validos.sum()
# Historical raw vacancies CSVs are unavailable in this checkout. Reconstruct
# district seat counts from distinct elected candidates in the proportional races;
# retain the resulting table so this substitute denominator is reviewable.
vagas=r[(r.nr_turno==1)&r.ds_cargo.isin(['DEPUTADO FEDERAL','DEPUTADO ESTADUAL'])&r.ds_sit_tot_turno.isin(build.TXT_ELEITOS)].groupby(['ano_eleicao','sg_uf','ds_cargo'],as_index=False).nr_candidato.nunique().rename(columns={'nr_candidato':'qt_vaga'})
vagas.to_csv(OUT/'mea_vagas_reconstruidas.csv',index=False)
votes=r[(r.nr_turno==1)&r.ds_cargo.isin(['DEPUTADO FEDERAL','DEPUTADO ESTADUAL'])].groupby(['ano_eleicao','sg_uf','ds_cargo','nr_cpf_candidato'],as_index=False).qt_votos_nominais.sum()
votes=votes.merge(vv,on=['ano_eleicao','sg_uf','ds_cargo'],how='left',validate='m:1').merge(vagas,on=['ano_eleicao','sg_uf','ds_cargo'],how='left',validate='m:1')
votes['qualifica']=votes.qt_votos_nominais/(votes.votos_validos/votes.qt_vaga)>=.1
outputs=[]; diffs=[]
for year in [2018,2022]:
 g=rrd[rrd.ano_eleicao==year].copy()
 win=r[(r.ano_eleicao<year)&r.ds_cargo.isin(cargos)&r.ds_sit_tot_turno.isin(build.TXT_ELEITOS)]
 h= votes[(votes.ano_eleicao<year)&votes.qualifica]
 valid=lambda s:set(s.dropna().astype(str))-{'-4','-1','nan'}
 literal=g.nr_cpf_candidato.isin(valid(win.nr_cpf_candidato)|valid(h.nr_cpf_candidato))
 dis=r[(r.ano_eleicao<year)&(r.ds_cargo=='DEPUTADO DISTRITAL')&r.ds_sit_tot_turno.isin(build.TXT_ELEITOS)]
 pres=win[win.ds_cargo=='PRESIDENTE']
 g['literal']=literal; diff=g[literal!=g.candidato_competitivo]
 diffs.append(diff[['ano_eleicao','sg_uf','sg_partido','nr_candidato','nm_candidato','literal','candidato_competitivo']])
 outputs.append(dict(ano=year,literal=int(literal.sum()),implementado=int(g.candidato_competitivo.sum()),discordantes=len(diff),candidatos_com_vitoria_presidencial=int(g.nr_cpf_candidato.isin(valid(pres.nr_cpf_candidato)).sum()),candidatos_com_vitoria_distrital=int(g.nr_cpf_candidato.isin(valid(dis.nr_cpf_candidato)).sum()),historico_anos=sorted(map(int,r[r.ano_eleicao<year].ano_eleicao.unique()))))
pd.concat(diffs).to_csv(OUT/'mea_historico_discordancias.csv',index=False)
(OUT/'mea_historico.json').write_text(json.dumps(outputs,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(outputs,indent=2,ensure_ascii=False))
