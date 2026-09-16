"""Audita tabelas, navegação e interações do relatório descritivo."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'tese/old/relatorios-descritivos/resultados-descritivos-nucleo'
REPORT=ROOT/'tese/old/relatorios-descritivos/relatorio-exploracao-nucleo.html'
party=pd.read_csv(OUT/'partidos.csv')
nation=pd.read_csv(OUT/'panorama.csv').set_index('Ano')
assert party.groupby('Ano').size().tolist()==[35,32]
for year,g in party.groupby('Ano'):
    for col in ['Candidatos','Posições no núcleo','Eleitos','Eleitos dentro','Eleitos fora','Não eleitos dentro']:
        assert np.isclose(g[col].sum(),nation.loc[year,col]),col
    assert np.allclose(g['Eleitos dentro']+g['Eleitos fora'],g.Eleitos)
    assert g.loc[g.Eleitos.eq(0),'Cobertura %'].isna().all()
profiles=pd.read_csv(OUT/'composicao_partidos.csv')
for _,r in profiles.iterrows():
    k=party[(party.Ano==r.Ano)&party.Partido.eq(r.Partido)]['Posições no núcleo'].iloc[0]
    assert np.isclose(r['Núcleo válido (ponderado)']+r['Ausência no núcleo (ponderada)'],k)
    if r['Candidatos com perfil']:
        assert np.isclose(r['Entrada no núcleo entre candidatos do perfil %'],100*r['Perfil no núcleo (ponderado)']/r['Candidatos com perfil'])
    if r['Núcleo válido (ponderado)']:
        assert np.isclose(r['Composição do núcleo %'],100*r['Perfil no núcleo (ponderado)']/r['Núcleo válido (ponderado)'])
audit=json.loads((OUT/'auditoria.json').read_text(encoding='utf-8'))
assert all(audit['verificacoes'].values())
soup=BeautifulSoup(REPORT.read_text(encoding='utf-8'),'html.parser')
ids=[node['id'] for node in soup.select('[id]')]
assert len(ids)==len(set(ids))
assert not soup.select('script[src]')
for a in soup.select('a[href]'):
    link=a['href']
    if link.startswith('#'):assert soup.find(id=link[1:])
    else:assert (REPORT.parent/link).exists()
for t in soup.select('script'):t.decompose()
text=soup.get_text(' ',strip=True).lower()
for term in ['p-valor','regressão','regressões','bootstrap','holm','wald']:
    assert term not in text,term

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,channel='msedge')
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.goto(REPORT.as_uri(),wait_until='load')
    assert page.locator('.plotly-graph-div').count()==audit['graficos']
    assert page.locator('.year-panel[data-year="2018"]').is_visible()
    page.select_option('#party-year','2022')
    assert page.locator('.year-panel[data-year="2022"]').is_visible()
    assert not page.locator('.year-panel[data-year="2018"]').is_visible()
    page.locator('input[data-table="tbl-partidos"]').fill('PSOL')
    assert page.locator('#tbl-partidos tbody tr:visible').count()==2
    page.locator('input[data-table="tbl-partidos"]').fill('')
    assert page.locator('#tbl-partidos tbody tr:visible').count()==67
    page.screenshot(path=str(OUT/'verificacao-desktop.png'),full_page=False)
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#panorama').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT/'verificacao-mobile.png'),full_page=False)
    assert not errors,errors
    browser.close()
print('OK: somas partidárias, denominadores, links, conteúdo descritivo, seletor de ano e filtro por partido.')
