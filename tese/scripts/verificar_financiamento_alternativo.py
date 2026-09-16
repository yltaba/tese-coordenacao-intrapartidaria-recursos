from pathlib import Path
import json
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parents[1] / 'resultados-financiamento-alternativo'
with sync_playwright() as p:
    with p.chromium.launch(channel='msedge') as browser:
        page = browser.new_page(viewport={'width':1440,'height':1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto((out/'financiamento-alternativo-top-necr.html').as_uri())
        assert page.locator('.js-plotly-plot').count() == 2
        page.screenshot(path=str(out/'previa-desktop.png'))
        n = page.locator('#cases tbody tr:visible').count()
        page.locator('#search').fill('zzzinexistente')
        assert page.locator('#cases tbody tr:visible').count() == 0
        page.locator('#search').fill('')
        assert page.locator('#cases tbody tr:visible').count() == n
        page.set_viewport_size({'width':390,'height':844})
        page.evaluate('window.scrollTo(0,0)')
        page.wait_for_timeout(500)
        page.screenshot(path=str(out/'previa-mobile.png'))
        overflow = page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
        if overflow:
            print(page.evaluate('Array.from(document.querySelectorAll("body *")).filter(e=>e.getBoundingClientRect().right>395 && !e.closest(".scroll")).slice(0,20).map(e=>[e.tagName,e.className,e.getBoundingClientRect().right])'))
        assert not overflow
        assert not errors
        result = dict(graficos=2,linhas_candidatos=n,filtro='passou',mobile_sem_overflow=True,erros_javascript=errors)
        (out/'verificacao-interface.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(result)
