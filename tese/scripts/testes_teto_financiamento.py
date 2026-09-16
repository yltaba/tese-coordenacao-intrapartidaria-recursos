"""Teto de gastos, financiamento alternativo e alocação partidária.
Reprodução: python tese/scripts/testes_teto_financiamento.py
"""
from pathlib import Path
import sys
import json
import hashlib
import html
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import plotly.graph_objects as go
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tese/resultados-teto-financiamento'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT/'src/2_gold'))
from cap3_taa_features import norm_partido, N_ELEICOES_COLS, acertos_fracionarios
from financiamento_alternativo_top_necr import membership

KEY = ['ano_eleicao','sg_uf','nr_candidato']
LIST = ['ano_eleicao','sg_uf','sg_partido_norm']
CAP = {2018:2500000., 2022:3176572.53}
SOURCES = {
    'Tetos 2018 e 2022 — anexo da Portaria TSE 647/2022': 'https://sintse.tse.jus.br/documentos/2022/Jul/19/diario-da-justica-eletronico-tse-edicao-extraordinaria/anexo-portaria-no-647-de-12-de-julho-de-2022-divulga-os-limites-de-gastos-nas-campanhas-eleitorais-d',
    'TSE — Resolução 23.704/2022': 'https://www.tse.jus.br/legislacao/compilada/res/2022/resolucao-no-23-704-de-30-de-junho-de-2022',
    'TRE-MG — teto de deputado federal em 2022': 'https://www.tre-mg.jus.br/comunicacao/noticias/2022/Julho/eleicoes-2022-tse-divulga-limites-de-gastos-nas-campanhas-666390',
    'TRE-PR — teto de deputado federal em 2018': 'https://www.tre-pr.jus.br/comunicacao/noticias/2018/Junho/tse-publica-limite-de-gastos',
}
LABEL = {'outros':'Não partidários (amplo)','privado':'Próprios + pessoas físicas'}
CTRL = ['vitoria_previa','qe_previo','lag','lag2','hist_ausente','lag_ausente','mulher','negra','demografia_ausente']
CHECKS = {}


def check(name, ok):
    CHECKS[name] = bool(ok)
    assert ok, name


def fit(g, outcome, predictor, controls=(), weight=None, fe=True):
    """WLS within transform, CR1 cluster covariance with absorbed FE degrees."""
    g = g.copy()
    g['_weight'] = 1. if weight is None else np.asarray(weight)
    g = g[g._weight.gt(0)].reset_index(drop=True)
    w = g._weight.to_numpy(float)
    codes, labels = pd.factorize(pd.MultiIndex.from_frame(g[LIST]))
    G, n = len(labels), len(g)
    names = [predictor] + list(controls)
    X = g[names].to_numpy(float)
    y = g[outcome].to_numpy(float)
    if fe:
        sw = np.bincount(codes, weights=w)
        X = X - np.column_stack([np.bincount(codes, weights=w*X[:,j])/sw for j in range(X.shape[1])])[codes]
        y = y - (np.bincount(codes, weights=w*y)/sw)[codes]
    else:
        X = np.column_stack([X, np.ones(n)])
        names += ['constant']
    # Preserve the focal predictor, then omit only linearly dependent controls.
    kept = []
    for j in range(X.shape[1]):
        if np.linalg.matrix_rank(X[:,kept+[j]], tol=1e-9) > len(kept):
            kept.append(j)
    assert 0 in kept, 'Preditor sem variação identificadora'
    X = X[:,kept]
    retained = [names[j] for j in kept]
    xw, yw = X*np.sqrt(w[:,None]), y*np.sqrt(w)
    inv = np.linalg.inv(xw.T@xw)
    beta = np.linalg.lstsq(xw,yw,rcond=None)[0]
    residual = y-X@beta
    score = np.zeros((G,len(kept)))
    np.add.at(score,codes,X*(w*residual)[:,None])
    p = len(kept)+(G if fe else 0)
    covariance = inv@(score.T@score)@inv * (G/(G-1))*((n-1)/(n-p))
    se = float(np.sqrt(covariance[0,0]))
    b = float(beta[0])
    cv = stats.t.ppf(.975,G-1)
    variation = g.groupby(LIST)[predictor].agg(lambda v: v.max()-v.min()).gt(1e-12).sum()
    result = dict(N=n, N_ponderado=float(w.sum()), Listas=G, Listas_variacao_X=int(variation),
                  Beta=b, EP=se, IC_inf=b-cv*se, IC_sup=b+cv*se,
                  p_bilateral=2*stats.t.sf(abs(b/se),G-1),
                  Controles_retidos='; '.join(retained[1:]))
    return result


def weighted_quantile(x,w,q):
    ix = np.argsort(x)
    x,w = np.asarray(x)[ix],np.asarray(w)[ix]
    return float(x[np.searchsorted(np.cumsum(w),q*w.sum(),side='left')])


def build():
    d = pd.read_parquet(ROOT/'data/processed/rrd_df_novo.parquet')
    d = d[d.ano_eleicao.isin(CAP)].copy().reset_index(drop=True)
    d['sg_partido_norm'] = d.sg_partido.map(norm_partido)
    check('Candidatos únicos',not d.duplicated(KEY).any())
    check('513 eleitos por ano',d.groupby('ano_eleicao').eleito.sum().eq(513).all())
    rec = pd.read_parquet(ROOT/'data/processed/receitas.parquet')
    rec = rec[rec.ano_eleicao.isin(CAP) & rec.ds_cargo.eq('DEPUTADO FEDERAL')].copy()
    check('Todas as receitas têm data',rec.dt_receita.notna().all())
    rec['partido'] = np.where(rec.ds_origem_receita.eq('Recursos de partido político'),rec.vr_receita,0.)
    rec['outros'] = rec.vr_receita-rec.partido
    rec['privado'] = np.where(rec.ds_origem_receita.isin(['Recursos próprios','Recursos de pessoas físicas']),rec.vr_receita,0.)
    aggregates = rec.groupby(KEY)[['partido','outros','privado']].sum().reset_index()
    d = d.merge(aggregates,on=KEY,how='left',validate='one_to_one')
    d[['partido','outros','privado']] = d[['partido','outros','privado']].fillna(0)
    check('Partidário reconciliado',np.allclose(d.partido,d.vr_receita_recursos_partidos.fillna(0)))
    check('Não partidário reconciliado',np.allclose(d.outros,d.vr_receita_outros.fillna(0)))
    check('Valores não negativos',d[['partido','outros','privado']].ge(0).all().all())
    d['teto'] = d.ano_eleicao.map(CAP)
    for c in ['partido','outros','privado']:
        d[c+'_pct'] = 100*d[c]/d.teto
    d['total_pct'] = d.partido_pct+d.outros_pct
    for rule in ['piso','arredondado','teto']:
        d['top_'+rule] = 0.
    d['lista_sem_recursos'] = False
    for _,g in d.groupby(LIST):
        v = g.partido.to_numpy(float)
        necr = v.sum()**2/(v@v) if v.sum() else np.nan
        d.loc[g.index,'lista_sem_recursos'] = not bool(v.sum())
        for rule,value in [('piso',np.floor(necr)),('arredondado',np.floor(necr+.5)),('teto',np.ceil(necr))]:
            k = max(1,int(value)) if np.isfinite(value) else 0
            w = membership(v,k)
            d.loc[g.index,'top_'+rule] = w
            assert np.isclose(w.sum(),min(k,len(v)))
            assert np.isclose(w@g.eleito,acertos_fracionarios(v,g.eleito,k) if k else 0)
    check('Cobertura original 2018',np.isclose(d.loc[d.ano_eleicao.eq(2018),'top_arredondado']@d.loc[d.ano_eleicao.eq(2018),'eleito'],445))
    check('Cobertura original 2022',np.isclose(d.loc[d.ano_eleicao.eq(2022),'top_arredondado']@d.loc[d.ano_eleicao.eq(2022),'eleito'],475.1923076923))
    d['fora'] = 1-d.top_arredondado
    d['hist_ausente'] = d[N_ELEICOES_COLS+['alcancou_10pct_qe_hist']].isna().any(axis=1).astype(int)
    d['vitoria_previa'] = d[N_ELEICOES_COLS].fillna(0).sum(axis=1).gt(0).astype(int)
    d['qe_previo'] = d.alcancou_10pct_qe_hist.fillna(False).astype(int)
    d['competitivo'] = d.vitoria_previa.eq(1)|d.qe_previo.eq(1)
    d['lag_ausente'] = d.prop_votos_nominais_lag_candidato.isna().astype(int)
    d['lag'] = d.prop_votos_nominais_lag_candidato.fillna(0)
    d['lag2'] = d.lag**2
    d['demografia_ausente'] = d[['mulher','negra']].isna().any(axis=1).astype(int)
    d[['mulher','negra']] = d[['mulher','negra']].fillna(0)
    # Temporal split: early recorded receipts through Aug 31; later Sep 1–30.
    month = rec.dt_receita.dt.month
    same_year = rec.dt_receita.dt.year.eq(rec.ano_eleicao)
    temporal_audit = []
    for suffix,mask in [('antes',same_year & month.lt(9)),('setembro',same_year & month.eq(9))]:
        a = rec[mask].groupby(KEY)[['partido','outros','privado']].sum().add_suffix('_'+suffix).reset_index()
        d = d.merge(a,on=KEY,how='left',validate='one_to_one')
        for col in ['partido','outros','privado']:
            name = col+'_'+suffix
            d[name] = d[name].fillna(0)
            d[name+'_pct'] = 100*d[name]/d.teto
        for year,g in rec.groupby('ano_eleicao'):
            temporal_audit.append(dict(Ano=year,Janela=suffix,Registros=int(mask.loc[g.index].sum()),Valor=g.loc[mask.loc[g.index],'vr_receita'].sum()))
    pd.DataFrame(temporal_audit).to_csv(OUT/'janelas_temporais.csv',index=False,encoding='utf-8-sig')
    return d


def main():
    d = build()
    descriptive, tests, slopes, temporal, robustness, thresholds = [],[],[],[],[],[]
    for year,g in d.groupby('ano_eleicao'):
        for metric in ['outros','privado']:
            y = metric+'_pct'
            for comp,sub in [('Todos',g),('Competitivos prévios',g[g.competitivo]),('Sem credencial prévia',g[~g.competitivo])]:
                for elected in [0,1]:
                    a = sub[sub.eleito.eq(elected)&sub.fora.gt(0)]
                    w = a.fora.to_numpy()
                    descriptive.append(dict(Ano=year,Fonte=LABEL[metric],Estrato=comp,Eleito=elected,
                         N=len(a),N_ponderado=w.sum(),Media_pct=np.average(a[y],weights=w),
                         Mediana_pct=weighted_quantile(a[y],w,.5),P90_pct=weighted_quantile(a[y],w,.9)))
            for spec,controls,fe in [('Bruto',[],False),('Ajustado por lista e histórico',CTRL,True)]:
                r = fit(g,y,'eleito',controls,g.fora,fe)
                tests.append(dict(Ano=year,Fonte=LABEL[metric],Modelo=spec,**r))
            for spec,sub in [('Todas as candidaturas',g),('Só competitivos prévios',g[g.competitivo])]:
                r = fit(sub,'partido_pct',y,CTRL)
                slopes.append(dict(Ano=year,Fonte=LABEL[metric],Modelo=spec,**r))
            r = fit(g,'partido_setembro_pct',metric+'_antes_pct',CTRL+['partido_antes_pct'])
            temporal.append(dict(Ano=year,Fonte=LABEL[metric],**r))
            for rule in ['piso','arredondado','teto']:
                sub = g.copy()
                w = 1-sub['top_'+rule]
                r = fit(sub,y,'eleito',CTRL,w)
                robustness.append(dict(Teste='T1',Ano=year,Fonte=LABEL[metric],Variante='Top '+rule,**r))
            for label,mask in [('Sem empates no corte',g.top_arredondado.isin([0,1])),('Sem listas zeradas',~g.lista_sem_recursos),('Receita total ≤ 100% teto',g.total_pct.le(100)),('Histórico observado',g.hist_ausente.eq(0)&g.lag_ausente.eq(0))]:
                sub=g[mask]
                robustness.append(dict(Teste='T1',Ano=year,Fonte=LABEL[metric],Variante=label,**fit(sub,y,'eleito',CTRL,sub.fora)))
                robustness.append(dict(Teste='T2',Ano=year,Fonte=LABEL[metric],Variante=label,**fit(sub,'partido_pct',y,CTRL)))
            # Fixed external thresholds and proximity to ceiling, among elected outsiders.
            a = g[g.eleito.eq(1)&g.fora.gt(0)]
            for cutoff in [10,25,50]:
                mask=a[y].ge(cutoff)
                thresholds.append(dict(Ano=year,Fonte=LABEL[metric],Corte_pct=cutoff,
                    N_fora_alto=float(a.loc[mask,'fora'].sum()),
                    Parcela_fora_pct=100*a.loc[mask,'fora'].sum()/a.fora.sum(),
                    N_fora_alto_total80=float(a.loc[mask&a.total_pct.ge(80),'fora'].sum())))
    desc,t1,t2,t3,rob,thr = map(pd.DataFrame,[descriptive,tests,slopes,temporal,robustness,thresholds])
    for frame,mask in [(t1,t1.Modelo.eq('Ajustado por lista e histórico')),(t2,t2.Modelo.eq('Todas as candidaturas')),(t3,np.ones(len(t3),bool))]:
        frame.loc[mask,'p_Holm'] = multipletests(frame.loc[mask,'p_bilateral'],method='holm')[1]
    # Verify within estimator against explicit FE dummies on a bounded real subset.
    sub = d[d.ano_eleicao.eq(2018)].copy()
    ids = sub.groupby(LIST).ngroup()
    sub=sub[ids.lt(20)].copy()
    r=fit(sub,'partido_pct','privado_pct',[],fe=True)
    dummy=pd.get_dummies(sub.groupby(LIST).ngroup(),dtype=float)
    X=pd.concat([sub[['privado_pct']].reset_index(drop=True),dummy.reset_index(drop=True)],axis=1)
    reference=sm.OLS(sub.partido_pct.to_numpy(),X.to_numpy()).fit(cov_type='cluster',cov_kwds={'groups':sub.groupby(LIST).ngroup().to_numpy()})
    check('Coeficiente FE reproduz dummies explícitas',np.isclose(r['Beta'],reference.params[0]))
    check('Erro padrão cluster reproduz dummies explícitas',np.isclose(r['EP'],reference.bse[0]))
    sub = sub[sub.fora.gt(0)].copy()
    r = fit(sub,'partido_pct','privado_pct',[],sub.fora,True)
    dummy = pd.get_dummies(sub.groupby(LIST).ngroup(),dtype=float)
    X = pd.concat([sub[['privado_pct']].reset_index(drop=True),dummy.reset_index(drop=True)],axis=1)
    reference = sm.WLS(sub.partido_pct.to_numpy(),X.to_numpy(),weights=sub.fora.to_numpy()).fit(cov_type='cluster',cov_kwds={'groups':sub.groupby(LIST).ngroup().to_numpy()})
    check('Coeficiente ponderado reproduz WLS com dummies',np.isclose(r['Beta'],reference.params[0]))
    check('EP ponderado reproduz WLS com dummies',np.isclose(r['EP'],reference.bse[0]))
    sub=d[d.ano_eleicao.eq(2018)].copy()
    r1=fit(sub,'privado_pct','eleito',[],sub.fora,False)
    sub['privado_reais']=sub.privado
    r2=fit(sub,'privado_reais','eleito',[],sub.fora,False)
    check('Normalizar pelo teto preserva estatística t',np.isclose(r1['Beta']/r1['EP'],r2['Beta']/r2['EP']))
    exports={'descritivos.csv':desc,'teste1_eleitos_fora.csv':t1,'teste2_alocacao.csv':t2,'teste3_temporal.csv':t3,'robustez.csv':rob,'limiares_teto.csv':thr}
    for f,frame in exports.items():
        frame.to_csv(OUT/f,index=False,encoding='utf-8-sig')
    cols=KEY+['nm_candidato','sg_partido_norm','eleito','competitivo','teto','partido','outros','privado','partido_pct','outros_pct','privado_pct','total_pct','fora','top_piso','top_arredondado','top_teto']+CTRL+['partido_antes_pct','partido_setembro_pct','privado_antes_pct','outros_antes_pct']
    d[cols].to_csv(OUT/'candidatos.csv',index=False,encoding='utf-8-sig')
    audit={'checks':CHECKS,'fontes':SOURCES,'consulta_fontes':'2026-09-11','tetos':CAP,
      'N':len(d),'historico_ausente':int(d.hist_ausente.sum()),'lag_ausente':int(d.lag_ausente.sum()),
      'sha256':{f:hashlib.sha256((ROOT/'data/processed'/f).read_bytes()).hexdigest() for f in ['rrd_df_novo.parquet','receitas.parquet']}}
    (OUT/'verificacao.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    render(d,desc,t1,t2,t3,rob,thr,exports)
    print(t1.to_string(index=False)); print(t2.to_string(index=False)); print(t3.to_string(index=False))
    print(OUT/'testes-teto-financiamento.html')


def number(x,digits=2):
    return f'{x:,.{digits}f}'.replace(',','X').replace('.',',').replace('X','.')


def table(frame):
    frame=frame.copy()
    for col in frame.select_dtypes(include='number'):
        if col in ['Ano','ano_eleicao','Eleito','N','Listas','Listas_variacao_X','Candidatos','Receita_total_acima_teto','Privado_acima_teto','Competitivos','Hist_ausente','Lag_ausente']:
            frame[col]=frame[col].map(lambda x:str(int(x)) if pd.notna(x) else '—')
        else:
            frame[col]=frame[col].map(lambda x: ('<0,0001' if col.startswith('p_') and pd.notna(x) and x<.0001 else number(x,4 if col.startswith('p_') else 2)) if pd.notna(x) else '—')
    for col in frame.select_dtypes(include='bool'):
        frame[col]=frame[col].map({True:'Sim',False:'Não'})
    frame=frame.rename(columns={'ano_eleicao':'Ano','sg_uf':'UF','sg_partido_norm':'Partido','nm_candidato':'Nome','competitivo':'Competitivo prévio','fora':'Peso fora','privado_pct':'Privado / teto (%)','outros_pct':'Não partidário / teto (%)','partido_pct':'Partidário / teto (%)','total_pct':'Total / teto (%)','N_ponderado':'N ponderado','Listas_variacao_X':'Listas com variação em X','Media_pct':'Média (%)','Mediana_pct':'Mediana (%)','P90_pct':'P90 (%)','IC_inf':'IC95 inferior','IC_sup':'IC95 superior','p_bilateral':'p bilateral','p_Holm':'p Holm','Corte_pct':'Corte (% teto)','N_fora_alto':'Peso fora acima do corte','Parcela_fora_pct':'% dos eleitos fora','N_fora_alto_total80':'Peso também com total ≥80%'})
    return '<div class="scroll">'+frame.to_html(index=False,border=0,escape=True)+'</div>'


def render(d,desc,t1,t2,t3,rob,thr,exports):
    p=['''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Teto de gastos e financiamento alternativo</title><style>
*{box-sizing:border-box}body{margin:0;background:#eff3f6;color:#172a3c;font:16px/1.65 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:28px 22px 65px}header{padding:42px;background:#142c44;color:white;border-radius:18px}h1{font-size:39px;line-height:1.18;margin:15px 0}h2{font-size:27px;line-height:1.25;margin:0 0 18px}h3{font-size:20px}.lead{font-size:20px}section{background:white;border-radius:15px;padding:30px;margin-top:24px}.note{font-size:14px;color:#52667a}.callout{background:#edf8f5;border-left:5px solid #148879;padding:18px;margin:18px 0}.warn{background:#fff6e7;border-color:#cc8a26}nav{margin-top:25px}nav a{margin-right:18px;color:#bce9f3}a{color:#126486}a,code{overflow-wrap:anywhere}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:11px;text-align:left;border-bottom:1px solid #dce5ed}th{background:#eef3f7}details{margin:20px 0}input{padding:12px;border:1px solid #9cafbf;border-radius:8px;width:min(100%,500px)}.equation{padding:20px;background:#f1f5fa;font:18px/1.7 ui-monospace,monospace;overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.metric{padding:20px;background:#f2f6fa;border-radius:12px}.metric strong{font-size:28px;display:block}@media(max-width:650px){header,section{padding:20px}h1{font-size:29px}.grid{grid-template-columns:1fr}}@media print{body{background:white}header{background:white;color:#172a3c}nav,input{display:none}section{break-inside:avoid}}
</style></head><body><main><header><p>CAPÍTULO 3 · DIAGNÓSTICO DE FINANCIAMENTO</p><h1>O teto de gastos muda a leitura dos eleitos fora do Top-NECr?</h1><p class="lead">Duas perguntas distintas: os vencedores fora do núcleo têm mais recursos alternativos? E a capacidade privada se associa a menos financiamento partidário, dadas as credenciais anteriores?</p><nav><a href="#sintese">Resultados</a><a href="#t1">Teste 1</a><a href="#t2">Teste 2</a><a href="#tempo">Sequência temporal</a><a href="#casos">Casos</a><a href="#metodo">Método</a></nav></header>''']
    p.append('<section id="sintese"><h2>O que cada teste permite concluir</h2>')
    for year in [2018,2022]:
        a=desc[desc.Ano.eq(year)&desc.Fonte.eq(LABEL['outros'])&desc.Estrato.eq('Todos')].set_index('Eleito')
        b=t1[t1.Ano.eq(year)&t1.Fonte.eq(LABEL['outros'])&t1.Modelo.str.startswith('Ajustado')].iloc[0]
        c=t2[t2.Ano.eq(year)&t2.Fonte.eq(LABEL['privado'])&t2.Modelo.eq('Todas as candidaturas')].iloc[0]
        p.append(f'<div class="callout"><strong>{year} · Fora do Top-NECr:</strong> a média de recursos não partidários equivale a {number(a.loc[1,"Media_pct"])}% do teto entre eleitos e {number(a.loc[0,"Media_pct"])}% entre não eleitos. Com ajuste por nominata e histórico, a diferença é {number(b.Beta)} pontos percentuais (IC95% {number(b.IC_inf)} a {number(b.IC_sup)}).</div>')
        p.append(f'<p><strong>Alocação partidária em {year}:</strong> mais 10 pontos percentuais de cobertura privada/própria se associam a {number(10*c.Beta)} pontos percentuais de financiamento partidário, após os ajustes (IC95% {number(10*c.IC_inf)} a {number(10*c.IC_sup)}). O sinal esperado para substituição seria negativo.</p>')
    p.append('<div class="callout warn"><strong>Resultado central: capacidade alternativa entre vencedores, sem evidência de substituição partidária nos modelos estimados.</strong> O Teste 1 é positivo nos dois anos, inclusive após ajuste e correção de Holm (p &lt; 0,0001). No Teste 2, os coeficientes são positivos no universo completo; entre competitivos prévios, os intervalos incluem zero. O teste temporal também é inconclusivo. Isso qualifica os casos fora do indicador, mas não demonstra que o partido deliberadamente completou o orçamento dessas candidaturas.</div><p>A confirmação do primeiro padrão, isoladamente, mostra que o indicador deixa de capturar alguns vencedores com recursos alternativos. Não demonstra que o partido reduziu transferências por conhecer essa capacidade. O segundo teste examina uma implicação mais exigente da hipótese, ainda como associação observacional.</p></section>')
    p.append('<section><h2>Uma escala externa, sem redefinir prioridade</h2><div class="grid"><div class="metric">Teto de deputado federal · 2018<strong>R$ 2.500.000,00</strong></div><div class="metric">Teto de deputado federal · 2022<strong>R$ 3.176.572,53</strong></div></div><div class="equation">Cobertura alternativa = 100 × recursos não partidários / teto<br>Cobertura partidária = 100 × recursos partidários / teto</div>')
    p.append('<p>Os tetos são iguais em todas as UFs dentro de cada ano. Dividir por eles preserva rankings e estatísticas t em comparações anuais equivalentes; o ganho é interpretar valores em uma escala externa à nominata. Não há variação intranual do teto que permita identificar seu efeito causal.</p><p>O teto regula <strong>gastos</strong>, enquanto o numerador aqui mede <strong>receitas registradas</strong>. Receita/teto pode superar 100%, por exemplo com transferências e recursos não gastos, sem que este cálculo constitua diagnóstico de infração. Não se impõe artificialmente o limite de 100% aos dados, nem se define “necessidade” como 100 menos a cobertura: essa operação produziria uma relação negativa por construção.</p><p class="note">Valores: <a href="'+SOURCES['Tetos 2018 e 2022 — anexo da Portaria TSE 647/2022']+'">anexo oficial da Portaria TSE 647/2022</a>. A <a href="'+SOURCES['TSE — Resolução 23.704/2022']+'">Resolução 23.704/2022</a> estabelece a atualização dos limites de 2018.</p></section>')
    p.append('<section id="t1"><h2>Teste 1 · Vencedores e perdedores fora do núcleo</h2><div class="equation">E[cobertura alternativa | eleito, fora] &gt; E[cobertura alternativa | não eleito, fora]</div><p>O teste bruto compara médias ponderadas pelo peso fora do Top-NECr. O teste ajustado estima cobertura = efeito da nominata + β × eleito + histórico e características observadas. β mede a diferença condicional em pontos percentuais do teto; não mede o efeito causal de ser eleito.</p>')
    chart=go.Figure()
    for winner,color in [(0,'#adbdcd'),(1,'#148879')]:
        a=desc[desc.Estrato.eq('Todos')&desc.Eleito.eq(winner)]
        chart.add_bar(name='Eleitos' if winner else 'Não eleitos',x=[str(r.Ano)+' · '+r.Fonte for _,r in a.iterrows()],y=a.Media_pct,marker_color=color,text=[number(v)+'%' for v in a.Media_pct],textposition='outside')
    chart.update_layout(template='plotly_white',barmode='group',height=450,yaxis_title='Receitas / teto (%)',legend_orientation='h',margin=dict(t=35,b=95),yaxis_rangemode='tozero')
    p.append(chart.to_html(full_html=False,include_plotlyjs=True,config={'displaylogo':False,'responsive':True}))
    p.append(table(t1.drop(columns=['Controles_retidos'])))
    p.append('<p class="note">No recorte fora do núcleo, apenas 40 nominatas em 2018 e 26 em 2022 contêm tanto eleitos como não eleitos com peso positivo. São elas que oferecem contraste direto de resultado dentro da lista; as demais ajudam a estimar os controles. A coluna Listas_variacao_X explicita esse suporte limitado, apesar do grande número total de candidaturas.</p>')
    p.append('<h3>A comparação dentro dos estratos de competitividade anterior</h3><p>“Competitivo prévio” segue a base canônica: vitória anterior em cargo diferente de vereador ou alcance histórico de 10% do quociente eleitoral. Ausência dessa credencial não equivale a inviabilidade. As credenciais são anteriores ao pleito, mas não observam diretamente a expectativa do partido.</p>'+table(desc)+'<p class="note">N é a quantidade de registros com peso positivo; N_ponderado é a soma dos pesos fora, preservando empates fracionários. Mediana e P90 também são ponderados.</p></section>')
    p.append('<section id="t2"><h2>Teste 2 · Capacidade privada e alocação partidária</h2><div class="equation">Partidário/teto = efeito da nominata + β × alternativo/teto + controles históricos</div><p>A expectativa de substituição exige β &lt; 0. O modelo principal usa todas as candidaturas, sem selecionar pelo resultado eleitoral ou pelo Top-NECr, que já é função do financiamento partidário. O modelo restrito a competitivos prévios verifica se o padrão permanece entre candidaturas com credenciais anteriores. Não se controla o total arrecadado: por ser a soma das fontes, isso induziria uma relação negativa contábil.</p>')
    display=t2.drop(columns=['Controles_retidos']).copy()
    for c in ['Beta','EP','IC_inf','IC_sup']:display[c]*=10
    p.append('<p><strong>Escala da tabela:</strong> variação da cobertura partidária (p.p.) associada a +10 p.p. de cobertura alternativa. Os CSVs preservam os coeficientes por +1 p.p.</p>'+table(display))
    fig=go.Figure()
    for year,color in [(2018,'#148879'),(2022,'#c4812b')]:
        z=display[display.Ano.eq(year)]
        fig.add_scatter(x=z.Beta,y=[r.Fonte+' · '+r.Modelo for _,r in z.iterrows()],mode='markers',name=str(year),marker=dict(size=11,color=color),error_x=dict(type='data',array=z.IC_sup-z.Beta,arrayminus=z.Beta-z.IC_inf))
    fig.add_vline(x=0,line_dash='dot')
    fig.update_layout(template='plotly_white',height=400,xaxis_title='Δ cobertura partidária (p.p.) por +10 p.p. alternativos',margin=dict(l=30,r=25,t=30,b=50),legend_orientation='h')
    p.append(fig.to_html(full_html=False,include_plotlyjs=False,config={'displaylogo':False,'responsive':True}))
    p.append('<p>Um coeficiente positivo é compatível com candidaturas que captam mais de ambas as fontes; não confirma substituição no agregado. Um coeficiente negativo seria compatível com complementação até um orçamento, mas também com seleção e restrições contábeis. Nenhum dos sinais, sozinho, identifica a decisão da liderança.</p></section>')
    p.append('<section id="tempo"><h2>Exploração temporal · Recursos anteriores, transferências posteriores</h2><p>A base permite ordenar receitas pela data registrada. A exposição é a cobertura alternativa acumulada de janeiro a agosto do ano eleitoral. O desfecho é o financiamento partidário recebido de 1º a 30 de setembro. Controlam-se financiamento partidário até agosto, histórico e nominata. A janela comum termina antes da votação nos dois anos e não utiliza votos ou eleição corrente como controles.</p><div class="equation">Partidário setembro/teto = efeito da nominata + β × alternativo até agosto/teto + partidário até agosto/teto + histórico</div>')
    z=t3.drop(columns=['Controles_retidos']).copy()
    for c in ['Beta','EP','IC_inf','IC_sup']:z[c]*=10
    p.append('<p>Coeficientes por +10 p.p. de cobertura alternativa anterior:</p>'+table(z))
    p.append('<p class="note">Exploratório: o corte foi escolhido para separar janelas comuns, não como choque exógeno. A data da receita não informa quando houve promessa de doação, negociação ou conhecimento pelo partido. Credenciais anteriores são ex ante; arrecadação até agosto já é uma variável da campanha. Dependência temporal observada não resolve causalidade, e receitas fora das duas janelas não entram neste teste.</p></section>')
    p.append('<section><h2>Quão frequente é o exemplo “50% privados + complementação”?</h2><p>Entre eleitos fora do Top-NECr, contamos cobertura alternativa de pelo menos 10%, 25% e 50% do teto. A última coluna exige também receita total equivalente a pelo menos 80% do teto — uma proximidade ilustrativa, sem tratar receita como gasto efetivo. Esses cortes são diagnósticos descritivos, não novas medidas de prioridade.</p>'+table(thr)+'<p>O mecanismo do teto é mais plausível como restrição ativa nas campanhas que se aproximam dele. Alta arrecadação relativa aos demais candidatos não implica proximidade do teto; os casos abaixo permitem verificar essa diferença.</p></section>')
    p.append('<section><h2>O caso de metade do teto é uma minoria</h2><p>Com a definição estrita de recursos próprios + pessoas físicas, há <strong>5 eleitos fora com cobertura de pelo menos 50% em 2018</strong> (7,35% do peso fora) e <strong>3 em 2022</strong> (7,93%). Exigindo também receita total de pelo menos 80% do teto, restam 2 em 2018 e nenhum em 2022. A explicação por fontes alternativas é mais abrangente que a explicação específica de complementação junto ao teto.</p><p>Esses limiares não provam que o teto era irrelevante nos demais casos: não observamos o orçamento desejado ou a decisão contrafactual do partido. Mas os dados não autorizam apresentar a situação “metade privada, metade partidária até o teto” como descrição típica dos vencedores fora do núcleo.</p></section>')
    p.append('<section id="casos"><h2>Eleitos com algum peso fora do Top-NECr</h2><input id="search" aria-label="Filtrar candidatos" placeholder="Buscar nome, partido, UF ou ano"><p class="note">Coberturas em % do teto. O peso fora varia entre 0 e 1. Competitividade prévia segue as credenciais históricas.</p><div id="cases">')
    cases=d[d.eleito.eq(1)&d.fora.gt(0)].sort_values(['ano_eleicao','privado_pct'],ascending=[True,False])
    p.append(table(cases[['ano_eleicao','sg_uf','sg_partido_norm','nm_candidato','competitivo','fora','privado_pct','outros_pct','partido_pct','total_pct']])+'</div><p>A provocação de Glauco é tratada como argumento sobre o mecanismo. Não se atribui a ele uma candidatura ou um resultado eleitoral.</p></section>')
    p.append('<section><h2>Robustez e observações fora da escala de 100%</h2><p>Reestimamos o Teste 1 com piso e teto do NECr, sem empates fracionários, sem nominatas de recursos zerados, com histórico observado e excluindo receitas totais superiores ao teto. O Teste 2 também recebe as quatro exclusões. São verificações exploratórias; não se escolhe uma especificação por seu p-valor.</p><details><summary>Ver todas as estimativas de robustez (β por +1 p.p. no Teste 2)</summary>'+table(rob.drop(columns=['Controles_retidos']))+'</details>')
    p.append('<p>Nas variantes executadas, os coeficientes do Teste 1 continuam positivos, entre 11,61 e 14,12 p.p. Os coeficientes do Teste 2 com todas as candidaturas também permanecem positivos nas quatro exclusões. A ausência de um sinal agregado de substituição não decorre apenas dos registros acima de 100% do teto.</p>')
    audit=[]
    for year,g in d.groupby('ano_eleicao'):
        audit.append(dict(Ano=year,Candidatos=len(g),Receita_total_acima_teto=int(g.total_pct.gt(100).sum()),Privado_acima_teto=int(g.privado_pct.gt(100).sum()),Eleitos_fora_ponderados=float((g.fora*g.eleito).sum()),Competitivos=int(g.competitivo.sum()),Hist_ausente=int(g.hist_ausente.sum()),Lag_ausente=int(g.lag_ausente.sum())))
    p.append(table(pd.DataFrame(audit))+'</section>')
    p.append('''<section id="metodo"><h2>Método, alcance e reprodução</h2><p><strong>Universo:</strong> candidaturas a deputado federal de 2018 e 2022 na base consolidada. Nominata = partido × UF × ano; federações de 2022 e coligações de 2018 não são reagrupadas. O Top-NECr conserva o ranking financeiro original, arredondamento convencional e empates fracionários. Listas sem recursos têm núcleo vazio.</p><p><strong>Fontes alternativas:</strong> a definição ampla soma todas as origens exceto “Recursos de partido político”, inclusive outros candidatos, rendimentos e origens não identificadas. A definição estrita soma “Recursos próprios” e “Recursos de pessoas físicas”; não inclui financiamento coletivo. A origem declarada não rastreia a fonte última. Zeros incluem ausência de receita registrada conforme o pipeline; não implicam ausência de subdeclaração.</p><p><strong>Controles:</strong> vitória anterior em cargo diferente de vereador; histórico de 10% do QE; participação nominal na lista da eleição anterior, pela identidade do candidato na UF (robusta a migração de partido), e seu quadrado; gênero e raça conforme as flags da base. Ausências são preenchidas com zero e acompanhadas por indicadores. Controles sem variação ou redundantes no modelo são omitidos e registrados nos CSVs. Vitória anterior não é necessariamente mandato em exercício. O código do histórico usa pleitos anteriores ao ano analisado, e nenhuma medida de voto corrente entra nos controles.</p><p><strong>Estimação:</strong> mínimos quadrados com efeitos fixos de nominata, por transformação dentro de cada grupo; no Teste 1, pesos iguais à fração fora do Top-NECr. Erros padrão CR1 agrupados por nominata, com graus de liberdade dos efeitos fixos absorvidos e referência t com G−1 graus. ICs são bilaterais de 95%. Holm corrige quatro testes por família: dois anos × duas fontes, separadamente para T1 ajustado, T2 com todas as candidaturas e o teste temporal. Modelos brutos, restritos e sensibilidades são exploratórios, com p-valores não corrigidos.</p><p><strong>Interpretação:</strong> os dados cobrem o universo observado, e a inferência é baseada no modelo, não em amostragem de eleitores. A competitividade esperada é aproximada por credenciais anteriores; não é observada integralmente. O Teste 1 condiciona à posição financeira e usa o resultado eleitoral ex post. O Teste 2 contemporâneo não distingue causa, seleção ou captação conjunta. O teste temporal melhora a ordenação das receitas, mas não observa o processo decisório. O teto é uma referência externa e não um instrumento causal.</p><h3>Para o argumento do capítulo</h3><p>O diagnóstico pode qualificar a leitura dos “erros” do Top-NECr sem redefinir o indicador para absorvê-los. Demonstrar que vencedores fora do núcleo tinham fontes alternativas é diferente de demonstrar que o partido antecipou essa capacidade e completou sua necessidade. Essa distinção sustenta a exigência de evidências ex ante para interpretar alocação como estratégia, em vez de reconstruir a estratégia apenas a partir dos vencedores.</p><h3>Reprodução e arquivos</h3><p><code>python tese/scripts/testes_teto_financiamento.py</code><br>Fontes locais: <code>data/processed/rrd_df_novo.parquet</code> e <code>data/processed/receitas.parquet</code>. Gráficos incorporados; o HTML funciona sem internet.</p>''')
    p.append('<p>'+' · '.join(f'<a href="{f}">{f}</a>' for f in [*exports,'candidatos.csv','janelas_temporais.csv','verificacao.json'])+'</p><h3>Fontes oficiais dos tetos</h3><ul>'+''.join(f'<li><a href="{url}">{html.escape(label)}</a></li>' for label,url in SOURCES.items())+'</ul><p class="note">Consultadas em 11/09/2026. Os resultados estatísticos são cálculos próprios sobre as bases locais.</p><h3>Verificações executadas</h3>'+table(pd.DataFrame([{'Verificação':k,'Passou':v} for k,v in CHECKS.items()])))
    p.append('</section></main><script>document.getElementById("search").addEventListener("input",function(){const q=this.value.toLocaleLowerCase("pt-BR");document.querySelectorAll("#cases tbody tr").forEach(r=>r.hidden=!r.textContent.toLocaleLowerCase("pt-BR").includes(q));});</script></body></html>')
    (OUT/'testes-teto-financiamento.html').write_text(''.join(p),encoding='utf-8')


if __name__=='__main__':
    main()
