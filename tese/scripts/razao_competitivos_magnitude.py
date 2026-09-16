"""Gera razão de somas C/F por eleição e magnitude a partir do relatório do cap. 3."""
import csv
import hashlib
from collections import defaultdict
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'resultados-capitulo-3'
SOURCE = OUT / '25_todas_nominatas.csv'
STEM = 'razao-competitivos-candidatos-magnitude'
MAG = ['Pequeno (8–12)', 'Médio (16–31)', 'Grande (39–70)']


def read(name):
    with (OUT / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def number(value, digits=0):
    return f'{value:,.{digits}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def main():
    base = read(SOURCE.name)
    groups = defaultdict(lambda: [0, 0, 0])
    keys = set()
    for row in base:
        key = (row['Ano'], row['UF'], row['Partido'])
        assert key not in keys, f'Nominata duplicada: {key}'
        keys.add(key)
        c, f = int(row['C']), int(row['F'])
        assert 0 <= f <= c and c > 0
        assert row['Magnitude'] in MAG
        for magnitude in [row['Magnitude'], 'Total']:
            g = groups[(int(row['Ano']), magnitude)]
            g[0] += f
            g[1] += c
            g[2] += 1
    years = sorted({key[0] for key in groups})
    # Confronta tanto os totais nacionais quanto o cruzamento já publicado.
    for row in read('01_universos.csv'):
        f, c, n = groups[(int(row['Ano']), 'Total')]
        assert (f, c, n) == (int(row['Competitivas']), int(row['Candidaturas']), int(row['Nominatas']))
    reference = defaultdict(lambda: [0, 0, 0])
    for row in read('03_competitivos_magnitude_tipo.csv'):
        g = reference[(int(row['Ano']), row['Magnitude'])]
        for i, col in enumerate(['Competitivos', 'Candidatos', 'Listas']):
            g[i] += int(row[col])
    assert all(groups[k] == v for k, v in reference.items())
    records = []
    for year in years:
        for mag in MAG + ['Total']:
            f, c, n = groups[(year, mag)]
            assert f > 0, "Razão C/F exige competitivos no grupo"
            records.append(dict(Ano=year, Magnitude=mag, Competitivos=f, Candidatos=c,
                                Nominatas=n, Candidatos_por_competitivo=c/f))
    with (OUT / f'{STEM}.csv').open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    cards = ''.join(f'<article><span>Eleição {r["Ano"]} · total</span><strong>1 para {number(r["Candidatos_por_competitivo"], 2)}</strong><p>{number(r["Competitivos"])} competitivos em {number(r["Candidatos"])} candidatos totais</p></article>' for r in records if r['Magnitude'] == 'Total')
    scale = 15
    assert max(r['Candidatos_por_competitivo'] for r in records) <= scale
    chart = ''
    for mag in MAG:
        chart += f'<div class="group"><h3>{escape(mag)}</h3>'
        for year in years:
            f, c, _ = groups[(year, mag)]
            ratio = c/f
            chart += f'<div class="barrow"><span>{year}</span><div class="track"><div class="bar y{year}" style="width:{100*ratio/scale}%"></div></div><b>1 : {number(ratio, 2)}</b></div>'
        chart += '</div>'
    rows = ''.join(f'<tr class="{"total" if r["Magnitude"] == "Total" else ""}"><td>{r["Ano"]}</td><td>{escape(r["Magnitude"])}</td><td>{number(r["Competitivos"])}</td><td>{number(r["Candidatos"])}</td><td>1 para {number(r["Candidatos_por_competitivo"], 2)}</td></tr>' for r in records)
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    page = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Competitivos / candidatos · Capítulo 3</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f4f6f8;color:#1d3040;font:16px/1.6 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:48px 24px}h1{font-size:clamp(28px,4vw,43px);line-height:1.15;margin:12px 0 22px}h2{font-size:23px}h3{font-size:17px;margin:0 0 10px}.eyebrow{color:#526674;letter-spacing:.12em;font-size:12px;font-weight:700}.lead{max-width:850px;color:#526674}.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin:28px 0}article,section{background:white;border:1px solid #dce4e9;border-radius:14px;padding:25px;margin-bottom:22px}article{margin:0}article strong{display:block;font-size:42px;color:#176c72}article p{margin:0;color:#526674}.formula{background:#e8f2f2;padding:16px;border-radius:8px;font-weight:600}.group{margin:25px 0}.barrow{display:grid;grid-template-columns:48px 1fr 80px;align-items:center;gap:12px;margin:8px 0}.track{height:25px;background:#edf1f4;border-radius:4px;overflow:hidden}.bar{height:100%;background:#176c72}.y2022{background:#b76436}.barrow b{text-align:right}.note,footer{font-size:13px;color:#526674}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;white-space:nowrap;font-variant-numeric:tabular-nums}th,td{padding:12px;text-align:right;border-bottom:1px solid #e1e7ec}th{font-size:13px;color:#526674}th:nth-child(2),td:nth-child(2){text-align:left}.total{font-weight:bold;background:#f0f5f6}a{color:#176c72}code{overflow-wrap:anywhere}@media(max-width:600px){main{padding:24px 14px}.cards{grid-template-columns:1fr}article,section{padding:18px}.barrow{gap:6px;grid-template-columns:42px 1fr 70px}}@media print{body{background:white}main{padding:0}section,article{break-inside:avoid}}</style></head><body><main>
<div class="eyebrow">TESE · RESULTADOS DO CAPÍTULO 3</div><h1>Um candidato competitivo para quantos candidatos totais?</h1>
<p class="lead">Eleições para deputado federal de 2018 e 2022, por categorias de magnitude do distrito (número de cadeiras da UF). Todos os partidos são agregados em cada categoria.</p>
<div class="formula">X = total de candidatos (C) / total de competitivos (F)<br>Leitura: 1 candidato competitivo para X candidatos totais.</div>
''' + f'<div class="cards">{cards}</div>' + '''<section><h2>Candidatos totais por competitivo</h2><p class="note">As barras usam a mesma escala, de 0 a 15 candidatos totais por competitivo. A relação 1 : 10 significa 1 competitivo para 10 candidatos totais. O total inclui o próprio competitivo.</p>''' + chart + '''</section><section><h2>Contagem e cálculo</h2><p>Somam-se C e F em cada grupo e calcula-se C / F. Por exemplo, 100 candidatos e 10 competitivos resultam em 1 competitivo para 10 totais. Valores menores de X indicam maior presença de competitivos.</p><div class="scroll"><table><thead><tr><th>Eleição</th><th>Magnitude (cadeiras)</th><th>Competitivos (F)</th><th>Totais (C)</th><th>Competitivo : totais</th></tr></thead><tbody>''' + rows + f'''</tbody></table></div><p class="note">Valores exibidos com duas casas decimais; cálculos realizados antes do arredondamento. <a href="{STEM}.csv" download>Baixar dados em CSV</a>.</p></section>
<section><h2>Critérios e fonte</h2><p>Competitividade preserva a classificação do relatório original: vitória anterior para prefeito, deputado estadual/distrital, deputado federal, governador ou senador, ou alcance histórico de 10% do quociente eleitoral. Vereador é excluído do critério de vitória.</p><p>O total C inclui todas as candidaturas presentes nas nominatas da base analítica, inclusive listas sem recursos e sem eleitos. A unidade de origem é partido × UF × eleição; federações não são agregadas. Os totais descrevem a base do capítulo e não presumem cobertura de todas as inscrições brutas no TSE.</p><p>Fonte: <a href="25_todas_nominatas.csv">25_todas_nominatas.csv</a>, colunas Ano, Magnitude, F e C. Contagens conferidas com <a href="01_universos.csv">01_universos.csv</a> e <a href="03_competitivos_magnitude_tipo.csv">03_competitivos_magnitude_tipo.csv</a>, agregando os tipos de partido.</p><p class="note">Verificação: nominatas sem duplicação; 0 ≤ F ≤ C; totais nacionais e por magnitude coincidem com as tabelas de origem.</p></section><footer>Gerador: tese/scripts/razao_competitivos_magnitude.py<br>SHA-256 da fonte: <code>{digest}</code></footer></main></body></html>'''
    (OUT / f'{STEM}.html').write_text(page, encoding='utf-8')
    print(f'HTML: {OUT / (STEM + ".html")}')
    for r in records:
        print(f'{r["Ano"]} | {r["Magnitude"]} | 1 competitivo para {r["Candidatos_por_competitivo"]:.4f} totais')
    print('Verificações de consistência: OK')


if __name__ == '__main__':
    main()
