"""Verifica identidades contábeis e integridade do relatório exploratório."""
from pathlib import Path
from html.parser import HTMLParser
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'tese/resultados-exploracao-nucleo'
d = pd.read_csv(OUT/'base_analitica.csv')
groups = pd.read_csv(OUT/'grupos.csv')
for year,g in d.groupby('ano_eleicao'):
    x=groups[groups.Ano.eq(year)].set_index('Grupo')['N ponderado']
    assert np.isclose(x['Núcleo eleito']+x['Fora eleito'],513)
    assert np.isclose(x['Núcleo não eleito']+x['Fora não eleito'],len(g)-513)
    assert np.isclose(x['Núcleo']+x['Fora'],len(g))
    assert np.allclose(g.top+g.fora,1)
    assert g.top.between(0,1).all()
    for source in ['proprios','pessoas_fisicas','privado_proprio']:
        e=g[g.eleito.eq(1)]
        high=e[source]>e[source].median()
        t=pd.read_csv(OUT/'testes_financiamento.csv').query('Ano == @year and Fonte == @source').iloc[0]
        assert np.isclose(t['Fora alto %'],100*np.average(high,weights=e.fora))
        assert np.isclose(t['Dentro alto %'],100*np.average(high,weights=e.top))
profile=pd.read_csv(OUT/'composicao.csv')
assert profile.Percentual.between(0,100).all()
for _,r in profile.iterrows():
    n=groups[(groups.Ano==r.Ano)&groups.Grupo.eq(r.Grupo)]['N ponderado'].iloc[0]
    assert np.isclose(r['N válido ponderado']+r['Ausente ponderado'],n)
audit=json.loads((OUT/'auditoria.json').read_text(encoding='utf-8'))
assert all(audit['verificacoes'].values())
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.links=[]
        self.scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='script' and 'src' in a:self.scripts.append(a['src'])
p=Parser()
h=(ROOT/'tese/old/relatorios-descritivos/relatorio-exploracao-nucleo-inferencial.html').read_text(encoding='utf-8')
p.feed(h)
assert len(p.ids)==len(set(p.ids))
assert not p.scripts, 'Dependência JavaScript externa'
for link in p.links:
    if link.startswith('#'): assert link[1:] in p.ids
    else: assert (ROOT/'tese'/link).exists(),link
assert all(f'fig-{i}' in p.ids for i in range(1,4))
assert 'modelos_inclusao.csv' in h
print('OK: quadrantes, pesos, percentuais, financiamento, auditoria, gráficos e links locais.')
