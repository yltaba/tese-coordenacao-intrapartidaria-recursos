"""Verifica gráficos, links, filtro e apresentação móvel da exploração de gastos."""
from pathlib import Path
import json
import pandas as pd
from playwright.sync_api import sync_playwright

out=Path(__file__).resolve().parents[1]/'exploracao-gastos-teto'
expected=int(pd.read_csv(out/'candidatos.csv').gasto_pct.ge(80).sum())
with sync_playwright() as p:
    with p.chromium.launch(channel='msedge') as b:
        page=b.new_page(viewport={'width':1440,'height':1000})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((out/'exploracao-gastos-teto.html').as_uri())
        assert page.locator('.js-plotly-plot').count()==2
        page.screenshot(path=str(out/'previa-desktop.png'))
        page.locator('#distribuicao').screenshot(path=str(out/'previa-distribuicao.png'))
        assert page.locator('#cases tbody tr:visible').count()==expected
        page.locator('#search').fill('zzzinexistente')
        assert page.locator('#cases tbody tr:visible').count()==0
        page.locator('#search').fill('')
        assert page.locator('#cases tbody tr:visible').count()==expected
        for a in page.locator('a[href]').all():
            href=a.get_attribute('href')
            if href.startswith('#'):assert page.locator(href).count()==1
            elif not href.startswith('http'):assert (out/href).is_file(),href
        page.set_viewport_size({'width':390,'height':844})
        page.evaluate('window.scrollTo(0,0)')
        page.wait_for_timeout(500)
        page.screenshot(path=str(out/'previa-mobile.png'))
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        assert not errors,errors
        result=dict(graficos=2,candidatos_na_tabela=expected,filtro='passou',links='passou',mobile_sem_overflow=True,erros_javascript=errors)
        (out/'verificacao-interface.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(result)
