"""Validação final dos arquivos e dos números exibidos nas figuras novas."""
from pathlib import Path
from html.parser import HTMLParser
import re
import json
import zipfile
import hashlib
import numpy as np
import pandas as pd

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]


class Parser(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.external=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='a':self.links.append(attrs.get('href',''))
        if tag=='script' and 'src' in attrs:self.external.append(attrs['src'])


text=(OUT/'relatorio.html').read_text(encoding='utf-8')
p=Parser();p.feed(text)
assert not p.external
assert len(p.ids)==len(set(p.ids))
for link in p.links:
    assert link[1:] in p.ids if link.startswith('#') else (OUT/link).is_file(),link
charts=re.findall(r'Plotly\.newPlot\(\s*"([^"]+)"',text)
assert len(charts)==5 and len(set(charts))==5
audit=json.loads((OUT/'auditoria.json').read_text(encoding='utf-8'))
assert all(audit['checks'].values())
for file,sha in audit['fontes_sha256'].items():
    assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==sha,file
data=pd.read_csv(OUT/'resumo_nacional.csv')
points=0
for filename in ['03-top-necr-dados.csv']:
    for _,r in pd.read_csv(OUT/filename).iterrows():
        rule='top_necr' if r.serie=='acaso' else r.serie
        ref=data[(data.ano_eleicao==r.ano_eleicao)&(data.desfecho==r.desfecho)&(data.regra==rule)].iloc[0]
        target=(1 if r.indicador=='lift' else ref[r.indicador+'_acaso']) if r.serie=='acaso' else ref[r.indicador]
        if r.indicador!='lift':target*=100
        assert np.isclose(target,r.valor_exibido)
        points+=1
with zipfile.ZipFile(OUT/'pacote-figuras.zip') as z:
    assert len(z.namelist())==12
    assert z.testzip() is None
    for filename in z.namelist():
        assert z.read(filename)==(OUT/filename).read_bytes()
qmd=(OUT/'figuras-para-tese.qmd').read_text(encoding='utf-8')
assert qmd.count('![Figura ')==0
assert qmd.count('{#fig-cap3-')==5
result={'status':'OK','figuras_interativas':len(charts),'arquivos_no_pacote':12,'pontos_reconciliados':points,'links_validos':len(p.links),'checks_consolidacao':len(audit['checks']),'revisao_visual':'PNGs inspecionados após a remoção dos títulos gerais e dos textos inferiores; HTML verificado estruturalmente, sem navegador disponível.'}
(OUT/'verificacao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
