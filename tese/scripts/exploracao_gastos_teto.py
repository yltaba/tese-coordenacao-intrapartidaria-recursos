"""Exploração de despesas contratadas/teto, deputado federal, 2018 e 2022."""
from pathlib import Path
import sys
import json
import hashlib
import numpy as np
import pandas as pd
import plotly.graph_objects as go

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'tese/exploracao-gastos-teto'
OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'src/2_gold'))
from cap3_taa_features import norm_partido,N_ELEICOES_COLS,acertos_fracionarios
from financiamento_alternativo_top_necr import membership

KEY=['ano_eleicao','sg_uf','nr_candidato']
LIST=['ano_eleicao','sg_uf','sg_partido_norm']
CAP={2018:2500000.,2022:3176572.53}
LAW18='https://www.tse.jus.br/legislacao/compilada/res/2017/resolucao-no-23-553-de-18-de-dezembro-de-2017'
LAW22='https://www.tse.jus.br/legislacao/compilada/res/2019/resolucao-no-23-607-de-17-de-dezembro-de-2019'
LIMIT22='https://www.tre-mg.jus.br/comunicacao/noticias/2022/Julho/eleicoes-2022-tse-divulga-limites-de-gastos-nas-campanhas-666390'
CHECK={}


def check(name,ok):
    CHECK[name]=bool(ok)
    assert ok,name


def fmt(x,n=2):
    return f'{x:,.{n}f}'.replace(',','X').replace('.',',').replace('X','.')


def table(d):
    d=d.copy()
    for c in d.columns:
        if pd.api.types.is_bool_dtype(d[c]):d[c]=d[c].map({True:'Sim',False:'Não'})
        elif pd.api.types.is_integer_dtype(d[c]):d[c]=d[c].map(str)
        elif pd.api.types.is_float_dtype(d[c]):d[c]=d[c].map(lambda v:fmt(v) if pd.notna(v) else 'Sem registro')
    return '<div class="scroll">'+d.to_html(index=False,border=0,escape=True)+'</div>'


def summarize(g,w,label,year,metric='gasto_pct'):
    w=np.asarray(w,float)
    observed=g[metric].notna().to_numpy() & (w>0)
    x=g.loc[observed,metric].to_numpy(float)
    wo=w[observed]
    def quantile(q):
        ix=np.argsort(x)
        return x[ix][np.searchsorted(np.cumsum(wo[ix]),q*wo.sum())]
    result=dict(Ano=int(year),Grupo=label,Medida=metric,N_universo=float(w.sum()),N_com_registro=float(wo.sum()),N_sem_registro=float(w.sum()-wo.sum()),
        Media_pct=np.average(x,weights=wo),Mediana_pct=quantile(.5),P90_pct=quantile(.9),P95_pct=quantile(.95),P99_pct=quantile(.99),Max_pct=x.max())
    for cut in [10,50,80,90,95,99,100]:
        n=wo[x>=cut-1e-10].sum()
        result[f'N_ge{cut}']=float(n)
        result[f'Pct_ge{cut}']=100*n/wo.sum()
    result['N_igual100']=float(wo[np.abs(x-100)<1e-10].sum())
    result['N_acima100']=float(wo[x>100+1e-10].sum())
    result['Pct_observada_ge95_no_universo']=100*result['N_ge95']/w.sum()
    return result


def main():
    d=pd.read_parquet(ROOT/'data/processed/rrd_df_novo.parquet')
    d=d[d.ano_eleicao.isin(CAP)].copy().reset_index(drop=True)
    d.nr_candidato=d.nr_candidato.astype(int)
    d['sg_partido_norm']=d.sg_partido.map(norm_partido)
    check('Candidatos únicos',not d.duplicated(KEY).any())
    check('513 eleitos em cada ano',d.groupby('ano_eleicao').eleito.sum().eq(513).all())
    exp=pd.read_parquet(ROOT/'data/processed/despesas.parquet')
    exp=exp[exp.ano_eleicao.isin(CAP)&exp.ds_cargo.eq('DEPUTADO FEDERAL')].copy()
    check('Despesas finitas e não negativas',np.isfinite(exp.vr_despesa_contratada).all() and exp.vr_despesa_contratada.ge(0).all())
    exp['desconto_2022']=np.where(exp.ano_eleicao.eq(2022)&exp.ds_origem_despesa.isin(['Serviços advocatícios','Serviços contábeis']),exp.vr_despesa_contratada,0.)
    agg=exp.groupby(KEY).agg(gasto_bruto=('vr_despesa_contratada','sum'),exclusao_2022=('desconto_2022','sum'),registros=('vr_despesa_contratada','size')).reset_index()
    match=agg.merge(d[KEY],on=KEY,how='left',indicator=True,validate='one_to_one')
    unmatched=match[match._merge.eq('left_only')].drop(columns='_merge')
    unmatched.to_csv(OUT/'despesas_fora_universo.csv',index=False,encoding='utf-8-sig')
    d=d.merge(agg,on=KEY,how='left',validate='one_to_one')
    d['tem_despesa']=d.gasto_bruto.notna()
    check('Todos os eleitos têm despesas registradas',d.loc[d.eleito.eq(1),'tem_despesa'].all())
    check('Valores agregados reconciliados',np.isclose(d.gasto_bruto.sum()+unmatched.gasto_bruto.sum(),exp.vr_despesa_contratada.sum()))
    d['gasto_bruto']=d.gasto_bruto.round(2)
    d['exclusao_2022']=d.exclusao_2022.round(2)
    d['gasto_aproximado']=(d.gasto_bruto-d.exclusao_2022).round(2)
    check('Ajuste não aumenta gastos',d.loc[d.tem_despesa,'gasto_aproximado'].le(d.loc[d.tem_despesa,'gasto_bruto']+.001).all())
    d['teto']=d.ano_eleicao.map(CAP)
    d['gasto_pct']=100*d.gasto_aproximado/d.teto
    d['bruto_pct']=100*d.gasto_bruto/d.teto
    d['receita_pct']=100*(d.vr_receita_recursos_partidos.fillna(0)+d.vr_receita_outros.fillna(0))/d.teto
    d['top']=0.
    for _,g in d.groupby(LIST):
        v=g.vr_receita_recursos_partidos.fillna(0).to_numpy(float)
        necr=v.sum()**2/(v@v) if v.sum() else np.nan
        k=max(1,int(np.floor(necr+.5))) if np.isfinite(necr) else 0
        w=membership(v,k)
        d.loc[g.index,'top']=w
        assert np.isclose(w@g.eleito,acertos_fracionarios(v,g.eleito,k) if k else 0)
    d['fora']=1-d.top
    d['competitivo']=d[N_ELEICOES_COLS].fillna(0).sum(axis=1).gt(0)|d.alcancou_10pct_qe_hist.fillna(False)
    summaries=[]
    for year,g in d.groupby('ano_eleicao'):
        groups={'Todos':np.ones(len(g)),'Eleitos':g.eleito,'Não eleitos':1-g.eleito,
                'Competitivos prévios':g.competitivo.astype(int),'Dentro Top-NECr':g.top,'Fora Top-NECr':g.fora,
                'Eleitos dentro Top-NECr':g.eleito*g.top,'Eleitos fora Top-NECr':g.eleito*g.fora}
        for label,w in groups.items():
            for metric in ['gasto_pct','bruto_pct']:
                summaries.append(summarize(g,w,label,year,metric))
    summary=pd.DataFrame(summaries)
    bands=['Sem registro','0 a <10%','10 a <25%','25 a <50%','50 a <80%','80 a <90%','90 a <95%','95 a <99%','99 a 100%','Acima de 100%']
    d['faixa']='Sem registro'
    ranges=[(0,10),(10,25),(25,50),(50,80),(80,90),(90,95),(95,99),(99,100+1e-9),(100+1e-9,np.inf)]
    for label,(lo,hi) in zip(bands[1:],ranges):
        d.loc[d.gasto_pct.ge(lo)&d.gasto_pct.lt(hi),'faixa']=label
    check('Faixas cobrem todos os registros',d.loc[d.tem_despesa,'faixa'].ne('Sem registro').all())
    dist=[]
    for year,g in d.groupby('ano_eleicao'):
        for label,sub in [('Todos',g),('Eleitos',g[g.eleito.eq(1)]),('Não eleitos',g[g.eleito.eq(0)])]:
            for band in bands:
                n=int(sub.faixa.eq(band).sum())
                dist.append(dict(Ano=year,Grupo=label,Faixa=band,N=n,Percentual=100*n/len(sub)))
    distribution=pd.DataFrame(dist)
    check('Distribuição soma 100%',np.allclose(distribution.groupby(['Ano','Grupo']).Percentual.sum(),100))
    geography=[]
    for (year,uf),g in d.groupby(['ano_eleicao','sg_uf']):
        for label,sub in [('Todos',g),('Eleitos',g[g.eleito.eq(1)])]:
            r=summarize(sub,np.ones(len(sub)),label,year)
            geography.append(dict(UF=uf,**r))
    geo=pd.DataFrame(geography)
    sources=exp.groupby(['ano_eleicao','ds_origem_despesa']).vr_despesa_contratada.sum().reset_index()
    universe=[]
    for year,g in d.groupby('ano_eleicao'):
        a=unmatched[unmatched.ano_eleicao.eq(year)]
        universe.append(dict(Ano=year,Candidatos=len(g),Com_despesas=int(g.tem_despesa.sum()),Sem_registro=int((~g.tem_despesa).sum()),Chaves_despesas_fora_universo=len(a),Valor_fora_universo=a.gasto_bruto.sum(),Total_bruto_no_universo=g.gasto_bruto.sum(),Desconto_2022=g.exclusao_2022.sum()))
    univ=pd.DataFrame(universe)
    exports={'resumo.csv':summary,'distribuicao.csv':distribution,'por_uf.csv':geo,'universo.csv':univ,'categorias_despesa.csv':sources}
    for f,frame in exports.items():frame.to_csv(OUT/f,index=False,encoding='utf-8-sig')
    columns=KEY+['nm_candidato','sg_partido_norm','eleito','competitivo','tem_despesa','registros','teto','gasto_bruto','exclusao_2022','gasto_aproximado','gasto_pct','bruto_pct','receita_pct','top','fora','faixa']
    d[columns].to_csv(OUT/'candidatos.csv',index=False,encoding='utf-8-sig')
    # Machine-readable audit: no raw expense files are available for invoice-level review.
    audit={'checks':CHECK,'fontes':{'2018':LAW18,'2022':LAW22,'teto2022':LIMIT22},'data_consulta':'2026-09-11',
           'sha256':{f:hashlib.sha256((ROOT/'data/processed'/f).read_bytes()).hexdigest() for f in ['rrd_df_novo.parquet','despesas.parquet']}}
    (OUT/'verificacao.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    render(d,summary,distribution,geo,univ,exports)
    print(summary[summary.Medida.eq('gasto_pct')&summary.Grupo.isin(['Todos','Eleitos','Não eleitos','Eleitos fora Top-NECr'])][['Ano','Grupo','N_com_registro','N_sem_registro','Mediana_pct','Pct_ge90','Pct_ge95','N_ge95','N_igual100','N_acima100']].to_string(index=False))
    print(OUT/'exploracao-gastos-teto.html')


def render(d,s,dist,geo,univ,exports):
    primary=s[s.Medida.eq('gasto_pct')]
    p=['''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Candidatos geralmente atingem o teto de gastos?</title><style>
*{box-sizing:border-box}body{margin:0;background:#f0f4f7;color:#172c40;font:16px/1.65 system-ui,sans-serif}main{max-width:1200px;padding:28px 22px 70px;margin:auto}header{background:#142d45;color:white;padding:40px;border-radius:18px}h1{font-size:39px;line-height:1.2}h2{font-size:27px;line-height:1.3;margin-top:0}h3{font-size:20px}section{background:white;padding:30px;border-radius:16px;margin-top:24px}.lead{font-size:20px}.note{font-size:14px;color:#53677b}.callout{background:#ecf7f4;border-left:5px solid #148c7b;padding:20px;margin:18px 0}.warn{background:#fff7e9;border-color:#c3882b}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:11px;text-align:left;border-bottom:1px solid #dce5ec}th{background:#eef3f8}a{color:#136585}a,code{overflow-wrap:anywhere}nav a{color:#bde8f2;margin-right:17px}details{margin:18px 0}input{padding:12px;border:1px solid #a8b8c8;border-radius:8px;width:min(100%,500px)}@media(max-width:650px){header,section{padding:20px}h1{font-size:29px}}@media print{header{background:white;color:#172c40}nav,input{display:none}section{break-inside:avoid}}
</style></head><body><main><header><p>CAPÍTULO 3 · ANÁLISE EXPLORATÓRIA</p><h1>Candidatos geralmente atingem o teto de gastos?</h1><p class="lead">Deputados federais, 2018 e 2022. Distância até o limite, diferenças entre vencedores e perdedores e relação com o Top-NECr.</p><nav><a href="#resposta">Resposta</a><a href="#distribuicao">Distribuição</a><a href="#proximidade">Proximidade</a><a href="#nucleo">Top-NECr</a><a href="#casos">Casos</a><a href="#metodo">Método</a></nav></header><section id="resposta"><h2>Em geral, os gastos registrados ficam abaixo do teto</h2>''']
    for year in CAP:
        a=primary[primary.Ano.eq(year)&primary.Grupo.eq('Todos')].iloc[0]
        b=primary[primary.Ano.eq(year)&primary.Grupo.eq('Eleitos')].iloc[0]
        p.append(f'<div class="callout"><strong>{year}:</strong> entre candidaturas com despesas registradas, a mediana equivale a <strong>{fmt(a.Mediana_pct)}% do teto</strong>; {fmt(a.Pct_ge95)}% chegam a pelo menos 95%. Entre os 513 eleitos, a mediana é <strong>{fmt(b.Mediana_pct)}%</strong> e {int(b.N_ge95)} ({fmt(b.Pct_ge95)}%) chegam a pelo menos 95%.</div>')
    p.append('<p><strong>Resposta curta:</strong> atingir ou ficar muito perto do teto não é a situação típica na medida disponível. Os eleitos se aproximam muito mais dele que os não eleitos. Isso é compatível com o teto importar especialmente para uma parcela das campanhas mais financiadas, mas não demonstra que ele determina o orçamento da maioria.</p><p class="note">Medida principal: despesas contratadas registradas, descontando em 2022 as categorias advocatícia e contábil. É uma aproximação da utilização do teto, não a totalidade jurídica apurada pela Justiça Eleitoral. “Muito perto” = pelo menos 95%; os cortes de 80%, 90%, 99% e 100% também são apresentados.</p></section>')
    p.append('<section><h2>O que significa “atingir”?</h2><p>Usamos duas leituras complementares: proximidade prática, com patamares de 80%, 90%, 95% e 99%; e igualdade ao valor do teto, usando totais arredondados em centavos. Valores acima de 100% ficam separados. As proporções “≥95%” incluem os casos acima de 100% e não significam, necessariamente, estar dentro do intervalo legal.</p><p>Os limites usados são R$ 2.500.000,00 em 2018 e R$ 3.176.572,53 em 2022, comuns às UFs para deputado federal. Fontes: <a href="'+LAW18+'">Resolução TSE 23.553/2017, art. 6º</a> e <a href="'+LIMIT22+'">divulgação oficial de 2022</a>.</p></section>')
    p.append('<section id="distribuicao"><h2>Como os gastos se distribuem?</h2><p>Esta distribuição mantém todas as candidaturas no denominador. “Sem registro” é uma categoria própria e não é convertida em gasto zero. Os demais gráficos e quantis usam apenas candidaturas com despesas registradas.</p>')
    colors=['#ccd3da','#dce9ee','#b3d5d8','#80bfc0','#4ba5a2','#198b84','#217084','#3f566f','#997344','#c48138']
    fig=go.Figure()
    for band,color in zip(dist.Faixa.unique(),colors):
        a=dist[dist.Faixa.eq(band)]
        fig.add_bar(name=band,x=[f'{r.Ano} · {r.Grupo}' for _,r in a.iterrows()],y=a.Percentual,customdata=a.N,marker_color=color,hovertemplate='%{x}<br>%{y:.2f}% · %{customdata} candidaturas<extra>%{fullData.name}</extra>')
    fig.update_layout(template='plotly_white',barmode='stack',height=480,yaxis_title='% do universo do grupo',legend_orientation='h',margin=dict(t=20,b=115),yaxis_range=[0,100])
    p.append(fig.to_html(full_html=False,include_plotlyjs=True,config={'displaylogo':False,'responsive':True}))
    p.append('<details><summary>Contagens por faixa</summary>'+table(dist)+'</details><h3>Distribuição acumulada dos gastos registrados</h3><p>Em cada ponto, o eixo vertical informa a porcentagem das candidaturas com gasto menor ou igual ao valor do eixo horizontal. A linha em 100% marca o teto. O gráfico preserva todos os extremos.</p>')
    fig=go.Figure()
    for year,color in [(2018,'#148879'),(2022,'#bc7925')]:
        for winner,dash in [(0,'dot'),(1,'solid')]:
            x=np.sort(d.loc[d.ano_eleicao.eq(year)&d.eleito.eq(winner)&d.tem_despesa,'gasto_pct'].to_numpy())
            fig.add_scatter(x=x,y=100*np.arange(1,len(x)+1)/len(x),mode='lines',name=f'{year} · '+('Eleitos' if winner else 'Não eleitos'),line=dict(color=color,dash=dash,shape='hv'))
    fig.add_vline(x=100,line_dash='dash',line_color='#9c5962')
    fig.update_layout(template='plotly_white',height=430,xaxis_title='Gastos / teto (%)',yaxis_title='% acumulado',legend=dict(orientation='h',y=-.28),margin=dict(t=25,b=105),xaxis_rangemode='tozero')
    p.append(fig.to_html(full_html=False,include_plotlyjs=False,config={'displaylogo':False,'responsive':True})+'</section>')
    p.append('<section id="proximidade"><h2>Quantos se aproximam de fato?</h2>')
    cols=['Ano','Grupo','N_com_registro','Mediana_pct','P90_pct','Pct_ge80','Pct_ge90','Pct_ge95','Pct_ge99','N_igual100','N_acima100']
    readable={'N_com_registro':'N com registro','Mediana_pct':'Mediana (%)','P90_pct':'P90 (%)','Pct_ge80':'≥80% (%)','Pct_ge90':'≥90% (%)','Pct_ge95':'≥95% (%)','Pct_ge99':'≥99% (%)','N_igual100':'N igual a 100%','N_acima100':'N acima de 100%'}
    p.append(table(primary[primary.Grupo.isin(['Todos','Eleitos','Não eleitos','Competitivos prévios'])][cols].rename(columns=readable)))
    p.append('<p class="note">Colunas ≥80%, ≥90%, ≥95% e ≥99%: porcentagens dos candidatos com registro no grupo, e não percentuais de gastos agregados. Os grupos se sobrepõem: competitivos prévios podem ser eleitos ou não.</p><h3>Bruto versus ajuste das categorias excluídas em 2022</h3>')
    p.append(table(s[s.Grupo.isin(['Todos','Eleitos'])][['Ano','Grupo','Medida','Mediana_pct','N_ge95','Pct_ge95','N_igual100','N_acima100']].replace({'Medida':{'gasto_pct':'Aproximação principal','bruto_pct':'Contratado bruto'}})))
    p.append('<p>Em 2018 as duas versões coincidem. Em 2022, a retirada de serviços advocatícios e contábeis reduz os valores comparados ao teto. Não se retroage essa exclusão para 2018. O ajuste é feito pelas categorias disponíveis, não por revisão individual dos contratos.</p></section>')
    p.append('<section><h2>O ajuste muda a contagem, mas não a resposta geral</h2><p>Em 2022, 71 candidaturas têm despesas contratadas brutas de pelo menos 95% do teto; após o desconto das duas categorias, são 40. Entre eleitos, a contagem passa de 44 para 32. Casos acima de 100% passam de 17 para 1 no conjunto observado. Isso mostra por que o total bruto não deve ser lido diretamente como gasto sujeito ao teto.</p><p>Nas duas versões, a proximidade ao limite permanece minoritária. O único registro exatamente igual ao teto na aproximação principal é de um não eleito em 2018; em 2022 não há igualdade exata. Essas contagens dependem da medida disponível e não substituem as contas oficiais.</p></section>')
    p.append('<section id="nucleo"><h2>O teto e o núcleo de financiamento partidário</h2><p>O Top-NECr é reconstruído a partir das receitas partidárias, preservando a regra anterior. Os empates no corte recebem pesos fracionários; por isso algumas contagens abaixo não são inteiras. Gastos e receitas têm papéis diferentes nesta comparação.</p>'+table(primary[primary.Grupo.str.contains('Top-NECr')][cols].rename(columns=readable)))
    for year in CAP:
        a=primary[primary.Ano.eq(year)&primary.Grupo.eq('Eleitos fora Top-NECr')].iloc[0]
        p.append(f'<p><strong>{year} · eleitos fora:</strong> a mediana de gastos é {fmt(a.Mediana_pct)}% do teto; {fmt(a.N_ge95)} de {fmt(a.N_com_registro)} eleitos ponderados alcançam pelo menos 95% ({fmt(a.Pct_ge95)}%).</p>')
    p.append('<div class="callout warn"><strong>Implicação para o capítulo:</strong> existência de financiamento privado não equivale a saturação do teto. A complementação partidária pode ocorrer em campanhas com orçamento desejado abaixo do limite legal. Estar longe do teto não prova ausência de estratégia, mas exige cuidado ao usar o teto como explicação geral dos eleitos fora do Top-NECr.</div></section>')
    p.append('<section><h2>Há diferenças entre UFs?</h2><p>O teto é igual dentro de cada ano, mas as distribuições estaduais variam. A tabela apresenta todos os estados e o DF; grupos pequenos devem ser lidos pelas contagens, sem transformar os percentuais em ranking de desempenho.</p><details><summary>Abrir tabela por UF e resultado eleitoral</summary>'+table(geo[['Ano','UF','Grupo','N_com_registro','N_sem_registro','Mediana_pct','N_ge95','Pct_ge95']])+'</details></section>')
    p.append('<section id="casos"><h2>Candidaturas com gasto aproximado ≥80% do teto</h2><p>A tabela é um diagnóstico descritivo da base. Valores acima de 100% não são classificados aqui como infrações. A relação entre despesas contratadas, gastos individualizados pelo partido, doações estimáveis e ajustes legais exige exame das contas.</p><input id="search" placeholder="Buscar nome, UF, partido ou ano" aria-label="Filtrar candidatos"><div id="cases">')
    cases=d[d.gasto_pct.ge(80)].sort_values(['ano_eleicao','gasto_pct'],ascending=[True,False])
    p.append(table(cases[['ano_eleicao','sg_uf','sg_partido_norm','nm_candidato','eleito','bruto_pct','gasto_pct','exclusao_2022']].rename(columns={'ano_eleicao':'Ano','sg_uf':'UF','sg_partido_norm':'Partido','nm_candidato':'Nome','eleito':'Eleito (1=sim)','bruto_pct':'Bruto / teto (%)','gasto_pct':'Aproximação / teto (%)','exclusao_2022':'Desconto 2022 (R$)'}))+'</div></section>')
    p.append('<section id="metodo"><h2>Base, denominadores e limites da medida</h2>'+table(univ))
    p.append('<p><strong>Ausência de registro:</strong> candidatos sem linha correspondente na base de despesas permanecem no universo e aparecem como “Sem registro”. Não são tratados como gasto efetivamente zero. Medianas e proporções de proximidade usam o subconjunto observado. Os quantis são obtidos pela inversa da distribuição empírica acumulada, com pesos fracionários nos grupos Top-NECr. O CSV de resumo também informa a fração do universo completo com proximidade documentada (Pct_observada_ge95_no_universo); ela não estima os gastos dos ausentes. Todos os eleitos possuem despesas registradas.</p><p><strong>Cruzamento:</strong> chaves ano × UF × número de candidatura; apenas deputado federal e 2018/2022. As chaves presentes nas despesas, mas ausentes do universo consolidado de candidatos, são exportadas separadamente. O relatório não amplia silenciosamente a população dos testes anteriores.</p>')
    p.append('<p><strong>O que a aproximação inclui:</strong> soma de vr_despesa_contratada na base processada. Em 2022 são subtraídas as categorias “Serviços advocatícios” e “Serviços contábeis”, conforme a exclusão prevista no art. 35, §3º da <a href="'+LAW22+'">Resolução TSE 23.607/2019</a>. Transferências já presentes na base não são adicionadas novamente nem retiradas indiscriminadamente.</p><p><strong>O que ela não reconstrói:</strong> a medida legal inclui também gastos partidários individualizáveis e doações estimáveis recebidas, além de regras específicas de transferências e sobras. A base disponível não identifica integralmente esses componentes nem sua eventual sobreposição. Portanto, a soma usada pode divergir da apuração oficial em qualquer direção. As definições estão no art. 7º da <a href="'+LAW18+'">Resolução 23.553/2017</a> e no art. 5º da <a href="'+LAW22+'">Resolução 23.607/2019</a>.</p>')
    p.append('<p><strong>Proveniência:</strong> o notebook consolidacao_base_despesas.ipynb agrupa despesas contratadas por candidato, fornecedor, origem e data, somando valores. Os arquivos brutos e os identificadores originais de documentos não estão disponíveis neste workspace; não é possível revisar retificações, duplicidades documentais ou perdas anteriores à consolidação. Não são eliminadas linhas iguais por suposição. A reconciliação verifica a consistência da agregação disponível, não certifica completude contábil.</p><p><strong>Escopo:</strong> análise exploratória descritiva, sem testes causais ou p-valores. Competitividade prévia segue vitória anterior em cargo diferente de vereador ou histórico de 10% do QE. Top-NECr usa partido × UF × ano, arredondamento convencional e empates fracionários. As comparações entre anos expressam proporções dos limites vigentes; não estimam isoladamente o efeito de mudança institucional.</p><h3>Arquivos e reprodução</h3><p><code>python tese/scripts/exploracao_gastos_teto.py</code><br>Fontes locais: <code>data/processed/despesas.parquet</code> e <code>data/processed/rrd_df_novo.parquet</code>. Fontes oficiais consultadas em 11/09/2026. HTML e gráficos funcionam sem internet.</p>')
    p.append('<p>'+' · '.join(f'<a href="{f}">{f}</a>' for f in [*exports,'candidatos.csv','despesas_fora_universo.csv','verificacao.json'])+'</p><h3>Verificações</h3>'+table(pd.DataFrame([{'Verificação':k,'Passou':v} for k,v in CHECK.items()])))
    p.append('</section></main><script>document.getElementById("search").addEventListener("input",function(){const q=this.value.toLocaleLowerCase("pt-BR");document.querySelectorAll("#cases tbody tr").forEach(r=>r.hidden=!r.textContent.toLocaleLowerCase("pt-BR").includes(q));});</script></body></html>')
    (OUT/'exploracao-gastos-teto.html').write_text(''.join(p),encoding='utf-8')


if __name__=='__main__':main()
