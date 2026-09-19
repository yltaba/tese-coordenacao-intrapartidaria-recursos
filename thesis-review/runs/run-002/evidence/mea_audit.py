"""Read-only measurement audit, Chapter 3, run-002. Outputs only here."""
from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'src/2_gold'))
from cap3_cs_features import gerar_features
from cap3_taa_features import norm_partido, acertos_fracionarios
d=gerar_features(pd.read_parquet(ROOT/'data/processed/rrd_df_novo.parquet'))
d=d[d.ano_eleicao.isin([2018,2022])].copy()
d['partido']=d.sg_partido.map(norm_partido)
rows=[]; examples={}; sums=[]
for key,g in d.groupby(['ano_eleicao','sg_uf','partido']):
 r=g.vr_receita_recursos_partidos.to_numpy(float); C=len(r); total=r.sum()
 necr=1/np.square(r/total).sum() if total>0 else np.nan
 k=int(np.floor(necr+.5)) if total>0 else 0
 order=np.sort(r)[::-1]; tie=bool(k>0 and k<C and order[k-1]==order[k])
 E=int(g.eleito.sum()); F=int(g.candidato_competitivo.sum())
 hE=acertos_fracionarios(r,g.eleito,k) if k else 0
 hF=acertos_fracionarios(r,g.candidato_competitivo,k) if k else 0
 row=dict(ano=int(key[0]),uf=key[1],partido=key[2],C=C,total=float(total),NECr=float(necr),k=k,E=E,F=F,hE=hE,hF=hF,esperado_E=E*k/C,esperado_F=F*k/C,empate=tie,recebedores=int((r>0).sum()))
 rows.append(row)
 for tag,cond in [('empate',tie and hF%1>0),('sem_recursos',total<=0 and E>0),('E_maior_k',total>0 and E>k)]:
  if cond and tag not in examples:
   examples[tag]=row
   g[['ano_eleicao','sg_uf','sg_partido','nr_candidato','vr_receita_recursos_partidos','eleito','candidato_competitivo']].to_csv(OUT/f'mea_caso_{tag}.csv',index=False)
lists=pd.DataFrame(rows); lists.to_csv(OUT/'mea_listas.csv',index=False)
for ano,g in d.groupby('ano_eleicao'):
 l=lists[lists.ano==ano]; funded=l.total>0
 residual=(g.vr_receita_recursos_partidos-g.vr_receita_fefc.fillna(0)-g.vr_receita_fp.fillna(0))
 lagdiff=(g.prop_votos_nominais_lag==0)&(g.prop_votos_nominais_lag_candidato>0)
 s=dict(ano=int(ano),N=len(g),listas=len(l),sem_recursos=int((~funded).sum()),eleitos=int(g.eleito.sum()),competitivos=int(g.candidato_competitivo.sum()),eleitos_sem_recursos=int(l.loc[~funded,'E'].sum()),competitivos_sem_recursos=int(l.loc[~funded,'F'].sum()),recebedores=int((g.vr_receita_recursos_partidos>0).sum()),recursos_total=float(g.vr_receita_recursos_partidos.sum()),recursos_fora_fefc_fp=float(residual.sum()),pct_fora_fefc_fp=100*float(residual.sum()/g.vr_receita_recursos_partidos.sum()),n_lag_zero_com_passado=int(lagdiff.sum()),n_cpf_invalido=int((g.nr_cpf_candidato=='-4').sum()),n_raca_nan=int(g.negra.isna().sum()),n_empates=int(l.empate.sum()),n_E_maior_k=int((l.E>l.k).sum()),n_k_C=int(((l.k==l.C)&funded).sum()),n_k_maior_recebedores=int((l.k>l.recebedores).sum()),cobertura_comp=float(l.hF.sum()/l.F.sum()),precisao_comp=float(l.hF.sum()/l.k.sum()),lift_comp=float(l.hF.sum()/l.esperado_F.sum()))
 # Reproduce sample filters without importing a script that creates output folders.
 rl=g.groupby(['sg_uf','sg_partido']).vr_receita_recursos_partidos.transform('sum')
 m=g[(rl>0)&(g.nr_cpf_candidato!='-4')].copy()
 cols=['prop_vr_receita_candidato','prop_votos_nominais_lag','mulher','negra']
 m=m.dropna(subset=cols); size=m.groupby(['sg_uf','sg_partido']).nr_candidato.transform('size'); m=m[size>1]
 s['modelo_N']=len(m); s['modelo_listas']=m.groupby(['sg_uf','sg_partido']).ngroups
 ss=m.groupby(['sg_uf','sg_partido']).prop_vr_receita_candidato.sum()
 bad=ss[abs(ss-1)>1e-8].rename('soma_shares').reset_index();bad['ano_eleicao']=int(ano)
 bad.to_csv(OUT/f'mea_denominadores_{ano}.csv',index=False)
 mf=g.merge(bad[['sg_uf','sg_partido']],on=['sg_uf','sg_partido'])
 mf[['ano_eleicao','sg_uf','sg_partido','nr_candidato','nm_candidato','vr_receita_recursos_partidos','prop_vr_receita_candidato','prop_votos_nominais_lag','negra','mulher']].to_csv(OUT/f'mea_denominadores_candidaturas_{ano}.csv',index=False)
 s['modelo_listas_share_nao_soma_1']=int((abs(ss-1)>1e-8).sum());s['modelo_share_min']=float(ss.min())
 sums.append(s)
report=dict(exemplos=examples,resumos=sums)
(OUT/'mea_audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
