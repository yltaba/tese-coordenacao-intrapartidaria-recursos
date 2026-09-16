"""Verificação estrutural do artefato, sem navegador disponível."""
from html.parser import HTMLParser
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent


class ReportParser(HTMLParser):
    links = []
    tables = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.tables += 1
        if tag == 'a':
            self.links.append(dict(attrs)['href'])


p = ReportParser()
content = (root/'relatorio.html').read_text(encoding='utf-8')
p.feed(content)
assert p.tables == 5
assert all((root/link).is_file() for link in p.links)
assert 'Plotly.newPlot' in content
assert len(pd.read_csv(root/'candidaturas.csv')) == 17305
assert len(pd.read_csv(root/'listas.csv')) == 1570
assert len(pd.read_csv(root/'resumo_nacional.csv')) == 12
print(f'HTML: {p.tables} tabelas, gráfico incorporado e {len(p.links)} links válidos.')
print(pd.read_csv(root/'concordancia.csv')[['ano_eleicao','par','jaccard_agregado']].to_string(index=False))
