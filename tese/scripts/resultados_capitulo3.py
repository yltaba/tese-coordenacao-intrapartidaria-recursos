"""Consolida e audita resultados locais do capítulo 3; gera HTML autossuficiente."""
from pathlib import Path
import sys
import hashlib
import html
import json
from datetime import datetime

import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src/2_gold'))
from cap3_cs_features import gerar_features
from cap3_taa_features import _preparar
from cap3_cobertura_top_necr import calcular_cobertura_top_necr

DATA = ROOT / 'data/processed'
OUT = ROOT / 'tese/reports/resultados-capitulo-3'
OUT.mkdir(exist_ok=True)
KEY = ['ano_eleicao', 'sg_uf', 'sg_partido_norm']
YEARS = [2018, 2022]
checks = []


def verify(label, condition):
    checks.append({'Verificação': label, 'Resultado': 'OK' if condition else 'DIVERGÊNCIA'})
    if not condition:
        raise AssertionError(label)


raw = pd.read_parquet(DATA / 'rrd_df_novo.parquet')
raw = raw[raw.ano_eleicao.isin(YEARS)].copy()
verify('Uma linha por candidatura (ano, UF, número)', not raw.duplicated(['ano_eleicao', 'sg_uf', 'nr_candidato']).any())
verify('Recursos partidários não negativos', raw.vr_receita_recursos_partidos.fillna(0).ge(0).all())
d = _preparar(gerar_features(raw))
p = pd.read_parquet(DATA / 'df_calibracao_lista.parquet').query('ano_eleicao in @YEARS').copy()
c = pd.read_parquet(DATA / 'df_cobertura_top_necr_lista.parquet').copy()
fresh, summary = calcular_cobertura_top_necr(raw)
stored_summary = pd.read_csv(DATA / 'df_cobertura_top_necr_resumo.csv')
for label, a, b, keys in [('Cobertura por nominata', c, fresh, KEY), ('Resumo nacional da cobertura', stored_summary, summary, ['ano_eleicao', 'regra_k'])]:
    a, b = a.sort_values(keys).reset_index(drop=True), b.sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b, check_dtype=False, rtol=1e-9, atol=1e-8)
    verify(label + ': arquivo salvo reproduzido a partir das candidaturas', True)
cross = p.merge(c, on=KEY, suffixes=('_p', '_c'), validate='one_to_one')
verify('Painéis de calibração e cobertura: NECr, candidatos e eleitos coincidem', len(cross) == len(p) and np.allclose(cross.NECr_p, cross.NECr_c) and (cross.n_cands == cross.n_candidatos).all() and (cross.S == cross.n_eleitos).all())
agg = d.groupby(KEY, observed=True).agg(Mp=('Mp','first'), qt_vaga=('qt_vaga','first'), tipo=('tipo_partido_exante','first'), F=('candidato_competitivo','sum'), F_nom=('candidato_competitivo_nom','sum')).reset_index()
l = c.merge(agg, on=KEY, validate='one_to_one')
verify('Todas as nominatas têm metadados', l.qt_vaga.notna().all())
verify('Bancada do painel salvo coincide com a junção atual', (p.merge(agg, on=KEY).Mp_x == p.merge(agg, on=KEY).Mp_y).all())
l = l.rename(columns={'n_candidatos':'C','n_eleitos':'E','n_com_recursos':'Recebedores','total_recursos_partidarios':'Recursos'})
l['Magnitude'] = pd.cut(l.qt_vaga, [0,12,31,70], labels=['Pequeno (8–12)','Médio (16–31)','Grande (39–70)']).astype(str)
l['D'] = l.C - l.NECr
l.loc[l.D.abs() < 1e-10, 'D'] = 0.0
l['Q'] = l.C / l.NECr
l['NECr_Mp'] = l.NECr / l.Mp.where(l.Mp > 0)
l['NECr_E'] = l.NECr / l.E.where(l.E > 0)
l['NECr_menos_E'] = l.NECr - l.E
l['NECr_menos_Mp'] = l.NECr - l.Mp
l['F_Mp'] = l.F / l.Mp.where(l.Mp > 0)
l['F_menos_Mp'] = l.F - l.Mp
l['Competitivos_pct'] = 100 * l.F / l.C
l['Sem_recursos'] = l.C - l.Recebedores
l['Cobertura_pct'] = 100 * l.eleitos_top_arredondado / l.E.where(l.E > 0)
l['Precisao_pct'] = 100 * l.eleitos_top_arredondado / l.k_arredondado.where(l.k_arredondado > 0)
l['Aleatoria_pct'] = 100 * l.eleitos_esperados_aleatorio_arredondado / l.E.where(l.E > 0)
fund = l[l.Recursos > 0].copy()
verify('NECr entre 1 e o número de recebedores', (fund.NECr >= 1-1e-9).all() and (fund.NECr <= fund.Recebedores+1e-9).all())
verify('513 eleitos em cada eleição', (l.groupby('ano_eleicao').E.sum() == 513).all())

LABELS = {'C':'Candidatos (C)', 'F':'Competitivos (F)', 'F_nom':'Competitivos: QE nominal (robustez)', 'Competitivos_pct':'Competitivos na lista (%)', 'Mp':'Bancada pré-eleitoral (Mp)', 'E':'Eleitos (E)', 'Recebedores':'Candidatos com recursos positivos', 'Sem_recursos':'Candidatos sem recursos partidários', 'Recursos':'Recursos partidários por lista (R$ nominais)', 'NECr':'NECr', 'D':'D = C − NECr', 'Q':'Q = C / NECr', 'NECr_Mp':'NECr / Mp (Mp > 0)', 'F_Mp':'F / Mp (Mp > 0)', 'F_menos_Mp':'F − Mp (Mp > 0)', 'NECr_menos_Mp':'NECr − Mp (Mp > 0)', 'NECr_E':'NECr / E (E > 0)', 'NECr_menos_E':'NECr − E', 'Cobertura_pct':'Cobertura Top-NECr por lista (%)', 'Precisao_pct':'Precisão Top-NECr por lista (%)', 'Aleatoria_pct':'Cobertura aleatória por lista (%)'}
tables = {}


def stats(frame, cols, by=('ano_eleicao',)):
    rows = []
    for key, g in frame.groupby(list(by), observed=True, sort=True):
        key = key if isinstance(key, tuple) else (key,)
        for col in cols:
            s = g[col].replace([np.inf, -np.inf], np.nan).dropna().astype(float)
            rows.append(dict(zip(by, key)) | {'Indicador':LABELS.get(col,col), 'N válido':len(s), 'Indefinidos':len(g)-len(s), 'Média':s.mean(), 'Desvio-padrão':s.std(ddof=1), 'Mínimo':s.min(), 'P25':s.quantile(.25), 'Mediana':s.median(), 'P75':s.quantile(.75), 'Máximo':s.max()})
    return pd.DataFrame(rows).rename(columns={'ano_eleicao':'Ano','sg_uf':'UF','sg_partido_norm':'Partido','tipo':'Tipo de partido'})


def fmt(x):
    if pd.isna(x): return '—'
    if isinstance(x, (int, np.integer)): return f'{x:,}'.replace(',','.')
    if isinstance(x, (float, np.floating)): return f'{x:,.3f}'.replace(',','X').replace('.',',').replace('X','.')
    return str(x)


def table(frame, name, title='', collapsed=False):
    tables[name] = frame
    frame.to_csv(OUT / (name+'.csv'), index=False, encoding='utf-8-sig')
    rendered = frame.map(fmt).to_html(index=False, escape=True, border=0, classes='data')
    content = f'<h3>{html.escape(title)}</h3>' if title else ''
    content += '<div class="scroll">'+rendered+'</div>'
    return f'<details><summary>{html.escape(title)} · {len(frame)} linhas</summary>{content}</details>' if collapsed else content


parts = []
def section(id_, title, text=''):
    parts.append(f'<section id="{id_}"><h2>{title}</h2>{text}')
def end(): parts.append('</section>')

universe = []
for year, g in l.groupby('ano_eleicao'):
    universe.append({'Ano':year,'Candidaturas':g.C.sum(),'Competitivas':g.F.sum(),'Competitivas (%)':100*g.F.sum()/g.C.sum(),'Nominatas':len(g),'Com recursos':(g.Recursos>0).sum(),'Sem recursos':(g.Recursos<=0).sum(),'Com Mp > 0':(g.Mp>0).sum(),'Com recursos e Mp > 0':((g.Recursos>0)&(g.Mp>0)).sum(),'Com eleitos':(g.E>0).sum(),'Com recursos e eleitos':((g.Recursos>0)&(g.E>0)).sum(),'Eleitos':g.E.sum(),'Eleitos em listas sem recursos':g.loc[g.Recursos<=0,'E'].sum()})
u = pd.DataFrame(universe)
section('panorama','1. Panorama e critérios de leitura', '<p>Deputado Federal, eleições de 2018 e 2022. Unidade principal: nominata <strong>partido × UF × eleição</strong>; federações não são agregadas. Os resultados descrevem a base analítica do repositório, sem presumir cobertura de todas as inscrições brutas no TSE.</p><p>As médias e os desvios-padrão são calculados entre nominatas, sem ponderação. O desvio-padrão usa denominador N − 1; não é erro-padrão. Percentuais nacionais de candidaturas e de eleitos são razões de somas e estão identificados como tais. Quartis usam interpolação linear. Valores exibidos com três casas; os CSVs preservam a precisão. “—” indica valor indefinido.</p>')
parts.append(table(u,'01_universos'))
synopsis = pd.concat([
    stats(fund,['NECr','D','Q','NECr_Mp','NECr_E']),
    stats(l,['F','Competitivos_pct']),
], ignore_index=True)
parts.append(table(synopsis[['Ano','Indicador','N válido','Média','Desvio-padrão','Mediana']], '00_sintese', 'Síntese dos indicadores centrais'))
parts.append('<p><strong>Leitura dos resultados.</strong> O número efetivo médio de candidaturas financiadas aumenta, assim como as razões NECr/Mp e NECr/E. Já a razão média C/NECr diminui: a ampliação do núcleo efetivo supera proporcionalmente a ampliação das listas. A cobertura nacional dos eleitos cresce de 86,745% para 92,630%, enquanto o benchmark aleatório permanece próximo de 43,8%. São comparações descritivas entre eleições.</p>')
parts.append('<p>Listas sem recursos permanecem no universo descritivo, mas têm NECr indefinido. NECr/Mp exige Mp &gt; 0; NECr/E exige E &gt; 0. A diferença C − NECr não conta candidatos sem financiamento. Recursos são valores nominais de cada eleição, sem correção monetária.</p>')
end()
section('competitivos','2. Candidaturas competitivas e referência pré-eleitoral', '<p>Classificação existente: vitória anterior para prefeito, deputado estadual/distrital, deputado federal, governador ou senador, ou alcance histórico de 10% do quociente eleitoral. Vereador é excluído do critério de vitória. Ver divergências de redação na seção 7. Tipo de partido: bancada nacional pré-eleitoral de ao menos 20 deputados; esta classificação é ex-ante.</p>')
parts.append(table(stats(l,['C','F','F_nom','Competitivos_pct','Mp','E']),'02_competitivos_ano'))
comp=[]
for keys,g in l.groupby(['ano_eleicao','Magnitude','tipo'],observed=True):
    comp.append(dict(zip(['Ano','Magnitude','Tipo de partido'],keys)) | {'Listas':len(g),'Candidatos':g.C.sum(),'Competitivos':g.F.sum(),'Competitivos / candidatos (%)':100*g.F.sum()/g.C.sum()})
parts.append(table(pd.DataFrame(comp),'03_competitivos_magnitude_tipo','Proporção agregada de candidaturas competitivas'))
parts.append(table(stats(l,['C','F','Competitivos_pct','Mp'],('ano_eleicao','Magnitude','tipo')),'04_competitivos_distribuicoes','Distribuições por magnitude e tipo de partido',True))
end()
section('concentracao','3. Concentração de recursos e número de candidatos', '<p><strong>NECr = 1 / Σsᵢ²</strong>, com sᵢ igual à fração dos recursos partidários da lista recebida pelo candidato. <strong>D = C − NECr</strong>; <strong>Q = C / NECr</strong>. Universo: nominatas com total positivo de recursos partidários.</p>')
cols=['C','Recebedores','Sem_recursos','Recursos','NECr','D','Q']
parts.append(table(stats(fund,cols),'05_concentracao_ano'))
parts.append(table(stats(fund,cols,('ano_eleicao','Magnitude')),'06_concentracao_magnitude','Resultados por magnitude'))
end()
section('bancada','4. Correspondência com a referência pré-eleitoral de cadeiras','<p><strong>CorrespondRec = NECr / Mp</strong>. A razão igual a 1 indica correspondência de escala; acima de 1, mais candidaturas efetivas que cadeiras da bancada; abaixo de 1, menos. Trata-se de referência observável, não de medida direta da expectativa da liderança.</p>')
parts.append(table(stats(fund,['NECr_Mp']),'07_razao_bancada_ano','NECr/Mp: válidos e exclusões'))
mp = fund[fund.Mp>0]
parts.append(table(stats(mp,['NECr','Mp','NECr_Mp','NECr_menos_Mp'],('ano_eleicao','Magnitude')),'08_razao_bancada_magnitude','NECr/Mp por magnitude'))
parts.append(table(stats(l[l.Mp>0],['F','Mp','F_Mp','F_menos_Mp']),'09_competitivos_bancada','Competitivos e bancada: todas as listas com Mp > 0'))
threshold=[]
for by in [('ano_eleicao',),('ano_eleicao','Magnitude')]:
    for keys,g in l[l.Mp>0].groupby(list(by),observed=True):
        keys=keys if isinstance(keys,tuple) else (keys,)
        for label, sub, flag in [('F ≤ Mp + 1',g,g.F<=g.Mp+1),('NECr ≤ Mp + 1 (contínuo)',g[g.Recursos>0],g.loc[g.Recursos>0,'NECr']<=g.loc[g.Recursos>0,'Mp']+1),('NECr arredondado ≤ Mp + 1 (figura antiga)',g[g.Recursos>0],g.loc[g.Recursos>0,'NECr'].round()<=g.loc[g.Recursos>0,'Mp']+1)]:
            threshold.append(dict(zip(by,keys))|{'Regra':label,'N':len(sub),'Listas dentro do limite':int(flag.sum()),'Dentro do limite (%)':100*flag.mean()})
th=pd.DataFrame(threshold).fillna({'Magnitude':'Total'}).rename(columns={'ano_eleicao':'Ano'})
parts.append(table(th,'10_limites_mp_mais_um','Correspondência com Mp + 1: regra contínua e arredondada'))
parts.append('<p>A figura antiga aplica round() ao NECr antes do corte. Para o indicador contínuo, a categoria complementar correta é NECr &gt; Mp + 1, pois o NECr não precisa ser inteiro.</p>')
end()
section('eleitos','5. Correspondência com o resultado eleitoral','<p><strong>CorrespondEleit = NECr / E</strong>, definida para E &gt; 0. A razão compara o tamanho efetivo da alocação ao número de eleitos e não identifica se os maiores recebedores venceram. A diferença NECr − E também é apresentada, com o universo explicitado.</p>')
parts.append(table(stats(fund,['NECr_E','NECr_menos_E']),'11_resultado_ano','Todas as listas financiadas: razão com exclusões e diferença'))
parts.append(table(stats(fund[fund.E>0],['E','NECr','NECr_E','NECr_menos_E']),'12_resultado_com_eleitos','Somente listas financiadas com eleitos'))
parts.append(table(stats(fund[fund.E>0],['NECr_E','NECr_menos_E'],('ano_eleicao','Magnitude')),'13_resultado_magnitude','Listas com eleitos, por magnitude'))
parts.append(table(stats(fund[fund.E==0],['C','NECr','Recursos']),'14_sem_eleitos','Listas financiadas sem eleitos'))
end()
section('cobertura','6. Eleitos entre os candidatos priorizados: Top-NECr','<p>Regra principal: k = floor(NECr + 0,5). Ordenação decrescente de recursos partidários; empates no corte recebem crédito fracionário. Por isso o número de eleitos cobertos pode ser fracionário. Sem recursos, k = 0. Todos os 513 eleitos permanecem no denominador nacional.</p><p><strong>Cobertura nacional = Σ eleitos no Top-k / 513</strong>. Benchmark: sorteio de k candidatos entre os C da própria nominata; cobertura esperada = Σ(E × k/C)/513. <strong>Precisão = Σ eleitos no Top-k / Σk</strong>. A média entre listas não equivale à cobertura nacional.</p>')
ss=summary.copy()
ss['Precisão nacional (%)']=100*ss.eleitos_top_necr/ss.n_posicoes_top_necr
ss['Ganho sobre aleatório (p.p.)']=100*(ss.cobertura-ss.cobertura_aleatoria)
ss['cobertura']*=100
ss['cobertura_aleatoria']*=100
ss=ss.rename(columns={'ano_eleicao':'Ano','regra_k':'Regra de k','eleitos_total':'Eleitos','eleitos_top_necr':'Eleitos cobertos (fracionários)','cobertura':'Cobertura nacional (%)','eleitos_esperados_aleatorio':'Eleitos esperados ao acaso','cobertura_aleatoria':'Cobertura aleatória (%)','n_posicoes_top_necr':'Posições Top-k','n_candidatos':'Candidatos','eleitos_em_listas_sem_recursos':'Eleitos em listas sem recursos'})
parts.append(table(ss,'15_cobertura_nacional','Resultado principal e sensibilidade ao arredondamento'))
parts.append(table(stats(l[l.E>0],['Cobertura_pct','Aleatoria_pct']),'16_cobertura_distribuicao','Distribuição da cobertura entre listas com eleitos'))
parts.append(table(stats(fund,['Precisao_pct']),'17_precisao_distribuicao','Distribuição da precisão entre listas financiadas'))
coverage=[]
for (year,mag),g in l.groupby(['ano_eleicao','Magnitude'],observed=True):
    coverage.append({'Ano':year,'Magnitude':mag,'Eleitos':g.E.sum(),'Eleitos cobertos':g.eleitos_top_arredondado.sum(),'Cobertura (%)':100*g.eleitos_top_arredondado.sum()/g.E.sum(),'Aleatória (%)':100*g.eleitos_esperados_aleatorio_arredondado.sum()/g.E.sum(),'Precisão (%)':100*g.eleitos_top_arredondado.sum()/g.k_arredondado.sum()})
parts.append(table(pd.DataFrame(coverage),'18_cobertura_magnitude','Cobertura agregada por magnitude'))
end()

section('auditoria','7. Conferência da redação e das fontes','<p>Os resultados acima reutilizam os painéis salvos e acrescentam apenas agregações e razões derivadas. A cobertura foi reproduzida desde a base de candidaturas; o NECr, C e E foram confrontados entre painéis. As observações abaixo devem orientar a atualização do texto antes da incorporação à tese.</p>')
issues=[
('Data da bancada','O texto diz véspera das convenções. O script de extração usa 20/07/2018 e 20/07/2022; o CSV não guarda a data de referência. Não é possível certificar pelo CSV que representa a véspera. As estatísticas usam o arquivo disponível.'),
('Competitivos até Mp + 1: números do texto','A redação informa 94% em 2018 e 56% em 2022. Os scripts atuais e a base consolidada retornam 238/292 = 81,507% e 102/252 = 40,476%. Estes números precisam ser corrigidos na redação; a divergência não é explicada pela normalização de siglas.'),
('Correção I-3-002: critério (ii) de competitivo restrito a disputa proporcional','Aplicada em 2026-09-14. O critério de 10% do quociente eleitoral (candidato_competitivo) passou a valer só para Dep. Federal/Estadual, removendo Governador/Senador/Prefeito de gerar_rrd.py::adicionar_alcancou_10pct_qe_hist, conforme tese/03-medindo-coordenacao-intrapartidaria.qmd l. 68 e a recomendação I-3-002 de thesis-review/runs/run-001/synthesis/final_review.md. F (candidato_competitivo) cai de 886→879 em 2018 e 1287→1261 em 2022 (Dep. Federal), antes da correção D2 abaixo. Base e relatório anteriores arquivados em data/processed/archive/pre-i3-002_2026-09-14/ e tese/reports/old/rascunhos/resultados-capitulo-3-pre-i3-002_2026-09-14/.'),
('Correção I-3-001/D2: zfill(11) no CPF de 2012/2014','Aplicada em 2026-09-14. gerar_rrd.py::carregar_dados passou a normalizar nr_cpf_candidato com zfill(11) na leitura de candidatos.parquet (28,6% dos CPFs de 2012 e 26,4% dos de 2014 estavam gravados sem zeros à esquerda, quebrando o merge histórico por CPF-string para candidaturas com CPF iniciado em "0"), conforme a recomendação nº 1 de I-3-001 em thesis-review/runs/run-001/synthesis/final_review.md. F (candidato_competitivo) sobe de 879→938 em 2018 e 1261→1275 em 2022 (Dep. Federal, já com I-3-002 aplicado).'),
('Correção I-3-001/D1+D3: ligação de CPF por cargo/município e desempate pelo registro APTO','Aplicada em 2026-09-14. gerar_rrd.py ganhou ligar_cpf/_preparar_candidatos_cpf, substituindo os antigos drop_duplicates(["ano","uf","numero"], keep="first") em construir_base, _construir_resultados_select e _gerar_resultados_cpf (recomendações 2-3 de I-3-001). A chave agora inclui o cargo e, em Prefeito/Vereador, também o município (D1); entre CPFs distintos sob o mesmo número (substituição de candidato), prioriza ds_situacao_candidatura == "APTO" em vez do primeiro registro do arquivo (D3). F (candidato_competitivo) sobe de 938→973 em 2018 e 1275→1354 em 2022. Checagens confirmadas: dos 378 deputados federais eleitos em 2014 que concorreram em 2018, 377/377 contam como competitivos (era 353/378); "2022 MG AVANTE 7025" caiu de 46 para 1 vitória de prefeito; os 3 casos de identidade trocada citados na revisão (Pauderney Avelino, Andréia Zemuner, José Arnon Bezerra) têm CPF/gênero corrigidos. Residual: casamento de município por nome não recupera mojibake já corrompido na origem (~0,7% das linhas de Prefeito 2012-2022 ficam sem CPF ligado). Bases e relatórios anteriores a cada correção arquivados em data/processed/archive/pre-i3-002_2026-09-14/, pre-i3-001-d2-zfill_2026-09-14/ e pre-i3-001-d1d3_2026-09-14/, e em tese/reports/old/rascunhos/resultados-capitulo-3-pre-i3-002_2026-09-14/, -pre-i3-001-d2-zfill_2026-09-14/ e -pre-i3-001-d1d3_2026-09-14/.'),
('Diferença NECr − eleitos','As medianas 1,25 e 4,18 do texto correspondem a todas as listas financiadas, incluindo listas sem eleitos. Restritas às listas com eleitos, as medianas são 0,908 e 4,402. A razão NECr/E necessariamente usa apenas listas com eleitos.'),
('Origem partidária e fonte pública','gerar_rrd.py define vr_receita_recursos_partidos pela origem “Recursos de partido político”. A coluna não é selecionada exclusivamente pela fonte FEFC/FP. A redação deve distinguir origem partidária de fonte pública; o relatório preserva a variável usada nos indicadores existentes.'),
('Histórico de vitórias','O texto encerra o histórico em 2014 e 2018; gerar_rrd.py considera vitórias até 2016 para 2018 e até 2020 para 2022, incluindo eleições municipais anteriores.'),
('Cargos elegíveis','A redação inclui Presidente. A classificação implementada não contém coluna de vitórias presidenciais; inclui deputado distrital junto de estadual. Estes resultados preservam a implementação existente.'),
('Gráfico de competitivos','O script atual cap3_plot_competitivos_mag.py agrega somente por magnitude. O parágrafo da tese também descreve tipos de partido; os cruzamentos estão fornecidos na seção 2 com tipo ex-ante.'),
('Tipo de partido','gerar_features define tipo_partido pelo resultado nacional da própria eleição. O relatório usa tipo_partido_exante da bancada prévia para evitar usar o resultado na classificação do partido.'),
('NECr e Mp + 1','O script das figuras arredonda NECr antes da comparação. O relatório distingue a regra contínua da arredondada e usa a junção normalizada da bancada.'),
('Siglas da bancada','Painéis consolidados normalizam acentos e aliases e somam por chave. Scripts antigos de figuras fazem junção por sigla sem a mesma normalização. A comparação numérica entre essas versões aparece abaixo.'),
('Interpretação','Diferença C − NECr não é contagem de candidatos sem financiamento; aumento descritivo entre 2018 e 2022 não identifica efeito causal de mudanças institucionais. Cobertura dos eleitos tampouco demonstra isoladamente coordenação intencional.'),
]
parts.append(table(pd.DataFrame(issues,columns=['Ponto','Constatação']),'19_notas_redacao'))
# Reproduzir exatamente a junção e o arredondamento dos scripts das figuras.
from cap3_cs_plot_necr_eficiencia_bancada import carregar_bancada as bancada_antiga, calcular_nec_lista_painel
from cap3_cs_plot_fortes_vagas_bancada import gerar_listas_tab4, gerar_listas_nec
old_b=bancada_antiga()
features=gerar_features(raw)
old_f=gerar_listas_tab4(features,old_b)
old_n=gerar_listas_nec(features,old_f)
reconcile=[]
for year in YEARS:
    old=calcular_nec_lista_painel(features[features.ano_eleicao==year],old_b[old_b.ano_eleicao==year],'vr_receita_recursos_partidos',str(year))
    for mag in sorted(l.Magnitude.unique()):
        a=old[old.dm_cat.astype(str)==mag].nec_eficiencia
        b=mp[(mp.ano_eleicao==year)&(mp.Magnitude==mag)].NECr_Mp
        reconcile.append({'Ano':year,'Indicador':'Média NECr/Mp — '+mag,'Script antigo':a.mean(),'Junção consolidada':b.mean(),'N antigo':len(a),'N consolidado':len(b)})
    for label,a,b in [('F ≤ Mp + 1 (%)',old_f[old_f.ano_eleicao==year].excesso.le(1), l[(l.ano_eleicao==year)&(l.Mp>0)].F_menos_Mp.le(1)),('NECr arredondado ≤ Mp + 1 (%)',old_n[old_n.ano_eleicao==year].excesso_nec.le(1),mp[mp.ano_eleicao==year].NECr.round().le(mp[mp.ano_eleicao==year].Mp+1))]:
        reconcile.append({'Ano':year,'Indicador':label,'Script antigo':100*a.mean(),'Junção consolidada':100*b.mean(),'N antigo':len(a),'N consolidado':len(b)})
parts.append(table(pd.DataFrame(reconcile),'20_confronto_scripts','Figuras existentes versus junção consolidada'))
parts.append(table(pd.DataFrame(checks),'21_verificacoes','Verificações executadas'))
end()

section('apendices','8. Resultados completos por partido, UF e nominata','<p>As tabelas expansíveis preservam todas as linhas. Use a busca para localizar partido, UF ou indicador. Nas distribuições abaixo, C, F, Mp e E descrevem todas as listas; os indicadores de recursos têm N válido próprio. Razões com denominador zero permanecem indefinidas.</p>')
allcols=['C','F','Competitivos_pct','Mp','E','NECr','D','Q','NECr_Mp','NECr_E','NECr_menos_E','Cobertura_pct','Precisao_pct']
parts.append(table(stats(l,allcols,('ano_eleicao','sg_partido_norm')),'22_por_partido','Estatísticas por partido e eleição',True))
parts.append(table(stats(l,allcols,('ano_eleicao','sg_uf')),'23_por_uf','Estatísticas por UF e eleição',True))
parts.append(table(stats(l,allcols,('ano_eleicao','Magnitude','tipo')),'24_por_magnitude_tipo','Estatísticas por magnitude e tipo de partido',True))
detailcols=KEY+['Magnitude','tipo','C','F','Mp','E','Recursos','Recebedores','Sem_recursos','NECr','D','Q','NECr_Mp','NECr_E','NECr_menos_E','k_arredondado','eleitos_top_arredondado','Cobertura_pct','Precisao_pct']
parts.append(table(l[detailcols].sort_values(KEY).rename(columns={'ano_eleicao':'Ano','sg_uf':'UF','sg_partido_norm':'Partido'}),'25_todas_nominatas','Painel completo de nominatas',True))
end()

section('fontes','9. Arquivos encontrados e reprodução','<p>Escopo principal determinado pelas seções do capítulo 3. Bases de sobrevivência, modelos de montante e timing pertencem ao mecanismo causal do capítulo 4 e não foram misturadas a este relatório. TAA, decomposições do NECr e métricas antigas de concentração são inventariadas como materiais complementares.</p>')
roles={
'rrd_df_novo.parquet':'Base de candidaturas: classificação competitiva e verificação independente de NECr e cobertura.',
'bancada_partido_uf.csv':'Referência pré-eleitoral de cadeiras (Mp).',
'df_calibracao_lista.parquet':'Painel salvo: NECr, candidatos, eleitos, Mp, diferenças e razões; confrontado com cobertura.',
'df_cobertura_top_necr_lista.parquet':'Painel principal de nominatas, inclui listas sem recursos.',
'df_cobertura_top_necr_resumo.csv':'Cobertura nacional e sensibilidade: piso, arredondamento e teto.',
'df_taa_lista.parquet':'Complementar: acerto entre os Mp maiores recebedores; não confundir com Top-NECr.',
'df_metricas_concentracao_recursos.parquet':'Complementar antigo: Gini e NECr por vaga distrital, distintos de NECr/Mp e NECr/E.',
'historico_eleitoral_deputados_2018_2022.parquet':'Histórico auxiliar; classificação deste relatório utiliza flags da base consolidada.',
}
inventory=[]
for name,role in roles.items():
    f=DATA/name
    inventory.append({'Arquivo':'data/processed/'+name,'Uso':role,'Bytes':f.stat().st_size,'Modificado em':datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec='seconds'),'SHA-256':hashlib.sha256(f.read_bytes()).hexdigest()})
parts.append(table(pd.DataFrame(inventory),'26_fontes','Rastreabilidade dos dados'))
parts.append('<p>Reprodução, a partir da raiz do repositório: <code>python tese/scripts/resultados_capitulo3.py</code>. Dependências: Python, pandas, NumPy, leitor Parquet e Plotly (importado pelos scripts existentes). A execução só grava nesta pasta de resultados, preservando bases e texto da tese.</p>')
parts.append('<p>Scripts consultados: <code>src/2_gold/cap3_cs_features.py</code>, <code>cap3_taa_features.py</code>, <code>cap3_calibracao_features.py</code>, <code>cap3_cobertura_top_necr.py</code>, <code>cap3_plot_competitivos_mag.py</code>, <code>cap3_cs_plot_necr_eficiencia_bancada.py</code>, <code>cap3_cs_plot_fortes_vagas_bancada.py</code>, <code>src/1_silver/gerar_rrd.py</code> e <code>src/0_bronze/bancada_por_partido_uf.py</code>.</p>')
end()

css='''body{margin:0;background:#f3f5f7;color:#203047;font:15px/1.6 system-ui,sans-serif}header{background:#173b50;color:white;padding:40px max(4%,calc((100vw - 1400px)/2))}header p{max-width:1000px;color:#dbe7eb}h1{font-size:34px;line-height:1.2}h2{color:#173b50;font-size:25px}h3{font-size:18px}main{max-width:1400px;margin:auto;padding:24px}section{background:white;padding:26px;margin:20px 0;border-radius:10px;border:1px solid #dce3e8}nav{display:flex;gap:15px;flex-wrap:wrap}nav a{color:#fff}p{max-width:1150px}.scroll{overflow:auto;max-height:680px;border:1px solid #dde5eb;margin:16px 0}table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}td,th{padding:9px 12px;border-bottom:1px solid #e1e6eb;text-align:right;white-space:nowrap}th{position:sticky;top:0;background:#eaf0f4;color:#173b50;z-index:1}td:first-child,th:first-child{text-align:left}tr:nth-child(even){background:#f6f9fb}tr:hover{background:#e9f3f5}#auditoria td,#fontes td{white-space:normal;min-width:140px;text-align:left}details{margin:20px 0;border:1px solid #dce3e8;padding:15px;border-radius:6px}summary{cursor:pointer;font-weight:650;color:#15516b}input{padding:12px;border:1px solid #abbec9;border-radius:5px;width:min(90%,500px)}button{padding:11px 18px;background:#17647a;color:white;border:0;border-radius:5px;cursor:pointer}code{background:#edf2f5;padding:3px 6px}header code{background:#285267}.hint{color:#526878}.cards{display:flex;flex-wrap:wrap;gap:15px}.card{background:#f1f7f9;border-left:4px solid #1d7485;padding:15px;flex:1;min-width:240px}.card strong{font-size:25px;display:block}.bar{height:12px;background:#20798c;border-radius:3px;margin:5px 0}@media print{body{background:white}header{color:black;background:white;padding:0}header p,nav a{color:black}main{padding:0}section{break-inside:auto;border:0;padding:5px}.scroll{max-height:none;overflow:visible}table{font-size:8px}td,th{padding:3px;white-space:normal}input,button,nav{display:none}details:not([open]){display:none}}'''
nav=''.join(f'<a href="#{i}">{t}</a>' for i,t in [('panorama','Panorama'),('competitivos','Competitivos'),('concentracao','Concentração'),('bancada','Bancada'),('eleitos','Resultado eleitoral'),('cobertura','Top-NECr'),('auditoria','Conferência'),('apendices','Tabelas completas'),('fontes','Fontes')])
cards=[]
for year in YEARS:
    g=fund[fund.ano_eleicao==year]
    s=summary[(summary.ano_eleicao==year)&(summary.regra_k=='arredondado')].iloc[0]
    cards.append(f'<div class="card">{year} · NECr médio<strong>{fmt(g.NECr.mean())}</strong>DP {fmt(g.NECr.std())} · mediana {fmt(g.NECr.median())}<br>Cobertura nacional: {fmt(100*s.cobertura)}%<div class="bar" style="width:{100*s.cobertura:.2f}%"></div>{len(g)} nominatas financiadas</div>')
js='''document.getElementById('search').addEventListener('input',function(){const q=this.value.toLocaleLowerCase('pt-BR');document.querySelectorAll('tbody tr').forEach(r=>r.hidden=q&&!r.textContent.toLocaleLowerCase('pt-BR').includes(q));});document.getElementById('expand').onclick=()=>document.querySelectorAll('details').forEach(d=>d.open=true);'''
doc='<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Capítulo 3 — Resultados completos</title><style>'+css+'</style></head><body><header><p>TESE · CADERNO DE RESULTADOS</p><h1>Medindo coordenação intrapartidária</h1><p>Capítulo 3 · 2018 e 2022 · Estatísticas completas, universos explícitos e conferência dos indicadores já calculados.</p><nav>'+nav+'</nav></header><main><div class="cards">'+''.join(cards)+'</div><p><label for="search">Buscar nas tabelas: </label><input id="search" placeholder="Ex.: NECr, 2022, SP, PT"><button id="expand">Expandir apêndices</button></p><p class="hint">HTML autossuficiente, sem conexão externa. Para imprimir os apêndices, expanda-os antes. Gerado em '+datetime.now().isoformat(timespec='seconds')+'.</p>'+''.join(parts)+'</main><script>'+js+'</script></body></html>'
(OUT/'resultados-capitulo-3.html').write_text(doc,encoding='utf-8')
(OUT/'verificacao.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(u.to_string(index=False))
print(pd.DataFrame(reconcile).to_string(index=False))
print(f'HTML: {OUT / "resultados-capitulo-3.html"}; tabelas CSV: {len(tables)}; verificações: {len(checks)}')
