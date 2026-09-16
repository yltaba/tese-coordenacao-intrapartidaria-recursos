"""Confere referências, figuras e tabelas novas do capítulo contra os CSVs."""
from pathlib import Path
import re
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
TESE=ROOT/'tese'
path=TESE/'03-medindo-coordenacao-intrapartidaria-reestruturado.qmd'
source=path.read_text(encoding='utf-8')
ids=re.findall(r'\{#([\w-]+)',source)
assert len(ids)==len(set(ids))
refs=set(re.findall(r'@(\w[\w-]*)',source))
bib=set(re.findall(r'@\w+\{([^,]+),',(TESE/'references.bib').read_text(encoding='utf-8')))
assert not refs-set(ids)-bib
images=re.findall(r'!\[.*?\]\(([^)]+)\)',source)
assert all((TESE/x).is_file() for x in images)
tables={name:[[v.strip() for v in row.strip().strip('|').split('|')] for row in text.strip().splitlines()[2:]]
        for text,name in re.findall(r'((?:\|[^\n]*\n)+)\n: [^\n]*\{#(tbl-[^}]+)\}',source)}

def f(x):return f'{x:.2f}'.replace('.',',').replace('-','−')
def interval(lo,hi):return '['+f(lo)+'; '+f(hi)+']'

t1=pd.read_csv(TESE/'resultados-teto-financiamento/teste1_eleitos_fora.csv')
desc=pd.read_csv(TESE/'resultados-teto-financiamento/descritivos.csv')
for row in tables['tbl-alternativos-fora']:
    year=int(row[0]); broad=row[1]=='Não partidários'
    label='Não partidários (amplo)' if broad else 'Próprios + pessoas físicas'
    a=desc[(desc.Ano==year)&(desc.Fonte==label)&(desc.Estrato=='Todos')].set_index('Eleito')
    b=t1[(t1.Ano==year)&(t1.Fonte==label)&t1.Modelo.str.startswith('Ajustado')].iloc[0]
    assert row[2:]==[f(a.loc[1,'Media_pct']),f(a.loc[0,'Media_pct']),f(b.Beta),interval(b.IC_inf,b.IC_sup)],row
t2=pd.read_csv(TESE/'resultados-teto-financiamento/teste2_alocacao.csv')
t3=pd.read_csv(TESE/'resultados-teto-financiamento/teste3_temporal.csv')
for row in tables['tbl-apendice-substituicao']:
    frame=t3 if row[0].startswith('Temporal') else t2
    label='Não partidários (amplo)' if row[1]=='Não partidários' else 'Próprios + pessoas físicas'
    expected=[]
    for year in [2018,2022]:
        g=frame[(frame.Ano==year)&(frame.Fonte==label)]
        if frame is t2:g=g[g.Modelo.eq('Só competitivos prévios' if 'competitivos' in row[0] else 'Todas as candidaturas')]
        b=g.iloc[0]
        expected += [f(10*b.Beta),interval(10*b.IC_inf,10*b.IC_sup)]
    assert row[2:]==expected,row
expense=pd.read_csv(TESE/'exploracao-gastos-teto/resumo.csv')
for row in tables['tbl-apendice-gastos']:
    label='Todos' if row[0].startswith('Todos') else row[0].replace(' do Top',' Top')
    g=expense[(expense.Grupo==label)&expense.Medida.eq('gasto_pct')].set_index('Ano')
    assert row[1:]==[f(g.loc[y,c]) for y in [2018,2022] for c in ['Mediana_pct','Pct_ge95']],row
quad=pd.read_csv(TESE/'resultados-financiamento-alternativo/testes.csv')
for row in tables['tbl-apendice-eleitos-alternativos']:
    g=quad[(quad.Ano==int(row[0]))&quad.Medida.eq('privado_proprio')].iloc[0]
    assert row[3]==f(100*g.diferenca)
    assert row[4]==interval(100*g.ic95_inf,100*g.ic95_sup)
    assert row[5]==str(int(g.listas_informativas))
    assert row[6]==f'{g.p_bilateral:.3f}'.replace('.',',')
    assert row[7]==f'{g.p_holm:.3f}'.replace('.',',')
result={'referencias_resolvidas':len(refs),'identificadores_unicos':len(ids),'figuras_existentes':len(images),
        'tabelas_numericas_novas_conferidas':4,'linhas_numericas_conferidas':16,'resultado':'passou'}
(ROOT/'revisoes/verificacao-capitulo-3-reestruturado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(result)
