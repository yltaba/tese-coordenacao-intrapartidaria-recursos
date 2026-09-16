"""Exporta as figuras de amplitude e concentração para inclusão na tese."""
from pathlib import Path
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[2]
for slug, width, height in [
	('amplitude-proposta-2', 1200, 540),
	('concentracao-barras', 1200, 540),
]:
	fig = pio.read_json(ROOT / f'tese/resultados-capitulo-3/{slug}.plotly.json')
	target = ROOT / f'figs/cap3_fig_{"amplitude" if slug.startswith("amplitude") else "concentracao"}_barras.png'
	fig.write_image(target, width=width, height=height, scale=3)
	print(target)
