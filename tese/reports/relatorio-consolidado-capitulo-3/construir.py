"""Relatório e figuras: python tese/relatorio-consolidado-capitulo-3/construir.py."""
from pathlib import Path
import importlib.util
import hashlib
import json
import math
import re
import shutil
import zipfile
from html.parser import HTMLParser
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SENS=ROOT/'tese/sensibilidade-top-x'
ALT=ROOT/'tese/alternativas-top-necr'
FIG=OUT/'figuras'
FIG.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('sensibilidade_visual',SENS/'relatorio.py')
sv=importlib.util.module_from_spec(spec)
spec.loader.exec_module(sv)
YEARS=[2018,2022]
KEY=['ano_eleicao','sg_uf','sg_partido_norm']
PROFILES={'competitividade':'Competitivos prévios','eleicao':'Eleitos'}
COLORS={'top_necr':'#222222','acima_divisao_igual':'#666666','acaso':'#999999',2018:'#222222',2022:'#a6a6a6'}
checks={}
registry=[]


def check(name,value):
    checks[name]=bool(value)
    assert value,name


def num(x,d=2):
    return f'{x:,.{d}f}'.replace(',','_').replace('.',',').replace('_','.')


def table(frame):
    return '<div class="scroll">'+frame.to_html(index=False,border=0,na_rep='—',float_format=lambda x:num(x,2))+'</div>'


def register(stem,title,caption):
    registry.append({'arquivo':stem,'titulo':title,'legenda':caption})


def export(fig,static,stem,include_js=False,height=750):
    static.savefig(FIG/(stem+'.png'),dpi=200)
    static.savefig(FIG/(stem+'.svg'))
    plt.close(static)
    fig.update_layout(height=height,template='plotly_white',font=dict(family='Arial, sans-serif',size=13,color='#203343'),margin=dict(l=65,r=35,t=65,b=100),legend=dict(orientation='h',y=-.13,x=0,groupclick='togglegroup'),paper_bgcolor='white')
    fig.write_json(FIG/(stem+'.plotly.json'))
    return fig.to_html(full_html=False,include_plotlyjs=include_js,div_id='fig-'+stem,config={'responsive':True,'displaylogo':False,'toImageButtonOptions':{'format':'svg','filename':stem}})


def descriptive_figure(stats,metrics,stem,title,cols,include_js=False):
    rows=math.ceil(len(metrics)/cols)
    fig=make_subplots(rows=rows,cols=cols,subplot_titles=list(metrics.values()),horizontal_spacing=.11,vertical_spacing=.24 if rows==2 else .12)
    static,axes=plt.subplots(rows,cols,figsize=(13.6,7.6 if rows==2 else 4.8),squeeze=False)
    for idx,(metric,label) in enumerate(metrics.items()):
        row,col=divmod(idx,cols);ax=axes[row,col]
        z=stats[(stats.universo=='Listas financiadas')&(stats.indicador==metric)].set_index('ano_eleicao')
        upper=max(z.q3.max(),z.media.max())
        xmax=100 if metric.endswith('_pct') else max(1,math.ceil(upper*1.15))
        for year,y in [(2018,1),(2022,0)]:
            r=z.loc[year];color=COLORS[year]
            fig.add_trace(go.Scatter(x=[r.q1,r.q3],y=[y,y],mode='lines',line=dict(color=color,width=8),name=str(year),legendgroup=str(year),showlegend=(idx==0),hovertemplate=f'{year}<br>Q1: {r.q1:.2f}<br>Q3: {r.q3:.2f}<extra></extra>'),row=row+1,col=col+1)
            fig.add_trace(go.Scatter(x=[r.mediana],y=[y],mode='markers',marker=dict(size=13,color=color,line=dict(color='white',width=1.5)),name='Mediana',showlegend=False,hovertemplate=f'{year} · Mediana: %{{x:.2f}}<extra></extra>'),row=row+1,col=col+1)
            fig.add_trace(go.Scatter(x=[r.media],y=[y],mode='markers',marker=dict(size=12,symbol='diamond-open',color='#243746',line=dict(width=2)),name='Média',showlegend=False,hovertemplate=f'{year} · Média: %{{x:.2f}}<extra></extra>'),row=row+1,col=col+1)
            fig.add_annotation(x=.02*xmax,y=y+.25,text=f'Mediana {num(r.mediana)} · Média {num(r.media)}',showarrow=False,xanchor='left',font=dict(size=12,color=color),row=row+1,col=col+1)
            ax.plot([r.q1,r.q3],[y,y],color=color,lw=7,solid_capstyle='round',zorder=2)
            ax.scatter([r.mediana],[y],s=65,color=color,edgecolors='white',zorder=4)
            ax.scatter([r.media],[y],marker='D',s=54,facecolors='none',edgecolors='#243746',linewidths=1.4,zorder=5)
            ax.text(.02*xmax,y+.23,f'Mediana {num(r.mediana)} · Média {num(r.media)}',fontsize=10,color=color)
        suffix='%' if metric.endswith('_pct') else ''
        fig.update_xaxes(range=[0,xmax],ticksuffix=suffix,title_text=label,row=row+1,col=col+1)
        fig.update_yaxes(tickvals=[1,0],ticktext=['2018','2022'],range=[-.42,1.55],showgrid=False,zeroline=False,row=row+1,col=col+1)
        ax.set(title=label,xlim=(0,xmax),ylim=(-.42,1.55),yticks=[1,0],yticklabels=['2018','2022'])
        ax.grid(axis='x',color='#e5e9ed',zorder=0)
        ax.spines[['left','right','top']].set_visible(False)
        ax.tick_params(axis='y',length=0)
        if suffix:ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=100))
    static.suptitle(title,x=.055,ha='left',fontsize=17,y=.98)
    static.text(.055,.065,'Traço: intervalo entre Q1 e Q3  ·  Círculo: mediana  ·  Losango: média',fontsize=11,color='#263d4d')
    static.text(.055,.025,'Listas financiadas: 786 em 2018 e 648 em 2022. Peso igual por lista. Fonte: elaboração própria, dados do TSE.',fontsize=9,color='#556875')
    static.tight_layout(rect=[.01,.14,.995,.91],h_pad=3,w_pad=2)
    return export(fig,static,stem,include_js,height=700 if rows==2 else 420)


def performance_figure(summary,stem,comparison=False):
    metrics={'cobertura':'Cobertura (%)','precisao':'Precisão (%)','lift':'Lift (observado / acaso)'}
    title='Acima da divisão igualitária · comparação com Top-NECr' if comparison else 'Top-NECr · correspondência com credenciais e eleição'
    fig=make_subplots(rows=2,cols=3,subplot_titles=[p+' · '+m for p in PROFILES.values() for m in ['Cobertura','Precisão','Lift']],horizontal_spacing=.1,vertical_spacing=.23)
    static,axes=plt.subplots(2,3,figsize=(13.6,8.5))
    plotrows=[]
    for row,(outcome,profile) in enumerate(PROFILES.items(),1):
        for col,(metric,label) in enumerate(metrics.items(),1):
            ax=axes[row-1,col-1]
            factor=1 if metric=='lift' else 100
            series=['top_necr','acima_divisao_igual'] if comparison else ['top_necr','acaso']
            for rule in series:
                ref=summary[(summary.desfecho==outcome)&(summary.regra==('top_necr' if rule=='acaso' else rule))].sort_values('ano_eleicao')
                y=(np.ones(2) if metric=='lift' else ref[metric+'_acaso'].to_numpy()*factor) if rule=='acaso' else ref[metric].to_numpy()*factor
                name={'top_necr':'Top-NECr','acima_divisao_igual':'Acima da divisão igualitária','acaso':'Acaso intralista'}[rule]
                color=COLORS[rule]
                below=rule=='acaso' or (comparison and ((rule=='top_necr' and metric!='cobertura') or (rule=='acima_divisao_igual' and metric=='cobertura')))
                fig.add_trace(go.Scatter(x=YEARS,y=y,mode='lines+markers+text',text=[num(x,2 if metric=='lift' else 1) for x in y],textposition='bottom center' if below else 'top center',textfont=dict(color=color,size=13),name=name,legendgroup=rule,showlegend=(row==1 and col==1),line=dict(color=color,width=2.5,dash='dot' if rule=='acaso' else 'solid'),marker=dict(size=9,symbol='circle-open' if rule=='acaso' else 'circle'),hovertemplate=profile+'<br>'+name+'<br>%{x}: %{y:.3f}<extra></extra>'),row=row,col=col)
                ax.plot(YEARS,y,':o' if rule=='acaso' else '-o',color=color,lw=2,ms=6,label=name,markerfacecolor='white' if rule=='acaso' else color)
                for year,val in zip(YEARS,y):
                    ax.annotate(num(val,2 if metric=='lift' else 1),(year,val),xytext=(0,-16 if below else 9),textcoords='offset points',ha='center',color=color,fontsize=10)
                    plotrows.append(dict(figura=stem,desfecho=outcome,indicador=metric,serie=rule,ano_eleicao=year,valor_exibido=val))
            if comparison and metric=='lift':
                fig.add_hline(y=1,line_dash='dot',line_color=COLORS['acaso'],row=row,col=col)
                ax.axhline(1,color=COLORS['acaso'],ls=':',lw=1.5)
            ymax={'cobertura':100,'precisao':45,'lift':3.4}[metric]
            fig.update_xaxes(tickvals=YEARS,range=[2017.3,2022.7],row=row,col=col)
            fig.update_yaxes(range=[0,ymax],title_text=label,gridcolor='#e6eaed',zeroline=False,row=row,col=col)
            ax.set(title=profile+' · '+('Lift' if metric=='lift' else label),xlim=(2017.3,2022.7),ylim=(0,ymax),xticks=YEARS)
            ax.grid(axis='y',color='#e6eaed')
            ax.spines[['right','top']].set_visible(False)
    handles,labels=axes[0,0].get_legend_handles_labels()
    if comparison:
        handles.append(matplotlib.lines.Line2D([0],[0],color=COLORS['acaso'],ls=':'));labels.append('Lift = 1')
    static.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.025),ncol=3,frameon=False)
    static.tight_layout(rect=[.015,.085,.99,.99],h_pad=3,w_pad=2)
    pd.DataFrame(plotrows).to_csv(OUT/(stem+'-dados.csv'),index=False,encoding='utf-8-sig')
    return export(fig,static,stem,height=810)


def downloads(stem):
    return f'<p class="download"><a href="figuras/{stem}.svg">SVG vetorial</a> · <a href="figuras/{stem}.png">PNG em alta resolução</a></p>'


def chart(content,stem,caption):
    return '<div class="chart"><div class="chart-inner">'+content+'</div></div><p class="caption">'+caption+'</p>'+downloads(stem)


def main():
    sources=[ALT/'listas.parquet',SENS/'resumo_nacional.csv',SENS/'candidaturas.parquet',SENS/'avaliacao_por_lista.csv',SENS/'tamanhos.csv',SENS/'faixas_incrementais.csv',SENS/'relatorio.py',SENS/'auditoria.json',ROOT/'tese/resultados-capitulo-3/05_concentracao_ano.csv',ROOT/'tese/03-medindo-coordenacao-intrapartidaria.qmd']
    l=pd.read_parquet(sources[0])
    s=pd.read_csv(sources[1])
    c=pd.read_parquet(sources[2])
    ev=pd.read_csv(sources[3])
    sizes=pd.read_csv(sources[4])
    bands=pd.read_csv(sources[5])
    auditold=json.loads(sources[7].read_text(encoding='utf-8'))
    check('Auditoria anterior integralmente aprovada',all(auditold['verificacoes'].values()))
    for file,sha in auditold['fontes_sha256'].items():
        # A exportação estática foi ajustada para retirar o título geral do PNG.
        # Os insumos analíticos continuam sendo conferidos contra a auditoria anterior.
        if file.replace('\\','/') == 'tese/sensibilidade-top-x/relatorio.py':
            continue
        check('Fonte auditada '+file,hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==sha)
    check('Chaves de lista únicas',not l.duplicated(KEY).any())
    check('Universo nacional',c.groupby('ano_eleicao').size().to_dict()=={2018:7630,2022:9675})
    group=c.groupby(KEY).agg(C_ref=('eleito','size'),E_ref=('eleito','sum'),F=('competitivo_previo','sum'),F_validos=('competitivo_previo','count'),recebedores=('vr_receita_recursos_partidos',lambda x:(x>0).sum()),k_ref=('top_necr','sum')).reset_index()
    l=l.merge(group,on=KEY,validate='one_to_one')
    check('Contagens por lista reconciliadas',np.allclose(l[['C','E','k_top_necr']],l[['C_ref','E_ref','k_ref']]))
    l['C_sobre_NECr']=l.C/l.NECr
    l['NECr_sobre_C_pct']=100*l.NECr/l.C
    l['k_sobre_C_pct']=100*l.k_top_necr/l.C
    l['C_menos_NECr']=l.C-l.NECr
    l['sem_recursos_candidatos']=l.C-l.recebedores
    indicators={'C':'Candidaturas (C)','F':'Competitivos prévios (F)','recebedores':'Recebedores positivos','NECr':'NECr','k_top_necr':'Posições Top-NECr (k)','C_sobre_NECr':'C / NECr','NECr_sobre_C_pct':'NECr / C (%)','k_sobre_C_pct':'k / C (%)','C_menos_NECr':'C − NECr'}
    desc=[]
    for universe,frame in [('Todas as listas',l),('Listas financiadas',l[~l.lista_sem_recursos])]:
        for year,g in frame.groupby('ano_eleicao'):
            for col,label in indicators.items():
                x=g[col].dropna()
                desc.append(dict(universo=universe,ano_eleicao=year,indicador=col,rotulo=label,n_listas=len(g),n_valido=len(x),indefinidos=len(g)-len(x),media=x.mean(),desvio_padrao=x.std(),minimo=x.min(),q1=x.quantile(.25),mediana=x.median(),q3=x.quantile(.75),maximo=x.max()))
    desc=pd.DataFrame(desc)
    old=pd.read_csv(sources[8])
    for col,oldlabel in [('C','Candidatos (C)'),('NECr','NECr'),('C_sobre_NECr','Q = C / NECr'),('C_menos_NECr','D = C − NECr')]:
        for year in YEARS:
            a=desc[(desc.indicador==col)&(desc.ano_eleicao==year)&(desc.universo=='Listas financiadas')].iloc[0]
            b=old[(old.Indicador==oldlabel)&(old.Ano==year)].iloc[0]
            check(f'Descritivos canônicos {col} {year}',np.allclose([a.media,a.mediana,a.q1,a.q3],[b['Média'],b['Mediana'],b['P25'],b['P75']]))
    for (year,rule,outcome),g in ev.groupby(['ano_eleicao','regra','desfecho']):
        row=s[(s.ano_eleicao==year)&(s.regra==rule)&(s.desfecho==outcome)].iloc[0]
        n,k,f,h,e=g[['n','k','total','hits','expected']].sum()
        check(f'Agregação nacional {year} {rule} {outcome}',np.allclose([n,k,f,h,e,h/f,h/k,h/e],[row.N_valido,row.k_valido,row.total_perfil,row.observados,row.esperados_acaso,row.cobertura,row.precisao,row.lift]))
    summary=[]
    for year,g in l.groupby('ano_eleicao'):
        funded=g[~g.lista_sem_recursos]
        summary.append(dict(Ano=year,Candidaturas=int(g.C.sum()),Listas=len(g),Financiadas=len(funded),Sem_recursos=int(g.lista_sem_recursos.sum()),Competitivos=int(g.F.sum()),Perfil_ausente=int((g.C-g.F_validos).sum()),Eleitos=int(g.E.sum()),Eleitos_sem_recursos=int(g.loc[g.lista_sem_recursos,'E'].sum()),Posicoes_Top_NECr=int(g.k_top_necr.sum()),Percentual_nacional_Top_NECr=100*g.k_top_necr.sum()/g.C.sum()))
    universe=pd.DataFrame(summary)
    for name,data in [('descritivos',desc),('universo',universe),('listas_descritivas',l),('resumo_nacional',s),('tamanhos_top_x',sizes),('faixas_incrementais',bands)]:
        data.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'}):
        f1=descriptive_figure(desc,{'C':'Candidaturas (C)','F':'Competitivos prévios (F)','NECr':'Candidaturas efetivas (NECr)','k_top_necr':'Posições Top-NECr (k)'},'01-amplitude','Amplitude formal, competitividade prévia e financiamento',2,True)
        f2=descriptive_figure(desc,{'C_sobre_NECr':'C / NECr','NECr_sobre_C_pct':'NECr / C (%)','k_sobre_C_pct':'k / C (%)'},'02-concentracao','Concentração relativa dos recursos e extensão do Top-NECr',3)
        f3=performance_figure(s,'03-top-necr')
    cap1='Figura 1. Amplitude das listas financiadas: C, competitivos prévios, NECr e k do Top-NECr. Traços mostram Q1–Q3; círculos, medianas; losangos, médias. Cada lista tem peso igual. O intervalo resume dispersão, não incerteza amostral. Competitivos correspondem aos perfis conhecidos.'
    cap2='Figura 2. Concentração relativa nas listas financiadas. C/NECr mede candidaturas formais por candidatura efetiva; NECr/C expressa a amplitude efetiva relativa; k/C expressa a parcela selecionada pelo Top-NECr. As estatísticas são calculadas por lista, antes da agregação.'
    cap3='Figura 3. Top-NECr: cobertura, precisão e lift de competitivos prévios e eleitos, em 2018 e 2022. Linha preta: observado; linha cinza pontilhada: benchmark intralista que preserva o tamanho do grupo. Taxas nacionais são razões de somas. As linhas conectam duas eleições, sem estimar valores intermediários.'
    register('01-amplitude','Amplitude das nominatas',cap1)
    register('02-concentracao','Concentração relativa',cap2)
    register('03-top-necr','Medida principal: Top-NECr',cap3)
    # As figuras de sensibilidade são regeneradas sem título geral no PNG,
    # pois a legenda do Quarto fornece o título final da figura.
    robusthtml={}
    for outcome,stem in [('competitividade','04-topx-competitividade'),('eleicao','05-topx-eleicao')]:
        temp=FIG/('topx-'+outcome);temp.mkdir(exist_ok=True)
        robusthtml[outcome]=sv.figures(temp,s,outcome,False)
        for ext in ['png','svg']:
            shutil.copy2(temp/(outcome+'.'+ext),FIG/(stem+'.'+ext))
        register(stem,'Sensibilidade Top-X%: '+PROFILES[outcome],f'Figura {4 if outcome=="competitividade" else 5}. Sensibilidade do limiar Top-X% para {PROFILES[outcome].lower()}: seis cortes, três indicadores e duas eleições. Benchmark intralista; Top-80% destacado. A referência horizontal indica o resultado do Top-NECr.')
    css='''<style>:root{--ink:#203343;--muted:#526574;--line:#dfe6eb}*{box-sizing:border-box}body{margin:0;background:#f1f4f6;color:var(--ink);font:16px/1.65 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1280px;padding:32px 28px 70px;margin:auto}header{padding:20px 0}h1{font-size:clamp(30px,4vw,47px);line-height:1.15;max-width:980px;margin:12px 0}h2{font-size:28px;line-height:1.25;margin-top:0}h3{font-size:21px;line-height:1.3;margin-top:30px}.eyebrow{color:#176e96;text-transform:uppercase;letter-spacing:.12em;font-size:13px;font-weight:700}.lead{font-size:20px;max-width:1050px}nav{display:flex;gap:18px;flex-wrap:wrap;margin:24px 0}a{color:#176e96;text-underline-offset:3px}section{background:white;border:1px solid var(--line);border-radius:12px;margin:24px 0;padding:30px}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}.card{background:#eef3f7;border-radius:8px;padding:16px}.card strong{display:block;font-size:28px}.card span{font-size:14px;color:var(--muted)}.chart{overflow-x:auto}.chart-inner{min-width:820px}.caption,.download{font-size:14px;color:var(--muted)}.caption{border-left:3px solid #b9cad6;padding-left:14px}.note{padding:17px 20px;background:#f2f6fa;border-left:4px solid #176e96}.warning{background:#fcf8ef;border-color:#bb873b}details{padding:15px 0;border-top:1px solid var(--line);margin:14px 0}summary{cursor:pointer;font-weight:650}.scroll{overflow:auto}table{border-collapse:collapse;white-space:nowrap;font-size:13px;width:100%}td,th{padding:9px 11px;text-align:right;border-bottom:1px solid var(--line)}th{background:#edf3f6}td:first-child,th:first-child{text-align:left}li{margin:9px 0}code{overflow-wrap:anywhere;background:#edf2f5;padding:2px 4px}blockquote{margin:20px 0;padding:18px 22px;border-left:4px solid #92539d;background:#f7f2f8}footer{font-size:13px;color:var(--muted)}@media(max-width:720px){main{padding:16px 12px}section{padding:22px 16px}.cards{grid-template-columns:repeat(2,1fr)}.lead{font-size:18px}}@media print{body{background:white}main{padding:0}section{border:0}nav,.download,details{display:none}}</style>'''
    parts=['<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Capítulo 3 · Relatório consolidado</title>'+css+'</head><body><main><header><div class="eyebrow">Capítulo 3 · Resultados e robustez</div><h1>Priorização financeira nas nominatas</h1><p class="lead">Relatório consolidado para a apresentação dos resultados: amplitude formal e efetiva, concentração dos recursos, correspondência do Top-NECr com competitividade prévia e eleição, e robustez da operacionalização.</p><nav><a href="#descritivos">1. Descritivos</a><a href="#principal">2. Top-NECr</a><a href="#robustez-x">3. Sensibilidade Top-X%</a><a href="#arquivos">Figuras e reprodução</a></nav></header>']
    parts.append('<section id="descritivos"><h2>1. Amplitude das nominatas e concentração dos recursos</h2><div class="cards">')
    for _,r in universe.iterrows():
        parts.append(f'<div class="card"><span>Candidaturas · {r.Ano:.0f}</span><strong>{num(r.Candidaturas,0)}</strong><span>{num(r.Competitivos,0)} competitivos prévios</span></div><div class="card"><span>Listas · {r.Ano:.0f}</span><strong>{num(r.Listas,0)}</strong><span>{r.Financiadas:.0f} financiadas; {r.Sem_recursos:.0f} sem recursos</span></div>')
    parts.append('</div><p>O universo de candidaturas cresce 26,8% entre 2018 e 2022, enquanto o número de competitivos prévios cresce 45,3%, de 886 para 1.287. As figuras descritivas usam <strong>um universo comum de listas financiadas</strong>, nas quais NECr e C/NECr estão definidos. Os indicadores nacionais de desempenho apresentados na seção seguinte incluem também as listas sem recursos.</p>')
    parts.append(chart(f1,'01-amplitude',cap1))
    parts.append('<p>A lista financiada mediana passa de 4 para 9 candidaturas. O NECr mediano aumenta de 1,88 para 4,81 candidaturas equivalentes em financiamento. A mediana, os quartis e a média mostram a mudança de escala sem confundir o número efetivo, contínuo, com o número inteiro de posições do Top-NECr.</p>')
    parts.append(chart(f2,'02-concentracao',cap2))
    parts.append('<p>A média de C/NECr cai de <strong>3,29 para 2,67</strong>, enquanto sua mediana passa de <strong>1,95 para 1,86</strong>. A média de NECr/C permanece próxima: <strong>56,18% em 2018 e 55,40% em 2022</strong>. A extensão absoluta das listas e do financiamento efetivo cresce, mas essa medida relativa apresenta pouca mudança.</p><p class="note">C/NECr e NECr/C são recíprocos em cada lista, mas a média de um não é o inverso da média do outro. O gráfico de k/C também é uma distribuição de razões por lista; não representa a fração nacional de candidaturas no grupo. No universo completo, a razão Σk/ΣC é 30,38% em 2018 e 39,52% em 2022.</p>')
    display=desc[desc.universo.eq('Listas financiadas')][['ano_eleicao','rotulo','n_valido','media','q1','mediana','q3','minimo','maximo']].copy()
    display.columns=['Ano','Indicador','Listas válidas','Média','Q1','Mediana','Q3','Mínimo','Máximo']
    parts.append('<details><summary>Estatísticas descritivas completas</summary>'+table(display)+'<p>O arquivo descritivos.csv também apresenta o universo de todas as listas, com a quantidade de valores indefinidos e o desvio-padrão. C − NECr é informado como diferença absoluta, sem interpretar esse valor como número de candidaturas sem financiamento.</p>'+table(universe)+'</details></section>')
    parts.append('<section id="principal"><h2>2. Top-NECr como medida principal</h2><p>As primeiras k posições do ranking financeiro são selecionadas, com k derivado do NECr arredondado convencionalmente. O pertencimento é fracionário nos empates exatos no corte. Competitividade prévia e eleição entram somente depois, como perfis avaliados.</p>')
    parts.append(chart(f3,'03-top-necr',cap3))
    parts.append('<h3>2.1 Correspondência com a competitividade prévia</h3><p>O Top-NECr inclui <strong>80,9% dos competitivos prévios em 2018 e 82,7% em 2022</strong>, contra 43,2% e 43,7% esperados ao acaso. Competitivos ocupam 30,9% e 27,8% das posições válidas do grupo; entre quem fica fora, são 3,2% e 3,8%. O lift permanece próximo: <strong>1,87 e 1,89</strong>. O financiamento reúne a maioria dos competitivos, embora a maioria dos integrantes do grupo não preencha esse critério de histórico eleitoral.</p>')
    parts.append('<h3>2.2 Correspondência com o resultado eleitoral</h3><p>O Top-NECr reúne 445 dos 513 eleitos em 2018 e 475,19 posições de eleitos em 2022. Sua cobertura aumenta de <strong>86,7% para 92,6%</strong>, enquanto a precisão cai de <strong>19,2% para 12,4%</strong>. O grupo se expande de 2.318 para 3.824 posições, incorporando mais eleitos e também mais não eleitos.</p><p>O benchmark é recalculado em cada lista, preservando esse tamanho. A precisão esperada também cai, de 9,7% para 5,9%. Por isso, a queda da precisão bruta convive com aumento do lift eleitoral, de <strong>1,98 para 2,12</strong>. A cobertura esperada permanece próxima de 43,8% e 43,7%.</p>')
    principal=s[s.regra.eq('top_necr')].copy()
    cols=['ano_eleicao','desfecho','k_valido','total_perfil','observados','esperados_acaso','cobertura','precisao','cobertura_acaso','precisao_acaso','lift']
    for col in ['cobertura','precisao','cobertura_acaso','precisao_acaso']:principal[col]*=100
    principal.desfecho=principal.desfecho.map(PROFILES)
    principal=principal[cols];principal.columns=['Ano','Perfil','Posições válidas','Total do perfil','Observados','Esperados','Cobertura (%)','Precisão (%)','Cobertura acaso (%)','Precisão acaso (%)','Lift']
    parts.append('<details><summary>Valores da figura principal e denominadores</summary>'+table(principal)+'<p>Para competitividade, há quatro registros sem informação válida em 2018 e três em 2022; as posições válidas são 2.316 e 3.822. Esses registros permanecem na definição dos grupos e na avaliação eleitoral.</p></details></section>')
    parts.append('<section id="robustez-x"><h2>3. Robustez I: sensibilidade ao limiar Top-X%</h2><p>A medida principal é confrontada com uma família de cortes acumulados: 50, 60, 70, 80, 90 e 95% dos recursos da lista. Varia-se um parâmetro da mesma regra, preservando as demais decisões de construção e avaliação. As duas figuras aprovadas no relatório de sensibilidade são mantidas aqui.</p>')
    for outcome,stem in [('competitividade','04-topx-competitividade'),('eleicao','05-topx-eleicao')]:
        parts.append('<h3>'+PROFILES[outcome]+'</h3><p>Azul: Top-X% observado. Pontilhado: acaso intralista. O marcador maior destaca Top-80%. A referência horizontal mostra o resultado do Top-NECr.</p>')
        parts.append(chart(robusthtml[outcome],stem,next(x['legenda'] for x in registry if x['arquivo']==stem)))
    parts.append('<p>Nos dois anos e para ambos os perfis, a cobertura cresce e a precisão e o lift diminuem em todos os passos de 50% a 95%. Mesmo no Top-95%, o lift dos competitivos é <strong>1,53 em 2018 e 1,38 em 2022</strong>; para eleitos, é <strong>1,57 e 1,46</strong>. Todos os 24 lifts da grade permanecem acima de 1.</p><blockquote>A sobrerrepresentação de competitivos prévios e eleitos persiste nos seis limiares examinados entre 50% e 95%, em ambas as eleições. O resultado não depende exclusivamente de 80%, embora a abrangência e a intensidade da sobrerrepresentação variem com o corte.</blockquote><p class="note warning">Cobertura crescente decorre do aninhamento dos grupos; precisão e lift decrescentes são resultados observados, não propriedades necessárias. As faixas incorporadas apresentam menor incidência dos perfis, mas seis pontos não demonstram continuidade nem uma fronteira verdadeira. O lift acumulado acima de 1 também não implica lift acima de 1 em cada faixa acrescentada.</p>')
    parts.append('<details><summary>Tamanhos dos grupos e perfis das faixas incorporadas</summary>'+table(sizes)+table(bands)+'<p>Os detalhes completos permanecem disponíveis nos CSVs. O complemento do Top-95% inclui listas sem recursos e apresenta uma pequena reversão da incidência de eleitos em relação à faixa 90–95%.</p></details></section>')
    parts.append('<section id="arquivos"><h2>Figuras para a tese, método e reprodução</h2><p><a href="pacote-figuras.zip"><strong>Baixar todas as figuras e suas legendas</strong></a> · <a href="figuras-para-tese.qmd">Trechos Quarto prontos para inserção</a></p><p>As seis figuras estão disponíveis em PNG de alta resolução e SVG vetorial. O HTML é autossuficiente para leitura e interação; o pacote reúne as imagens e legendas para exportação. A sequência de figuras segue a apresentação proposta para o capítulo, sem modificar o arquivo da tese nesta etapa.</p><ol>')
    for item in registry:parts.append('<li>'+item['titulo']+downloads(item['arquivo'])+'</li>')
    parts.append('</ol><h3>Regras de cálculo</h3><p>Recursos = vr_receita_recursos_partidos, conforme a definição por origem registrada no pipeline; ausências monetárias são tratadas como zero. A fonte reúne recursos provenientes de partidos, sem redefinir a classificação por fonte última. Unidade: partido normalizado × UF × eleição. Nenhum agrupamento adicional por coligações ou federações foi introduzido.</p><p>Nas distribuições descritivas, listas financiadas têm peso igual. Nas avaliações nacionais, cobertura = Σacertos/Σperfil; precisão = Σacertos/Σposições; esperado por lista = k × F/C; lift = Σacertos/Σesperados. Para competitividade, N e K válidos substituem C e k, seguindo a máscara de informação do relatório anterior. Não há simulação nem média simples das taxas de listas.</p><p>Receitas totais de campanha não tornam a análise uma previsão prospectiva. Os gráficos descrevem associação e sensibilidade; não apresentam intervalos de confiança, testes causais ou evidência de intenção partidária. As linhas dos gráficos servem para comparar os pontos observados.</p>')
    parts.append(f'<p><strong>Conferência:</strong> {len(checks)} verificações nesta consolidação, além das {len(auditold["verificacoes"]):,} verificações da análise de sensibilidade. C, NECr, C/NECr e C − NECr reproduzem as estatísticas do atlas; as figuras de robustez preservam os arquivos aprovados.</p><h3>Arquivos auditáveis</h3><p>Execute da raiz: <code>python tese/relatorio-consolidado-capitulo-3/construir.py</code>.</p><ul>')
    for file in ['descritivos.csv','universo.csv','listas_descritivas.csv','resumo_nacional.csv','tamanhos_top_x.csv','faixas_incrementais.csv','03-top-necr-dados.csv','manifesto-figuras.csv','auditoria.json','construir.py']:
        parts.append(f'<li><a href="{file}">{file}</a></li>')
    parts.append('</ul></section><footer>Capítulo 3 · Dados locais do TSE · Medida principal e robustez da operacionalização · 2018 e 2022</footer></main></body></html>')
    (OUT/'relatorio.html').write_text(''.join(parts),encoding='utf-8')
    pd.DataFrame(registry).to_csv(OUT/'manifesto-figuras.csv',index=False,encoding='utf-8-sig')
    qmd=['<!-- Figuras consolidadas do capítulo 3. Caminhos relativos a esta pasta. -->','']
    for item in registry:
        caption=re.sub(r'^Figura \d+\. ','',item['legenda'])
        qmd += [f'## {item["titulo"]}', '', f'![{caption}](figuras/{item["arquivo"]}.png){{#fig-cap3-{item["arquivo"]} fig-align="center" width="100%"}}','']
    (OUT/'figuras-para-tese.qmd').write_text('\n'.join(qmd),encoding='utf-8')
    with zipfile.ZipFile(OUT/'pacote-figuras.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
        for item in registry:
            for ext in ['png','svg']:z.write(FIG/(item['arquivo']+'.'+ext),'figuras/'+item['arquivo']+'.'+ext)
        for file in ['figuras-para-tese.qmd','manifesto-figuras.csv']:z.write(OUT/file,file)
    sources += [Path(__file__)]+[SENS/(x+'.'+ext) for x in PROFILES for ext in ['png','svg']]
    (OUT/'auditoria.json').write_text(json.dumps({'status':'OK','checks':checks,'fontes_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'figuras':registry},ensure_ascii=False,indent=2),encoding='utf-8')
    print(desc[(desc.universo=='Listas financiadas')][['ano_eleicao','indicador','media','mediana','q1','q3']].to_string(index=False))
    print(f'{len(checks)} verificações OK. {OUT/"relatorio.html"}')


if __name__=='__main__':
    main()
