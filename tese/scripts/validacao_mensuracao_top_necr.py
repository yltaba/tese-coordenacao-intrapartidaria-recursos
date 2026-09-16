"""NECr → Top-NECr: construção e três dimensões de validade.

python tese/scripts/validacao_mensuracao_top_necr.py
Referências aleatórias e perturbações são exercícios de mensuração, sem regressões.
"""
from pathlib import Path
import hashlib
import html
import json
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'tese/resultados-validacao-top-necr'
OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'src/2_gold'))
from cap3_cobertura_top_necr import calcular_cobertura_top_necr

SEED=13092026
B=10000
STRESS=200
checks={}
def check(name,value):
    checks[name]=bool(value)
    assert value,name

def weights(v,k):
    v=np.asarray(v,float)
    k=min(len(v),max(0,int(k)))
    if not k:return np.zeros(len(v))
    cut=np.sort(v)[-k]
    high=v>cut
    tied=v==cut
    return high.astype(float)+tied*(k-high.sum())/tied.sum()

def k_round(v):
    if v.sum()==0:return 0
    s=v/v.sum()
    return min(len(v),max(1,int(np.floor(1/(s@s)+.5))))

base=ROOT/'tese/resultados-exploracao-nucleo/base_analitica.csv'
d=pd.read_csv(base,low_memory=False,float_precision='round_trip')
old_audit=json.loads((base.parent/'auditoria.json').read_text(encoding='utf-8'))
rawpath=ROOT/'data/processed/rrd_df_novo.parquet'
check('Base primária corresponde à base auditada',hashlib.sha256(rawpath.read_bytes()).hexdigest()==old_audit['fontes_sha256']['data/processed/rrd_df_novo.parquet'])
check('Universos do capítulo',d.groupby('ano_eleicao').size().tolist()==[7630,9675])
check('Uma candidatura por chave',not d.duplicated(['ano_eleicao','sg_uf','nr_candidato']).any())
check('513 eleitos por ano',d.groupby('ano_eleicao').eleito.sum().eq(513).all())
check('Receitas finitas não negativas',np.isfinite(d.vr_receita_recursos_partidos).all() and d.vr_receita_recursos_partidos.ge(0).all())
major=['n_eleicoes_'+x for x in ['prefeito','deputado_estadual','deputado_federal','governador','senador']]
known=d[major].notna().all(axis=1)&d.voto_relevante.notna()&d.vitoria_qualquer.notna()
d['credencial_previa']=((d[major].gt(0).any(axis=1))|d.voto_relevante.eq(1)).astype(float).where(known)
FEATURES={'credencial_previa':'Competitivo prévio (critério operacional do capítulo)',
          'reeleicao_proxy':'Eleito federal no pleito anterior',
          'ex_federal_proxy':'Vitória federal antiga, sem vitória no pleito anterior',
          'vitoria_estadual':'Vitória anterior estadual/distrital',
          'vitoria_prefeito':'Vitória anterior para prefeito',
          'vitoria_vereador':'Vitória anterior para vereador',
          'voto_relevante':'Votação histórica ≥ 10% do QE',
          'mulher':'Mulheres (descrição, não critério de validade)',
          'negra':'Pessoas pretas ou pardas (descrição, não critério de validade)'}

listrows=[]
featrows=[]
stressrows=[]
candidate_rows=[]
for keys,g in d.groupby(['ano_eleicao','sg_uf','sg_partido_norm'],sort=True):
    year,uf,party=keys
    common={'Ano':int(year),'UF':uf,'Partido':party,'Magnitude':g.magnitude.iloc[0]}
    v=g.vr_receita_recursos_partidos.to_numpy(float)
    elected=g.eleito.to_numpy(int)
    n=len(v);total=v.sum();funded=total>0
    necr=total**2/(v@v) if funded else np.nan
    k=k_round(v)
    w0=weights(v,k)
    check(f'Peso canônico {keys}',np.allclose(w0,g.top.to_numpy()))
    check(f'Invariância à ordem {keys}',np.allclose(weights(v[::-1],k)[::-1],w0))
    scale_same=k_round(v*7)==k and np.allclose(weights(v*7,k_round(v*7)),w0)
    cents=np.round(v,2)
    ks={'Arredondado':k,
        'Piso':min(n,max(1,int(np.floor(necr)))) if funded else 0,
        'Teto':min(n,max(1,int(np.ceil(necr)))) if funded else 0,
        'Uma posição a menos':max(1,k-1) if funded else 0,
        'Uma posição a mais':min(n,k+1) if funded else 0,
        'Acumulado ≥ 80%':min(n,int(np.searchsorted(np.cumsum(np.sort(v)[::-1]),.8*total))+1) if funded else 0,
        'Receitas arredondadas a centavos':k_round(cents)}
    for rule,kk in ks.items():
        ranking_v=cents if rule=='Receitas arredondadas a centavos' else v
        w=weights(ranking_v,kk)
        mass=w@v
        cash=mass/total if funded else np.nan
        amp=kk/n
        valid_boundary=0<kk<n
        ordered=np.sort(ranking_v)[::-1]
        rk=ordered[kk-1] if kk else np.nan
        nextv=ordered[kk] if valid_boundary else np.nan
        gap=(rk-nextv)/rk if valid_boundary and rk>0 else np.nan
        uncertain=(w>0)&(w<1)
        tie_positions=w[uncertain].sum()
        tie_winners=elected[uncertain].sum()
        fixed=w[~uncertain]@elected[~uncertain]
        minhit=fixed+max(0,tie_positions-(uncertain.sum()-tie_winners))
        maxhit=fixed+min(tie_positions,tie_winners)
        fcount=(v>0).sum()
        funded_elected=elected[v>0].sum()
        intersect=np.minimum(w0,w).sum()
        union=np.maximum(w0,w).sum()
        row=common|{'Regra':rule,'C':n,'Financiados':int(fcount),'E':int(elected.sum()),'Recursos R$':total,
                    'NECr':necr,'K':kk,'Recursos no núcleo R$':mass,'Massa de recursos %':100*cash,
                    'Amplitude %':100*amp,'Excesso de massa pp':100*(cash-amp),
                    'Fronteira válida':valid_boundary,'Distância relativa no corte %':100*gap,
                    'Empate na fronteira':bool(valid_boundary and rk==nextv),
                    'Candidatos com peso fracionário':int(uncertain.sum()),'Posições fracionárias':tie_positions,
                    'Acertos':float(w@elected),'Acertos mínimos por desempate':minhit,'Acertos máximos por desempate':maxhit,
                    'Esperado aleatório':kk*elected.sum()/n,
                    'Esperado entre financiados':min(kk,fcount)*funded_elected/fcount if fcount else 0,
                    'K sorteio financiados':min(kk,fcount),'Eleitos financiados':funded_elected,
                    'Jaccard com principal':intersect/union if union else np.nan,
                    'Composição idêntica à principal':bool(np.allclose(w,w0)),
                    'Reescala x7 preserva implementação':bool(scale_same)}
        check(f'Posições {keys} {rule}',np.isclose(w.sum(),kk))
        check(f'Massa ao menos proporcional {keys} {rule}',not funded or cash+1e-10>=amp)
        check(f'Limites do empate {keys} {rule}',minhit-1e-8<=w@elected<=maxhit+1e-8)
        if rule=='Acumulado ≥ 80%':check(f'Corte 80% {keys}',not funded or cash>=.8-1e-10)
        listrows.append(row)
        for feature,label in FEATURES.items():
            z=g[feature].to_numpy(float)
            valid=np.isfinite(z)
            nn=valid.sum();ww=w[valid];zz=z[valid]
            success=zz.sum();obs=ww@zz
            featrows.append(common|{'Regra':rule,'Perfil':label,'N válido':nn,'Total com perfil':success,
                                    'K válido':ww.sum(),'Perfil no núcleo':obs,
                                    'Perfil fora':success-obs,'N fora válido':nn-ww.sum(),
                                    'Esperado perfil':ww.sum()*success/nn if nn else 0,
                                    'Ausência de perfil':n-nn})
        if rule=='Arredondado':
            for idx,wi in zip(g.index,w):
                candidate_rows.append({'Indice':int(idx),'Peso principal':wi})
    if funded:
        rng=np.random.default_rng(SEED+int(year)*10000+int(g.lista.iloc[0]))
        for delta in [.05,.10]:
            pert=v[None,:]*rng.uniform(1-delta,1+delta,size=(STRESS,n))
            sns=pert/pert.sum(axis=1)[:,None]
            nk=np.clip(np.floor(1/(sns*sns).sum(axis=1)+.5).astype(int),1,n)
            cutoff=np.sort(pert,axis=1)[np.arange(STRESS),n-nk]
            high=pert>cutoff[:,None];tied=pert==cutoff[:,None]
            pw=high.astype(float)+tied*((nk-high.sum(axis=1))/tied.sum(axis=1))[:,None]
            j=np.minimum(pw,w0).sum(axis=1)/np.maximum(pw,w0).sum(axis=1)
            stressrows.append(common|{'Perturbação máxima %':int(delta*100),'N cenários':STRESS,
                                     'K original':k,'C':n,'Fronteira original válida':0<k<n,
                                     'Jaccard médio':j.mean(),'Jaccard P10':np.quantile(j,.1),
                                     'Cenários com K alterado %':100*np.mean(nk!=k),
                                     'Cenários com composição alterada %':100*np.mean(np.max(np.abs(pw-w0),axis=1)>1e-8)})

lists=pd.DataFrame(listrows)
fl=pd.DataFrame(featrows)
stress=pd.DataFrame(stressrows)
main=lists[lists.Regra.eq('Arredondado')].copy()
_,canonical=calcular_cobertura_top_necr()
for _,r in canonical.iterrows():
    rule={'piso':'Piso','arredondado':'Arredondado','teto':'Teto'}[r.regra_k]
    z=lists[lists.Ano.eq(r.ano_eleicao)&lists.Regra.eq(rule)]
    check(f'Reprodução externa {r.ano_eleicao} {rule}',np.isclose(z.Acertos.sum(),r.eleitos_top_necr))

def internal_summary(frame,by):
    rows=[]
    for keys,g in frame.groupby(by,sort=True):
        keys=keys if isinstance(keys,tuple) else (keys,)
        f=g[g['Recursos R$']>0]
        b=f[f['Fronteira válida']]
        rows.append(dict(zip(by,keys))|{'Listas':len(g),'Listas financiadas':len(f),'Listas sem recursos':len(g)-len(f),
                    'Núcleo = lista inteira':int((f.K==f.C).sum()),'Fronteiras comparáveis':len(b),
                    'NECr mediano':f.NECr.median(),'K total':g.K.sum(),
                    'Massa agregada %':100*f['Recursos no núcleo R$'].sum()/f['Recursos R$'].sum() if len(f) else np.nan,
                    'Massa por lista P25 %':f['Massa de recursos %'].quantile(.25),'Massa por lista mediana %':f['Massa de recursos %'].median(),
                    'Massa por lista P75 %':f['Massa de recursos %'].quantile(.75),
                    'Amplitude mediana %':f['Amplitude %'].median(),'Excesso de massa mediano pp':f['Excesso de massa pp'].median(),
                    'Distância no corte mediana %':b['Distância relativa no corte %'].median(),
                    'Empates no corte':int(b['Empate na fronteira'].sum()),
                    'Empates entre fronteiras %':100*b['Empate na fronteira'].mean() if len(b) else np.nan,
                    'Candidatos com peso fracionário':g['Candidatos com peso fracionário'].sum()})
    return pd.DataFrame(rows)

internal=internal_summary(main,['Ano'])
party_internal=internal_summary(main,['Ano','Partido'])
robust=[]
for (year,rule),g in lists.groupby(['Ano','Regra']):
    f=g[g['Recursos R$']>0]
    valid=f[f['Fronteira válida']]
    robust.append({'Ano':year,'Regra':rule,'Listas financiadas':len(f),'K total':g.K.sum(),
                   'Massa agregada %':100*f['Recursos no núcleo R$'].sum()/f['Recursos R$'].sum(),
                   'Massa mediana por lista %':f['Massa de recursos %'].median(),
                   'Jaccard mediano por lista financiada':f['Jaccard com principal'].median(),
                   'Jaccard P10 por lista financiada':f['Jaccard com principal'].quantile(.1),
                   'Listas financiadas com composição idêntica %':100*f['Composição idêntica à principal'].mean(),
                   'Cobertura %':100*g.Acertos.sum()/g.E.sum(),
                   'Precisão %':100*g.Acertos.sum()/g.K.sum(),
                   'Lift eleitoral':g.Acertos.sum()/g['Esperado aleatório'].sum()})
robust=pd.DataFrame(robust)
stress_summary=[]
for (year,delta),g in stress.groupby(['Ano','Perturbação máxima %']):
    for label,z in [('Todas as listas financiadas',g),('Só listas originalmente com núcleo parcial',g[g['Fronteira original válida']])]:
        stress_summary.append({'Ano':year,'Perturbação máxima %':delta,'Universo':label,'Listas':len(z),'Cenários por lista':STRESS,
                               'Jaccard médio entre listas':z['Jaccard médio'].mean(),
                               'K alterado: média das frequências %':z['Cenários com K alterado %'].mean(),
                               'Composição alterada: média das frequências %':z['Cenários com composição alterada %'].mean()})
stress_summary=pd.DataFrame(stress_summary)

def substantive(frame,by):
    rows=[]
    for keys,g in frame.groupby(by,sort=True):
        keys=keys if isinstance(keys,tuple) else (keys,)
        n=g['N válido'].sum();k=g['K válido'].sum();f=g['Total com perfil'].sum();a=g['Perfil no núcleo'].sum();expected=g['Esperado perfil'].sum()
        rows.append(dict(zip(by,keys))|{'N válido':n,'Ausentes':g['Ausência de perfil'].sum(),'Total com perfil':f,
                    'Posições válidas no núcleo':k,'Perfil no núcleo':a,'Esperado intralista':expected,
                    'Composição do núcleo %':100*a/k if k else np.nan,
                    'Composição fora %':100*(f-a)/(n-k) if n>k else np.nan,
                    'Cobertura do perfil %':100*a/f if f else np.nan,
                    'Cobertura esperada do perfil %':100*expected/f if f else np.nan,
                    'Entrada entre sem perfil %':100*(k-a)/(n-f) if n>f else np.nan,
                    'Lift do perfil':a/expected if expected else np.nan})
    return pd.DataFrame(rows)

exante=substantive(fl[fl.Regra.eq('Arredondado')],['Ano','Perfil'])
exante_robust=substantive(fl[fl.Perfil.eq(FEATURES['credencial_previa'])],['Ano','Regra'])
exante_party=substantive(fl[fl.Regra.eq('Arredondado')&fl.Perfil.eq(FEATURES['credencial_previa'])],['Ano','Partido'])

external=[]
nullrows=[]
for year,g in main.groupby('Ano'):
    for universe in ['Todos os candidatos','Apenas recebedores positivos']:
        rng=np.random.default_rng(SEED+year+(universe.startswith('Apenas')))
        sims=np.zeros(B,dtype=int)
        expected=0.;variance=0.
        for _,r in g.iterrows():
            n=int(r.C if universe.startswith('Todos') else r.Financiados)
            e=int(r.E if universe.startswith('Todos') else r['Eleitos financiados'])
            k=int(r.K if universe.startswith('Todos') else r['K sorteio financiados'])
            if not n:continue
            sims+=rng.hypergeometric(e,n-e,k,size=B)
            expected+=k*e/n
            if n>1:variance+=k*(e/n)*(1-e/n)*(n-k)/(n-1)
        check(f'Média simulada {year} {universe}',abs(sims.mean()-expected)<max(.15,6*np.sqrt(variance/B)))
        obs=g.Acertos.sum();total_e=g.E.sum();total_k=g.K.sum()
        external.append({'Ano':year,'Sorteio dentro da lista':universe,'Eleitos':total_e,'K total':total_k,
                         'Observados':obs,'Esperados':expected,'Sorteio P2,5':np.quantile(sims,.025),'Sorteio P97,5':np.quantile(sims,.975),
                         'Cobertura observada %':100*obs/total_e,'Cobertura esperada %':100*expected/total_e,
                         'Precisão observada %':100*obs/total_k,'Precisão esperada %':100*expected/total_k,
                         'Lift':obs/expected,'Acertos mínimos entre desempates':g['Acertos mínimos por desempate'].sum(),
                         'Acertos máximos entre desempates':g['Acertos máximos por desempate'].sum(),
                         'N sorteios':B})
        nullrows.extend({'Ano':year,'Universo':universe,'Acertos simulados':int(x)} for x in sims)
external=pd.DataFrame(external)
nulls=pd.DataFrame(nullrows)
party_external=[]
for (year,p),g in main.groupby(['Ano','Partido']):
    party_external.append({'Ano':year,'Partido':p,'Eleitos':g.E.sum(),'Eleitos no núcleo':g.Acertos.sum(),
                           'Esperados':g['Esperado aleatório'].sum(),
                           'Cobertura eleitoral %':100*g.Acertos.sum()/g.E.sum() if g.E.sum() else np.nan,
                           'Precisão eleitoral %':100*g.Acertos.sum()/g.K.sum() if g.K.sum() else np.nan,
                           'Lift eleitoral':g.Acertos.sum()/g['Esperado aleatório'].sum() if g['Esperado aleatório'].sum() else np.nan})
party_external=pd.DataFrame(party_external)
party=party_internal[['Ano','Partido','Listas financiadas','Massa por lista mediana %','Distância no corte mediana %','Empates no corte']].merge(
    exante_party[['Ano','Partido','Total com perfil','Cobertura do perfil %','Lift do perfil']],on=['Ano','Partido'],validate='one_to_one').merge(party_external,on=['Ano','Partido'],validate='one_to_one')

examples=[]
for name,v in [('Distribuição A',np.array([.4,.3,.2,.1])),('Distribuição B',np.array([(.5+np.sqrt(.05))/2]*2+[(.5-np.sqrt(.05))/2]*2)),('Recursos iguais',np.ones(4)/4),('Concentração quase total',np.array([.97,.01,.01,.01]))]:
    k=k_round(v);w=weights(v,k)
    examples.append({'Exemplo':name,'Participações %':'; '.join(f'{100*x:.2f}' for x in v),'NECr':1/(v@v),'K':k,
                     'Pesos Top-NECr':'; '.join(f'{x:.2f}' for x in w),'Recursos no núcleo %':100*(v@w)})
examples=pd.DataFrame(examples)
check('Mesmo NECr, massas distintas',np.isclose(examples.NECr.iloc[0],examples.NECr.iloc[1]) and not np.isclose(examples['Recursos no núcleo %'].iloc[0],examples['Recursos no núcleo %'].iloc[1]))

tables={}
fig_num=0
def fmt(x):
    return f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
def table(frame,name,filterable=False):
    tables[name]=frame
    frame.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
    search=f'<label class="filter">Filtrar tabela <input type="search" data-table="t-{name}" placeholder="Ano, partido, perfil ou regra"></label>' if filterable else ''
    return search+'<div class="scroll" tabindex="0">'+frame.to_html(index=False,border=0,table_id='t-'+name,na_rep='—',float_format=fmt)+f'</div><p class="download"><a href="resultados-validacao-top-necr/{name}.csv">Baixar CSV</a></p>'
def fig(f):
    global fig_num
    fig_num+=1
    f.update_layout(template='plotly_white',font=dict(family='Arial',size=14),margin=dict(l=30,r=30,t=65,b=45))
    return '<div class="plot-wrap">'+f.to_html(full_html=False,include_plotlyjs=True if fig_num==1 else False,div_id=f'valid-fig-{fig_num}',config={'displaylogo':False,'responsive':True})+'</div>'

parts=['''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Do NECr ao Top-NECr: construção e validade do núcleo</title><style>
body{margin:0;background:#f2f5f6;color:#243547;font:17px/1.65 system-ui}main{max-width:1240px;margin:auto;padding:28px 18px 70px}header{background:#173d4b;color:white;border-radius:16px;padding:36px}h1{font-size:39px;line-height:1.2}h2{line-height:1.3}h3{margin-top:30px}section{margin-top:24px;background:white;padding:28px;border-radius:14px}nav{display:flex;flex-wrap:wrap;gap:15px}a{color:#00697e}header a{color:#b9f0e4}.note{padding:17px;background:#eaf5f2;border-left:4px solid #148476}.caution{padding:17px;background:#fcf4e8;border-left:4px solid #b77830}.scroll{overflow:auto;max-height:650px;border:1px solid #dce4e8}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:9px;text-align:left;border-bottom:1px solid #dce4e8}th{position:sticky;top:0;background:#eaf0f4}input{padding:10px;border:1px solid #8aa3af;font:inherit;border-radius:5px;max-width:90%}.filter{display:block;margin:16px 0}.download{font-size:14px}.formula{background:#f3f6f8;padding:14px;font:18px/1.7 Georgia,serif;overflow:auto}.flow{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:22px 0}.flow div{padding:20px;border:1px solid #a7c8cf;border-radius:8px;background:#f5faf9}.flow strong{display:block;font-size:20px}.plot-wrap{overflow:auto}code{overflow-wrap:anywhere}@media(max-width:650px){h1{font-size:29px}header,section{padding:18px}.flow{grid-template-columns:1fr}}@media print{header{background:white;color:#243547}.scroll{max-height:none}nav,input{display:none}body{background:white}}
</style></head><body><main><header><p>CAPÍTULO 3 · RELATÓRIO DE MENSURAÇÃO</p><h1>Do NECr ao Top-NECr: quando falar em núcleo priorizado?</h1><p>Construção do conjunto, propriedades internas, credenciais anteriores e correspondência com a eleição · 2018 e 2022.</p><nav><a href="#sintese">Síntese</a><a href="#construcao">Construção</a><a href="#interna">Validade interna</a><a href="#robustez">Robustez</a><a href="#exante">Validade ex ante</a><a href="#expost">Validade ex post</a><a href="#partidos">Partidos</a><a href="#interpretacao">Interpretação</a><a href="#metodo">Reprodução</a></nav></header>''']

parts.append('<section id="sintese"><h2>1. O problema de mensuração</h2><p>O NECr descreve a concentração de uma distribuição, mas não identifica, sozinho, suas candidaturas individualmente priorizadas. A contribuição metodológica para o capítulo está em explicitar a passagem do tamanho efetivo para uma regra de identificação e avaliar o que essa regra permite observar.</p><div class="flow"><div><strong>NECr</strong>Tamanho efetivo da distribuição de recursos.</div><div><strong>Top-NECr</strong>Regra de tradução: ordenar recursos e atribuir pertencimento às primeiras k posições.</div><div><strong>Núcleo priorizado</strong>Interpretação empírica apoiada em propriedades internas e correspondência com critérios externos à fórmula.</div></div><p>A apresentação é descritiva. Os exercícios aleatórios servem como referência de mensuração com tamanho fixo por lista. As perturbações são cenários de sensibilidade, sem regressões ou interpretação causal.</p>')
for _,r in internal.iterrows():
    yr=int(r.Ano)
    ante=exante[(exante.Ano==yr)&exante.Perfil.eq(FEATURES['credencial_previa'])].iloc[0]
    post=external[(external.Ano==yr)&external['Sorteio dentro da lista'].eq('Todos os candidatos')].iloc[0]
    parts.append(f'<p><strong>{yr}.</strong> A lista financiada mediana concentra {fmt(r["Massa por lista mediana %"])}% dos recursos no núcleo; a distância relativa mediana no corte é {fmt(r["Distância no corte mediana %"])}% entre listas com fronteira comparável. O núcleo inclui {fmt(ante["Cobertura do perfil %"])}% dos competitivos prévios (lift {fmt(ante["Lift do perfil"])}). Entre os eleitos, inclui {fmt(post["Cobertura observada %"])}%, contra {fmt(post["Cobertura esperada %"])}% esperados por sorteio intralista (lift {fmt(post.Lift)}).</p>')
parts.append('<p class="note">A leitura conjunta é mais informativa que qualquer resultado isolado. Massa financeira elevada não é validação independente de uma regra baseada no ranking financeiro. Credenciais e eleição são referências externas à fórmula; ainda assim, não identificam intenção partidária, causalidade ou previsão feita antes da campanha.</p></section>')

parts.append('<section id="construcao"><h2>2. Do tamanho efetivo ao pertencimento individual</h2><div class="formula">sᵢ = Rᵢ / ΣRⱼ &nbsp;;&nbsp; NECr = 1 / Σsᵢ² &nbsp;;&nbsp; k = min(C, floor(NECr + 0,5))</div><p>Rᵢ representa recursos partidários, C é o número de candidaturas da lista e k é o inteiro mais próximo do NECr. Ordenam-se as candidaturas por Rᵢ em ordem decrescente. A fórmula do NECr não utiliza identidade, credenciais ou eleição; o Top-NECr acrescenta uma regra explícita de pertencimento.</p><p>Se houver empate no valor da k-ésima posição, quem está estritamente acima recebe peso 1; quem está abaixo recebe 0; cada empatado recebe (k − número acima) ÷ número de empatados. Assim, Σwᵢ = k. O pertencimento é fracionário quando o corte não distingue candidaturas: não há um conjunto binário único sem outra regra de desempate.</p><p>Listas sem recursos têm NECr indefinido e núcleo vazio. Recursos iguais entre todos produzem NECr = C e núcleo igual à lista inteira, sem distinção interna. Multiplicar todos os recursos por uma constante positiva ou mudar a ordem das linhas não altera a construção.</p>')
parts.append(table(examples,'exemplos_construcao'))
parts.append('<p><strong>O mesmo NECr não determina a mesma estrutura de corte.</strong> As distribuições A e B têm NECr = 3,33 e k = 3. A primeira coloca 90% do dinheiro no núcleo e separa o terceiro do quarto recebedor; a segunda coloca 86,18% e apresenta empate na fronteira. Esses exemplos mostram por que o passo de identificação merece discussão própria.</p><p class="caution">Arredondamento, ranking e tratamento de empates são escolhas de operacionalização. O NECr não contém uma prova de que exatamente k pessoas formem um grupo latente, nem garante uma ruptura natural na distribuição. O Top-NECr é uma tradução transparente e auditável, que precisa ter seu desempenho descrito.</p></section>')

parts.append('<section id="interna"><h2>3. Propriedades internas: massa e separação</h2><h3>Quanto dinheiro o núcleo reúne?</h3><div class="formula">Massa financeira = ΣwᵢRᵢ / ΣRᵢ &nbsp;;&nbsp; amplitude = k/C<br>Excesso de massa = massa financeira − k/C</div><p>A massa financeira informa a parcela dos recursos retida pelo conjunto. O excesso de massa a compara com sua parcela de candidaturas. Como o Top-NECr reúne os maiores valores, a massa é necessariamente ao menos k/C. O tamanho desse excesso é descritivo; seu sinal positivo não é evidência independente de validade.</p>')
parts.append(table(internal,'validade_interna'))
parts.append('<p><strong>As dimensões não se movem juntas.</strong> De 2018 para 2022, a massa financeira mediana cai de 96,7% para 88,2%, e a distância mediana no corte cai de 83,3% para 19,2%. Ao mesmo tempo, a cobertura eleitoral aumenta. O Top-NECr de 2022 corresponde a mais eleitos, mas tem uma fronteira financeira menos marcada na lista mediana. Há 207 listas financiadas com núcleo igual à lista inteira em 2018 e 100 em 2022; esses casos não discriminam prioridade interna.</p>')
f=main[main['Recursos R$']>0].copy();f['Ano']=f.Ano.astype(str)
plot=f.melt(id_vars=['Ano','UF','Partido'],value_vars=['Massa de recursos %','Amplitude %'],var_name='Medida',value_name='Percentual')
parts.append(fig(px.box(plot,x='Ano',y='Percentual',color='Medida',points=False,height=430,title='Distribuições entre listas financiadas: massa e amplitude')))
parts.append('<p>A massa agregada dá maior peso às listas com mais dinheiro. Mediana e quartis dão peso igual a cada lista financiada. Listas sem recursos são contabilizadas separadamente, porque nelas a massa financeira é indefinida. Listas cujo núcleo inclui todos os candidatos podem ter massa de 100% sem qualquer focalização interna.</p><h3>Existe uma separação no ponto de corte?</h3><div class="formula">Distância relativa no corte = 100 × (R₍ₖ₎ − R₍ₖ₊₁₎) / R₍ₖ₎</div><p>Esse indicador só é definido quando 0 &lt; k &lt; C. Zero indica empate; valores próximos de zero indicam vizinhos financeiros próximos; 100% indica que o primeiro valor fora do corte é zero. A ordenação garante distância não negativa, mas não garante um salto grande nem a existência de dois agrupamentos naturais.</p>')
b=main[main['Fronteira válida']].copy();b['Ano']=b.Ano.astype(str)
parts.append(fig(px.histogram(b,x='Distância relativa no corte %',color='Ano',facet_col='Ano',nbins=20,height=400,title='Distância no corte entre listas com núcleo parcial')))
parts.append(table(main[['Ano','UF','Partido','C','NECr','K','Massa de recursos %','Amplitude %','Distância relativa no corte %','Fronteira válida','Empate na fronteira','Candidatos com peso fracionário']],'fronteiras_listas',True))
parts.append('</section>')

parts.append('<section id="robustez"><h2>4. A identificação depende muito do corte?</h2><p>Comparamos arredondamento, piso, teto e uma posição a menos ou a mais (mínimo de uma nas listas financiadas). Acrescentamos o menor k que atinge ao menos 80% dos recursos: esta última regra responde a outra pergunta, cobertura financeira fixa, e não é um estimador alternativo do mesmo tamanho efetivo. A linha de centavos é uma sensibilidade numérica, descrita abaixo.</p><div class="formula">Jaccard fracionário = Σ min(wᵢ, wᵢ′) / Σ max(wᵢ, wᵢ′)</div><p>O Jaccard é 1 quando os pesos são idênticos e se aproxima de zero quando há pouca sobreposição. As comparações excluem listas sem recursos, nas quais ambos os núcleos são vazios. Os cortes no mesmo ranking são aninhados: sobreposição elevada é parcialmente mecânica, sobretudo em núcleos maiores. Por isso também mostramos quantas listas mantêm exatamente os mesmos pesos. A linha de centavos pode mudar os blocos de empate.</p>')
parts.append(table(robust,'robustez_cortes'))
parts.append('<h3>Empate financeiro e precisão numérica</h3><p>A referência principal reproduz os valores binários do pipeline, recuperados do CSV com leitura round-trip. Existem diferenças inferiores a um centavo, como 11.081,78 e 11.081,779999999999. A comparação exata pode distinguir esses valores no corte. A sensibilidade a centavos arredonda cada soma de receita para duas casas e recalcula tanto o NECr como os pesos; a massa retida continua sendo contabilizada nos valores originais.</p>')
for year,g in main.groupby('Ano'):
    cent=lists[lists.Ano.eq(year)&lists.Regra.eq('Receitas arredondadas a centavos')]
    changed=int((~cent['Composição idêntica à principal']).sum())
    scaled=int((~g['Reescala x7 preserva implementação']).sum())
    parts.append(f'<p><strong>{year}:</strong> arredondar a centavos muda os pesos em {changed} listas. Uma reescala de todos os recursos por 7, sem normalizar centavos, muda a implementação em {scaled} listas. Em aritmética exata, a escala não poderia mudar o Top-NECr: eventuais diferenças refletem precisão numérica, não priorização partidária.</p>')
parts.append('<p class="caution">Para uma versão definitiva da mensuração, convém estabelecer uma unidade monetária comum (por exemplo, centavos inteiros) antes de identificar empates e documentar a atualização das contagens. Este relatório mantém a referência do capítulo e torna essa decisão visível; as bases e figuras do capítulo não foram recalculadas com outra convenção.</p>')
plot=robust.copy();plot['Ano']=plot.Ano.astype(str)
parts.append(fig(px.scatter(plot,x='Massa agregada %',y='Cobertura %',color='Ano',symbol='Regra',hover_data=['K total','Precisão %','Lift eleitoral'],height=470,title='Consequências de cada corte: massa financeira e cobertura eleitoral')))
parts.append('<h3>Sensibilidade a pequenas mudanças dos recursos</h3><p>Em cada lista financiada, multiplicamos os recursos de cada candidatura por um fator independente uniforme entre 0,95 e 1,05, ou entre 0,90 e 1,10. Fazemos 200 cenários por intensidade, recalculando tanto o NECr quanto o ranking e os pesos. Zeros permanecem zeros. São perturbações hipotéticas, não estimativas de erro de declaração nem intervalos de confiança.</p>')
parts.append(table(stress_summary,'sensibilidade_recursos'))
parts.append('<p><strong>Leitura:</strong> entre listas originalmente com núcleo parcial, perturbações de até 10% mantêm Jaccard médio de 0,952 em 2018 e 0,921 em 2022. Apesar da sobreposição alta, a composição se altera em média em 16,2% e 35,2% dos cenários por lista, respectivamente. “O núcleo é parecido” e “os mesmos candidatos permanecem com os mesmos pesos” são afirmações diferentes.</p>')
parts.append('<p>Os resultados dão peso igual às listas. A segunda linha de universo exclui os casos originalmente sem fronteira interna, que podem tornar a estabilidade global artificialmente alta. Uma pequena perturbação pode romper empates ou cruzar um limiar de arredondamento. O exercício informa a estabilidade local da classificação, não a confiabilidade dos registros eleitorais.</p>')
parts.append(table(stress,'sensibilidade_por_lista',True))
parts.append('</section>')

parts.append('<section id="exante"><h2>5. Validade substantiva ex ante: credenciais anteriores</h2><p>A referência principal é o critério operacional de competitividade do capítulo: vitória anterior para prefeito, deputado estadual/distrital, deputado federal, governador ou senador, ou votação histórica de ao menos 10% do QE. Vitória para vereador é apresentada separadamente. São informações anteriores à eleição estudada, não componentes do ranking financeiro.</p><p>Há duas perguntas complementares: quanto do núcleo possui credenciais e quanto dos portadores dessas credenciais aparece no núcleo? Um núcleo pode incluir a maioria dos competitivos e ainda ser composto majoritariamente por candidaturas sem esse registro.</p><div class="formula">Observados com perfil = ΣwᵢFᵢ<br>Esperados com perfil = Σlistas (Kᵥ × Fᵥ / Nᵥ)<br>Lift do perfil = observados / esperados</div><p>Nᵥ é o número de candidatos com informação válida na lista; Fᵥ é o total com a credencial; Kᵥ é a soma dos pesos do núcleo entre esses candidatos válidos. O benchmark preserva a composição da lista e a massa de posições entre registros válidos. É uma expectativa descritiva de atribuição intercambiável de pesos, inclusive fracionários; não requer sorteio de um número fracionário de pessoas.</p>')
parts.append(table(exante,'validade_exante'))
plot=exante[~exante.Perfil.str.contains('descrição')].melt(id_vars=['Ano','Perfil'],value_vars=['Cobertura do perfil %','Cobertura esperada do perfil %'],var_name='Referência',value_name='Percentual')
parts.append(fig(px.bar(plot,x='Percentual',y='Perfil',color='Referência',facet_col='Ano',orientation='h',barmode='group',height=610,title='Quanto de cada perfil entra: observado e referência intralista')))
for year in [2018,2022]:
    r=exante[(exante.Ano==year)&exante.Perfil.eq(FEATURES['credencial_previa'])].iloc[0]
    parts.append(f'<p><strong>{year}:</strong> {fmt(r["Composição do núcleo %"])}% do núcleo válido possui o critério de competitividade anterior; a cobertura desses candidatos é {fmt(r["Cobertura do perfil %"])}%, frente a {fmt(r["Cobertura esperada do perfil %"])}% esperados dentro das listas. O lift é {fmt(r["Lift do perfil"])}. A composição do núcleo e a cobertura das credenciais não devem ser confundidas.</p>')
parts.append('<p>Gênero e raça/cor são descrições da composição, não credenciais de competitividade nem requisitos para “validar” uma priorização. Os indicadores de trajetória se sobrepõem. Ausência de vitória ou votação histórica relevante não significa ausência de capital político.</p><h3>As credenciais permanecem concentradas sob outros cortes?</h3>')
parts.append(table(exante_robust,'exante_por_corte'))
parts.append('<p>O lift de competitividade anterior permanece acima de 1 em todos os cortes examinados nos dois anos. Isso indica uma correspondência descritiva persistente com essa credencial, sem implicar que cada trajetória tenha o mesmo padrão nem que toda candidatura sem a credencial deixe de ser priorizada.</p>')
parts.append('</section>')

parts.append('<section id="expost"><h2>6. Validade externa ex post: correspondência com a eleição</h2><p>O resultado eleitoral não entra na construção do NECr, na definição de k nem no ranking. A comparação externa pergunta se os eleitos aparecem no conjunto em número maior que o esperado em conjuntos de mesmo tamanho nas mesmas nominatas.</p><div class="formula">A = ΣwᵢEᵢ &nbsp;;&nbsp; A₀ = Σlistas (k × E/C)<br>Cobertura = A / ΣE &nbsp;;&nbsp; precisão = A / Σk &nbsp;;&nbsp; lift = A/A₀</div><p>O benchmark principal sorteia k candidatos uniformemente dentro de cada lista, sem reposição. São 10.000 sorteios agregados por eleição. A faixa entre os percentis 2,5 e 97,5 descreve os resultados desses sorteios; não é intervalo de confiança da cobertura observada. As médias esperadas são calculadas analiticamente, e a simulação confere sua escala.</p>')
parts.append(table(external,'validade_expost'))
fige=go.Figure()
for yr in [2018,2022]:
    z=external[(external.Ano==yr)&external['Sorteio dentro da lista'].eq('Todos os candidatos')].iloc[0]
    fige.add_trace(go.Bar(name=str(yr),x=[f'{yr} observado',f'{yr} sorteio'],y=[z.Observados,z.Esperados],marker_color=['#148675','#a8bdc9'],error_y=dict(type='data',array=[0,z['Sorteio P97,5']-z.Esperados],arrayminus=[0,z.Esperados-z['Sorteio P2,5']],symmetric=False),text=[f'{z.Observados:.1f}',f'{z.Esperados:.1f}'],textposition='outside',showlegend=False))
fige.update_layout(height=440,title='Eleitos no núcleo: observado e referência aleatória',yaxis_title='Eleitos (contagem ponderada no observado)')
parts.append(fig(fige))
parts.append('<h3>Uma referência mais exigente: sortear apenas recebedores</h3><p>A segunda referência mantém o tamanho k e sorteia apenas entre candidatos com recursos partidários positivos. Ela distingue a correspondência do Top-NECr da simples exclusão de candidaturas sem repasses. O denominador da cobertura continua sendo todos os 513 eleitos, inclusive aqueles sem recursos.</p>')
for yr in [2018,2022]:
    r=external[(external.Ano==yr)&external['Sorteio dentro da lista'].eq('Apenas recebedores positivos')].iloc[0]
    parts.append(f'<p><strong>{yr}:</strong> o sorteio entre recebedores produziria cobertura média de {fmt(r["Cobertura esperada %"])}%, diante de {fmt(r["Cobertura observada %"])}% observados (lift {fmt(r.Lift)}).</p>')
parts.append('<h3>Empates e limites da leitura</h3><p>O observado com empate é a média dos acertos possíveis entre desempates uniformes no bloco empatado. A tabela informa também os mínimos e máximos obtidos ao resolver todos os empates de forma desfavorável ou favorável aos eleitos, mantendo ranking e k. Essa faixa é distinta da faixa dos sorteios completamente aleatórios.</p><p class="caution">Correspondência acima do sorteio apoia a relevância eleitoral do conjunto, mas não demonstra que financiar cause eleição. Como as receitas são totais da campanha, resultado externo à fórmula não equivale a teste prospectivo ou fora da amostra. Chamamos esta dimensão de validade externa em relação ao critério eleitoral; não se trata de validade externa no sentido de generalização para outros cargos ou períodos.</p></section>')

parts.append('<section id="partidos"><h2>7. As três dimensões por partido</h2><p>Esta abertura mantém todas as siglas e ambos os anos. Massa e distância no corte são medianas das listas estaduais elegíveis; os lifts de credenciais e eleição são razões de somas. Grupos sem denominador ficam com “—”. Um retrato nacional favorável pode coexistir com padrões partidários distintos.</p>')
parts.append(table(party,'validade_por_partido',True))
plot=party.copy();plot['Ano']=plot.Ano.astype(str)
parts.append(fig(px.scatter(plot,x='Lift do perfil',y='Lift eleitoral',color='Ano',size='Eleitos',hover_name='Partido',hover_data=['Listas financiadas','Massa por lista mediana %','Total com perfil'],height=500,title='Correspondência substantiva e eleitoral por partido')))
parts.append('<p>O gráfico mostra partidos com referências definidas e número positivo de eleitos. Lifts elevados com denominadores esperados pequenos pedem leitura das contagens na tabela. Nenhuma combinação de indicadores é convertida em nota ou ranking geral de validade.</p>')
parts.append('</section>')

parts.append('<section id="interpretacao"><h2>8. O que autoriza a expressão “núcleo priorizado”?</h2><p>A expressão pode ser usada como interpretação operacional de um conjunto que reúne as maiores posições do financiamento, apresenta concentração e estabilidade documentadas e corresponde a credenciais e resultados além do esperado pelo seu tamanho. Ela deve vir depois da construção e da apresentação dessas evidências, não como premissa da mensuração.</p><p>Não há limiar universal aqui estabelecido para aprovar um núcleo. Massa, separação, sensibilidade, credenciais e eleição descrevem propriedades distintas. Núcleos que abrangem toda a lista não discriminam prioridade interna; fronteiras empatadas não autorizam separar categoricamente os candidatos; sensibilidade a pequenas mudanças deve acompanhar a descrição.</p><h3>Uma formulação possível para o capítulo</h3><blockquote>O NECr expressa o tamanho efetivo da distribuição de recursos partidários. Para identificar candidaturas correspondentes a essa dimensão, construo o Top-NECr: as primeiras k posições do ranking financeiro de cada nominata, com k obtido pelo arredondamento do NECr e pertencimento fracionário nos empates. Avalio sua capacidade de representar um núcleo de priorização financeira descrevendo a massa de recursos retida, a separação no corte e a estabilidade da composição. Em seguida, examino sua correspondência com credenciais eleitorais anteriores e com os candidatos eleitos, tomando como referência conjuntos do mesmo tamanho nas mesmas listas.</blockquote><p>“Priorização financeira observada” delimita melhor a interpretação que prioridade deliberada ou expectativa partidária de eleição. O procedimento identifica a posição relativa na distribuição registrada. A investigação sobre quem decidiu os repasses, quando decidiu e com quais expectativas permanece uma pergunta substantiva adicional.</p></section>')

parts.append('<section id="metodo"><h2>9. Fontes, limites de operacionalização e reprodução</h2><p>Universo: 7.630 candidaturas em 2018 e 9.675 em 2022, com 513 eleitos em cada ano. Unidade: partido × UF × eleição. Siglas são as normalizadas no pipeline, sem agregar coligações de 2018 ou federações de 2022. Recursos são nominais de cada campanha; proporções internas são invariantes à escala monetária.</p><p>Credenciais usam a base histórica existente, com ausências preservadas. As colunas n_eleicoes contam vitórias, apesar do nome. A proxy de incumbência é vitória federal no pleito anterior, não exercício efetivo do mandato. Vitórias municipais chegam a 2016 e 2020 nas duas eleições; a flag de votação utiliza todos os anos estritamente anteriores ao ano-alvo, incluindo eleições municipais.</p><p class="caution"><strong>Ponto de mensuração a resolver na redação.</strong> O capítulo menciona Presidência e janelas gerais até 2014/2018. O pipeline disponível não inclui vitória presidencial nas colunas do critério, inclui as eleições municipais anteriores e, na flag de votação, utiliza também cargos majoritários com referência operacional de votos válidos/vagas. Portanto, “10% do QE” é aqui o indicador implementado, não uma equivalência automática a quociente legal para todos os cargos. O relatório documenta essa diferença e não reconstrói o histórico. A interpretação substantiva deve alinhar texto, cargos e janelas antes da versão final da tese.</p><p>O conjunto e seus cortes foram avaliados nas duas eleições disponíveis; isto não estabelece novidade em relação a toda a literatura de mensuração nem validade para outros universos. A contribuição discutida é a explicitação e avaliação do procedimento no capítulo.</p>')
parts.append(f'<p>Reproduzir: <code>python tese/scripts/validacao_mensuracao_top_necr.py</code>. Semente: {SEED}; {B:,} sorteios por eleição/referência; {STRESS} perturbações por lista/intensidade. HTML autossuficiente, com tabelas CSV na pasta <code>tese/resultados-validacao-top-necr</code>.</p>')
for name,frame in [('auditoria_listas_cortes',lists),('auditoria_credenciais',fl)]:
    tables[name]=frame
    frame.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
    parts.append(f'<p><a href="resultados-validacao-top-necr/{name}.csv">Baixar {name}</a> · {len(frame):,} linhas de auditoria.</p>')
parts.append(f'<p><strong>Auditoria:</strong> {len(checks):,} verificações concluídas, incluindo fontes, universos, invariância à ordem, posições, massa financeira, limites dos empates, reprodução da cobertura canônica e médias dos sorteios. A sensibilidade numérica à escala é documentada separadamente.</p></section></main><script>document.querySelectorAll("input[data-table]").forEach(input=>input.addEventListener("input",()=>{{const q=input.value.toLocaleLowerCase("pt-BR");document.querySelectorAll("#"+input.dataset.table+" tbody tr").forEach(row=>row.hidden=!row.textContent.toLocaleLowerCase("pt-BR").includes(q));}}));</script></body></html>')
report=ROOT/'tese/relatorio-validacao-top-necr.html'
report.write_text('\n'.join(parts),encoding='utf-8')
nulls.to_csv(OUT/'sorteios_referencia.csv',index=False,encoding='utf-8-sig')
sources=[rawpath,base,Path(__file__),ROOT/'src/2_gold/cap3_cobertura_top_necr.py',ROOT/'src/1_silver/gerar_rrd.py',ROOT/'tese/03-medindo-coordenacao-intrapartidaria.qmd']
(OUT/'auditoria.json').write_text(json.dumps({'verificacoes':checks,'semente':SEED,'sorteios':B,'perturbacoes':STRESS,'fontes_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'tabelas':list(tables),'graficos':fig_num,'python':sys.version,'pandas':pd.__version__,'numpy':np.__version__},ensure_ascii=False,indent=2),encoding='utf-8')
print(report)
print(internal.to_string(index=False))
print(exante[exante.Perfil.eq(FEATURES['credencial_previa'])].to_string(index=False))
print(external.to_string(index=False))
