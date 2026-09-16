"""Confere integridade dos arquivos, HTML e valores da síntese."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import pandas as pd
import numpy as np

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]


class HTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.ids=[]
        self.external_scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='script' and 'src' in a:self.external_scripts.append(a['src'])


h=(OUT/'relatorio.html').read_text(encoding='utf-8')
p=HTML();p.feed(h)
assert not p.external_scripts
assert len(p.ids)==len(set(p.ids))
for link in p.links:
    assert link[1:] in p.ids if link.startswith('#') else (OUT/link).is_file(),link
assert 'curva-competitividade' in p.ids and 'curva-eleicao' in p.ids
assert len(re.findall(r'Plotly\.newPlot\(\s*"curva-(?:competitividade|eleicao)"',h))==2
audit=json.loads((OUT/'auditoria.json').read_text(encoding='utf-8'))
assert all(audit['verificacoes'].values())
for file,sha in audit['fontes_sha256'].items():
    assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==sha,file
s=pd.read_csv(OUT/'resumo_nacional.csv')
c=s[s.limiar.notna()]
assert len(c)==24 and len(s)==32
assert c.lift.gt(1).all()
assert np.isclose(c.lift.min(),1.3753664916688668)
assert not s.duplicated(['ano_eleicao','regra','desfecho']).any()
b=pd.read_csv(OUT/'faixas_incrementais.csv')
for _,g in b[b.ordem.lt(95)].groupby(['ano_eleicao','desfecho']):
    assert (np.diff(g.sort_values('ordem').incidencia)<0).all()
assert b[b.desfecho.eq('eleicao')&b.ordem.eq(70)].lift.lt(1).all()
assert b[b.desfecho.eq('competitividade')&b.ordem.isin([80,90])].lift.lt(1).all()
result={'html':'OK','graficos_interativos':2,'links_validos':len(p.links),
        'verificacoes_analiticas':len(audit['verificacoes']),
        'conferencias':'Integridade das fontes; grade completa; ausência de duplicatas; síntese e faixas marginais reconciliadas.',
        'revisao_visual':'PNGs das duas figuras inspecionados; navegador indisponível para inspeção visual do HTML.'}
(OUT/'verificacao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
