"""Verificações independentes de identidades, referências e HTML de mensuração."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'tese/resultados-validacao-top-necr'
REPORT=ROOT/'tese/relatorio-validacao-top-necr.html'
lists=pd.read_csv(OUT/'auditoria_listas_cortes.csv',float_precision='round_trip')
fl=pd.read_csv(OUT/'auditoria_credenciais.csv',float_precision='round_trip')
main=lists[lists.Regra.eq('Arredondado')]
assert main.groupby('Ano').size().tolist()==[859,711]
assert not lists.duplicated(['Ano','UF','Partido','Regra']).any()
assert lists.K.between(0,lists.C).all()
assert np.allclose(lists['Esperado aleatório'],lists.K*lists.E/lists.C)
assert (lists.Acertos<=np.minimum(lists.K,lists.E)+1e-8).all()
funded=lists[lists['Recursos R$']>0]
assert (funded['Massa de recursos %']+1e-8>=funded['Amplitude %']).all()
assert np.allclose(funded['Massa de recursos %'],100*funded['Recursos no núcleo R$']/funded['Recursos R$'])
assert lists.loc[~lists['Fronteira válida'],'Distância relativa no corte %'].isna().all()
assert lists.loc[lists['Empate na fronteira'],'Distância relativa no corte %'].dropna().eq(0).all()
assert (lists.Acertos>=lists['Acertos mínimos por desempate']-1e-8).all()
assert (lists.Acertos<=lists['Acertos máximos por desempate']+1e-8).all()
assert np.allclose(fl['Perfil no núcleo']+fl['Perfil fora'],fl['Total com perfil'])
assert np.allclose(fl['K válido']+fl['N fora válido'],fl['N válido'])
z=fl[fl['N válido']>0]
assert np.allclose(z['Esperado perfil'],z['K válido']*z['Total com perfil']/z['N válido'])
post=pd.read_csv(OUT/'validade_expost.csv')
for _,r in post.iterrows():
    g=main[main.Ano.eq(r.Ano)]
    assert np.isclose(r.Observados,g.Acertos.sum())
    expected='Esperado aleatório' if r['Sorteio dentro da lista']=='Todos os candidatos' else 'Esperado entre financiados'
    assert np.isclose(r.Esperados,g[expected].sum())
    assert np.isclose(r.Lift,r.Observados/r.Esperados)
    assert np.isclose(r.Lift,r['Precisão observada %']/r['Precisão esperada %'])
    assert np.isclose(r.Lift,r['Cobertura observada %']/r['Cobertura esperada %'])
party=pd.read_csv(OUT/'validade_por_partido.csv')
assert party.groupby('Ano').size().tolist()==[35,32]
assert party.groupby('Ano').Eleitos.sum().eq(513).all()
internal=pd.read_csv(OUT/'validade_interna.csv')
for _,r in internal.iterrows():
    g=main[main.Ano.eq(r.Ano)&main['Recursos R$'].gt(0)]
    assert np.isclose(r['Massa por lista mediana %'],g['Massa de recursos %'].median())
    assert r['Fronteiras comparáveis']==g['Fronteira válida'].sum()
audit=json.loads((OUT/'auditoria.json').read_text(encoding='utf-8'))
assert all(audit['verificacoes'].values())
for source,sha in audit['fontes_sha256'].items():
    assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==sha,source
soup=BeautifulSoup(REPORT.read_text(encoding='utf-8'),'html.parser')
ids=[x['id'] for x in soup.select('[id]')]
assert len(ids)==len(set(ids))
assert not soup.select('script[src]')
for a in soup.select('a[href]'):
    h=a['href']
    assert (soup.find(id=h[1:]) is not None) if h.startswith('#') else (REPORT.parent/h).exists(),h
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,channel='msedge')
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.goto(REPORT.as_uri(),wait_until='load')
    assert page.locator('.plotly-graph-div').count()==audit['graficos']
    page.locator('input[data-table="t-validade_por_partido"]').fill('PSOL')
    assert page.locator('#t-validade_por_partido tbody tr:visible').count()==2
    page.locator('input[data-table="t-validade_por_partido"]').fill('')
    assert page.locator('#t-validade_por_partido tbody tr:visible').count()==67
    page.locator('#sintese').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT/'verificacao-desktop.png'))
    page.locator('#valid-fig-4').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT/'verificacao-grafico.png'))
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#sintese').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT/'verificacao-mobile.png'))
    assert not errors,errors
    browser.close()
print('OK: identidades contábeis, benchmarks intralista, perfis, cortes, auditoria, gráficos e filtro por partido.')
