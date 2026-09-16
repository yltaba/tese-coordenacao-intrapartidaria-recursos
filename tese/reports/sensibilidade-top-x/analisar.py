"""python tese/sensibilidade-top-x/analisar.py — análise e HTML autossuficiente."""
from pathlib import Path
from decimal import Decimal
import sys
import json
import hashlib
import platform
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PREVIOUS = ROOT/'tese/alternativas-top-necr'
sys.path.insert(0, str(PREVIOUS))
from analisar import grupo_acumulado, evaluate, select, LK, CK
from cap3_taa_features import norm_partido, acertos_fracionarios
from cap3_cobertura_top_necr import calcular_cobertura_top_necr

THRESHOLDS = [50,60,70,80,90,95]
OUTCOMES = {'competitividade':'competitivo_previo', 'eleicao':'eleito'}
checks = {}


def check(name, condition):
    checks[name] = bool(condition)
    assert condition, name


def ratio(a,b):
    return a/b if b else np.nan


def summarize(ev, d):
    rows=[]
    for (year,rule,outcome),g in ev.groupby(['ano_eleicao','regra','desfecho'],sort=False):
        n,k,f,h,e = g[['n','k','total','hits','expected']].sum()
        rows.append(dict(ano_eleicao=year,regra=rule,limiar=g.limiar.iloc[0],desfecho=outcome,
                         N_valido=n,ausentes=int(d.ano_eleicao.eq(year).sum()-n),k_valido=k,
                         total_perfil=f,observados=h,esperados_acaso=e,cobertura=ratio(h,f),
                         precisao=ratio(h,k),proporcao_perfil_fora=ratio(f-h,n-k),
                         cobertura_acaso=ratio(e,f),precisao_acaso=ratio(e,k),lift=ratio(h,e)))
    return pd.DataFrame(rows)


def main():
    sources=[PREVIOUS/'candidaturas.parquet', PREVIOUS/'resumo_nacional.csv',
             ROOT/'data/processed/rrd_df_novo.parquet',
             ROOT/'tese/resultados-exploracao-nucleo/base_analitica.csv']
    d=pd.read_parquet(sources[0]).reset_index(drop=True)
    previous=pd.read_csv(sources[1])
    raw=pd.read_parquet(sources[2])
    oldaudit=json.loads((PREVIOUS/'auditoria.json').read_text(encoding='utf-8'))
    for path in sources[2:]:
        check('Integridade '+path.name,hashlib.sha256(path.read_bytes()).hexdigest()==oldaudit['fontes_sha256'][str(path.relative_to(ROOT))])
    check('Universo 7630 e 9675',d.groupby('ano_eleicao').size().to_dict()=={2018:7630,2022:9675})
    check('Chave única',not d.duplicated(CK).any())
    ref=raw[raw.ano_eleicao.isin([2018,2022])].copy()
    ref['nr_candidato']=pd.to_numeric(ref.nr_candidato,errors='raise').astype('int64')
    ref['sg_partido_norm']=ref.sg_partido.map(norm_partido)
    merged=d.merge(ref[CK+['sg_partido_norm','vr_receita_recursos_partidos','eleito']],on=CK,validate='one_to_one',suffixes=('','_raw'))
    check('Recursos e eleição iguais à base primária',len(merged)==len(ref)==len(d) and np.array_equal(merged.vr_receita_recursos_partidos,merged.vr_receita_recursos_partidos_raw.fillna(0)) and np.array_equal(merged.eleito,merged.eleito_raw) and (merged.sg_partido_norm==merged.sg_partido_norm_raw).all())
    base=pd.read_csv(sources[3],float_precision='round_trip',low_memory=False)
    major=['n_eleicoes_'+x for x in ['prefeito','deputado_estadual','deputado_federal','governador','senador']]
    known=base[major].notna().all(axis=1)&base.voto_relevante.notna()&base.vitoria_qualquer.notna()
    base['competitivo_ref']=(base[major].gt(0).any(axis=1)|base.voto_relevante.eq(1)).astype(float).where(known)
    credentials=d.merge(base[CK+['competitivo_ref']],on=CK,validate='one_to_one')
    check('Credenciais e ausências iguais à análise atual',np.allclose(credentials.competitivo_previo,credentials.competitivo_ref,equal_nan=True))
    canonical,national=calcular_cobertura_top_necr(raw)
    canonical=canonical.set_index(LK)
    check('Recursos válidos',np.isfinite(d.vr_receita_recursos_partidos).all() and d.vr_receita_recursos_partidos.ge(0).all())
    # Casos de fronteira, incluindo igualdade exata e grupo inteiro.
    check('Exemplo 40/25/10/8',grupo_acumulado([40,25,10,8,7,5,5],80)[1]==4)
    check('80% exatos',grupo_acumulado([80,20],80)[1]==1)
    check('Decimal exato',grupo_acumulado([.1,.1],50)[1]==1)
    check('Empate fracionário',np.allclose(grupo_acumulado([10]*5,80)[0],.8))
    check('Sem recursos',all(grupo_acumulado([0,0],t)[1]==0 for t in THRESHOLDS))
    check('100% não inclui zeros',grupo_acumulado([10,0,0],100)[1]==1)
    check('Um candidato',all(grupo_acumulado([10],t)[1]==1 for t in THRESHOLDS))
    evrows, listrows, bands=[] ,[],[]
    for t in THRESHOLDS:
        d[f'top_{t}']=0.
    for keys,g in d.groupby(LK,sort=True):
        common=dict(zip(LK,keys))
        v=g.vr_receita_recursos_partidos.to_numpy(float)
        reference=canonical.loc[keys]
        check(f'k e NECr canônicos {keys}',g.k_top_necr.eq(reference.k_arredondado).all() and np.allclose(g.NECr,reference.NECr,equal_nan=True))
        _,oldweights,k80=select(v,int(reference.k_arredondado))
        for rule,w in oldweights.items():
            check(f'Pesos anteriores {keys} {rule}',np.allclose(w,g[rule]))
        prev_w=np.zeros(len(g)); prev_t=0
        amounts=sorted([Decimal(str(x)) for x in v],reverse=True)
        total=sum(amounts,Decimal(0))
        for t in THRESHOLDS:
            w,k=grupo_acumulado(v,t)
            check(f'Conjunto mínimo {keys} {t}',(k==0 and total==0) or (sum(amounts[:k])>=Decimal(t)/100*total and (k==1 or sum(amounts[:k-1])<Decimal(t)/100*total)))
            check(f'Aninhamento e posições {keys} {t}',np.all(w>=prev_w-1e-12) and np.isclose(w.sum(),k) and k<=len(g))
            check(f'Invariância à ordem {keys} {t}',np.allclose(grupo_acumulado(v[::-1],t)[0][::-1],w))
            if t==80:
                check(f'Top80 idêntico {keys}',np.allclose(w,g.nucleo_80) and k==k80)
            if k:
                check(f'Empates canônicos {keys} {t}',np.isclose(w@g.eleito.to_numpy(),acertos_fracionarios(v,g.eleito,k)))
            d.loc[g.index,f'top_{t}']=w
            listrows.append(common|dict(limiar=t,C=len(g),k=k,proporcao=k/len(g),lista_sem_recursos=total==0,
                                       massa_financeira=ratio(w@v,v.sum()),empate_corte=bool(((w>0)&(w<1)).any())))
            for outcome,col in OUTCOMES.items():
                y=g[col].to_numpy(float)
                evrows.append(common|dict(regra=f'top_{t}',limiar=t,desfecho=outcome)|evaluate(w,y))
                bands.append(common|dict(faixa=f'{prev_t}–{t}%',ordem=prev_t,desfecho=outcome)|evaluate(w-prev_w,y))
            prev_w=w;prev_t=t
        for outcome,col in OUTCOMES.items():
            y=g[col].to_numpy(float)
            bands.append(common|dict(faixa='Fora do Top-95%',ordem=95,desfecho=outcome)|evaluate(1-prev_w,y))
            for rule in ['top_necr','acima_divisao_igual']:
                evrows.append(common|dict(regra=rule,limiar=np.nan,desfecho=outcome)|evaluate(g[rule].to_numpy(),y))
    ev=pd.DataFrame(evrows)
    lists=pd.DataFrame(listrows)
    summary=summarize(ev,d)
    # Reproduz todos os indicadores disponíveis das três referências anteriores.
    metrics=['N_valido','ausentes','k_valido','total_perfil','observados','esperados_acaso','cobertura','precisao','proporcao_perfil_fora','cobertura_acaso','precisao_acaso','lift']
    for _,r in previous.iterrows():
        rule='top_80' if r.regra=='nucleo_80' else r.regra
        row=summary[(summary.ano_eleicao==r.ano_eleicao)&(summary.regra==rule)&(summary.desfecho==r.desfecho)].iloc[0]
        check(f'Resumo anterior {r.ano_eleicao} {rule} {r.desfecho}',np.allclose(row[metrics].to_numpy(float),r[metrics].to_numpy(float)))
    for _,r in national[national.regra_k.eq('arredondado')].iterrows():
        row=summary[(summary.ano_eleicao==r.ano_eleicao)&(summary.regra=='top_necr')&(summary.desfecho=='eleicao')].iloc[0]
        check(f'Cobertura canônica {r.ano_eleicao}',np.allclose([row.observados,row.esperados_acaso,row.k_valido],[r.eleitos_top_necr,r.eleitos_esperados_aleatorio,r.n_posicoes_top_necr]))
    check('Lift idêntico por cobertura e precisão',np.allclose(summary.lift,summary.cobertura/summary.cobertura_acaso) and np.allclose(summary.lift,summary.precisao/summary.precisao_acaso))
    trajectories=[]
    for (year,outcome),g in summary[summary.limiar.notna()].groupby(['ano_eleicao','desfecho']):
        g=g.sort_values('limiar')
        for metric in ['k_valido','cobertura','precisao','lift']:
            delta=np.diff(g[metric])
            trajectories.append(dict(ano_eleicao=year,desfecho=outcome,indicador=metric,
                                     nao_decrescente=bool((delta>=-1e-12).all()),nao_crescente=bool((delta<=1e-12).all()),
                                     minimo=g[metric].min(),maximo=g[metric].max(),valor_50=g[metric].iloc[0],valor_95=g[metric].iloc[-1],
                                     passos_aumento=int((delta>1e-12).sum()),passos_queda=int((delta<-1e-12).sum())))
    trajectories=pd.DataFrame(trajectories)
    check('Cobertura não decrescente',trajectories[trajectories.indicador.eq('cobertura')].nao_decrescente.all())
    sizes=lists.groupby(['ano_eleicao','limiar']).agg(listas=('C','size'),candidatos=('C','sum'),posicoes=('k','sum'),k_medio=('k','mean'),k_mediano=('k','median'),k_q1=('k',lambda x:x.quantile(.25)),k_q3=('k',lambda x:x.quantile(.75)),sem_recursos=('lista_sem_recursos','sum'),empates=('empate_corte','sum')).reset_index()
    sizes['proporcao_nacional']=sizes.posicoes/sizes.candidatos
    banddetail=pd.DataFrame(bands)
    band=banddetail.groupby(['ano_eleicao','desfecho','ordem','faixa'])[['n','k','total','hits','expected']].sum().reset_index()
    band['incidencia']=band.hits/band.k
    band['lift']=band.hits/band.expected
    for (year,outcome),g in band.groupby(['ano_eleicao','desfecho']):
        ref=summary[(summary.ano_eleicao==year)&(summary.desfecho==outcome)].iloc[0]
        check(f'Faixas particionam universo válido {year} {outcome}',np.allclose([g.k.sum(),g.hits.sum()],[ref.N_valido,ref.total_perfil]))
    data={'resumo_nacional':summary,'tamanhos':sizes,'listas_top_x':lists,'avaliacao_por_lista':ev,'trajetorias':trajectories,'faixas_incrementais':band}
    for name,frame in data.items():
        frame.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
    d.to_parquet(OUT/'candidaturas.parquet',index=False)
    d.to_csv(OUT/'candidaturas.csv',index=False,encoding='utf-8-sig')
    sources += [Path(__file__),OUT/'relatorio.py',PREVIOUS/'analisar.py',ROOT/'src/2_gold/cap3_cobertura_top_necr.py',ROOT/'src/2_gold/cap3_taa_features.py',ROOT/'tese/scripts/financiamento_alternativo_top_necr.py']
    audit={'status':'OK','limiares':THRESHOLDS,'verificacoes':checks,'fontes_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'versoes':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},'interpretacao':'Expectativas descritivas exatas; sem inferência amostral ou seleção de limiar por desempenho.'}
    (OUT/'auditoria.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    from relatorio import create_report
    create_report(OUT,summary,sizes,trajectories,band,audit)
    print(summary[summary.limiar.notna()][['ano_eleicao','desfecho','limiar','k_valido','cobertura','precisao','lift']].to_string(index=False))
    print(trajectories.to_string(index=False))
    print(f'{len(checks)} verificações OK; {OUT / "relatorio.html"}')


if __name__=='__main__':
    main()
