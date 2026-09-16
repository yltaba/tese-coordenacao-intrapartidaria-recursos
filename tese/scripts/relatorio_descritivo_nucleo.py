"""Descrição do núcleo partidário, com abertura explícita por partido.

Usa a base auditada da exploração e confere a cobertura com o pipeline canônico.
Execute: python tese/scripts/relatorio_descritivo_nucleo.py
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
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'tese/old/relatorios-descritivos/resultados-descritivos-nucleo'
OUT.mkdir(exist_ok=True)
BASE = ROOT/'tese/resultados-exploracao-nucleo/base_analitica.csv'
sys.path.insert(0,str(ROOT/'src/2_gold'))
from cap3_cobertura_top_necr import calcular_cobertura_top_necr

checks = {}
def check(label, condition):
    checks[label] = bool(condition)
    assert condition, label

audit = json.loads((BASE.parent/'auditoria.json').read_text(encoding='utf-8'))
for source in ['data/processed/rrd_df_novo.parquet','data/processed/receitas.parquet']:
    check('Fonte inalterada: '+source,hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==audit['fontes_sha256'][source])
d = pd.read_csv(BASE,low_memory=False)
check('Candidaturas únicas',not d.duplicated(['ano_eleicao','sg_uf','nr_candidato']).any())
check('Universos',d.groupby('ano_eleicao').size().tolist()==[7630,9675])
check('Eleitos',d.groupby('ano_eleicao').eleito.sum().eq(513).all())
check('Pesos complementares',np.allclose(d.top+d.fora,1) and d.top.between(0,1).all())
_, canonical=calcular_cobertura_top_necr()
for _,r in canonical.iterrows():
    g=d[d.ano_eleicao.eq(r.ano_eleicao)]
    check(f'Cobertura {r.ano_eleicao} {r.regra_k}',np.isclose(g.eleito@g['top_'+r.regra_k],r.eleitos_top_necr))

LABELS = {
    'reeleicao_proxy':'Eleito federal no pleito anterior',
    'ex_federal_proxy':'Vitória federal mais antiga, sem vitória no pleito anterior',
    'vitoria_estadual':'Vitória anterior para deputado estadual/distrital',
    'vitoria_prefeito':'Vitória anterior para prefeito',
    'vitoria_vereador':'Vitória anterior para vereador',
    'voto_relevante':'Votação histórica ≥ 10% do QE',
    'vitoria_qualquer':'Alguma vitória eleitoral anterior',
    'sem_credencial':'Sem vitória nem votação relevante registrada',
    'mulher':'Mulheres', 'negra':'Pessoas pretas ou pardas',
}
d['acerto']=d.top*d.eleito
l=d.groupby(['ano_eleicao','sg_partido_norm','sg_uf'],as_index=False).agg(
    C=('eleito','size'),E=('eleito','sum'),K=('top','sum'),A=('acerto','sum'),M=('qt_vaga','first'),magnitude=('magnitude','first'))
l['esperado']=l.E*l.K/l.C
l['amplitude']=100*l.K/l.C
l['cobertura']=100*l.A/l.E.replace(0,np.nan)
l['precisao']=100*l.A/l.K.replace(0,np.nan)

def overview(group_cols):
    rows=[]
    for keys,g in l.groupby(group_cols,sort=True):
        keys=keys if isinstance(keys,tuple) else (keys,)
        rows.append(dict(zip(group_cols,keys))|{
            'Listas':len(g),'Listas sem núcleo':int(g.K.eq(0).sum()),'Candidatos':g.C.sum(),
            'Posições no núcleo':g.K.sum(),'Eleitos':g.E.sum(),'Eleitos dentro':g.A.sum(),
            'Eleitos fora':g.E.sum()-g.A.sum(),'Não eleitos dentro':g.K.sum()-g.A.sum(),
            'Amplitude agregada %':100*g.K.sum()/g.C.sum(),
            'Amplitude mediana das listas %':g.amplitude.median(),
            'Cobertura %':100*g.A.sum()/g.E.sum() if g.E.sum() else np.nan,
            'Precisão %':100*g.A.sum()/g.K.sum() if g.K.sum() else np.nan,
            'Lift':g.A.sum()/g.esperado.sum() if g.esperado.sum() else np.nan,
        })
    return pd.DataFrame(rows).rename(columns={'ano_eleicao':'Ano','sg_partido_norm':'Partido','sg_uf':'UF','magnitude':'Magnitude'})

nation=overview(['ano_eleicao'])
party=overview(['ano_eleicao','sg_partido_norm'])
mag=overview(['ano_eleicao','magnitude'])
uf=overview(['ano_eleicao','sg_uf'])

def profiles(frame,group_cols):
    rows=[]
    for keys,g in frame.groupby(group_cols,sort=True):
        keys=keys if isinstance(keys,tuple) else (keys,)
        for feature,label in LABELS.items():
            z=g[g[feature].notna()]
            present=z[feature].eq(1)
            n=present.sum()
            inside=z.loc[present,'top'].sum()
            rows.append(dict(zip(group_cols,keys))|{'Perfil':label,
                'Candidatos com perfil':n,'Perfil no núcleo (ponderado)':inside,
                'Núcleo válido (ponderado)':z.top.sum(),'Ausência no núcleo (ponderada)':g.top.sum()-z.top.sum(),
                'Composição do núcleo %':100*inside/z.top.sum() if z.top.sum() else np.nan,
                'Composição fora %':100*z.loc[present,'fora'].sum()/z.fora.sum() if z.fora.sum() else np.nan,
                'Entrada no núcleo entre candidatos do perfil %':100*inside/n if n else np.nan})
    return pd.DataFrame(rows).rename(columns={'ano_eleicao':'Ano','sg_partido_norm':'Partido'})

national_profiles=profiles(d,['ano_eleicao'])
party_profiles=profiles(d,['ano_eleicao','sg_partido_norm'])
quad=[]
quad_profiles=[]
for year,g in d.groupby('ano_eleicao'):
    for name,w in [('Núcleo · eleito',g.top*g.eleito),('Núcleo · não eleito',g.top*(1-g.eleito)),('Fora · eleito',g.fora*g.eleito),('Fora · não eleito',g.fora*(1-g.eleito))]:
        quad.append({'Ano':year,'Grupo':name,'Candidaturas ponderadas':w.sum()})
        for f,label in LABELS.items():
            valid=g[f].notna()
            n=w[valid].sum()
            quad_profiles.append({'Ano':year,'Grupo':name,'Perfil':label,'N válido ponderado':n,
                                  'Ausência ponderada':w[~valid].sum(),
                                  'Percentual':100*(w[valid]@g.loc[valid,f])/n if n else np.nan})
quad=pd.DataFrame(quad)
quad_profiles=pd.DataFrame(quad_profiles)

def quantile(x,w,q):
    x,w=np.asarray(x,float),np.asarray(w,float)
    valid=np.isfinite(x)&(w>0)
    x,w=x[valid],w[valid]
    if not len(x):return np.nan
    order=np.argsort(x)
    return x[order][np.searchsorted(np.cumsum(w[order]),q*w.sum(),side='left')]

money=[]
money_party=[]
sources={'vr_receita_recursos_partidos':'Partidários','proprios':'Próprios','pessoas_fisicas':'Pessoas físicas','privado_proprio':'Próprios + pessoas físicas'}
e=d[d.eleito.eq(1)].copy()
e['outras_fontes']=e.vr_receita_outros.fillna(0)-e.privado_proprio
check('Outras receitas reconciliadas',e.outras_fontes.ge(-0.01).all())
e['outras_fontes']=e.outras_fontes.clip(lower=0)
e['total']=e.vr_receita_recursos_partidos+e.vr_receita_outros.fillna(0)
shares=[]
for year,g in e.groupby('ano_eleicao'):
    for group,weight in [('Dentro','top'),('Fora','fora')]:
        w=g[weight]
        for col,label in sources.items():
            money.append({'Ano':year,'Grupo':group,'Fonte':label,'Eleitos ponderados':w.sum(),
                          'P25 R$':quantile(g[col],w,.25),'Mediana R$':quantile(g[col],w,.5),'P75 R$':quantile(g[col],w,.75),
                          'Com receita positiva %':100*w[g[col]>0].sum()/w.sum()})
        total=g.total@w
        for col,label in list(sources.items())[:3]+[('outras_fontes','Outras origens')]:
            shares.append({'Ano':year,'Grupo':group,'Fonte':label,'Participação nos recursos do grupo %':100*(g[col]@w)/total})
for (year,p),g in e.groupby(['ano_eleicao','sg_partido_norm']):
    for group,weight in [('Dentro','top'),('Fora','fora')]:
        w=g[weight]
        money_party.append({'Ano':year,'Partido':p,'Grupo':group,'Eleitos ponderados':w.sum(),
                            'Mediana próprios R$':quantile(g.proprios,w,.5),
                            'Mediana pessoas físicas R$':quantile(g.pessoas_fisicas,w,.5),
                            'Mediana privados/próprios R$':quantile(g.privado_proprio,w,.5)})
money=pd.DataFrame(money)
shares=pd.DataFrame(shares)
money_party=pd.DataFrame(money_party)

tables={}
def table(frame,name,search=False):
    tables[name]=frame
    frame.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
    control=f'<label class="filter">Filtrar esta tabela <input type="search" data-table="tbl-{name}" placeholder="Digite partido, ano ou perfil"></label>' if search else ''
    return control+f'<div class="scroll" tabindex="0">'+frame.to_html(index=False,border=0,table_id='tbl-'+name,na_rep='—',float_format=lambda x:f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X','.'))+f'</div><p class="download"><a href="resultados-descritivos-nucleo/{name}.csv">Baixar tabela CSV</a></p>'

fig_num=0
def chart(f):
    global fig_num
    fig_num+=1
    f.update_layout(template='plotly_white',font=dict(family='Arial',size=13),margin=dict(l=25,r=25,t=65,b=40))
    return f.to_html(full_html=False,include_plotlyjs=True if fig_num==1 else False,div_id=f'desc-fig-{fig_num}',config={'displaylogo':False,'responsive':True})

parts=['''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>O núcleo partidário: uma descrição por partido</title><style>
body{margin:0;background:#f3f5f7;color:#233447;font:17px/1.65 system-ui}main{max-width:1250px;margin:auto;padding:25px 18px 60px}header{background:#173c4c;color:white;padding:36px;border-radius:16px}h1{font-size:38px;line-height:1.2}h2{line-height:1.3}h3{margin-top:30px}section{background:white;padding:28px;margin-top:24px;border-radius:14px}nav{display:flex;flex-wrap:wrap;gap:16px}a{color:#006984}header a{color:#bdf5f0}.note{background:#edf6f5;border-left:4px solid #218579;padding:16px}.scroll{overflow:auto;max-height:720px;border:1px solid #dbe3e8}table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:9px;border-bottom:1px solid #dbe3e8;text-align:left}th{background:#eaf1f5;position:sticky;top:0}input,select{padding:10px;font:inherit;border:1px solid #97acb7;border-radius:5px}.filter{display:block;margin:16px 0}.download{font-size:14px}.year-controls{margin:18px 0}code{overflow-wrap:anywhere}.plot-container{min-width:0}@media(max-width:650px){h1{font-size:29px}header,section{padding:18px}}@media print{body{background:white}header{background:white;color:#233447}.scroll{max-height:none}input,nav,.year-controls{display:none}.year-panel{display:block!important}section{break-inside:avoid}}
</style></head><body><main><header><p>CAPÍTULO 3 · RELATÓRIO DESCRITIVO</p><h1>O núcleo partidário: composição, diferenças entre partidos e correspondência eleitoral</h1><p>Deputado federal · 2018 e 2022</p><nav><a href="#panorama">Panorama</a><a href="#partidos">Abertura por partido</a><a href="#composicao">Composição</a><a href="#territorio">Magnitude e UF</a><a href="#grupos">Dentro e fora</a><a href="#receitas">Receitas dos eleitos</a><a href="#metodo">Definições</a></nav></header>''']

parts.append('<section id="panorama"><h2>1. O núcleo e seu lugar nas nominatas</h2><p>Este relatório aprofunda a descrição do capítulo: quem aparece no núcleo de financiamento, como os padrões variam entre partidos e territórios e quais candidaturas se elegem dentro ou fora dele. As comparações são apresentadas em contagens, proporções e distribuições.</p>')
parts.append(table(nation,'panorama'))
parts.append('<p>O núcleo passa de 2.318 para 3.824 posições. Sua cobertura dos eleitos aumenta de 86,7% para 92,6%, enquanto a precisão diminui de 19,2% para 12,4%. A ampliação incorpora mais eleitos e também mais candidaturas que não se elegem.</p><p class="note"><strong>Três perguntas distintas.</strong> Amplitude: qual parcela dos candidatos entra no núcleo? Cobertura: qual parcela dos eleitos está no núcleo? Precisão: qual parcela do núcleo se elege? O lift compara os eleitos observados no núcleo com o número esperado por sorteio do mesmo tamanho dentro de cada lista.</p></section>')

parts.append('<section id="partidos"><h2>2. Abertura por partido</h2><p>A unidade de construção do núcleo continua sendo partido × UF × eleição. Aqui somamos seus componentes para descrever cada partido nacionalmente. Todos os partidos aparecem em ordem alfabética, inclusive os que não elegeram deputados. O seletor alterna as duas eleições nos gráficos desta seção; as tabelas mantêm ambos os anos.</p><div class="year-controls"><label for="party-year">Eleição nos gráficos por partido: </label><select id="party-year"><option value="2018">2018</option><option value="2022">2022</option></select></div>')
for year in [2018,2022]:
    p=party[party.Ano.eq(year)].sort_values('Partido')
    parts.append(f'<div class="year-panel" data-year="{year}"'+(' style="display:none"' if year==2022 else '')+f'><h3>{year} · amplitude, cobertura e precisão</h3>')
    f=make_subplots(rows=1,cols=3,shared_yaxes=True,subplot_titles=['Amplitude agregada (%)','Cobertura (%)','Precisão (%)'],horizontal_spacing=.05)
    for j,(metric,color) in enumerate([('Amplitude agregada %','#17867b'),('Cobertura %','#286d9c'),('Precisão %','#ba723c')],1):
        f.add_trace(go.Bar(x=p[metric],y=p.Partido,orientation='h',marker_color=color,showlegend=False,
                           customdata=p[['Candidatos','Posições no núcleo','Eleitos','Eleitos fora']].to_numpy(),
                           hovertemplate='%{y}<br>%{x:.2f}%<br>Candidatos: %{customdata[0]:.0f}<br>Posições: %{customdata[1]:.2f}<br>Eleitos: %{customdata[2]:.0f}<br>Eleitos fora: %{customdata[3]:.2f}<extra></extra>'),row=1,col=j)
        f.update_xaxes(range=[0,102],row=1,col=j)
    f.update_yaxes(autorange='reversed')
    f.update_layout(height=1050)
    parts.append(chart(f))
    parts.append('<p>Barras ausentes de cobertura indicam ausência de eleitos; precisão é indefinida quando não há posições no núcleo. Zero e ausência não são equivalentes. Passe o cursor para ver os denominadores.</p>')
    hp=party_profiles[party_profiles.Ano.eq(year)]
    cols=[LABELS[k] for k in ['reeleicao_proxy','ex_federal_proxy','vitoria_estadual','vitoria_prefeito','vitoria_vereador','voto_relevante','sem_credencial','mulher','negra']]
    pivot=hp.pivot(index='Partido',columns='Perfil',values='Composição do núcleo %').reindex(index=p.Partido,columns=cols)
    short=['Federal no<br>pleito anterior','Vitória federal<br>mais antiga','Vitória<br>estadual/distrital','Vitória<br>prefeito','Vitória<br>vereador','Votação<br>histórica relevante','Sem credencial<br>registrada','Mulheres','Pretas/<br>pardas']
    heat=go.Figure(go.Heatmap(z=pivot.to_numpy(),x=short,y=pivot.index,zmin=0,zmax=100,colorscale='Blues',colorbar=dict(title='% núcleo'),text=pivot.to_numpy(),texttemplate='%{text:.0f}',hoverongaps=False,hovertemplate='%{y}<br>%{x}<br>%{z:.2f}% do núcleo válido<extra></extra>'))
    heat.update_layout(height=1120,title='Quem compõe o núcleo de cada partido?')
    heat.update_yaxes(autorange='reversed')
    parts.append(chart(heat))
    parts.append('<p>As colunas de experiência se sobrepõem. Cada célula é a participação daquele perfil no núcleo do partido, entre registros válidos. Células vazias indicam denominador zero. A tabela de composição abaixo informa os denominadores e permite consultar também a entrada no núcleo entre candidatos de cada perfil.</p></div>')

parts.append('<h3>Leitura de alguns contrastes</h3><p>Em 2018, PT e PP incluem todos os seus eleitos no núcleo, mas com precisões de 44,8% e 50,0%, respectivamente. O PSOL também apresenta cobertura de 100%, com precisão de 5,0%: seus 10 eleitos ocupam 201 posições no núcleo. Uma mesma cobertura, portanto, acompanha abrangências e resultados distintos.</p><p>O PSL de 2018 apresenta cobertura de 41,3% entre seus 52 eleitos. Em 2022, o PL inclui 80,5% de seus 99 eleitos, com precisão de 48,6%; o PT inclui 98,6% de seus 69 eleitos, com precisão de 42,5%. São descrições de partidos em eleições específicas, sem tratar essas siglas como uma sequência organizacional única.</p>')
parts.append('<h3>Tabela completa por partido</h3><p>Amplitude agregada = soma das posições ÷ soma dos candidatos. A mediana das amplitudes dá peso igual a cada lista estadual. Cobertura e precisão são razões de somas. O lift agregado usa Σ(eleitos × posições ÷ candidatos) como denominador esperado. Não se toma a média simples das coberturas estaduais.</p>')
parts.append(table(party,'partidos',True))
parts.append('<h3>Composição e entrada no núcleo por partido</h3><p>Exemplo de leitura: “mulheres como percentual do núcleo” descreve sua composição; “entrada entre mulheres candidatas” descreve a parcela das mulheres daquele partido situada no núcleo. O mesmo procedimento vale para cada trajetória.</p>')
parts.append(table(party_profiles,'composicao_partidos',True))
parts.append('<h3>Diferenças entre as listas estaduais do mesmo partido</h3><p>Cada ponto é uma lista de UF. As caixas mostram mediana e quartis de sua amplitude, com bigodes até 1,5 intervalo interquartil. Um valor nacional pode reunir listas bastante diferentes; passe o cursor para identificar a UF.</p>')
box=l.rename(columns={'sg_partido_norm':'Partido','sg_uf':'UF','ano_eleicao':'Ano','amplitude':'Amplitude da lista %'}).copy()
box['Ano']=box.Ano.astype(str)
f=px.box(box,x='Amplitude da lista %',y='Partido',color='Ano',points='all',hover_data=['UF','C','K','E'],category_orders={'Partido':sorted(box.Partido.unique())},height=1450,color_discrete_sequence=['#168579','#c77a42'])
parts.append(chart(f))
parts.append(table(l.rename(columns={'ano_eleicao':'Ano','sg_partido_norm':'Partido','sg_uf':'UF'}),'listas_estaduais',True))
parts.append('</section>')

parts.append('<section id="composicao"><h2>3. Quem compõe o núcleo no conjunto das candidaturas?</h2><p>Eleitos federais no pleito anterior representam cerca de 11% do núcleo em cada eleição. Candidaturas sem vitória ou votação histórica relevante registrada representam 66,6% em 2018 e 68,9% em 2022. Isso não significa ausência de experiência política: os registros utilizados captam apenas determinadas credenciais eleitorais.</p>')
long=national_profiles.melt(id_vars=['Ano','Perfil'],value_vars=['Composição do núcleo %','Composição fora %'],var_name='Grupo',value_name='Percentual')
parts.append(chart(px.bar(long,x='Percentual',y='Perfil',color='Grupo',facet_col='Ano',barmode='group',height=680,orientation='h',title='Composição dentro e fora do núcleo')))
parts.append(table(national_profiles,'composicao_nacional'))
parts.append('<p>As mulheres passam de 32,9% para 36,2% das posições do núcleo. As experiências anteriores não formam categorias exclusivas: uma candidatura pode ter vitórias em mais de um cargo e votação relevante no histórico. Prefeitos e vereadores são identificados por vitória anterior, não pelo exercício atual do mandato.</p></section>')

parts.append('<section id="territorio"><h2>4. Variação por magnitude e UF</h2><p>As faixas seguem o capítulo: 8–12, 16–31 e 39–70 cadeiras. As taxas agregadas informam a correspondência eleitoral no conjunto das listas de cada faixa; a mediana da amplitude descreve a lista típica.</p>')
parts.append(table(mag,'magnitude'))
parts.append('<p>Nos distritos grandes, a cobertura sobe de 81,5% para 93,8%, enquanto a precisão cai de 24,2% para 16,7%. Nos pequenos, a cobertura fica em 93,0% e 94,2%, com precisões de 13,8% e 9,0%. Os distritos grandes apresentam maior lift nos dois anos. Esses indicadores descrevem aspectos diferentes do núcleo e devem ser lidos conjuntamente.</p>')
plot=uf.copy();plot['Ano']=plot.Ano.astype(str)
parts.append(chart(px.scatter(plot,x='Cobertura %',y='Precisão %',color='Ano',size='Eleitos',hover_name='UF',hover_data=['Listas','Posições no núcleo','Eleitos fora','Lift'],height=460,title='Cobertura e precisão por UF')))
parts.append(table(uf,'ufs',True))
parts.append('</section><section id="grupos"><h2>5. Eleitos e não eleitos, dentro e fora</h2><p>Os quatro grupos tornam visíveis os encontros e desencontros entre o núcleo financeiro e o resultado eleitoral. Não eleger uma candidatura financiada não revela, por si só, um erro: o resultado eleitoral não informa todos os objetivos do partido.</p>')
parts.append(table(quad,'quatro_grupos'))
selected=[LABELS[x] for x in ['reeleicao_proxy','voto_relevante','sem_credencial','mulher']]
parts.append(chart(px.bar(quad_profiles[quad_profiles.Perfil.isin(selected)],x='Perfil',y='Percentual',color='Grupo',facet_col='Ano',barmode='group',height=560,title='Perfis dos quatro grupos')))
parts.append(table(quad_profiles,'perfis_quatro_grupos',True))
parts.append('<h3>Onde estão os eleitos fora?</h3><p>Esta abertura identifica a contribuição de cada partido para o total de eleitos fora do núcleo. Uma contagem grande pode decorrer do tamanho da bancada; por isso a tabela também informa a proporção de seus eleitos que fica fora.</p>')
outside=party[['Ano','Partido','Eleitos','Eleitos dentro','Eleitos fora','Não eleitos dentro','Posições no núcleo']].copy()
outside['Fora entre eleitos do partido %']=100*outside['Eleitos fora']/outside.Eleitos.replace(0,np.nan)
outside['Parcela dos eleitos fora do ano %']=100*outside['Eleitos fora']/outside.groupby('Ano')['Eleitos fora'].transform('sum')
parts.append(table(outside,'eleitos_fora_partido',True))
parts.append('</section><section id="receitas"><h2>6. Receitas dos eleitos dentro e fora do núcleo</h2><p>Recursos próprios e doações de pessoas físicas são apresentados separadamente. As medianas e quartis descrevem as distribuições dos valores recebidos, ponderadas pelo pertencimento ao núcleo. Valores nominais de campanhas diferentes não são comparados como poder de compra.</p>')
parts.append(table(money,'receitas_eleitos'))
shares['Ano e grupo']=shares.Ano.astype(str)+' · '+shares.Grupo
parts.append(chart(px.bar(shares,x='Ano e grupo',y='Participação nos recursos do grupo %',color='Fonte',barmode='stack',height=450,title='De onde vêm os recursos dos eleitos de cada grupo?')))
parts.append('<p>O gráfico divide a soma ponderada de cada fonte pela soma de todas as receitas do grupo. É uma composição de valores agregados, não a média das participações individuais. “Outras origens” reúne as demais receitas não partidárias. Estar fora do núcleo não significa receber zero do partido.</p>')
parts.append(table(shares.drop(columns='Ano e grupo'),'composicao_receitas'))
parts.append('<h3>Receitas dos eleitos por partido</h3><p>As medianas abaixo permitem localizar onde os perfis monetários se diferenciam. Grupos com poucos eleitos — ou apenas uma fração de candidatura devido a empate — descrevem poucos casos; o denominador acompanha cada linha. Um grupo sem eleitos tem mediana indefinida.</p>')
parts.append(table(money_party,'receitas_por_partido',True))
parts.append('<h3>Candidatos eleitos com participação fora do núcleo</h3><p>Inclui todos os casos com peso positivo fora, inclusive empates no corte. O peso fora informa quanto cada candidatura contribui às contagens anteriores.</p>')
cases=e[e.fora.gt(0)][['ano_eleicao','sg_partido_norm','sg_uf','nm_candidato','fora','vr_receita_recursos_partidos','proprios','pessoas_fisicas']+list(LABELS)].rename(columns={'ano_eleicao':'Ano','sg_partido_norm':'Partido','sg_uf':'UF','nm_candidato':'Candidato','fora':'Peso fora',**LABELS})
parts.append(table(cases.sort_values(['Ano','Partido','UF']),'casos_eleitos_fora',True))
parts.append('</section>')

parts.append('<section id="metodo"><h2>7. Definições e notas de leitura</h2><ul><li>NECr = (Σ recursos partidários)² / Σ recursos partidários². O núcleo tem k = floor(NECr + 0,5), limitado ao número de candidaturas; listas sem recursos têm núcleo vazio. Nos empates no corte, as posições são repartidas igualmente entre os empatados. As contagens ponderadas podem ter decimais.</li><li>Siglas são as normalizadas no pipeline em cada ano. Federações de 2022 e coligações de 2018 não são agregadas. Não são reconstruídas séries de fusões ou mudanças de nome.</li><li>“Eleito federal no pleito anterior” é uma aproximação de incumbência obtida pela vitória quatro anos antes, por CPF. Não identifica suplentes em exercício, afastamentos ou saída do mandato. “Vitória federal mais antiga” indica vitória histórica sem vitória no pleito imediatamente anterior.</li><li>Vitórias históricas usam as colunas n_eleicoes da base rrd, que contam vitórias no pipeline. As janelas chegam a 2016 para candidaturas de 2018 e a 2020 para candidaturas de 2022. A votação relevante usa a flag histórica ≥ 10% do QE da base, sem o resultado corrente.</li><li>Ausências de informação não são tratadas como ausência de experiência. Os percentuais de perfil usam apenas registros válidos; os denominadores são informados nas tabelas. Pessoas pretas ou pardas e mulheres seguem as variáveis da base analítica.</li><li>Quantis ponderados são o primeiro valor em ordem crescente cuja soma acumulada de pesos alcança 25%, 50% ou 75% do total. Receitas próprias e de pessoas físicas seguem a origem declarada; não rastreiam a fonte última dos repasses.</li><li>Os dados descrevem o universo do capítulo, com 7.630 candidaturas em 2018 e 9.675 em 2022. As receitas são totais da campanha; as descrições não estabelecem o que era conhecido no momento de cada decisão de financiamento.</li></ul>')
rob=[]
for _,r in canonical.iterrows():
    rob.append({'Ano':int(r.ano_eleicao),'Regra':r.regra_k,'Eleitos dentro':r.eleitos_top_necr,'Eleitos fora':513-r.eleitos_top_necr,'Cobertura %':100*r.cobertura})
parts.append('<h3>Nota de sensibilidade ao arredondamento</h3><p>As descrições principais usam arredondamento convencional. A tabela registra a mudança de cobertura ao usar piso ou teto, mantendo a regra fracionária dos empates.</p>')
parts.append(table(pd.DataFrame(rob),'arredondamento'))
parts.append('<p>Reprodução: <code>python tese/scripts/relatorio_descritivo_nucleo.py</code>. A base intermediária auditada está em <code>tese/resultados-exploracao-nucleo/base_analitica.csv</code>. Este relatório arquivado e suas tabelas estão em <code>tese/old/relatorios-descritivos</code>. O HTML incorpora seus gráficos e funciona sem internet.</p>')
for year,g in party.groupby('Ano'):
    check(f'Somas por partido {year}',np.isclose(g['Eleitos dentro'].sum(),nation.loc[nation.Ano.eq(year),'Eleitos dentro'].iloc[0]) and g.Eleitos.sum()==513)
check('Quatro grupos recompõem universo',np.allclose(quad.groupby('Ano')['Candidaturas ponderadas'].sum(),[7630,9675]))
check('Fontes recompõem total',np.allclose(shares.groupby(['Ano','Grupo'])['Participação nos recursos do grupo %'].sum(),100))
parts.append(f'<p>Auditoria: {len(checks)} verificações concluídas de fontes, universos, pesos, cobertura canônica, somas partidárias e composição das receitas.</p></section>')
parts.append('''</main><script>
document.querySelectorAll('input[data-table]').forEach(input=>input.addEventListener('input',()=>{
 const q=input.value.toLocaleLowerCase('pt-BR');
 document.querySelectorAll('#'+input.dataset.table+' tbody tr').forEach(row=>row.hidden=!row.textContent.toLocaleLowerCase('pt-BR').includes(q));
}));
document.getElementById('party-year').addEventListener('change',event=>{
 document.querySelectorAll('.year-panel').forEach(panel=>{
  panel.style.display=panel.dataset.year===event.target.value?'block':'none';
  if(panel.style.display==='block')panel.querySelectorAll('.plotly-graph-div').forEach(div=>Plotly.Plots.resize(div));
 });
});
</script></body></html>''')
target=ROOT/'tese/old/relatorios-descritivos/relatorio-exploracao-nucleo.html'
target.write_text('\n'.join(parts),encoding='utf-8')
(OUT/'auditoria.json').write_text(json.dumps({'verificacoes':checks,'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'fontes_sha256':{s:audit['fontes_sha256'][s] for s in ['data/processed/rrd_df_novo.parquet','data/processed/receitas.parquet']},'tabelas':list(tables),'graficos':fig_num},ensure_ascii=False,indent=2),encoding='utf-8')
print(target)
print(f'{len(party)} combinações partido/ano; {fig_num} gráficos; {len(checks)} verificações OK.')
