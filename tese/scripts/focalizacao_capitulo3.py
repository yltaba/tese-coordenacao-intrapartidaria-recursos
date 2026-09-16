"""Extensões auditáveis de focalização para a segunda versão do atlas."""
import sys
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def calcular(root, out, listas):
    sys.path.insert(0, str(root / 'src/2_gold'))
    from cap3_cs_features import gerar_features
    from cap3_taa_features import _preparar, acertos_fracionarios

    raw = pd.read_parquet(root / 'data/processed/rrd_df_novo.parquet')
    raw = raw[raw.ano_eleicao.isin([2018, 2022])].copy()
    assert not raw.duplicated(['ano_eleicao', 'sg_uf', 'nr_candidato']).any()
    assert raw.vr_receita_recursos_partidos.fillna(0).ge(0).all()
    raw = _preparar(gerar_features(raw))
    rows = []
    for (ano, uf, partido), g in raw.groupby(['ano_eleicao', 'sg_uf', 'sg_partido_norm']):
        recursos = g.vr_receita_recursos_partidos.to_numpy(float)
        necr = recursos.sum() ** 2 / np.square(recursos).sum() if recursos.sum() > 0 else np.nan
        k = max(1, int(np.floor(necr + .5))) if recursos.sum() > 0 else 0
        rows.append(dict(Ano=ano, UF=uf, Partido=partido, C_check=len(g),
                         F_check=int(g.candidato_competitivo.sum()), K_check=k,
                         H_check=acertos_fracionarios(recursos, g.eleito, k) if k else 0,
                         Competitivos_top=acertos_fracionarios(recursos, g.candidato_competitivo, k) if k else 0))
    d = listas.merge(pd.DataFrame(rows), on=['Ano', 'UF', 'Partido'], validate='one_to_one')
    assert len(d) == len(listas) == 1570
    for a, b in [('C', 'C_check'), ('F', 'F_check'), ('k_arredondado', 'K_check'), ('eleitos_top_arredondado', 'H_check')]:
        assert np.allclose(d[a], d[b]), (a, b)
    d = d.drop(columns=['C_check', 'F_check', 'K_check', 'H_check'])
    k = d.k_arredondado
    d['Fracao_nucleo_pct'] = 100 * d.NECr / d.C
    d['Aleatoria_pct'] = (100 * k / d.C).where(d.E > 0)
    expected = d.E * k / d.C
    d['Lift'] = d.eleitos_top_arredondado / expected.where(expected > 0)
    d['Excedente_pp'] = d.Cobertura_pct - d.Aleatoria_pct
    d['Precisao_aleatoria_pct'] = (100 * d.E / d.C).where(k > 0)
    d['Cobertura_competitiva_pct'] = 100 * d.Competitivos_top / d.F.where(d.F > 0)
    d['Lift_competitivo'] = d.Competitivos_top / (d.F * k / d.C).where(d.F * k > 0)
    mask = (d.E > 0) & (k > 0)
    assert np.allclose(d.loc[mask, 'Lift'], (d.Precisao_pct / d.Precisao_aleatoria_pct)[mask])
    assert d.Competitivos_top.between(0, np.minimum(d.F, k) + 1e-9).all()
    summaries = []
    for year in [2018, 2022]:
        for mag in ['Total'] + list(d.Magnitude.unique()):
            g = d[(d.Ano == year) & ((d.Magnitude == mag) if mag != 'Total' else True)]
            for target, total_col, hits_col in [('Eleitos', 'E', 'eleitos_top_arredondado'), ('Competitivos prévios', 'F', 'Competitivos_top')]:
                total, hits, positions = g[total_col].sum(), g[hits_col].sum(), g.k_arredondado.sum()
                chance = (g[total_col] * g.k_arredondado / g.C).sum()
                summaries.append({'Ano': year, 'Magnitude': mag, 'Alvo': target, 'Total alvo': total,
                                  'No núcleo': hits, 'Esperados ao acaso': chance, 'Posições': positions,
                                  'Cobertura (%)': 100 * hits / total, 'Aleatória (%)': 100 * chance / total,
                                  'Excedente (p.p.)': 100 * (hits - chance) / total, 'Lift': hits / chance,
                                  'Precisão (%)': 100 * hits / positions, 'Precisão aleatória (%)': 100 * chance / positions})
    s = pd.DataFrame(summaries)
    d.to_csv(out / 'v2_focalizacao_nominatas.csv', index=False, encoding='utf-8-sig')
    s.to_csv(out / 'v2_focalizacao_resumo.csv', index=False, encoding='utf-8-sig')
    return d, s


def abertura(d, s, chart, number):
    rows = []
    for ano in [2018, 2022]:
        g = d[(d.Ano == ano) & (d.Recursos > 0)]
        e = s[(s.Ano == ano) & (s.Magnitude == 'Total') & (s.Alvo == 'Eleitos')].iloc[0]
        rows.append({'Ano': ano, 'N médio (financiadas)': number(g.C.mean()), 'NEC-R médio': number(g.NECr.mean()),
                     'NEC-R mediano': number(g.NECr.median()), 'N / NEC-R médio': number(g.Q.mean()),
                     'NEC-R / N médio (%)': number((100*g.NECr/g.C).mean()),
                     'Cobertura (%)': number(e['Cobertura (%)']), 'Lift agregado': number(e.Lift)})
    return '''<section id="argumento"><div class="eyebrow">ARGUMENTO / DUAS PERGUNTAS</div>
<h2>Coordenação intrapartidária não se reduz à máxima concentração</h2>
<p class="lead">Os partidos selecionam núcleos de candidaturas eleitoralmente relevantes. Entre 2018 e 2022, esses núcleos se ampliam, mas permanecem fortemente alinhados à distribuição das cadeiras. A menor concentração relativa não basta para concluir que houve menos coordenação.</p>
<h3>1. Há evidências de coordenação por meio dos recursos?</h3><p>Nas duas eleições, o núcleo efetivo é menor que a nominata e contém uma proporção dos eleitos muito superior à esperada ao acaso. A inclusão de candidaturas com credenciais eleitorais anteriores permite avaliar também a focalização ex ante. São evidências observacionais consistentes com coordenação, sem identificar o processo decisório das lideranças.</p>
<h3>2. A forma dessa coordenação muda?</h3><p>O padrão passa de um núcleo mais estreito em 2018 para um núcleo ampliado em 2022: mais candidaturas, relativamente mais competitivas e mais candidaturas efetivas em recursos. A cobertura dos eleitos continua elevada, inclusive após o ajuste pelo tamanho do núcleo.</p>
<div class="tablewrap"><table><thead><tr><th>Dimensão</th><th>Pergunta</th><th>Indicadores</th></tr></thead><tbody>
<tr><td>Amplitude</td><td>Quantas candidaturas são efetivamente financiadas?</td><td>NEC-R; NEC-R/Mp; NEC-R/E</td></tr>
<tr><td>Concentração relativa</td><td>Quão pequeno é o núcleo diante da nominata?</td><td>N/NEC-R; NEC-R/N</td></tr>
<tr><td>Focalização estratégica</td><td>Quem está no núcleo?</td><td>Competitivos prévios; cobertura; precisão; lift acima do acaso</td></tr>
</tbody></table></div><p class="note">N = C nos gráficos legados: número de candidaturas da lista. NEC-R = NECr = 1/Σs², com s igual à participação nos recursos partidários da lista; não é uma contagem literal de recebedores. O Top-k operacionaliza um núcleo de pessoas, com k = floor(NEC-R + 0,5). Mp é a bancada de referência disponível, não a magnitude distrital; E é o número de eleitos.</p>
''' + '<div class="tablewrap">' + pd.DataFrame(rows).to_html(index=False, border=0) + '''</div>
<p class="note">Amplitude e concentração: médias entre listas com recursos positivos (786 e 648). Cobertura e lift: razões de somas nacionais, com todos os 513 eleitos de cada ano. Razão de médias, média de razões e benchmark ponderado pelos eleitos são medidas distintas. Em 2022, 5,90 é média do NEC-R; a mediana é 4,81.</p></section>'''


def focalizacao(d, s, chart, number, colors):
    national = s[s.Magnitude == 'Total']
    fig = go.Figure()
    for year in [2018, 2022]:
        g = national[national.Ano == year]
        fig.add_trace(go.Bar(x=g.Alvo, y=g.Lift, name=str(year), marker_color=colors[year],
                            text=[number(x)+'×' for x in g.Lift], textposition='outside',
                            hovertemplate='%{x}<br>Lift: %{y:.3f}×<extra>%{fullData.name}</extra>'))
    fig.add_hline(y=1, line_dash='dot', annotation_text='Seleção aleatória de mesmo tamanho')
    fig.update_layout(barmode='group', yaxis_title='Acertos observados / esperados ao acaso', yaxis_rangemode='tozero')
    display = national[['Ano', 'Alvo', 'Total alvo', 'No núcleo', 'Esperados ao acaso', 'Cobertura (%)', 'Aleatória (%)', 'Excedente (p.p.)', 'Lift']].copy()
    for col in display.columns[3:]:
        display[col] = display[col].map(number)
    p = ['<section id="focalizacao"><div class="eyebrow">FOCALIZAÇÃO / AJUSTE PELO TAMANHO</div><h2>Quanto o núcleo identifica acima do acaso?</h2>',
         '<p class="lead">Ampliar o Top-k pode aumentar mecanicamente a cobertura. O benchmark sorteia k pessoas dentro de cada nominata, preservando seu tamanho e o número de eleitos ou competitivos prévios. O lift compara os acertos observados com os esperados nesse sorteio.</p>',
         chart(fig, 'v2_lift'), '<div class="tablewrap">'+display.to_html(index=False, border=0)+'</div>',
         '<h3>O ajuste é calculado lista a lista</h3><p>Para a nominata i: Nᵢ candidatos, Kᵢ posições, Eᵢ eleitos e Hᵢ eleitos no núcleo.</p>',
         '<div class="note">Coberturaᵢ = Hᵢ/Eᵢ &nbsp; · &nbsp; Esperadaᵢ = Kᵢ/Nᵢ<br>Liftᵢ = (Hᵢ/Eᵢ)/(Kᵢ/Nᵢ) = (Hᵢ/Kᵢ)/(Eᵢ/Nᵢ)<br>Excedenteᵢ = 100 × [Hᵢ/Eᵢ − Kᵢ/Nᵢ] pontos percentuais.</div>',
         '<p>A identidade entre os lifts de cobertura e precisão vale quando Eᵢ e Kᵢ são positivos. Com Eᵢ = 0, cobertura e lift são indefinidos; com Kᵢ = 0, precisão e lift são indefinidos. Listas sem recursos têm Kᵢ = 0 e acertos nulos, mas seus eleitos permanecem no denominador nacional.</p>',
         '<p>No agregado, a cobertura aleatória é Σ(EᵢKᵢ/Nᵢ)/ΣEᵢ e o lift é ΣHᵢ/Σ(EᵢKᵢ/Nᵢ). Não é a média simples dos lifts. A precisão aleatória agregada é Σ(EᵢKᵢ/Nᵢ)/ΣKᵢ, preservando a mesma identidade. Para competitivos, substitui-se Eᵢ por Fᵢ e Hᵢ pelos competitivos no núcleo.</p>',
         '<p><strong>O benchmark nacional dos eleitos permanece em aproximadamente 43,8% nos dois pleitos.</strong> A comparação aproximada 2,96/9 versus 5,90/14 não recupera esse benchmark: usa médias de outro universo, ignora o arredondamento e não pondera as listas pelos eleitos. O ganho observado de cobertura não desaparece ao ajustar o tamanho do núcleo.</p>',
         '<h3>Credenciais anteriores → núcleo financiado → eleição</h3>']
    fig = go.Figure()
    comp = national[national.Alvo == 'Competitivos prévios']
    for year in [2018, 2022]:
        r = comp[comp.Ano == year].iloc[0]
        fig.add_trace(go.Bar(x=['Observada', 'Esperada ao acaso'], y=[r['Cobertura (%)'], r['Aleatória (%)']],
                            name=str(year), marker_color=colors[year], text=[number(r[c])+'%' for c in ['Cobertura (%)', 'Aleatória (%)']], textposition='outside'))
    fig.update_layout(barmode='group', yaxis_title='Competitivos prévios incorporados ao núcleo (%)', yaxis_range=[0, 105])
    p.append(chart(fig, 'v2_competitivos_nucleo'))
    p.append('<p><strong>A focalização ex ante também aparece nas duas eleições:</strong> o núcleo incorpora 80,90% dos competitivos prévios em 2018 e 82,68% em 2022, contra 43,19% e 43,75% esperados ao acaso. Os lifts são 1,87 e 1,89. A ampliação do núcleo preserva uma incorporação de candidaturas com credenciais anteriores muito superior à seleção aleatória.</p>')
    p.append('<p>Competitividade prévia segue a definição canônica da base: vitória anterior em cargo diferente de vereador ou alcance histórico de pelo menos 10% do quociente eleitoral. A medida usa as variáveis históricas consolidadas; não incorpora o desempenho na eleição corrente. O cálculo reproduz os totais de candidatos, competitivos, K e eleitos no Top-k de todas as 1.570 nominatas. Empates de recursos no corte recebem crédito fracionário, também para competitividade.</p>')
    p.append('<p class="note">As setas organizam a hipótese substantiva; os dois testes medem associações, não uma mediação causal. Os recursos podem contribuir para a eleição, e a correspondência observada também pode refletir capacidade individual de captar recursos. Competitividade histórica não revela diretamente a intenção partidária e depende da cobertura do histórico disponível.</p>')
    p.append('<p><a href="v2_focalizacao_nominatas.csv">Baixar indicadores por nominata</a> · <a href="v2_focalizacao_resumo.csv">Baixar resultados nacionais e por magnitude</a></p></section>')
    return ''.join(p)


def contexto():
    return '''<section id="instituicoes"><div class="eyebrow">INTERPRETAÇÃO / MUDANÇA INSTITUCIONAL</div><h2>Coordenação mais ampla em um ambiente diferente</h2>
<p class="lead">Financiar um conjunto maior de candidaturas eleitoralmente produtivas é uma adaptação plausível às condições de 2022. Os resultados são consistentes com essa interpretação; a comparação entre dois pleitos não identifica os efeitos de cada mudança.</p>
<div class="tablewrap"><table><thead><tr><th>Instituição</th><th>2018</th><th>2022</th></tr></thead><tbody>
<tr><td>Coligações proporcionais</td><td>Permitidas</td><td>Primeira eleição geral sem coligações proporcionais</td></tr>
<tr><td>Cláusula de desempenho após o pleito</td><td>1,5% dos votos válidos nacionais para deputado federal, com ao menos 1% em 9 UFs; ou 9 deputados em 9 UFs</td><td>2% dos votos válidos nacionais para deputado federal, com ao menos 1% em 9 UFs; ou 11 deputados em 9 UFs</td></tr>
<tr><td>FEFC nacional, nominal</td><td>R$ 1.716.209.431</td><td>R$ 4.961.519.777</td></tr>
<tr><td>Federações</td><td>Não existiam</td><td>Atuam como uma única agremiação na disputa</td></tr>
<tr><td>Teto de candidaturas proporcionais</td><td>150% das vagas; 200% nos estados com até 12 vagas na Câmara</td><td>100% das vagas + 1 por partido ou federação</td></tr>
</tbody></table></div>
<p>Sem coligações proporcionais, a votação própria do partido ou da federação ganha centralidade na conversão de votos em cadeiras. O endurecimento da cláusula afeta o acesso ao Fundo Partidário e à propaganda gratuita, enquanto o aumento nominal do FEFC amplia a disponibilidade de financiamento. Esses fatores podem favorecer núcleos mais amplos; não demonstram que cada candidatura adicional resultou dessas regras.</p>
<p class="note">O FEFC acima é o orçamento nacional para todas as disputas, não o total de recursos partidários observado na amostra de candidaturas a deputado federal. A cláusula de desempenho não equivale à extinção jurídica do partido.</p>
<h3>Comparabilidade e robustez</h3><p>A unidade empírica deste atlas continua sendo partido × UF × ano. Em 2022, partidos de uma mesma federação aparecem separadamente. Reagrupar federações e, como comparação histórica, considerar coligações de 2018 exigiria recalcular NEC-R e o ranking a partir das candidaturas; somar os NEC-R partidários não é válido. Essa robustez institucional permanece pendente. Os tetos legais também se referem a unidades de registro diferentes, de modo que não se deve tratar cada lista partidária de 2018 como uma coligação inteira.</p>
<p>O aumento da amplitude, a menor concentração relativa e a focalização persistente descrevem uma mudança na forma da coordenação. Não autorizam uma classificação geral de partidos “melhores” ou “piores”, nem demonstram que a expansão institucional causou o aumento da cobertura.</p>
<p>Fontes institucionais: <a href="https://www.tse.jus.br/comunicacao/noticias/2021/Dezembro/tse-aprova-resolucao-sobre-escolha-e-registro-de-candidatos">TSE: fim das coligações em eleições gerais e federações</a>; <a href="https://www.tse.jus.br/comunicacao/noticias/2018/Dezembro/clausula-de-barreira-resultado-das-eleicoes-deste-ano-sera-considerado-para-a-proxima-legislatura">cláusula após 2018</a>; <a href="https://www.tse.jus.br/comunicacao/noticias/2023/Setembro/glossario-eleitoral-explica-o-que-e-clausula-de-barreira">cláusula após 2022</a>; <a href="https://www.tse.jus.br/eleicoes/eleicoes-2018/prestacao-de-contas-1/fundo-especial-de-financiamento-de-campanha-fefc">FEFC 2018</a>; <a href="https://www.tse.jus.br/eleicoes/eleicoes-2022/prestacao-de-contas/fundo-especial-de-financiamento-de-campanha-fefc">FEFC 2022</a>; <a href="https://www.tse.jus.br/comunicacao/noticias/2018/Janeiro/resolucao-define-regras-para-escolha-e-registro-dos-candidatos-das-eleicoes-gerais-2018">limites em 2018</a>; <a href="https://www.tse.jus.br/comunicacao/noticias/2022/Janeiro/eleicoes-2022-resolucao-reafirma-cotas-de-genero-para-registro-de-candidaturas">limites em 2022</a>.</p></section>'''
