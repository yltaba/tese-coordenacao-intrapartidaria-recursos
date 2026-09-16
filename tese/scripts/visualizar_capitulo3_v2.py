"""Atlas v2: amplitude, concentração e focalização da coordenação intrapartidária."""
from focalizacao_capitulo3 import calcular, abertura, focalizacao, contexto
from pathlib import Path
import json
import html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import get_plotlyjs
from benchmark_precisao_top_necr import calcular_benchmark

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tese/resultados-capitulo-3'
d = pd.read_csv(OUT / '25_todas_nominatas.csv')
coverage = pd.read_csv(OUT / '15_cobertura_nacional.csv')
comp = pd.read_csv(OUT / '03_competitivos_magnitude_tipo.csv')
limits = pd.read_csv(OUT / '10_limites_mp_mais_um.csv')
d, focus = calcular(ROOT, OUT, d)
fund = d[d.Recursos > 0]
COLORS = {2018:'#257a9b',2022:'#cc632e'}
MAG = ['Pequeno (8–12)','Médio (16–31)','Grande (39–70)']
chunks=[]
figures=[]

def number(x):
    return f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X','.')

def chart(fig, name, height=450):
    fig.update_layout(template='plotly_white', height=height, font=dict(family='Arial, sans-serif',size=13,color='#263d47'), margin=dict(l=65,r=25,t=55,b=70), legend=dict(orientation='h',y=1.14,x=0), paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)', separators=',.')
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    figures.append(name)
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=name, config={'responsive':True,'displaylogo':False,'scrollZoom':False,'toImageButtonOptions':{'format':'svg','filename':name}})

def section(n,title,lead):
    chunks.append(f'<section id="s{n}"><div class="eyebrow">{n:02d} / RESULTADOS</div><h2>{title}</h2><p class="lead">{lead}</p>')
def note(s): chunks.append(f'<p class="note">{s}</p>')
def end(): chunks.append('</section>')

def magnitude_summary(frame, metric, label, name, plot=True):
    """Mesmos grupos e estatísticas para gráfico, tabela e CSV."""
    rows=[]
    fig=go.Figure()
    for year in [2018,2022]:
        g=frame[frame.Ano==year].groupby('Magnitude')[metric].agg(['mean','std','median','count']).reindex(MAG)
        fig.add_trace(go.Scatter(x=MAG,y=g['mean'],mode='markers',name=str(year),marker=dict(color=COLORS[year],size=12),error_y=dict(type='data',array=g['std'],visible=True),customdata=g[['std','median','count']].to_numpy(),hovertemplate='%{x}<br>Média: %{y:.3f}<br>DP: %{customdata[0]:.3f}<br>Mediana: %{customdata[1]:.3f}<br>N: %{customdata[2]}<extra>%{fullData.name}</extra>'))
        for mag,s in g.iterrows():
            rows.append({'Magnitude':mag,'Ano':year,'Média':s['mean'],'DP':s['std'],'Mediana':s['median'],'N válido':int(s['count'])})
    result=pd.DataFrame(rows)
    result.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
    if plot:
        fig.update_layout(yaxis_title=label,yaxis_rangemode='tozero')
        if metric in ['NECr_Mp','NECr_E']:
            fig.add_hline(y=1,line_dash='dot',line_color='#62717a')
        chunks.append(chart(fig,name))
        note('Pontos: médias entre nominatas; barras: ±1 desvio-padrão, não intervalos de confiança. Uma barra pode ultrapassar os limites do indicador porque representa dispersão simétrica em torno da média.')
    display=result.copy()
    for col in ['Média','DP','Mediana']:
        display[col]=display[col].map(number)
    chunks.append('<div class="tablewrap">'+display.to_html(index=False,border=0)+'</div>')
    return result

chunks.append(abertura(d, focus, chart, number))

section(1,'A participação de competitivos cresce no total, com diferenças por magnitude','O total de candidaturas cresce 26,80%; o de competitivas cresce 45,26%. A proporção nacional passa de 11,61% para 13,30%. Nos distritos médios, porém, a participação recua ligeiramente: de 13,92% para 13,68%.')
fig=go.Figure()
groups=MAG+['Total']
for year in [2018,2022]:
    sub=comp[comp.Ano==year]
    vals=[]; counts=[]
    for mag in groups:
        g=sub if mag=='Total' else sub[sub.Magnitude==mag]
        vals.append(100*g.Competitivos.sum()/g.Candidatos.sum())
        counts.append([g.Competitivos.sum(),g.Candidatos.sum()])
    fig.add_trace(go.Bar(name=str(year),x=groups,y=vals,marker_color=COLORS[year],text=[number(v)+'%' for v in vals],textposition='outside',customdata=counts,hovertemplate='%{x}<br>%{y:.2f}% competitivas<br>%{customdata[0]} de %{customdata[1]} candidaturas<extra>%{fullData.name}</extra>'))
fig.update_layout(barmode='group',yaxis_title='Competitivas / total de candidaturas (%)',yaxis_range=[0,23])
chunks.append(chart(fig,'competitivas'))
note('Razão de somas de candidaturas, e não média dos percentuais das listas. Competitividade usa o histórico ex-ante da base consolidada. 2018: 886 de 7.630; 2022: 1.287 de 9.675.')
note('Correção de leitura: uma passagem de 13% para 13,6% seria aumento. Nos dados auditados dos distritos médios, porém, a comparação é 13,92% para 13,68%, um pequeno recuo. Os valores desta versão seguem a base, sem substituir essa comparação pelos números aproximados do relato.')
end()

section(2,'O núcleo se amplia e a concentração relativa diminui','O NECr médio sobe de 2,96 para 5,90, enquanto N/NECr diminui. O desvio-padrão do NECr passa de 3,17 para 4,87: a ampliação convive com maior dispersão entre listas. Isso não implica, por si só, perda de coordenação.')
fig=make_subplots(rows=1,cols=3,subplot_titles=['Candidatos formais (C)','Candidaturas efetivas (NECr)','Candidatos por efetiva (C/NECr)'])
for col,metric in enumerate(['C','NECr','Q'],1):
    for year in [2018,2022]:
        g=fund[fund.Ano==year]
        fig.add_trace(go.Box(y=g[metric],name=str(year),legendgroup=str(year),showlegend=col==1,marker_color=COLORS[year],boxmean='sd',boxpoints='outliers',jitter=.3,hovertemplate='%{y:.3f}<extra>'+str(year)+'</extra>'),row=1,col=col)
fig.update_yaxes(rangemode='tozero')
chunks.append(chart(fig,'distribuicoes',480))
note('Listas com recursos positivos: 786 em 2018 e 648 em 2022. Caixa: P25–P75; linha interna: mediana; marca pontilhada: média e desvio-padrão; pontos: observações além dos bigodes de 1,5 intervalo interquartil. Os extremos foram preservados.')
summary=[]
for metric,label in [('C','Candidatos'),('NECr','NECr'),('D','C − NECr'),('Q','C / NECr')]:
    for year in [2018,2022]:
        s=fund.loc[fund.Ano==year,metric]
        summary.append({'Indicador':label,'Ano':year,'Média':number(s.mean()),'DP':number(s.std()),'Mediana':number(s.median()),'N':len(s)})
chunks.append('<div class="tablewrap">'+pd.DataFrame(summary).to_html(index=False,border=0)+'</div>')
end()

section(3,'Mais candidaturas efetivas por cadeira de referência','A média de NECr/Mp aumenta em todas as magnitudes. Cada ponto representa a média das razões entre nominatas; a linha vertical mostra ±1 desvio-padrão.')
fig=go.Figure()
for year in [2018,2022]:
    g=fund[(fund.Ano==year)&(fund.Mp>0)].groupby('Magnitude').NECr_Mp.agg(['mean','std','median','count']).reindex(MAG)
    fig.add_trace(go.Scatter(x=MAG,y=g['mean'],mode='lines+markers',name=str(year),line_color=COLORS[year],marker_size=11,error_y=dict(type='data',array=g['std'],visible=True,thickness=1.5),customdata=g[['std','median','count']].to_numpy(),hovertemplate='%{x}<br>Média: %{y:.3f}<br>DP: %{customdata[0]:.3f}<br>Mediana: %{customdata[1]:.3f}<br>N: %{customdata[2]}<extra>%{fullData.name}</extra>'))
fig.add_hline(y=1,line_dash='dot',line_color='#62717a',annotation_text='NECr = Mp',annotation_position='bottom right')
fig.update_layout(yaxis_title='NECr / Mp',yaxis_rangemode='tozero')
chunks.append(chart(fig,'bancada'))
note('Somente listas com recursos positivos e Mp > 0: 290 em 2018; 250 em 2022. As barras indicam dispersão entre listas, não intervalo de confiança. Mp é a bancada disponível no arquivo local; a divergência entre a data do script e a redação da tese está documentada no relatório completo.')
magnitude_summary(fund[fund.Mp>0],'NECr_Mp','NECr / Mp','visual_necr_mp_magnitude',plot=False)
fig=go.Figure()
short=['Competitivos ≤ Mp + 1','NECr ≤ Mp + 1','NECr arredondado ≤ Mp + 1']
rules=['F ≤ Mp + 1','NECr ≤ Mp + 1 (contínuo)','NECr arredondado ≤ Mp + 1 (figura antiga)']
for year in [2018,2022]:
    g=limits[(limits.Ano==year)&(limits.Magnitude=='Total')].set_index('Regra').loc[rules]
    fig.add_trace(go.Bar(y=short,x=g['Dentro do limite (%)'],orientation='h',name=str(year),marker_color=COLORS[year],text=[number(v)+'%' for v in g['Dentro do limite (%)']],textposition='outside',customdata=g[['Listas dentro do limite','N']],hovertemplate='%{y}<br>%{x:.2f}%<br>%{customdata[0]} / %{customdata[1]} listas<extra>%{fullData.name}</extra>'))
fig.update_layout(barmode='group',xaxis_range=[0,105],xaxis_title='Listas dentro do limite (%)',yaxis_autorange='reversed')
chunks.append('<h3>O arredondamento altera a proporção dentro de Mp + 1</h3>'+chart(fig,'limites',370))
note('Competitivos: todas as listas com Mp > 0 (292 e 252). NECr: também exige recursos positivos (290 e 250). A regra contínua é distinta da regra arredondada usada nas figuras antigas. Os 84,93% e 45,63% corrigem os 94% e 56% registrados no texto.')
end()

section(4,'O número efetivo financiado costuma superar o de eleitos','Entre listas financiadas com eleitos, NECr/E tem média 2,13 em 2018 e 3,98 em 2022. Os pontos acima da diagonal representam mais candidaturas efetivas em recursos do que eleitos.')
fig=make_subplots(rows=1,cols=2,subplot_titles=['2018 · 300 listas','2022 · 207 listas'],shared_yaxes=True,shared_xaxes=True)
for col,year in enumerate([2018,2022],1):
    g=fund[(fund.Ano==year)&(fund.E>0)]
    fig.add_trace(go.Scatter(x=g.E,y=g.NECr,mode='markers',name=str(year),marker=dict(color=COLORS[year],size=8,opacity=.6),customdata=g[['Partido','UF','NECr_E','C']].to_numpy(),hovertemplate='%{customdata[0]} · %{customdata[1]}<br>Eleitos: %{x}<br>NECr: %{y:.3f}<br>NECr/E: %{customdata[2]:.3f}<br>Candidatos: %{customdata[3]}<extra></extra>'),row=1,col=col)
    fig.add_trace(go.Scatter(x=[0,18],y=[0,18],mode='lines',line=dict(color='#687b84',dash='dot'),showlegend=False,hoverinfo='skip'),row=1,col=col)
fig.update_xaxes(title_text='Eleitos na nominata (E)',range=[0,18],dtick=3)
fig.update_yaxes(range=[0,40])
fig.update_yaxes(title_text='NECr',row=1,col=1)
chunks.append(chart(fig,'eleitos',500))
note('Mesmas escalas nos dois painéis; diagonal NECr = E. Passar o cursor identifica cada partido e UF. DP de NECr/E: 1,75 e 2,99; medianas: 1,63 e 3,15. As 486 e 441 listas financiadas sem eleitos ficam fora desta razão. Correspondência de escala não identifica quais candidatos venceram.')
chunks.append('<h3>NECr por eleito, comparado entre categorias de magnitude</h3>')
magnitude_summary(fund[fund.E>0],'NECr_E','NECr / eleitos','visual_necr_e_magnitude')
note('Pequeno: 8–12 cadeiras; médio: 16–31; grande: 39–70. Universo: nominatas com recursos positivos e ao menos um eleito. Cada nominata tem o mesmo peso na média da razão NECr/E.')
end()

section(5,'O Top-NECr contém a maioria dos eleitos','A cobertura nacional aumenta de 86,74% para 92,63%, enquanto a cobertura esperada por sorteio permanece próxima de 43,8%. A precisão cai de 19,20% para 12,43%: núcleos maiores contêm mais não eleitos. O lift avalia a focalização descontando o tamanho do núcleo.')
fig=make_subplots(rows=1,cols=2,subplot_titles=['Quantos eleitos estavam no núcleo?','Quantos priorizados foram eleitos?'])
main=calcular_benchmark(OUT)
for year in [2018,2022]:
    s=main.loc[year]
    fig.add_trace(go.Bar(x=['Top-NECr','Aleatório'],y=[s['Cobertura nacional (%)'],s['Cobertura aleatória (%)']],name=str(year),legendgroup=str(year),marker_color=COLORS[year],text=[number(s['Cobertura nacional (%)'])+'%',number(s['Cobertura aleatória (%)'])+'%'],textposition='outside',hovertemplate='%{x}: %{y:.2f}%<extra>%{fullData.name}</extra>'),row=1,col=1)
    fig.add_trace(go.Bar(x=['Top-NECr','Aleatório'],y=[s['Precisão nacional (%)'],s['Precisão aleatória (%)']],name=str(year),legendgroup=str(year),showlegend=False,marker_color=COLORS[year],text=[number(s['Precisão nacional (%)'])+'%',number(s['Precisão aleatória (%)'])+'%'],textposition='outside',hovertemplate='%{x}: %{y:.2f}%<extra>%{fullData.name}</extra>'),row=1,col=2)
fig.update_yaxes(range=[0,105],ticksuffix='%')
fig.update_layout(barmode='group')
chunks.append(chart(fig,'cobertura'))
note('Precisão aleatória nacional = Σ(k × E/C) / Σk: média das taxas E/C ponderada pelas posições de cada núcleo. Listas com k = 0 não contribuem para a precisão. Os lifts nacionais de cobertura e precisão são iguais: eleitos observados no núcleo / eleitos esperados ao acaso. Essa identidade decorre da agregação e não representa duas evidências independentes.')
chunks.append('<p><strong>Lift nacional:</strong> '+ '; '.join(f'{year}: {number(main.loc[year,"Lift nacional"])} vezes' for year in [2018,2022])+'. A precisão bruta diminui, mas a razão entre observados e esperados ao acaso aumenta.</p>')
note('Cobertura = eleitos no Top-k / 513. Precisão = eleitos no Top-k / total de posições Top-k. k = floor(NECr + 0,5); empates no corte recebem crédito fracionário. Incluem-se no denominador os três eleitos de 2018 em listas sem recursos. Benchmark: sorteio de k candidatos dentro de cada lista, preservando C e E. Cobertura elevada pode coexistir com precisão baixa quando o núcleo contém muitos candidatos não eleitos.')
chunks.append('<h3>Cobertura Top-NECr por magnitude: observada e esperada ao acaso</h3>')
by_mag=[]
for year in [2018,2022]:
    for mag in MAG:
        g=d[(d.Ano==year)&(d.Magnitude==mag)]
        hits=g.eleitos_top_arredondado.sum()
        seats=g.E.sum()
        positions=g.k_arredondado.sum()
        random=(g.E*g.k_arredondado/g.C).sum()
        by_mag.append({'Ano':year,'Magnitude':mag,'Eleitos':int(seats),'Eleitos no Top-NECr':hits,'Posições Top-k':int(positions),'Cobertura (%)':100*hits/seats,'Aleatória (%)':100*random/seats,'Precisão (%)':100*hits/positions,'Listas com eleitos':int((g.E>0).sum())})
by_mag=pd.DataFrame(by_mag)
by_mag.to_csv(OUT/'visual_cobertura_magnitude.csv',index=False,encoding='utf-8-sig')
fig=make_subplots(rows=1,cols=2,subplot_titles=['2018','2022'],shared_yaxes=True)
for col,year in enumerate([2018,2022],1):
    g=by_mag[by_mag.Ano==year]
    for metric,label,opacity,pattern in [('Cobertura (%)','Observada',1,''),('Aleatória (%)','Aleatória',.5,'/')]:
        fig.add_trace(go.Bar(x=g.Magnitude,y=g[metric],name=f'{year} · {label}',marker=dict(color=COLORS[year],opacity=opacity,pattern_shape=pattern),text=[number(v)+'%' for v in g[metric]],textposition='outside',customdata=g[['Eleitos','Listas com eleitos']],hovertemplate='%{x}<br>%{y:.2f}%<br>Eleitos no grupo: %{customdata[0]}<br>Listas com eleitos: %{customdata[1]}<extra>%{fullData.name}</extra>'),row=1,col=col)
fig.update_layout(barmode='group')
fig.update_yaxes(range=[0,110],ticksuffix='%')
fig.update_xaxes(tickvals=MAG,ticktext=['Pequeno<br>8–12','Médio<br>16–31','Grande<br>39–70'])
chunks.append(chart(fig,'cobertura_magnitude',490))
note('Cobertura agregada de cada magnitude = soma dos eleitos no Top-k / soma dos eleitos naquele grupo. O benchmark mantém o sorteio dentro de cada nominata. Os eleitos de listas sem recursos continuam no denominador. As proporções agregadas não recebem um desvio-padrão entre listas: essa distribuição é apresentada separadamente abaixo.')
display=by_mag.copy()
for col in ['Eleitos no Top-NECr','Cobertura (%)','Aleatória (%)','Precisão (%)']:
    display[col]=display[col].map(number)
chunks.append('<div class="tablewrap">'+display.to_html(index=False,border=0)+'</div>')
note('Em 2018, a cobertura agregada cai de aproximadamente 93% para 88% e 81% entre distritos pequenos, médios e grandes. Em 2022, fica em aproximadamente 94%, 90% e 93%: deixa de se deteriorar sistematicamente com a magnitude. Isso descreve a correspondência com a representação obtida, sem estimar uma melhora causal de capacidade partidária.')
chunks.append('<h3>Como a cobertura varia entre nominatas de cada magnitude?</h3>')
magnitude_summary(d[d.E>0],'Cobertura_pct','Cobertura por nominata (%)','visual_cobertura_listas_magnitude')
note('Média, DP e mediana da cobertura das listas com E > 0, incluindo listas sem recursos. Aqui cada nominata pesa igualmente; por isso a média pode diferir da cobertura agregada do gráfico anterior.')
chunks.append('<h3>Precisão Top-NECr por magnitude</h3>')
fig=go.Figure()
for year in [2018,2022]:
    g=by_mag[by_mag.Ano==year]
    fig.add_trace(go.Bar(x=g.Magnitude,y=g['Precisão (%)'],name=str(year),marker_color=COLORS[year],text=[number(v)+'%' for v in g['Precisão (%)']],textposition='outside',customdata=g[['Eleitos no Top-NECr','Posições Top-k']],hovertemplate='%{x}<br>Precisão: %{y:.2f}%<br>Eleitos no núcleo: %{customdata[0]:.3f}<br>Posições: %{customdata[1]}<extra>%{fullData.name}</extra>'))
fig.update_layout(barmode='group',yaxis_title='Eleitos no Top-k / posições Top-k (%)',yaxis_range=[0,105])
chunks.append(chart(fig,'precisao_magnitude',380))
magnitude_summary(fund,'Precisao_pct','Precisão por nominata (%)','visual_precisao_listas_magnitude',plot=False)
note('Barras: precisão agregada de cada magnitude. Tabela: distribuição da precisão entre nominatas financiadas, inclusive as que não elegeram candidatos. A precisão de uma lista sem posições Top-k é indefinida.')
fig=go.Figure()
for year in [2018,2022]:
    g=coverage[coverage.Ano==year].set_index('Regra de k').loc[['piso','arredondado','teto']]
    fig.add_trace(go.Scatter(x=['Piso','Arredondamento principal','Teto'],y=g['Cobertura nacional (%)'],mode='lines+markers+text',name=str(year),line_color=COLORS[year],marker_size=10,text=[number(v)+'%' for v in g['Cobertura nacional (%)']],textposition='top center',hovertemplate='%{x}<br>%{y:.3f}%<extra>%{fullData.name}</extra>'))
fig.update_layout(yaxis_range=[0,105],yaxis_title='Cobertura nacional (%)')
chunks.append('<h3>A cobertura permanece alta nas três regras de corte</h3>'+chart(fig,'robustez',340))
end()

chunks.append(focalizacao(d, focus, chart, number, COLORS))
chunks.append(contexto())

section(6,'Onde as médias são maiores?','O mapa de calor compara NECr/Mp por UF. A cor usa a mesma escala nas duas eleições; o cursor revela a média, o desvio-padrão, a mediana e o número de listas.')
g=fund[fund.Mp>0].groupby(['UF','Ano']).NECr_Mp.agg(['mean','std','median','count'])
ufs=sorted(d.UF.unique())
z=[]; custom=[]
for uf in ufs:
    vals=[]; extra=[]
    for year in [2018,2022]:
        s=g.loc[(uf,year)] if (uf,year) in g.index else pd.Series({'mean':np.nan,'std':np.nan,'median':np.nan,'count':0})
        vals.append(s['mean']); extra.append([s['std'],s['median'],s['count']])
    z.append(vals);custom.append(extra)
fig=go.Figure(go.Heatmap(z=z,x=['2018','2022'],y=ufs,customdata=custom,colorscale=[[0,'#f2f7f7'],[.5,'#72b7b5'],[1,'#165c70']],zmin=0,colorbar_title='NECr/Mp<br>médio',text=[[number(v) for v in row] for row in z],texttemplate='%{text}',hovertemplate='%{y} · %{x}<br>Média: %{z:.3f}<br>DP: %{customdata[0]:.3f}<br>Mediana: %{customdata[1]:.3f}<br>N: %{customdata[2]}<extra></extra>'))
fig.update_yaxes(autorange='reversed',dtick=1)
chunks.append(chart(fig,'mapa_uf',820))
note('Média não ponderada de nominatas financiadas com Mp > 0. A composição partidária varia entre UFs e eleições; este gráfico não estima efeitos da UF. Grupos pequenos devem ser lidos junto do N exibido no cursor.')
end()

section(7,'Explore partidos, UFs e magnitudes','Selecione um indicador e recortes. O gráfico e os cartões abaixo se atualizam juntos. Cada observação é uma nominata; os valores indefinidos são contabilizados e excluídos das estatísticas.')
metrics={'Fracao_nucleo_pct':'NEC-R / N (%)','Lift':'Lift dos eleitos acima do acaso','Excedente_pp':'Cobertura excedente (p.p.)','Aleatoria_pct':'Cobertura aleatória (%)','Cobertura_competitiva_pct':'Competitivos prévios no núcleo (%)','Lift_competitivo':'Lift dos competitivos prévios','NECr':'NECr','C':'Candidatos formais (C)','F':'Candidatos competitivos (F)','D':'C − NECr','Q':'C / NECr','NECr_Mp':'NECr / Mp','NECr_E':'NECr / eleitos','NECr_menos_E':'NECr − eleitos','Cobertura_pct':'Cobertura por nominata (%)','Precisao_pct':'Precisão por nominata (%)'}
def select(id_,label,values):
    return '<label>'+label+f'<select id="{id_}">'+''.join(f'<option value="{html.escape(str(k))}">{html.escape(str(v))}</option>' for k,v in values)+'</select></label>'
chunks.append('<div class="controls">'+select('metric','Indicador',metrics.items())+select('party','Partido',[('', 'Todos')]+[(p,p) for p in sorted(d.Partido.unique())])+select('uf','UF',[('','Todas')]+[(u,u) for u in ufs])+select('mag','Magnitude',[('','Todas')]+[(m,m) for m in MAG])+'</div><p id="scope" class="note"></p><div id="stats" class="cards"></div><div id="explorer" style="min-height:450px"></div><p id="empty" role="status"></p>')
note('As médias de cobertura e precisão neste explorador são médias entre listas, diferentes das razões nacionais de somas da seção 5. C e F incluem todas as nominatas do recorte; os indicadores de concentração excluem listas sem recursos. NECr/Mp e NECr/eleitos exigem denominadores positivos.')
end()
chunks.append('<footer><h2>Como ler e reproduzir</h2><p>Azul: 2018. Laranja: 2022. Desvio-padrão amostral (N − 1), médias não ponderadas entre nominatas, salvo razões agregadas explicitamente identificadas. Nenhum gráfico identifica efeitos causais.</p><p>Fontes: tabelas CSV do caderno auditado, derivadas de <code>rrd_df_novo.parquet</code>, <code>df_calibracao_lista.parquet</code>, <code>df_cobertura_top_necr_lista.parquet</code> e <code>bancada_partido_uf.csv</code>. <a href="resultados-capitulo-3.html">Consultar o relatório completo, definições e divergências de redação</a>.</p><p>Reprodução: <code>python tese/scripts/visualizar_capitulo3_v2.py</code>. Os dados e a biblioteca gráfica estão incorporados neste HTML: funciona sem internet. Os controles dos gráficos permitem ampliar, restaurar a escala e exportar em SVG.</p></footer>')

css='''*{box-sizing:border-box}body{margin:0;background:#f1f4f4;color:#233c46;font:16px/1.65 Arial,sans-serif}header{padding:58px max(5%,calc((100vw - 1150px)/2));background:#123f50;color:#fff}h1{font-size:clamp(30px,4vw,48px);line-height:1.14;max-width:880px;margin:14px 0 24px}header p{color:#dae9ed;max-width:850px}nav{display:flex;gap:18px;flex-wrap:wrap;font-size:14px}nav a{color:#fff}main{max-width:1200px;margin:auto;padding:22px}section{background:white;border:1px solid #dce6e8;border-radius:12px;padding:32px;margin:24px 0}h2{font-size:28px;line-height:1.25;margin:12px 0}h3{margin-top:32px;font-size:20px}.eyebrow{font-size:12px;letter-spacing:2px;font-weight:bold;color:#4f7c85}.lead{font-size:18px;max-width:950px}.note{font-size:14px;color:#4f6570;border-left:3px solid #b5cfd5;padding:8px 14px;background:#f5f8f9}.cards{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0}.card{flex:1;min-width:230px;background:#f3f7f8;padding:20px;border-top:4px solid #257a9b;border-radius:5px}.card.orange{border-color:#cc632e}.card strong{font-size:29px;display:block}.card small{display:block;color:#536a75}.controls{display:flex;flex-wrap:wrap;gap:16px;margin:25px 0}label{font-size:13px;font-weight:bold;flex:1;min-width:160px}select{width:100%;padding:12px;border:1px solid #a3bac2;border-radius:5px;color:#203c47;background:white;margin-top:7px}.tablewrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:right;padding:10px;border-bottom:1px solid #dde6e9}td:first-child,th:first-child{text-align:left}th{background:#edf4f5}footer{padding:30px;color:#4a626d;font-size:14px}a{color:#176c89}code{font-size:12px;overflow-wrap:anywhere}.legend{display:flex;gap:22px;font-weight:bold;margin:24px 0}.dot{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:6px}.js-plotly-plot{width:100%}@media(max-width:650px){main{padding:8px}section{padding:18px 10px}h2{font-size:23px}.lead{font-size:16px}}@media print{body{background:white}header{background:white;color:#123f50;padding:20px}header p{color:#233c46}nav,.controls{display:none}section{break-inside:avoid;border:0;padding:10px}.modebar{display:none!important}}'''
data=d.to_json(orient='records',force_ascii=False)
js=r'''
const DATA=__DATA__, LABELS=__LABELS__;
const nf=new Intl.NumberFormat('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
function fmt(x){return Number.isFinite(x)?nf.format(x):'—'}
function quantile(a,p){const x=(a.length-1)*p,i=Math.floor(x);return a.length?a[i]+(a[Math.min(i+1,a.length-1)]-a[i])*(x-i):NaN}
function update(){
 const metric=document.getElementById('metric').value;
 const filters=['party','uf','mag'].map(id=>document.getElementById(id).value);
 const base=DATA.filter(r=>(!filters[0]||r.Partido===filters[0])&&(!filters[1]||r.UF===filters[1])&&(!filters[2]||r.Magnitude===filters[2]));
 let traces=[],cards=[],total=0;
 for(const [year,color] of [[2018,'#257a9b'],[2022,'#cc632e']]){
  const group=base.filter(r=>r.Ano===year),valid=group.filter(r=>Number.isFinite(r[metric]));
  const values=valid.map(r=>r[metric]).sort((a,b)=>a-b),n=values.length;
  const mean=n?values.reduce((a,b)=>a+b,0)/n:NaN;
  const sd=n>1?Math.sqrt(values.reduce((a,b)=>a+(b-mean)**2,0)/(n-1)):NaN;
  total+=n;
  cards.push(`<div class="card ${year===2022?'orange':''}">${year} · média<strong>${fmt(mean)}</strong><small>Desvio-padrão: ${fmt(sd)} · Mediana: ${fmt(quantile(values,.5))}</small><small>P25: ${fmt(quantile(values,.25))} · P75: ${fmt(quantile(values,.75))}</small><small>Mínimo: ${fmt(values[0])} · Máximo: ${fmt(values[n-1])}</small><small>N válido: ${n} · Indefinidos: ${group.length-n}</small></div>`);
  traces.push({type:'box',y:valid.map(r=>r[metric]),text:valid.map(r=>r.Partido+' · '+r.UF),name:String(year),marker:{color},boxmean:'sd',boxpoints:'all',jitter:.35,pointpos:-1.6,hovertemplate:'%{text}<br>%{y:.3f}<extra>'+year+'</extra>'});
 }
 document.getElementById('stats').innerHTML=cards.join('');
 document.getElementById('scope').textContent='Recorte: '+base.length+' nominatas. Indicador: '+LABELS[metric]+'. Valores com denominador zero ou NECr indefinido não entram na distribuição.';
 document.getElementById('empty').textContent=total?'':'Não há observações válidas neste recorte.';
 Plotly.react('explorer',traces,{height:460,paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{family:'Arial',color:'#233c46'},margin:{l:65,r:20,t:35,b:60},separators:',.',yaxis:{title:{text:LABELS[metric]},zeroline:true},showlegend:false},{responsive:true,displaylogo:false,toImageButtonOptions:{format:'svg',filename:'cap3-explorador'}});
}
['metric','party','uf','mag'].forEach(id=>document.getElementById(id).addEventListener('change',update));update();
'''.replace('__DATA__',data).replace('__LABELS__',json.dumps(metrics,ensure_ascii=False))
nav='<a href="#argumento">Argumento</a><a href="#focalizacao">Focalização</a><a href="#instituicoes">Instituições</a>'+''.join(f'<a href="#s{i}">{label}</a>' for i,label in enumerate(['Competitivos','Distribuições','Bancada','Eleitos','Top-NECr','UFs','Explorar'],1))
doc='<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Capítulo 3 — Coordenação intrapartidária · Atlas v2</title><style>'+css+'</style><script>'+get_plotlyjs()+'</script></head><body><header><div class="eyebrow" style="color:#a6cbd5">TESE / CAPÍTULO 3 / 2018 E 2022</div><h1>Núcleos mais amplos, focalização persistente</h1><p>Da coordenação concentrada em 2018 à coordenação ampliada em 2022: amplitude, concentração relativa e focalização acima do acaso. Versão 2 · 10 de setembro de 2026.</p><div class="legend"><span><i class="dot" style="background:#54b4d6"></i>2018</span><span><i class="dot" style="background:#f19b68"></i>2022</span></div><nav>'+nav+'</nav></header><main>'+''.join(chunks)+'</main><script>'+js+'</script></body></html>'
target=OUT/'atlas-visual-capitulo-3-v2.html'
target.write_text(doc,encoding='utf-8')
assert len(figures)==14 and len(d)==1570
print(str(target))
print(f'{len(figures)} graficos narrativos + explorador interativo; {len(d)} nominatas; {target.stat().st_size} bytes.')
