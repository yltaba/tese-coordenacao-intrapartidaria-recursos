"""Verificação do HTML local em navegador, desktop e mobile."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parents[1] / 'resultados-teto-financiamento'
with sync_playwright() as p:
    with p.chromium.launch(channel='msedge') as browser:
        page = browser.new_page(viewport={'width':1440,'height':1050})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto((out/'testes-teto-financiamento.html').as_uri())
        assert page.title() == 'Teto de gastos e financiamento alternativo'
        assert page.locator('.js-plotly-plot').count() == 2
        page.screenshot(path=str(out/'previa-desktop.png'))
        page.locator('#t1').screenshot(path=str(out/'previa-teste1.png'))
        page.locator('#t2').screenshot(path=str(out/'previa-teste2.png'))
        n = page.locator('#cases tbody tr:visible').count()
        assert n == 115
        page.locator('#search').fill('zzzinexistente')
        assert page.locator('#cases tbody tr:visible').count() == 0
        page.locator('#search').fill('')
        assert page.locator('#cases tbody tr:visible').count() == n
        for a in page.locator('a[href]').all():
            href = a.get_attribute('href')
            if href.startswith('#'):
                assert page.locator(href).count() == 1
            elif not href.startswith('http'):
                assert (out / href).is_file(), href
        page.set_viewport_size({'width':390,'height':844})
        page.evaluate('window.scrollTo(0,0)')
        page.wait_for_timeout(500)
        page.screenshot(path=str(out/'previa-mobile.png'))
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        assert not errors, errors
        result = dict(graficos=2,linhas_candidatos=n,filtro='passou',links_locais='passou',mobile_sem_overflow=True,erros_javascript=errors)
        (out/'verificacao-interface.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(result)
