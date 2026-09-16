"""Exporta o gráfico nacional de cobertura/precisão diretamente do HTML do atlas."""
import json
import re
from pathlib import Path
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'tese/resultados-capitulo-3/atlas-visual-capitulo-3-v2.html'
html = source.read_text(encoding='utf-8')
match = re.search(r'Plotly\.newPlot\(\s*"cobertura"\s*,\s*', html)
assert match, 'Gráfico cobertura não encontrado no atlas'
decoder = json.JSONDecoder()
data, end = decoder.raw_decode(html, match.end())
start = end
while html[start] in ' ,\r\n\t':
    start += 1
layout, _ = decoder.raw_decode(html, start)
assert len(data) == 4
fig = go.Figure(data=data, layout=layout)
fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
target = ROOT / 'figs/cap3_fig_top_necr_cobertura_precisao.png'
fig.write_image(target, width=1200, height=450, scale=3)
print(target)
