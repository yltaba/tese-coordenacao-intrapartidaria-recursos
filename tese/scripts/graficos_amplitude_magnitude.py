"""Barras agrupadas de amplitude por magnitude, com médias e medianas."""
from pathlib import Path
import math
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import get_plotlyjs

OUT = Path(__file__).resolve().parents[1] / 'resultados-capitulo-3'
MAG = ['Pequeno (8–12)', 'Médio (16–31)', 'Grande (39–70)']
METRICS = [('C', 'Candidaturas totais'), ('F', 'Candidaturas competitivas'), ('NECr', 'NECr')]
COLORS = {2018: '#257a9b', 2022: '#cc632e'}
STEM = 'amplitude-barras-por-magnitude'


def fmt(x):
    return f'{x:.2f}'.replace('.', ',')


def main():
    base = pd.read_csv(OUT / '25_todas_nominatas.csv')
    d = base.loc[base.Recursos > 0].copy()
    assert d.Magnitude.isin(MAG).all()
    assert not d.duplicated(['Ano', 'UF', 'Partido']).any()
    assert d.groupby('Ano').size().to_dict() == {2018: 786, 2022: 648}
    records = []
    for mag in MAG:
        for year in [2018, 2022]:
            group = d[(d.Magnitude == mag) & (d.Ano == year)]
            for metric, label in METRICS:
                assert group[metric].notna().all()
                records.append(dict(Magnitude=mag, Ano=year, Indicador=label, Variavel=metric,
                                    N=len(group), Media=group[metric].mean(), Mediana=group[metric].median()))
    summary = pd.DataFrame(records)
    summary.to_csv(OUT / f'{STEM}.csv', index=False, encoding='utf-8-sig')
    # As médias dos grupos, ponderadas por N, devem recuperar a média nacional.
    for year in [2018, 2022]:
        for metric, _ in METRICS:
            sub = summary[(summary.Ano == year) & (summary.Variavel == metric)]
            assert math.isclose((sub.Media * sub.N).sum() / sub.N.sum(), d.loc[d.Ano == year, metric].mean())
    upper = math.ceil(summary[['Media', 'Mediana']].max().max() * 1.16 / 5) * 5
    fig = make_subplots(rows=3, cols=2, horizontal_spacing=.22, vertical_spacing=.12,
                        subplot_titles=[f'{mag} · {stat}' for mag in MAG for stat in ['Média', 'Mediana']])
    for row, mag in enumerate(MAG, 1):
        for col, stat in enumerate(['Media', 'Mediana'], 1):
            for year in [2018, 2022]:
                sub = summary[(summary.Magnitude == mag) & (summary.Ano == year)].set_index('Variavel').loc[[m for m, _ in METRICS]]
                vals = sub[stat].tolist()
                fig.add_trace(go.Bar(x=vals, y=[label for _, label in METRICS], orientation='h',
                                    name=str(year), legendgroup=str(year), offsetgroup=str(year),
                                    showlegend=row == 1 and col == 1, marker_color=COLORS[year],
                                    text=[fmt(v) for v in vals], textposition='outside', cliponaxis=False,
                                    customdata=sub[['N']].to_numpy(),
                                    hovertemplate='%{y}<br>Valor: %{text}<br>Nominatas: %{customdata[0]}<extra>%{fullData.name}</extra>'), row=row, col=col)
    fig.update_layout(template='plotly_white', height=1100, barmode='group', bargap=.30,
                      margin=dict(l=185, r=65, t=100, b=65), separators=',.',
                      font=dict(family='Arial, sans-serif', size=13, color='#263d47'),
                      legend=dict(orientation='h', y=1.07, x=0))
    fig.update_xaxes(range=[0, upper], dtick=5, automargin=True, title_text='Candidaturas por nominata')
    fig.update_yaxes(categoryorder='array', categoryarray=[label for _, label in METRICS][::-1], automargin=True)
    fragment = fig.to_html(full_html=False, include_plotlyjs=False, div_id='magnitude-plot',
                           config=dict(responsive=True, displaylogo=False, scrollZoom=False,
                                       toImageButtonOptions=dict(format='svg', filename=STEM, width=1350, height=1100)))
    fig.write_json(OUT / f'{STEM}.plotly.json')
    counts = ''.join(f'<li><strong>{mag} cadeiras:</strong> '+ ' · '.join(f'{year}: {len(d[(d.Magnitude == mag) & (d.Ano == year)])} nominatas' for year in [2018, 2022])+'</li>' for mag in MAG)
    page = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Amplitude por magnitude · Barras agrupadas</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f3f5f7;color:#263d47;font:16px/1.65 Arial,sans-serif}main{max-width:1400px;margin:auto;padding:36px 24px}h1{font-size:34px;line-height:1.2}h2{font-size:22px}section{background:white;padding:24px;border-radius:12px;margin:24px 0;border:1px solid #dce3e7}.scroll{overflow-x:auto}.plot{min-width:1100px}.note{font-size:14px;color:#526672}a{color:#257a9b}.caption{border-left:3px solid #257a9b;padding-left:18px}@media(max-width:650px){main{padding:20px 12px}section{padding:12px}h1{font-size:27px}}</style><script>''' + get_plotlyjs() + '''</script></head><body><main><h1>Amplitude formal e efetiva por magnitude do distrito</h1><p>Barras agrupadas para comparar 2018 e 2022. As linhas separam os distritos pequenos, médios e grandes; as colunas separam média e mediana. Os seis painéis usam a mesma escala, com origem em zero.</p><p>Universo: nominatas com recursos partidários positivos. Cada nominata recebe o mesmo peso dentro de sua categoria; nominatas sem candidaturas competitivas permanecem no cálculo. Todos os partidos são considerados.</p><section><div class="scroll"><div class="plot">''' + fragment + '''</div></div><p class="note">Azul: 2018; laranja: 2022. Passe o cursor para consultar os valores e o número de nominatas. O botão de câmera exporta a figura completa em SVG. Em telas pequenas, deslize horizontalmente.</p></section><section><h2>Como ler a comparação</h2><p>Leia cada linha para comparar média e mediana dentro da mesma magnitude; leia cada coluna para comparar magnitudes. A escala comum preserva as diferenças de tamanho entre categorias. As barras de competitivas podem ser curtas: os rótulos permitem consultar os valores exatos, inclusive quando a mediana é zero.</p><p>NECr mede o número equivalente de candidaturas com parcelas iguais de recursos. Candidaturas competitivas integram o total; as três medidas não são componentes que possam ser empilhados ou somados.</p><h2>Nominatas em cada grupo</h2><ul>''' + counts + f'''</ul><p class="note"><a href="{STEM}.csv" download>Baixar médias, medianas e tamanhos dos grupos em CSV</a>. As estatísticas foram calculadas diretamente a partir das nominatas; as medianas não são médias de medianas de subgrupos.</p></section><section><h2>Legenda sugerida para a tese</h2><p class="caption">Amplitude formal e efetiva nas nominatas financiadas, por magnitude do distrito e eleição. Médias e medianas de candidaturas totais, candidaturas competitivas e NECr em 2018 e 2022. Distritos pequenos: 8–12 cadeiras; médios: 16–31; grandes: 39–70. Cada nominata recebe o mesmo peso nas estatísticas de sua categoria. Fonte: elaboração própria com base nos dados consolidados do TSE.</p></section><p class="note">Fonte de cálculo: <a href="25_todas_nominatas.csv">25_todas_nominatas.csv</a>, filtro Recursos &gt; 0. HTML autossuficiente. Gerador: tese/scripts/graficos_amplitude_magnitude.py.</p></main></body></html>'''
    (OUT / f'{STEM}.html').write_text(page, encoding='utf-8')
    print(summary.to_string(index=False))
    print(f'Criado: {OUT / (STEM + ".html")}')


if __name__ == '__main__':
    main()
