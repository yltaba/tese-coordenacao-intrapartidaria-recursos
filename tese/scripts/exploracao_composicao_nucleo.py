"""Versão inferencial anterior. A versão atual usa relatorio_descritivo_nucleo.py."""
from pathlib import Path
import sys, json, hashlib, html
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
import plotly.express as px

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src/2_gold'))
from cap3_taa_features import _preparar
from cap3_cobertura_top_necr import calcular_cobertura_top_necr
sys.path.insert(0, str(Path(__file__).parent))
from financiamento_alternativo_top_necr import membership, inference
OUT = ROOT / 'tese/resultados-exploracao-nucleo'
OUT.mkdir(exist_ok=True)
KEY = ['ano_eleicao', 'sg_uf', 'nr_candidato']
LK = ['ano_eleicao', 'sg_uf', 'sg_partido_norm']
checks = {}
def check(label, value):
    checks[label] = bool(value)
    assert value, label

raw = pd.read_parquet(ROOT / 'data/processed/rrd_df_novo.parquet')
d = _preparar(raw[raw.ano_eleicao.isin([2018, 2022])]).reset_index(drop=True)
check('Universos do capítulo', d.groupby('ano_eleicao').size().tolist() == [7630, 9675])
check('513 eleitos por ano', d.groupby('ano_eleicao').eleito.sum().eq(513).all())
check('Chaves únicas', not d.duplicated(KEY).any())
d['lista'] = d.groupby(LK).ngroup()
for rule in ['piso', 'arredondado', 'teto']:
    d['top_'+rule] = 0.
for _, g in d.groupby('lista'):
    v = g.vr_receita_recursos_partidos.to_numpy(float)
    necr = v.sum()**2 / (v*v).sum() if v.sum() else np.nan
    for rule, val in [('piso', np.floor(necr)), ('arredondado', np.floor(necr+.5)), ('teto', np.ceil(necr))]:
        k = max(1, int(val)) if np.isfinite(val) else 0
        w = membership(v, k)
        check(f'Posições {int(g.lista.iloc[0])} {rule}', np.isclose(w.sum(), min(k,len(g))))
        d.loc[g.index, 'top_'+rule] = w
_, canonical = calcular_cobertura_top_necr(raw)
for _, r in canonical.iterrows():
    g = d[d.ano_eleicao.eq(r.ano_eleicao)]
    check(f'Cobertura canônica {r.ano_eleicao} {r.regra_k}', np.isclose(g.eleito @ g['top_'+r.regra_k], r.eleitos_top_necr))

# Recalcula as origens monetárias, sem depender dos CSVs exploratórios anteriores.
rec = pd.read_parquet(ROOT / 'data/processed/receitas.parquet')
rec = rec[rec.ano_eleicao.isin([2018, 2022]) & rec.ds_cargo.eq('DEPUTADO FEDERAL')].copy()
rec['fonte'] = np.select([rec.ds_origem_receita.eq('Recursos próprios'), rec.ds_origem_receita.eq('Recursos de pessoas físicas')], ['proprios','pessoas_fisicas'], default='outras')
money = rec.groupby(KEY + ['fonte']).vr_receita.sum().unstack(fill_value=0).reset_index()
d = d.merge(money[KEY+['proprios','pessoas_fisicas']], on=KEY, how='left', validate='one_to_one')
d[['proprios','pessoas_fisicas']] = d[['proprios','pessoas_fisicas']].fillna(0)
d['privado_proprio'] = d.proprios + d.pessoas_fisicas
check('Dinheiro finito e não negativo', np.isfinite(d[['proprios','pessoas_fisicas']]).all().all() and d[['proprios','pessoas_fisicas']].ge(0).all().all())
del rec
valid = d.nr_cpf_candidato.astype(str).str.fullmatch(r'\d{11}') & ~d.nr_cpf_candidato.isin(['00000000000','99999999999'])
d['reeleicao_proxy'] = np.nan
for year in [2018, 2022]:
    previous = set(raw.loc[raw.ano_eleicao.eq(year-4) & raw.eleito.eq(1), 'nr_cpf_candidato'])
    mask = d.ano_eleicao.eq(year) & valid
    d.loc[mask, 'reeleicao_proxy'] = d.loc[mask, 'nr_cpf_candidato'].isin(previous).astype(float)
for name, col in [('vitoria_federal','deputado_federal'), ('vitoria_estadual','deputado_estadual'), ('vitoria_prefeito','prefeito'), ('vitoria_vereador','vereador')]:
    s = d['n_eleicoes_'+col]
    d[name] = (s > 0).astype(float).where(s.notna() & valid)
d['ex_federal_proxy'] = (d.vitoria_federal.eq(1) & d.reeleicao_proxy.eq(0)).astype(float).where(valid & d.vitoria_federal.notna())
d['voto_relevante'] = d.alcancou_10pct_qe_hist.astype(float).where(valid)
victory_cols = [c for c in d if c.startswith('n_eleicoes_')]
d['vitoria_qualquer'] = d[victory_cols].gt(0).any(axis=1).astype(float).where(valid & d[victory_cols].notna().all(axis=1))
d['sem_credencial'] = (d.vitoria_qualquer.eq(0) & d.voto_relevante.eq(0)).astype(float).where(d.vitoria_qualquer.notna() & d.voto_relevante.notna())
labels = {'reeleicao_proxy':'Eleito federal no pleito anterior (proxy)', 'ex_federal_proxy':'Vitória federal antiga, sem vitória no pleito anterior', 'vitoria_estadual':'Vitória anterior estadual/distrital', 'vitoria_prefeito':'Vitória anterior para prefeito', 'vitoria_vereador':'Vitória anterior para vereador', 'voto_relevante':'Votação histórica ≥ 10% do QE', 'vitoria_qualquer':'Alguma vitória anterior', 'sem_credencial':'Sem vitória nem votação histórica relevante', 'mulher':'Mulheres', 'negra':'Pessoas pretas ou pardas'}
features = list(labels)
d['top'] = d.top_arredondado
d['fora'] = 1-d.top
d['magnitude'] = pd.cut(d.qt_vaga, [0,12,31,70], labels=['8–12','16–31','39–70']).astype(str)
rows, matrix = [], []
for year, g in d.groupby('ano_eleicao'):
    groups = {'Núcleo':g.top, 'Fora':g.fora, 'Núcleo eleito':g.top*g.eleito, 'Núcleo não eleito':g.top*(1-g.eleito), 'Fora eleito':g.fora*g.eleito, 'Fora não eleito':g.fora*(1-g.eleito)}
    for group,w in groups.items():
        matrix.append({'Ano':year,'Grupo':group,'N ponderado':w.sum()})
        for f in features:
            mask = g[f].notna()
            denom = w[mask].sum()
            rows.append({'Ano':year,'Grupo':group,'Perfil':labels[f], 'N válido ponderado':denom,'Ausente ponderado':w[~mask].sum(), 'Percentual':100*(w[mask] @ g.loc[mask,f])/denom if denom else np.nan})
profile = pd.DataFrame(rows)

# Modelos lineares com efeitos fixos de lista por transformação within.
modelrows, modelmeta = [], []
controls = ['reeleicao_proxy','ex_federal_proxy','vitoria_estadual','vitoria_prefeito','vitoria_vereador','voto_relevante','mulher','negra']
def within(frame, outcome, xs, name, weight=None):
    z = frame.dropna(subset=[outcome]+xs).copy()
    z = z[z.groupby('lista').lista.transform('size') > 1]
    if weight:
        weighted = z[[outcome]+xs].mul(z[weight],axis=0)
        means = weighted.groupby(z.lista).transform('sum').div(z.groupby('lista')[weight].transform('sum'),axis=0)
        centered = z[[outcome]+xs] - means
    else:
        centered = z[[outcome]+xs] - z.groupby('lista')[[outcome]+xs].transform('mean')
    check('Posto completo '+name, np.linalg.matrix_rank(centered[xs]) == len(xs))
    m = sm.WLS(centered[outcome], centered[xs],weights=z[weight] if weight else np.ones(len(z))).fit(cov_type='cluster', cov_kwds={'groups':z.lista,'use_correction':False}, use_t=True)
    # CR1: inclui os efeitos fixos absorvidos na contagem de parâmetros.
    n, ng = len(z), z.lista.nunique()
    m.cov_params_default *= ng/(ng-1) * (n-1)/(n-len(xs)-ng)
    ci = m.conf_int()
    for x in xs:
        modelrows.append({'Modelo':name,'Variável':labels.get(x,x),'Coeficiente pp':100*m.params[x], 'IC95 inferior':100*ci.loc[x,0], 'IC95 superior':100*ci.loc[x,1], 'p':m.pvalues[x]})
    modelmeta.append({'Modelo':name,'N elegível':len(frame),'N usado':len(z),'Listas usadas':z.lista.nunique(), 'Listas com variação no desfecho':int(z.groupby('lista')[outcome].nunique().gt(1).sum()),'R2 within':m.rsquared})
for year, g in d.groupby('ano_eleicao'):
    within(g,'top',controls,f'Entrada no núcleo {year}')
    core = g[g.top.gt(0)].copy()
    core['nao_eleito'] = 1-core.eleito
    within(core,'nao_eleito',controls,f'Não eleição dentro do núcleo {year}',weight='top')
    within(g[g.eleito.eq(1)],'fora',controls,f'Eleito fora: capital político {year}')
    e = g[g.eleito.eq(1)].copy()
    for source in ['proprios','pessoas_fisicas']:
        e[source+'_percentil'] = e[source].rank(pct=True)
        labels[source+'_percentil'] = source.replace('_',' ')+' (percentil 0–1 entre eleitos do ano)'
    within(e,'fora',controls+['proprios_percentil','pessoas_fisicas_percentil'],f'Eleito fora: capital e receitas {year}')
models = pd.DataFrame(modelrows)
models['p BH (família de todos os coeficientes)'] = multipletests(models.p, method='fdr_bh')[1]

l = d.assign(acerto=d.top*d.eleito).groupby(LK+['lista']).agg(C=('eleito','size'), E=('eleito','sum'), K=('top','sum'), A=('acerto','sum'), M=('qt_vaga','first'), magnitude=('magnitude','first')).reset_index()
l['esperado'] = l.E*l.K/l.C
l['amplitude'] = l.K/l.C
l['cobertura'] = l.A/l.E.replace(0,np.nan)
l['precisao'] = l.A/l.K.replace(0,np.nan)
l['ganho_cobertura'] = l.cobertura-l.amplitude
variation = []
for dim in ['magnitude','sg_partido_norm','sg_uf']:
    for (year, group), g in l.groupby(['ano_eleicao',dim]):
        variation.append({'Dimensão':dim,'Ano':year,'Grupo':group,'Listas':len(g),'Listas com eleitos':g.E.gt(0).sum(),'Eleitos':g.E.sum(),'Posições':g.K.sum(),'Cobertura %':100*g.A.sum()/g.E.sum() if g.E.sum() else np.nan,'Precisão %':100*g.A.sum()/g.K.sum() if g.K.sum() else np.nan,'Lift':g.A.sum()/g.esperado.sum() if g.esperado.sum() else np.nan,'Amplitude média %':100*g.amplitude.mean()})
variation = pd.DataFrame(variation)
vtests = []
for year, g in l.groupby('ano_eleicao'):
    for outcome in ['amplitude','ganho_cobertura','precisao']:
        for dim in ['magnitude','sg_partido_norm','sg_uf']:
            z = g.dropna(subset=[outcome]).copy()
            # Remove categorias unitárias para inferência robusta HC3.
            z = z[z.groupby(dim)[dim].transform('size') >= 3]
            m = smf.ols(f'{outcome} ~ C({dim})',data=z.drop(columns='C')).fit(cov_type='HC3')
            restrictions = np.eye(len(m.params))[1:]
            rank = np.linalg.matrix_rank(restrictions @ m.cov_params() @ restrictions.T)
            pvalue = float(m.wald_test(restrictions, scalar=True).pvalue) if rank == len(restrictions) else np.nan
            vtests.append({'Ano':year,'Desfecho':outcome,'Dimensão':dim,'N listas':len(z),'Categorias':z[dim].nunique(),'R2':m.rsquared,'p':pvalue,'Estado':'OK' if np.isfinite(pvalue) else 'Covariância singular: teste global indisponível'})
vtests = pd.DataFrame(vtests)
vtests['p BH'] = np.nan
testable = vtests.p.notna()
# Mantém família planejada de 18 testes, atribuindo p=1 aos indisponíveis.
vtests.loc[testable,'p BH'] = multipletests(vtests.p.fillna(1),method='fdr_bh')[1][testable]

fin, robust = [], []
for year, g in d[d.eleito.eq(1)].groupby('ano_eleicao'):
    for source in ['proprios','pessoas_fisicas','privado_proprio']:
        high = g[source] > g[source].median()
        r = inference(g, high, int(year)+len(source))
        fin.append({'Ano':year,'Fonte':source,'Mediana R$':g[source].median(),'Fora alto %':100*np.average(high,weights=g.fora),'Dentro alto %':100*np.average(high,weights=g.top), **r})
        for rule in ['piso','arredondado','teto']:
            w = g['top_'+rule]
            robust.append({'Ano':year,'Fonte':source,'Regra':rule,'Eleitos fora':(1-w).sum(),'Diferença pp':100*(np.average(high,weights=1-w)-np.average(high,weights=w))})
fin = pd.DataFrame(fin)
fin['p Holm'] = multipletests(fin.p_bilateral,method='holm')[1]

tables = {}
def table(df, name, collapse=False):
    tables[name] = df
    df.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
    t = '<div class="scroll">'+df.to_html(index=False,border=0,float_format=lambda x:f'{x:.3f}',na_rep='—')+'</div>'
    return '<details><summary>Abrir tabela completa</summary>'+t+'</details>' if collapse else t
figcounter = 0
def fig(f):
    global figcounter
    f.update_layout(template='plotly_white',font=dict(family='Arial',size=14),margin=dict(l=25,r=25,t=65,b=35))
    figcounter += 1
    return f.to_html(full_html=False,include_plotlyjs=True if figcounter==1 else False, config={'displaylogo':False,'responsive':True},div_id=f'fig-{figcounter}')
parts = ['''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Composição e limites do núcleo partidário</title><style>body{margin:0;background:#f1f4f8;color:#203047;font:17px/1.65 system-ui}main{max-width:1200px;margin:auto;padding:30px 20px 70px}header{background:#18364a;color:white;padding:35px;border-radius:16px}h1{line-height:1.15;font-size:38px}section{background:white;padding:28px;margin-top:24px;border-radius:14px}h2{line-height:1.25}a{color:#086b85}header a{color:#bdefff;margin-right:16px}.scroll{overflow:auto;max-height:650px}table{border-collapse:collapse;font-size:13px;width:100%}td,th{padding:9px;border-bottom:1px solid #dce3e9;text-align:left}th{position:sticky;top:0;background:#eaf1f6}.note{background:#eef7f6;border-left:4px solid #168c81;padding:16px}details{margin:18px 0}summary{cursor:pointer;font-weight:600}code{overflow-wrap:anywhere}@media print{header{background:white;color:#203047}.scroll{max-height:none}section{break-inside:avoid}}</style></head><body><main><header><p>CAPÍTULO 3 · EXPLORAÇÃO EMPÍRICA · 2018 E 2022</p><h1>Quem compõe o núcleo e onde a coordenação encontra seus limites?</h1><p>Composição, heterogeneidade entre listas, inclusão de não eleitos e eleição fora do Top-NECr.</p><nav><a href="#sintese">Resultados</a><a href="#composicao">Composição</a><a href="#variacao">Listas</a><a href="#erros">Inclusão e exclusão</a><a href="#financas">Recursos alternativos</a><a href="#metodo">Método</a></nav></header>''']
parts.append('<section id="sintese"><h2>1. Principais resultados e alcance</h2><p>Exploração das bases locais utilizadas no capítulo, sem alterar seu texto. O núcleo segue exatamente o arredondamento e os empates do capítulo. Os resultados abaixo distinguem associações descritivas de comparações condicionadas à lista.</p>')
for year,g in d.groupby('ano_eleicao'):
    a = g.top@g.eleito
    parts.append(f'<p><strong>{year}:</strong> {len(g):,} candidaturas, {g.lista.nunique()} listas e {g.top.sum():,.0f} posições no núcleo. Cobertura de {100*a/513:.2f}%; precisão de {100*a/g.top.sum():.2f}%. Há {g.top.sum()-a:.2f} não eleitos dentro e {513-a:.2f} eleitos fora (contagens ponderadas).</p>')
for year in [2018,2022]:
    z=profile[(profile.Ano==year)&profile.Grupo.eq('Núcleo')]
    values=z.set_index('Perfil').Percentual
    parts.append(f'<p>Em {year}, o núcleo reúne {values[labels["reeleicao_proxy"]]:.1f}% de eleitos federais no pleito anterior, {values[labels["vitoria_vereador"]]:.1f}% com vitória prévia para vereador e {values[labels["sem_credencial"]]:.1f}% sem as credenciais eleitorais observadas; {values[labels["mulher"]]:.1f}% são mulheres. Os perfis de experiência podem se sobrepor.</p>')
parts.append('<p class="note">O núcleo é heterogêneo e não equivale a um conjunto de incumbentes. “Sem credencial observada” não significa ausência de capital político. “Erro” designa desacordo com o resultado eleitoral, sem pressupor que eleger cada financiado fosse o único objetivo partidário.</p></section>')
parts.append('<section id="composicao"><h2>2. Quem entra no núcleo?</h2><p>Percentuais dentro de cada grupo, excluindo ausências apenas no respectivo indicador. Vitórias para prefeito, vereador e deputado estadual/distrital indicam experiência anterior; não demonstram ocupação atual nem a condição estrita de ex-ocupante.</p>')
z=profile[profile.Grupo.isin(['Núcleo','Fora'])]
parts.append(fig(px.bar(z,x='Percentual',y='Perfil',color='Grupo',facet_col='Ano',barmode='group',orientation='h',height=640,title='Credenciais e composição social dentro e fora do núcleo')))
parts.append(table(z,'composicao',True))
parts.append('<h3>Entrada no núcleo dentro da mesma lista</h3><p>Modelo linear do peso de pertencimento (0–1), com efeitos fixos de lista, estimado separadamente por ano. Os coeficientes em pontos percentuais controlam simultaneamente os oito atributos apresentados. Erros-padrão agrupados por lista. Não são efeitos causais; o modelo linear pode produzir previsões fora do intervalo unitário e é usado para contrastes médios.</p>')
parts.append(table(models[models.Modelo.str.startswith('Entrada')],'modelos_entrada'))
parts.append('<p><strong>Leitura:</strong> dentro da mesma lista e controlando os demais atributos, a vitória federal no pleito anterior está associada a aproximadamente +43,5 pp de pertencimento em 2018 e +30,3 pp em 2022. A votação histórica relevante associa-se a cerca de +39 pp nos dois anos. Mulheres apresentam associação positiva de +8,2 e +6,9 pp: sua proporção bruta no núcleo e sua diferença ajustada de entrada são perguntas distintas. A credencial de prefeito tem associação negativa nesta especificação conjunta; ela não sustenta a ideia de que todas as trajetórias anteriores recebam a mesma prioridade, nem permite concluir que a experiência municipal cause desvantagem.</p>')
parts.append('</section><section id="variacao"><h2>3. O núcleo é mais “cirúrgico” em algumas listas?</h2><p>Três dimensões precisam ser separadas: amplitude K/C (quanto da lista entra), cobertura (quantos eleitos entram) e precisão (quantos integrantes são eleitos). O lift compara acertos observados com Σ(E×K/C), preservando o tamanho de cada lista. Um núcleo pequeno não implica boa focalização.</p>')
parts.append(table(variation[variation.Dimensão.eq('magnitude')],'variacao_magnitude'))
parts.append('<p><strong>Padrão substantivo:</strong> distritos grandes têm menor amplitude média e maior precisão e lift nos dois anos. Sua cobertura sobe de 81,5% para 93,8%, enquanto a precisão cai de 24,2% para 16,7%. Nos pequenos, a cobertura já é alta (93,0% e 94,2%), mas o lift é menor (aproximadamente 1,5 e 1,4). Portanto, cobertura elevada pode refletir um núcleo abrangente; a vantagem sobre o sorteio indica uma dimensão diferente da focalização.</p>')
parts.append(fig(px.scatter(variation[variation.Dimensão.eq('sg_uf')],x='Cobertura %',y='Precisão %',color='Ano',size='Eleitos',hover_name='Grupo',hover_data=['Listas','Lift','Amplitude média %'],title='UFs: cobertura e precisão agregadas',height=460)))
parts.append('<p>As taxas nas tabelas são razões de somas; a amplitude é média entre listas. Partidos são mantidos com sua identidade em cada eleição, sem painel artificial de fusões. Grupos pequenos devem ser lidos junto aos denominadores.</p>')
parts.append(table(variation,'variacao_todas',True))
parts.append('<h3>Testes globais de heterogeneidade</h3><p>Regressões separadas por ano, indicador e dimensão, com peso igual por lista e teste Wald conjunto dos indicadores de grupo (covariância HC3). Ganho de cobertura = cobertura − K/C: remove o benchmark de seleção aleatória do mesmo tamanho. Categorias com menos de três listas válidas são excluídas apenas destes testes. São comparações brutas, não efeitos próprios de partido, UF ou magnitude; magnitude é determinada pela UF e não deve ser interpretada como efeito separado em um modelo com efeitos fixos de UF. BH corrige os 18 testes.</p>')
parts.append(table(vtests,'testes_heterogeneidade'))
parts.append('<p>“Teste global indisponível” indica covariância singular dos contrastes, em geral associada a grupos sem dispersão no indicador. Não se interpreta o teste parcial que uma inversão generalizada produziria como teste de todos os grupos. Esses casos recebem p=1 apenas para preservar a família de 18 comparações na correção BH; permanecem sem p reportado.</p>')
parts.append('</section><section id="erros"><h2>4. Inclusão e exclusão: quatro grupos distintos</h2><p>Inclusão de não eleitos tem denominador K; exclusão de eleitos tem denominador E. As duas taxas são 1 − precisão e 1 − cobertura, respectivamente. Não confundir exclusão com a taxa de eleição entre todos os candidatos fora.</p>')
parts.append(table(pd.DataFrame(matrix),'grupos'))
quad=profile[~profile.Grupo.isin(['Núcleo','Fora'])]
parts.append(fig(px.bar(quad[quad.Perfil.isin([labels[x] for x in ['reeleicao_proxy','voto_relevante','mulher','sem_credencial']])],x='Perfil',y='Percentual',color='Grupo',facet_col='Ano',barmode='group',height=530,title='Credenciais nos quatro quadrantes')))
parts.append(table(quad,'perfis_quadrantes',True))
parts.append('<p>Comparar não eleitos do núcleo com eleitos do núcleo informa quais credenciais acompanham a conversão do apoio em mandato. Comparar eleitos fora com eleitos dentro examina trajetórias alternativas. Esses contrastes condicionam variáveis posteriores à alocação: não identificam eficiência causal nem a informação que o partido possuía antes da campanha.</p>')
parts.append(table(models[models.Modelo.str.contains('capital político')],'modelos_capital'))
parts.append('<h3>Quem não se elege dentro do núcleo?</h3><p>Modelo linear da não eleição entre candidatos com peso positivo no núcleo, ponderado pelo próprio peso de pertencimento, com efeitos fixos de lista e os mesmos controles. Coeficientes positivos indicam maior frequência de não eleição. Listas com apenas um caso completo são excluídas; listas sem variação eleitoral não identificam contrastes de resultado. Esta é uma associação condicionada ao apoio, não uma medida de desperdício.</p>')
parts.append(table(models[models.Modelo.str.startswith('Não eleição')],'modelos_inclusao'))
parts.append('</section><section id="financas"><h2>5. Eleitos fora: recursos próprios, doadores e capital político</h2><p>“Alto” significa estritamente acima da mediana dos 513 eleitos do mesmo ano, para cada fonte. Recursos privados/próprios somam apenas recursos próprios e doações de pessoas físicas, conforme a origem declarada. Valores nominais são comparados somente dentro do ano; a origem não rastreia a fonte última dos repasses.</p>')
for _,r in fin[fin.Fonte.eq('privado_proprio')].iterrows():
    parts.append(f'<p><strong>{int(r.Ano)}:</strong> {r["Fora alto %"]:.1f}% dos eleitos fora estão acima da mediana privada/própria, contra {r["Dentro alto %"]:.1f}% dentro; diferença {100*r.diferenca:+.1f} pp, IC95% [{100*r.ic95_inf:.1f}; {100*r.ic95_sup:.1f}]. Na permutação dentro das listas, p={r.p_bilateral:.4f}; após Holm para seis testes, p={r["p Holm"]:.4f}.</p>')
parts.append('<p>O intervalo usa 4.999 reamostragens de listas. O teste permuta a classificação de receita alta apenas entre eleitos da mesma lista, preservando os pesos do núcleo; sua estatística é centrada na média da distribuição permutada, que pode diferir de zero pela composição das listas. Por isso o intervalo marginal e o p condicionado respondem a perguntas diferentes. Listas informativas e tamanho efetivo aparecem abaixo.</p>')
parts.append(table(fin,'testes_financiamento'))
parts.append('<p><strong>Conclusão do teste:</strong> a diferença privada/própria agregada é positiva nos dois anos, mas nenhum dos seis testes condicionados à lista permanece abaixo de 5% após Holm. A evidência descritiva é compatível com uma via alternativa de financiamento; a evidência intralista disponível ainda não permite uma afirmação estatística forte. Não rejeitar a hipótese de permutabilidade não comprova igualdade nem ausência de mecanismo.</p>')
parts.append('<h3>Receitas e credenciais simultaneamente</h3><p>Entre eleitos de listas com pelo menos dois casos completos, o desfecho é peso fora do núcleo. Além das credenciais, entram percentis (0–1) de recursos próprios e pessoas físicas entre eleitos do ano. Um coeficiente corresponde à diferença de 100 pontos de percentil; para 10 pontos, divida-o por dez. Empates monetários recebem posto médio. A comparação é dentro da lista. Poucas listas têm eleitos dos dois lados: a inferência é exploratória e pode ser instável.</p>')
parts.append(table(models[models.Modelo.str.contains('capital e receitas')],'modelos_financiamento'))
parts.append(table(pd.DataFrame(modelmeta),'amostras_modelos'))
parts.append('<h3>Robustez ao tamanho do núcleo</h3><p>O corte monetário permanece fixo; altera-se apenas k para piso, arredondamento ou teto do NECr.</p>')
parts.append(table(pd.DataFrame(robust),'robustez'))
parts.append('</section><section><h2>6. Casos para aprofundamento</h2><p>Todos os eleitos com peso positivo fora do núcleo, inclusive empates parciais, podem ser identificados nesta tabela. O arquivo inclui ainda as credenciais. A investigação qualitativa pode distinguir autonomia financeira, trajetória anterior e financiamento partidário próximo ao corte.</p>')
cases=d[d.eleito.eq(1)&d.fora.gt(0)][KEY+['nm_candidato','sg_partido_norm','fora','vr_receita_recursos_partidos','proprios','pessoas_fisicas']+controls].sort_values(['ano_eleicao','fora'],ascending=[True,False])
parts.append(table(cases,'eleitos_fora',True))
parts.append('<h3>Como avançar no capítulo</h3><p>A composição pode formar uma seção sobre critérios observados de priorização, com o gráfico dentro/fora e o modelo de entrada. A heterogeneidade deve apresentar conjuntamente amplitude, cobertura e precisão, evitando um ranking único de coordenação. Os quatro quadrantes permitem discutir desacordos entre apoio e eleição. O financiamento alternativo funciona como teste dos limites da interpretação partidária, mas precisa ser apresentado junto à inferência intralista e ao controle de experiência.</p><p>Uma próxima etapa substantiva é vincular os candidatos aos mandatos efetivamente exercidos, suplências e cargos municipais, e estabelecer a cronologia de receitas e expectativas eleitorais. Os totais de campanha disponíveis não são informação necessariamente conhecida antes da alocação.</p></section>')
parts.append('<section id="metodo"><h2>7. Definições, limitações e reprodução</h2><ul><li>Unidade: partido × UF × eleição; federações de 2022 e coligações de 2018 não são agregadas, seguindo o capítulo.</li><li>NECr = (Σ recursos partidários)² / Σ recursos partidários². K = floor(NECr + 0,5); listas sem recursos têm K=0. Empates recebem a fração das posições restantes. Pesos complementares fora somam 1 por candidato.</li><li>Vitórias históricas usam as colunas n_eleicoes da base rrd: apesar do nome, elas contam vitórias no pipeline. O histórico de vitórias alcança 2016 para 2018 e 2020 para 2022. Votação relevante usa a flag histórica existente, sem resultado corrente. A redação do capítulo menciona janelas gerais anteriores mais curtas; documentar separadamente eleições municipais e gerais.</li><li>Incumbência é aproximada pela vitória federal quatro anos antes, identificada por CPF na própria base. Não captura suplentes em exercício, afastamentos ou saída do mandato. “Ex-federal” aqui é vitória histórica sem vitória no pleito imediatamente anterior. Vitórias municipais não comprovam exercício atual.</li><li>CPF inválido e atributos ausentes não viram ausência de experiência. Tabelas mostram perdas por atributo; modelos usam casos completos. Histórico sem registro não prova ausência de experiência política não eleitoral.</li><li>BH controla a taxa de falsas descobertas na família dos coeficientes exploratórios; Holm controla a família dos seis testes de financiamento. Os testes globais de heterogeneidade têm família BH separada. Não houve pré-registro.</li><li>Os dados representam o universo analítico do capítulo. Intervalos e p-valores são referências sob modelos de repetição ou permutação, não incerteza amostral de um sorteio de candidatos. Agrupamento por lista não elimina dependência adicional entre partidos ou UFs.</li><li>Receita é total de campanha: independência do resultado na fórmula do núcleo não estabelece antecedência temporal. Seleção entre eleitos pode induzir associação entre fontes de financiamento. Não há identificação causal, intenção partidária ou contrafactual de vitória sem apoio.</li></ul>')
parts.append('<p>Reproduzir: <code>python tese/scripts/exploracao_composicao_nucleo.py</code>. HTML autossuficiente, com gráficos incorporados, sem necessidade de internet. As tabelas CSV estão em <code>tese/resultados-exploracao-nucleo</code>.</p>')
parts.append('<p>Arquivos de dados: '+', '.join(f'<a href="resultados-exploracao-nucleo/{name}.csv">{html.escape(name)}</a>' for name in tables)+'.</p>')
parts.append(f'<p><strong>Auditoria:</strong> {len(checks)} verificações concluídas, incluindo posições por lista, universos, eleitos e reprodução da cobertura canônica para as três regras.</p></section></main></body></html>')
target=ROOT/'tese/old/relatorios-descritivos/relatorio-exploracao-nucleo-inferencial.html'
target.write_text('\n'.join(parts),encoding='utf-8')
d.drop(columns=['nr_cpf_candidato']).to_csv(OUT/'base_analitica.csv',index=False,encoding='utf-8-sig')
sources=['data/processed/rrd_df_novo.parquet','data/processed/receitas.parquet','tese/03-medindo-coordenacao-intrapartidaria.qmd','tese/scripts/exploracao_composicao_nucleo.py','tese/scripts/financiamento_alternativo_top_necr.py','src/2_gold/cap3_taa_features.py','src/2_gold/cap3_cobertura_top_necr.py']
manifest={'fontes_sha256':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},'verificacoes':checks,'python':sys.version,'pandas':pd.__version__,'numpy':np.__version__}
(OUT/'auditoria.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(target))
print(fin[['Ano','Fonte','Fora alto %','Dentro alto %','p Holm']].to_string(index=False))
