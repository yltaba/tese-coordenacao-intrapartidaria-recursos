"""Read-only audit of current chapter 3; all outputs stay beside this script."""
import ast
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm, t

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'src/2_gold'))
from cap3_cs_features import gerar_features
from cap3_taa_features import _preparar, acertos_fracionarios

def functions_from(path, names, namespace):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)

ns = dict(np=np, pd=pd, ROOT=ROOT, gerar_features=gerar_features)
tree = ast.parse((ROOT / 'tese/scripts/regressao_fracionaria_cap3.py').read_text(encoding='utf-8'))
keep = {'COVARS', 'CONTROLES', 'N_ELEICOES_COLS', 'MODELOS'}
for n in tree.body:
    if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id in keep for x in n.targets):
        exec(compile(ast.Module(body=[n], type_ignores=[]), '<constants>', 'exec'), ns)
functions_from(ROOT / 'tese/scripts/regressao_fracionaria_cap3.py',
    {'montar_base','_centrar_lista','_softmax_lista','_media_lista','logit_condicional_fracionario'}, ns)
rows=[]
sums=[]
for year in (2018,2022):
    df, sample=ns['montar_base'](year)
    g=pd.factorize(df.lista_id, sort=True)[0]
    s=df.prop_vr_receita_candidato.to_numpy(float)
    sums.append(dict(year=year, max_sum_error=float(abs(np.bincount(g,s)-1).max()), sample=sample))
    for model in ('R1','R2','interaction'):
        if model == 'interaction':
            names=['competitivo','comp_x_ln_magnitude','mulher','negra']
            c=df.competitivo.to_numpy(float)
            lm=np.log(df.qt_vaga.to_numpy(float))
            X=np.column_stack([c,c*(lm-lm.mean()),df.mulher,df.negra])
        else:
            names=[v[0] for v in ns['MODELOS'][model]]
            X=df[names].to_numpy(float)
        b,V,p,it=ns['logit_condicional_fracionario'](s,X,g)
        Xc=X-ns['_media_lista'](X,p,g)
        Hinv=np.linalg.inv((Xc*p[:,None]).T@Xc)
        for cluster in ('lista_id','sg_partido','sg_uf'):
            codes=pd.factorize(df[cluster])[0]
            L=codes.max()+1
            scores=np.column_stack([np.bincount(codes,(s-p)*X[:,j]) for j in range(X.shape[1])])
            vc=Hinv@(scores.T@scores)@Hinv*L/(L-1)
            for j,name in enumerate(names):
                se=np.sqrt(vc[j,j]); z=b[j]/se
                rows.append(dict(year=year,model=model,variable=name,cluster=cluster,n_clusters=L,
                    beta=b[j],se=se,ratio=np.exp(b[j]),p_norm=2*norm.sf(abs(z)),p_t=2*t.sf(abs(z),L-1)))
pd.DataFrame(rows).to_csv(OUT/'sta_cluster_sensitivity.csv',index=False)
(OUT/'sta_sample_checks.json').write_text(json.dumps(sums,indent=2),encoding='utf-8')

gns=dict(np=np,pd=pd,ROOT=ROOT,gerar_features=gerar_features,_preparar=_preparar,
    acertos_fracionarios=acertos_fracionarios,YEARS=[2018,2022],TAUS=[50,60,70,80,90,95])
functions_from(ROOT/'tese/scripts/regenerar_figuras_cap3.py', {'carregar_listas','nacional'},gns)
lists=gns['carregar_listas']()
out=[]
for outcome,target in [('competitividade','F'),('eleicao','E')]:
    for cutoff in ['topnecr',50,60,70,80,90,95]:
        k='k_arredondado' if cutoff=='topnecr' else f'k_{cutoff}'
        h=f'H_{outcome}_{cutoff}'
        for year,metrics in gns['nacional'](lists,outcome,k,h).items():
            d=lists[lists.ano_eleicao==year]
            metrics.update(year=year,outcome=outcome,cutoff=cutoff,
                mean_list_coverage=100*(d.loc[d[target]>0,h]/d.loc[d[target]>0,target]).mean(),
                mean_list_precision=100*(d.loc[d[k]>0,h]/d.loc[d[k]>0,k]).mean())
            out.append(metrics)
pd.DataFrame(out).to_csv(OUT/'sta_metrics.csv',index=False)
print('Completed audit: cluster sensitivity, sample sums, national and equal-list metrics.')
print(pd.DataFrame(sums).to_string(index=False))
print(pd.DataFrame(rows).query("model == 'R2' and variable == 'negra'").to_string(index=False))

def correct_fit(s,X,g,renormalize=False):
    mass=np.bincount(g,s)
    if renormalize:
        s=s/mass[g]
        mass=np.ones_like(mass)
    b=np.zeros(X.shape[1])
    for it in range(200):
        p=ns['_softmax_lista'](X@b,g)
        Xc=X-ns['_media_lista'](X,p,g)
        grad=Xc.T@s
        H=(Xc*(p*mass[g])[:,None]).T@Xc
        delta=np.linalg.solve(H,grad)
        b+=delta
        if abs(delta).max()<1e-10:
            break
    p=ns['_softmax_lista'](X@b,g)
    Xc=X-ns['_media_lista'](X,p,g)
    H=(Xc*(p*mass[g])[:,None]).T@Xc
    es=np.column_stack([np.bincount(g,(s-mass[g]*p)*X[:,j]) for j in range(X.shape[1])])
    hi=np.linalg.inv(H)
    V=hi@(es.T@es)@hi*len(mass)/(len(mass)-1)
    return b,V

correction=[]; massrows=[]
raw=gerar_features(pd.read_parquet(ROOT/'data/processed/rrd_df_novo.parquet'))
for year in (2018,2022):
    df,_=ns['montar_base'](year)
    g=pd.factorize(df.lista_id,sort=True)[0]
    s=df.prop_vr_receita_candidato.to_numpy(float)
    masses=df.groupby('lista_id').agg(mass=('prop_vr_receita_candidato','sum'),uf=('sg_uf','first'),party=('sg_partido','first'))
    for idx,r in masses[masses.mass<1-1e-8].iterrows():
        rd=raw[(raw.ano_eleicao==year)&(raw.sg_uf==r.uf)&(raw.sg_partido==r.party)]
        kept=df[df.lista_id==idx]
        massrows.append(dict(year=year,lista=idx,mass=r.mass,n_full=len(rd),n_kept=len(kept),
            full_sum_share=rd.prop_vr_receita_candidato.sum(),
            full_resources=rd.vr_receita_recursos_partidos.sum(),kept_resources=kept.vr_receita_recursos_partidos.sum()))
    for model in ('R1','R2'):
        names=[v[0] for v in ns['MODELOS'][model]]
        X=df[names].to_numpy(float)
        bo,vo,_,_=ns['logit_condicional_fracionario'](s,X,g)
        for handling in ('mass_weighted_PPML','renormalized_retained'):
            b,v=correct_fit(s,X,g,handling=='renormalized_retained')
            for j,name in enumerate(names):
                correction.append(dict(year=year,model=model,handling=handling,variable=name,
                    beta_original=bo[j],beta_corrected=b[j],se_original=np.sqrt(vo[j,j]),
                    se_corrected=np.sqrt(v[j,j]),p_corrected=2*norm.sf(abs(b[j]/np.sqrt(v[j,j])))))
pd.DataFrame(correction).to_csv(OUT/'sta_missing_mass_correction.csv',index=False)
pd.DataFrame(massrows).to_csv(OUT/'sta_lists_missing_mass.csv',index=False)
print(pd.DataFrame(massrows).to_string(index=False))
print(pd.DataFrame(correction).query("variable in ['competitivo','negra','n_eleicoes_governador']").to_string(index=False))
