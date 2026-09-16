"""Alternativas Plotly para a tabela de amplitude das nominatas financiadas."""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import get_plotlyjs

OUT = Path(__file__).resolve().parents[1] / 'resultados-capitulo-3'
COLORS = {2018: '#222222', 2022: '#a6a6a6'}
METRICS = [('C', 'Candidaturas totais'), ('F', 'Candidaturas competitivas'), ('NECr', 'NECr')]
YEARS = [2018, 2022]
STATS = [('mean', 'Média'), ('median', 'Mediana')]


def fmt(x):
    return f'{x:.2f}'.replace('.', ',')


def main():
    base = pd.read_csv(OUT / '25_todas_nominatas.csv')
    funded = base[base.Recursos > 0]
    values = funded.groupby('Ano')[[m for m, _ in METRICS]].agg(['mean', 'median'])
    expected = {2018: [9.41, 4, 1.11, 1, 2.96, 1.88], 2022: [14.42, 9, 1.98, 1, 5.90, 4.81]}
    for year in YEARS:
        actual = [round(values.loc[year, (m, s)], 2) for m, _ in METRICS for s, _ in STATS]
        assert actual == expected[year], (year, actual)
    assert funded.groupby('Ano').size().to_dict() == {2018: 786, 2022: 648}
    sections = []

    def add(fig, slug, title, explanation, note, height=540):
        fig.update_layout(template='plotly_white', height=height,
                          font=dict(family='Arial, sans-serif', size=13, color='#263d47'),
                          margin=dict(l=185, r=85, t=100, b=65), separators=',.',
                          legend=dict(orientation='h', x=0, y=1.16),
                          paper_bgcolor='white', plot_bgcolor='white')
        fig.update_xaxes(automargin=True, zeroline=False)
        fig.update_yaxes(automargin=True, zeroline=False)
        config = dict(responsive=True, displaylogo=False, scrollZoom=False,
                      toImageButtonOptions=dict(format='svg', filename=slug, width=1200, height=height, scale=1))
        fragment = fig.to_html(full_html=False, include_plotlyjs=False, div_id=f'{slug}-plot', config=config)
        sections.append(f'<section id="{slug}"><h2>{title}</h2><p>{explanation}</p><div class="scroll"><div class="plot">{fragment}</div></div><p class="note">{note}</p></section>')
        fig.write_json(OUT / f'{slug}.plotly.json')

    # Alternativa 1: pares de pontos com a mesma escala entre estatísticas.
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Média', 'Mediana'], horizontal_spacing=.20)
    labels = [label for _, label in METRICS]
    for col, (stat, _) in enumerate(STATS, 1):
        for m, label in METRICS:
            fig.add_trace(go.Scatter(x=[values.loc[y, (m, stat)] for y in YEARS], y=[label, label],
                                    mode='lines', line=dict(color='#bac5cc', width=3),
                                    showlegend=False, hoverinfo='skip'), row=1, col=col)
        for year in YEARS:
            xs = [values.loc[year, (m, stat)] for m, _ in METRICS]
            fig.add_trace(go.Scatter(x=xs, y=labels, mode='markers+text', name=str(year),
                                    legendgroup=str(year), showlegend=col == 1,
                                    marker=dict(size=12, color=COLORS[year], symbol='circle' if year == 2018 else 'diamond'),
                                    text=[fmt(x) for x in xs], textposition='top left' if year == 2018 else 'bottom right',
                                    cliponaxis=False, hovertemplate='%{y}<br>%{text}<extra>%{fullData.name}</extra>'), row=1, col=col)
    fig.update_xaxes(range=[0, 16.5], title_text='Candidaturas por nominata')
    fig.update_yaxes(categoryorder='array', categoryarray=labels[::-1])
    add(fig, 'amplitude-proposta-1', '1. Pontos conectados — recomendação para a tese',
        'Dois painéis separam média e mediana. Os pontos mostram cada eleição; o segmento facilita a leitura da mudança. A mesma escala permite comparar a amplitude formal, a competitividade e o NECr.',
        'Em competitivas, a mediana permanece em 1,00: os pontos coincidem. Os rótulos de 2018 ficam acima e os de 2022 abaixo. O segmento apenas liga estatísticas de dois anos, sem indicar trajetória intermediária.')

    # Alternativa 2: barras agrupadas, sem empilhar grandezas sobrepostas.
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Média', 'Mediana'], horizontal_spacing=.20)
    for col, (stat, _) in enumerate(STATS, 1):
        for year in YEARS:
            xs = [values.loc[year, (m, stat)] for m, _ in METRICS]
            fig.add_trace(go.Bar(x=xs, y=labels, orientation='h', name=str(year),
                                legendgroup=str(year), offsetgroup=str(year), showlegend=col == 1,
                                marker_color=COLORS[year], text=[fmt(x) for x in xs], textposition='outside',
                                cliponaxis=False, hovertemplate='%{y}<br>%{text}<extra>%{fullData.name}</extra>'), row=1, col=col)
    fig.update_layout(barmode='group', bargap=.30)
    fig.update_xaxes(range=[0, 17], title_text='Candidaturas por nominata')
    fig.update_yaxes(categoryorder='array', categoryarray=labels[::-1])
    add(fig, 'amplitude-proposta-2', '2. Barras agrupadas — comparação de níveis',
        'Uma alternativa familiar para mostrar a diferença de nível entre eleições. A origem em zero e a escala comum preservam a comparação dos tamanhos.',
        'As barras ficam lado a lado: competitivas fazem parte do total, e NECr é uma medida efetiva. Essas grandezas não devem ser somadas ou empilhadas.')

    concentration = funded.groupby('Ano').agg(
        Q_mean=('Q', 'mean'), Q_median=('Q', 'median'),
        R_mean=('NECr', lambda x: (x / funded.loc[x.index, 'C']).mean() * 100),
        R_median=('NECr', lambda x: (x / funded.loc[x.index, 'C']).median() * 100),
    )
    concentration_fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['C/NECr', 'NECr/C (%)'],
        horizontal_spacing=.24,
    )
    for col, metric, suffix, upper in [(1, 'Q', '', 5), (2, 'R', '%', 100)]:
        for year in YEARS:
            concentration_values = [concentration.loc[year, f'{metric}_{stat}'] for stat in ['mean', 'median']]
            concentration_fig.add_trace(go.Bar(
                x=concentration_values, y=['Média', 'Mediana'], orientation='h', name=str(year),
                legendgroup=str(year), offsetgroup=str(year), showlegend=col == 1,
                marker_color=COLORS[year], text=[fmt(v) + suffix for v in concentration_values],
                textposition='outside', cliponaxis=False,
                hovertemplate='%{y}<br>%{text}<extra>%{fullData.name}</extra>',
            ), row=1, col=col)
        concentration_fig.update_xaxes(range=[0, upper], row=1, col=col)
    concentration_fig.update_layout(barmode='group', bargap=.30)
    concentration_fig.update_yaxes(categoryorder='array', categoryarray=['Mediana', 'Média'])
    add(concentration_fig, 'concentracao-barras', 'Concentração relativa nas nominatas financiadas',
        'C/NECr e NECr/C mostram a relação entre a amplitude formal e o número efetivo de candidaturas financiadas. As duas medidas usam escalas próprias.',
        'Preto: 2018; cinza: 2022. Médias e medianas são calculadas por nominata. C/NECr é o número formal de candidaturas por candidatura efetiva; NECr/C é a proporção efetiva da nominata.')

    # Alternativa 3: cada indicador tem seu próprio painel, com escala comum.
    fig = make_subplots(rows=1, cols=3, subplot_titles=labels, horizontal_spacing=.10)
    for col, (metric, _) in enumerate(METRICS, 1):
        for stat, label in STATS:
            ys = [values.loc[year, (metric, stat)] for year in YEARS]
            fig.add_trace(go.Scatter(x=YEARS, y=ys, name=label, legendgroup=stat, showlegend=col == 1,
                                    mode='lines+markers+text', line=dict(color='#788993', dash='solid' if stat == 'mean' else 'dot'),
                                    marker=dict(color=[COLORS[y] for y in YEARS], size=11,
                                                symbol='circle' if stat == 'mean' else 'diamond'),
                                    text=[fmt(v) for v in ys], textposition='top center' if stat == 'mean' else 'bottom center',
                                    cliponaxis=False, hovertemplate='%{x}<br>%{text}<extra>%{fullData.name}</extra>'), row=1, col=col)
    fig.update_xaxes(tickvals=YEARS, range=[2017.2, 2022.8], title_text='Eleição')
    fig.update_yaxes(range=[0, 16.5])
    fig.update_yaxes(title_text='Candidaturas por nominata', row=1, col=1)
    add(fig, 'amplitude-proposta-3', '3. Inclinações por indicador — mudança entre eleições',
        'Três painéis mostram a evolução da média e da mediana de cada indicador. Círculos e linha contínua representam a média; losangos e linha pontilhada, a mediana.',
        'Azul: 2018; laranja: 2022. Todos os painéis usam a mesma escala. Há somente duas eleições observadas: as linhas não estimam valores entre elas. A escala comum torna as mudanças nas competitivas visualmente menores.', 570)

    html = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Propostas de gráficos · Amplitude das nominatas</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f3f5f7;color:#263d47;font:16px/1.65 Arial,sans-serif}main{max-width:1320px;margin:auto;padding:40px 24px}h1{font-size:36px;line-height:1.2}h2{font-size:24px}header{max-width:1050px;margin-bottom:30px}section{background:white;border:1px solid #dce3e7;border-radius:12px;padding:26px;margin:26px 0}a{color:#257a9b}nav{display:flex;gap:20px;flex-wrap:wrap}.note,footer{font-size:14px;color:#526672}.badge{font-size:12px;letter-spacing:.12em;font-weight:bold}.scroll{overflow-x:auto}.plot{min-width:950px}.caption{border-left:3px solid #257a9b;padding-left:18px}@media(max-width:650px){main{padding:22px 12px}section{padding:16px}h1{font-size:28px}}@media print{section{break-before:page;border:0}.plot{min-width:0}nav{display:none}}</style><script>''' + get_plotlyjs() + '''</script></head><body><main><header><div class="badge">CAPÍTULO 3 · ALTERNATIVAS VISUAIS</div><h1>Amplitude formal e efetiva nas nominatas financiadas</h1><p>Três propostas para substituir a tabela, preservando os seis indicadores e seus valores. Universo: 786 nominatas com recursos partidários positivos em 2018 e 648 em 2022. Cada nominata recebe o mesmo peso; listas sem candidatos competitivos permanecem no cálculo.</p><p><strong>Sugestão:</strong> a proposta 1 reúne os resultados com menos elementos visuais e facilita a comparação entre anos. A proposta 2 enfatiza os níveis; a proposta 3 enfatiza as mudanças de média e mediana.</p><nav><a href="#amplitude-proposta-1">1 · Pontos conectados</a><a href="#amplitude-proposta-2">2 · Barras agrupadas</a><a href="#amplitude-proposta-3">3 · Inclinações</a></nav><p class="note">Passe o cursor para consultar valores. O botão de câmera em cada gráfico exporta SVG. Em telas pequenas, deslize o gráfico horizontalmente.</p></header>''' + ''.join(sections) + '''<section><h2>Legenda sugerida para a figura escolhida</h2><p class="caption">Amplitude formal e efetiva nas nominatas financiadas, 2018 e 2022. Médias e medianas de candidaturas totais, candidaturas competitivas e número efetivo de candidaturas financiadas (NECr). Cada nominata recebe o mesmo peso nas estatísticas. Fonte: elaboração própria com base nos dados consolidados do TSE.</p><p class="note">As candidaturas totais e competitivas são contagens; NECr expressa o número equivalente de candidaturas com parcelas iguais de recursos. Os gráficos apresentam estatísticas descritivas, sem intervalos de confiança.</p></section><footer>Fonte de cálculo: <a href="25_todas_nominatas.csv">25_todas_nominatas.csv</a>, filtro Recursos &gt; 0. Valores recalculados sem arredondamento prévio e conferidos com a tabela fornecida. Gerador: tese/scripts/propostas_graficos_amplitude.py. HTML autossuficiente, com Plotly incorporado.</footer></main></body></html>'''
    target = OUT / 'propostas-graficos-amplitude.html'
    target.write_text(html, encoding='utf-8')
    print(f'Criado: {target}; 3 propostas; 12 valores conferidos com a tabela.')


if __name__ == '__main__':
    main()
