"""Figuras interativas e exportáveis para a análise de sensibilidade Top-X%."""
from pathlib import Path
import math
import html
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LABELS={'competitividade':'Competitivos prévios','eleicao':'Eleitos'}
RULES={'top_necr':'Top-NECr'}
METRICS={'cobertura':'Cobertura (%)','precisao':'Precisão (%)','lift':'Lift (observado / acaso)'}
COLORS={'observado':'#222222','acaso':'#999999','top_necr':'#666666','acima_divisao_igual':'#777777'}
T=[50,60,70,80,90,95]


def number(x,d=1):
    return f'{x:,.{d}f}'.replace(',','_').replace('.',',').replace('_','.')


def table(frame):
    return '<div class="scroll">'+frame.to_html(index=False,border=0,na_rep='—',escape=True,float_format=lambda x:number(x,3))+'</div>'


def figures(out,s,outcome,include_js):
    z=s[s.desfecho.eq(outcome)]
    fig=make_subplots(rows=2,cols=3,subplot_titles=[f'{year} · {name}' for year in [2018,2022] for name in ['Cobertura','Precisão','Lift']],horizontal_spacing=.085,vertical_spacing=.19)
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'}):
        static,axes=plt.subplots(2,3,figsize=(13.6,8.4))
        for row,year in enumerate([2018,2022],1):
            g=z[z.ano_eleicao.eq(year)&z.limiar.notna()].sort_values('limiar')
            refs=z[z.ano_eleicao.eq(year)&z.limiar.isna()].set_index('regra')
            for col,(metric,title) in enumerate(METRICS.items(),1):
                ax=axes[row-1,col-1]
                factor=1 if metric=='lift' else 100
                vals=g[metric].to_numpy()*factor
                max_all=z[metric].max()*factor
                ymax=100 if metric=='cobertura' else math.ceil(max_all/(1 if metric=='lift' else 10))*(1 if metric=='lift' else 10)
                if metric=='lift': ymax=max(2,ymax)
                custom=np.column_stack([g.k_valido,g.observados,g.esperados_acaso])
                fig.add_trace(go.Scatter(x=T,y=vals,mode='lines+markers',name='Top-X% observado',legendgroup='observado',showlegend=(row==1 and col==1),line=dict(color=COLORS['observado'],width=3),marker=dict(size=[8,8,8,12,8,8]),customdata=custom,
                                         hovertemplate='Top-%{x}%<br>'+title+': %{y:.2f}<br>Posições válidas: %{customdata[0]:.2f}<br>Perfil incluído: %{customdata[1]:.2f}<br>Esperado: %{customdata[2]:.2f}<extra></extra>'),row=row,col=col)
                ax.plot(T,vals,'o-',color=COLORS['observado'],lw=2,label='Top-X% observado',zorder=3)
                ax.scatter([80],[vals[3]],s=65,color=COLORS['observado'],zorder=4)
                if metric=='lift':
                    random=np.ones(6)
                else:
                    random=g[metric+'_acaso'].to_numpy()*factor
                fig.add_trace(go.Scatter(x=T,y=random,name='Acaso intralista',legendgroup='acaso',showlegend=(row==1 and col==1),mode='lines',line=dict(color=COLORS['acaso'],dash='dot',width=2),hovertemplate='Top-%{x}%<br>Acaso: %{y:.2f}<extra></extra>'),row=row,col=col)
                ax.plot(T,random,':',color=COLORS['acaso'],lw=1.8,label='Acaso intralista')
                for rule,name in RULES.items():
                    ref=float(refs.loc[rule,metric])*factor
                    fig.add_trace(go.Scatter(x=[50,95],y=[ref,ref],name=name+' (referência)',legendgroup=rule,showlegend=(row==1 and col==1),visible='legendonly',mode='lines',line=dict(color=COLORS[rule],dash='dash',width=1.6),hovertemplate=name+': %{y:.2f}<extra></extra>'),row=row,col=col)
                    ax.axhline(ref,color=COLORS[rule],ls='--',lw=1.1,label=name)
                fig.update_xaxes(tickvals=T,ticksuffix='%',range=[48,97],title_text='Limiar de recursos acumulados' if row==2 else None,row=row,col=col)
                fig.update_yaxes(range=[0,ymax],title_text=title,gridcolor='#e5e9ed',zeroline=False,row=row,col=col)
                ax.set(title=f'{year} · '+title,xlim=(48,97),ylim=(0,ymax),xticks=T)
                ax.set_xticklabels([str(x)+'%' for x in T],fontsize=9)
                ax.grid(axis='y',color='#e6e9ed',zorder=0)
                if row==2: ax.set_xlabel('Limiar de recursos acumulados')
        handles,labels=axes[0,0].get_legend_handles_labels()
        static.legend(handles,labels,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,.025))
        static.tight_layout(rect=[.025,.085,.99,.99],h_pad=3,w_pad=2)
        static.savefig(out/(outcome+'.png'),dpi=180)
        static.savefig(out/(outcome+'.svg'))
        plt.close(static)
    fig.update_layout(height=820,template='plotly_white',font=dict(family='Arial, sans-serif',size=13,color='#203343'),margin=dict(l=65,r=25,t=45,b=135),legend=dict(orientation='h',x=0,y=-.16,groupclick='togglegroup'),hovermode='closest',paper_bgcolor='white')
    return fig.to_html(full_html=False,include_plotlyjs=include_js,div_id='curva-'+outcome,config={'responsive':True,'displaylogo':False,'toImageButtonOptions':{'format':'svg','filename':'sensibilidade-'+outcome}})


def create_report(out,s,sizes,traj,bands,audit):
    curves=s[s.limiar.notna()].copy()
    minlift=curves.lift.min()
    conclusion=('A sobrerrepresentação permanece em todos os cortes avaliados.' if minlift>1 else 'A sobrerrepresentação não permanece em todos os cortes avaliados.')
    parts=['''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Sensibilidade Top-X% · 2018 e 2022</title>
<style>:root{--ink:#183244;--muted:#526574;--blue:#176e96;--paper:#f1f4f6}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1260px;margin:auto;padding:32px 28px 60px}header{padding:24px 0 12px}h1{font-size:clamp(30px,4vw,48px);line-height:1.13;max-width:900px;margin:12px 0 18px}h2{font-size:27px;line-height:1.25;margin-top:0}h3{line-height:1.3}.eyebrow{font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--blue);font-weight:700}.lead{font-size:20px;max-width:980px}section{background:white;padding:28px;border-radius:12px;margin:24px 0;border:1px solid #e1e7eb}nav{display:flex;flex-wrap:wrap;gap:16px;margin:24px 0}a{color:#146b91;text-underline-offset:3px}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{background:#eaf2f6;border-radius:9px;padding:17px}.card strong{display:block;font-size:31px;line-height:1.3}.card small{display:block;color:var(--muted)}.note{padding:16px 20px;background:#f3f7fa;border-left:4px solid var(--blue);margin:20px 0}.warning{border-color:#b78637;background:#fcf7ed}.muted{color:var(--muted);font-size:14px}.chart{overflow-x:auto}.chart-inner{min-width:790px}.scroll{overflow:auto}table{border-collapse:collapse;white-space:nowrap;font-size:13px;width:100%}td,th{text-align:right;padding:10px 12px;border-bottom:1px solid #dfe6eb}th{background:#edf3f6}td:first-child,th:first-child{text-align:left}details{border-top:1px solid #dfe6eb;padding:16px 0}summary{font-weight:650;cursor:pointer}li{margin:8px 0}code{overflow-wrap:anywhere;background:#edf2f5;padding:2px 4px}blockquote{margin:22px 0;padding:18px 22px;border-left:4px solid #218668;background:#f0f7f3}footer{font-size:13px;color:var(--muted)}@media(max-width:720px){main{padding:18px 12px}section{padding:20px 16px}.cards{grid-template-columns:repeat(2,1fr)}.lead{font-size:18px}}@media print{body{background:white}main{max-width:none;padding:0}section{break-inside:auto;border:0}nav,details{display:none}.chart-inner{min-width:0}}</style></head><body><main><header><div class="eyebrow">Mensuração da priorização financeira · Deputados federais</div><h1>O resultado depende do corte de 80%?</h1><p class="lead">Sensibilidade do Top-X% em 50, 60, 70, 80, 90 e 95% dos recursos partidários, com avaliações separadas de competitividade prévia e eleição em 2018 e 2022.</p><nav><a href="#achados">Achados</a><a href="#competitividade">Competitivos prévios</a><a href="#eleicao">Eleitos</a><a href="#interpretacao">Interpretação</a><a href="#metodo">Método e arquivos</a></nav></header>''']
    parts.append('<section id="achados"><h2>'+conclusion+'</h2><p>Os seis limiares foram aplicados às mesmas listas e candidaturas, antes da avaliação dos perfis. O menor lift de cada combinação de ano e desfecho resume o resultado mais próximo do acaso nessa faixa.</p><div class="cards">')
    for outcome in LABELS:
        for year in [2018,2022]:
            g=curves[(curves.desfecho==outcome)&(curves.ano_eleicao==year)]
            r=g.loc[g.lift.idxmin()]
            parts.append(f'<div class="card"><small>{LABELS[outcome]} · {year}</small><strong>{number(r.lift,2)}×</strong><small>Menor lift · Top-{r.limiar:.0f}%</small></div>')
    parts.append('</div><p>Lift = 1 é a expectativa aleatória intralista. Valores acima de 1 indicam maior presença do perfil do que a esperada apenas pelo tamanho do grupo e pela composição das listas.</p>')
    if minlift>1:
        parts.append(f'<p><strong>Todos os 24 resultados</strong> — seis cortes × dois anos × dois perfis — ficam acima de 1. O menor lift observado é {number(minlift,2)}. Essa constatação se refere à grade avaliada, sem afirmar invariância em qualquer limiar possível.</p>')
    parts.append('''<div class="note"><strong>Arquitetura da análise.</strong> O <strong>Top-NECr</strong> permanece como medida principal: o tamanho deriva da concentração observada, acompanhado das escolhas explícitas de arredondamento e empates. O <strong>Top-X%</strong> varia um parâmetro da mesma regra de acumulação.</div></section>''')
    for outcome,title in LABELS.items():
        parts.append(f'<section id="{outcome}"><h2>{title}: cobertura, precisão e lift</h2><p>Linhas pretas: resultados observados. Linhas pontilhadas: expectativa aleatória para o mesmo grupo em cada lista. O marcador maior identifica Top-80%. As linhas apenas conectam os seis pontos calculados.</p><p class="muted">A linha cinza escura horizontal mostra o resultado nacional do Top-NECr. Em telas pequenas, deslize o gráfico horizontalmente.</p><div class="chart"><div class="chart-inner">')
        parts.append(figures(out,s,outcome,include_js=(outcome=='competitividade')))
        parts.append(f'</div></div><p class="muted">Exportar figura com as referências: <a href="{outcome}.svg">SVG vetorial</a> · <a href="{outcome}.png">PNG em alta resolução</a>.</p>')
        for year in [2018,2022]:
            g=curves[(curves.desfecho==outcome)&(curves.ano_eleicao==year)].sort_values('limiar')
            first,last=g.iloc[0],g.iloc[-1]
            ts=traj[(traj.desfecho==outcome)&(traj.ano_eleicao==year)].set_index('indicador')
            behavior=('A precisão e o lift diminuem em todos os passos.' if ts.loc['precisao','passos_queda']==5 and ts.loc['lift','passos_queda']==5 else 'Precisão e lift não apresentam queda estrita em todos os passos; a tabela de trajetórias explicita as mudanças.')
            parts.append(f'<p><strong>{year}.</strong> Do Top-50% ao Top-95%, a cobertura passa de {number(100*first.cobertura)}% para {number(100*last.cobertura)}%, a precisão de {number(100*first.precisao)}% para {number(100*last.precisao)}% e o lift de {number(first.lift,2)} para {number(last.lift,2)}. {behavior}</p>')
        parts.append('</section>')
    parts.append('<section id="interpretacao"><h2>O que a sensibilidade permite afirmar</h2>')
    all_decreasing=bool(traj[traj.indicador.isin(['precisao','lift'])].nao_crescente.all())
    if all_decreasing:
        parts.append('<p>Nos dois anos e para os dois perfis, a expansão do limiar aumenta a cobertura e reduz a precisão e o lift ao longo da grade avaliada. O padrão é compatível com maior concentração de credenciais e vencedores nos grupos mais restritos do topo financeiro. A sobrerrepresentação, porém, persiste mesmo nos grupos mais amplos.</p>')
    else:
        parts.append('<p>A cobertura cresce com a expansão dos grupos, mas há ao menos uma quebra da trajetória não crescente de precisão ou lift. A hipótese de uma curva uniformemente descendente deve ser qualificada à luz dos passos observados abaixo.</p>')
    parts.append('<p>O aumento da cobertura decorre do aninhamento: elevar X não retira peso de quem já integrava o grupo. A queda da precisão não é uma propriedade necessária da regra; depende do perfil das candidaturas incorporadas e da composição das listas. O lift também pode aumentar ou diminuir, pois seu denominador é recalculado para os novos tamanhos em cada lista. Sua trajetória deve ser observada, não presumida.</p>')
    parts.append('<p>É importante distinguir o grupo acumulado das candidaturas acrescentadas. No acréscimo de Top-70% para Top-80%, o lift dos eleitos é inferior a 1 nos dois anos; para competitivos prévios, isso ocorre nos acréscimos de Top-80% para Top-90% e de Top-90% para Top-95%. Logo, um lift cumulativo acima de 1 nos cortes amplos não significa sobrerrepresentação em cada faixa incorporada. A concentração inicial dos perfis sustenta parte do resultado acumulado.</p>')
    parts.append('<h3>Tamanho dos grupos</h3>')
    for year,g in sizes.groupby('ano_eleicao'):
        first=g[g.limiar.eq(50)].iloc[0];last=g[g.limiar.eq(95)].iloc[0]
        parts.append(f'<p>Em {year}, os grupos passam de {number(first.posicoes,0)} para {number(last.posicoes,0)} posições, ou de {number(100*first.proporcao_nacional)}% para {number(100*last.proporcao_nacional)}% das candidaturas. A mediana por lista passa de {number(first.k_mediano,0)} para {number(last.k_mediano,0)}. O percentual X refere-se aos recursos acumulados, não ao percentual de candidaturas incluídas.</p>')
    parts.append('<h3>Uma redação sustentada pelos resultados</h3>')
    if minlift>1:
        parts.append('<blockquote>A sobrerrepresentação de candidaturas previamente competitivas e de candidaturas eleitas não depende exclusivamente do corte de 80%. Ao variar o percentual acumulado utilizado para delimitar o grupo financeiramente priorizado entre 50% e 95%, nos seis limiares examinados, o lift permanece acima de 1 em 2018 e 2022. A comparação preserva o tamanho dos grupos e a composição das listas no benchmark aleatório. Os resultados sustentam a robustez desse padrão à variação do limiar, embora a cobertura, a precisão e a intensidade da sobrerrepresentação dependam do corte adotado.</blockquote>')
    else:
        parts.append('<blockquote>A variação dos limiares mostra que a magnitude e a persistência da sobrerrepresentação dependem do corte. A alegação de robustez deve indicar explicitamente quais limiares, anos e perfis mantêm lift superior a 1.</blockquote>')
    parts.append('''<div class="note warning"><strong>Gradiente agregado não implica uma fronteira verdadeira.</strong> Seis médias cumulativas não demonstram uma relação contínua nem uma queda da incidência a cada posição individual do ranking. Cortes sucessivos podem incorporar números diferentes de candidaturas em listas diferentes. A análise tampouco identifica intenção partidária, efeito causal do financiamento ou validação independente: todas as regras usam os mesmos recursos e as avaliações usam os mesmos perfis.</div>''')
    parts.append('<details><summary>Diagnóstico adicional: perfis das faixas incorporadas</summary><p>Subtraímos os pesos dos grupos sucessivos: Top-50%, acréscimo 50–60%, …, acréscimo 90–95%, e o complemento do Top-95%. São blocos definidos por mudanças de corte, não intervalos de renda nem percentis de candidaturas. Empates podem repartir pesos entre faixas. Esse diagnóstico verifica se a incidência marginal também cai sem reversões; não substitui a curva cumulativa.</p>')
    marginal=[]
    for (year,outcome),g in bands.groupby(['ano_eleicao','desfecho']):
        delta=np.diff(g.sort_values('ordem').incidencia)
        increases=int((delta>1e-12).sum())
        marginal.append(dict(Ano=int(year),Perfil=LABELS[outcome],aumentos_entre_faixas=increases))
    parts.append(table(pd.DataFrame(marginal)))
    if any(x['aumentos_entre_faixas']>0 for x in marginal):
        parts.append('<p><strong>A incidência cai em todas as seis faixas incorporadas até Top-95%, para os dois perfis e nos dois anos.</strong> A única reversão ocorre ao passar para o complemento do Top-95%, no caso dos eleitos: de 1,24% para 1,31% em 2018 e de 0,49% para 0,62% em 2022. Esse complemento também inclui as listas sem recursos. Há evidência de um gradiente por blocos, mas a expressão “gradiente contínuo” seria mais forte do que essa análise de seis limiares permite.</p>')
    else:
        parts.append('<p>As incidências também são não crescentes entre as faixas examinadas. Isso acrescenta uma descrição do gradiente por blocos, sem demonstrar continuidade ou monotonicidade posição a posição.</p>')
    display=bands[['ano_eleicao','desfecho','faixa','k','hits','incidencia','lift']].copy()
    display['desfecho']=display.desfecho.map(LABELS);display.incidencia*=100
    display.columns=['Ano','Perfil','Faixa incorporada','Posições válidas','Perfil incluído','Incidência (%)','Lift da faixa']
    parts.append(table(display)+'</details></section>')
    parts.append('''<section id="metodo"><h2>Método, conferências e arquivos</h2><p><strong>Universo.</strong> 7.630 candidaturas em 859 listas em 2018; 9.675 candidaturas em 711 listas em 2022. Unidade da lista: partido normalizado × UF × eleição. As 73 e 63 listas sem recursos permanecem no universo e recebem grupo vazio. Partidos não são agregados por coligação ou federação.</p>
<p><strong>Recursos e seleção.</strong> Reutiliza-se <code>vr_receita_recursos_partidos</code>, com ausências tratadas como zero conforme o pipeline, e a função de pertencimento fracionário já usada no Top-NECr. Para cada X, k é o menor inteiro para o qual a soma das k maiores receitas atinge X% do total da lista. As posições restantes no corte são divididas igualmente entre os empatados. As comparações usam Decimal da representação round-trip dos valores, sem arredondar a centavos; o NECr e seu k permanecem os da função canônica.</p>
<p><strong>Competitividade.</strong> Vitória anterior para prefeito, deputado estadual/distrital, deputado federal, governador ou senador, ou votação histórica ≥10% do QE. Preserva-se a máscara de informação válida do relatório anterior: quatro ausências em 2018 e três em 2022; os totais de competitivos são 886 e 1.287. A eleição é avaliada para todas as candidaturas, com 513 eleitos em cada ano. Nenhum desses perfis define o grupo financeiro.</p>
<p><strong>Benchmark exato.</strong> Em cada lista, esperado = k × F/C, onde F é o total do perfil. Para competitividade, usam-se N válido e K válido entre registros conhecidos, exatamente como no relatório anterior. Cobertura nacional = Σacertos/ΣF; precisão = Σacertos/Σk; as respectivas taxas aleatórias substituem acertos por Σesperados; lift = Σacertos/Σesperados. Não se usa média simples de taxas das listas nem simulação.</p>
<p><strong>Alcance.</strong> A grade de seis cortes foi fixada no pedido antes deste cálculo, mas a análise é uma extensão exploratória posterior ao conhecimento dos resultados Top-80%; não se afirma pré-registro. O teste é descritivo de sensibilidade, sem p-valores ou intervalos de confiança. “Acima de 1 em todos os cortes” não equivale a significância estatística. Receitas totais da campanha não tornam o exercício uma previsão prospectiva.</p>''')
    parts.append(f'<p><strong>{len(audit["verificacoes"]):,} verificações passaram</strong>: integridade das fontes, reconciliação individual com a base primária, mesmo universo e credenciais, reprodução das três referências anteriores, Top-80% idêntico, menor k, empates, aninhamento, invariância à ordem e identidade dos lifts de cobertura e precisão.</p>')
    compact=s.copy();compact['regra']=compact.apply(lambda r:f'Top-{r.limiar:.0f}%' if pd.notna(r.limiar) else RULES[r.regra],axis=1)
    compact['desfecho']=compact.desfecho.map(LABELS)
    cols=['ano_eleicao','desfecho','regra','k_valido','observados','esperados_acaso','cobertura','cobertura_acaso','precisao','precisao_acaso','lift']
    compact=compact[cols]
    for c in ['cobertura','cobertura_acaso','precisao','precisao_acaso']:compact[c]*=100
    compact.columns=['Ano','Perfil','Regra','Posições válidas','Observados','Esperados','Cobertura (%)','Cobertura acaso (%)','Precisão (%)','Precisão acaso (%)','Lift']
    parts.append('<details><summary>Valores completos dos gráficos e das referências</summary>'+table(compact)+'</details>')
    parts.append('<details><summary>Distribuições dos tamanhos e diagnóstico das trajetórias</summary>'+table(sizes)+table(traj)+'</details>')
    files=['resumo_nacional.csv','tamanhos.csv','listas_top_x.csv','avaliacao_por_lista.csv','trajetorias.csv','faixas_incrementais.csv','candidaturas.parquet','candidaturas.csv','auditoria.json','analisar.py','relatorio.py']
    parts.append('<h3>Reprodução e dados</h3><p>Execute da raiz do repositório: <code>python tese/sensibilidade-top-x/analisar.py</code>. O relatório incorpora o JavaScript dos gráficos e funciona sem internet. Taxas nos CSVs estão entre 0 e 1; gráficos e tabelas de avaliação as exibem em porcentagem.</p><ul>')
    parts.extend(f'<li><a href="{html.escape(f)}">{html.escape(f)}</a></li>' for f in files)
    parts.append('</ul></section><footer>Fontes: bases locais do TSE e pipeline do capítulo 3. Relatório de sensibilidade da operacionalização; resultados nacionais de 2018 e 2022.</footer></main></body></html>')
    (out/'relatorio.html').write_text(''.join(parts),encoding='utf-8')
    (out/'interpretacao.json').write_text(json.dumps({'todos_24_lifts_acima_1':bool(minlift>1),'menor_lift':float(minlift),'precisao_lift_nao_crescentes':all_decreasing,'reversoes_faixas':marginal},ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    out=Path(__file__).resolve().parent
    create_report(out,*[pd.read_csv(out/(name+'.csv')) for name in ['resumo_nacional','tamanhos','trajetorias','faixas_incrementais']],json.loads((out/'auditoria.json').read_text(encoding='utf-8')))
