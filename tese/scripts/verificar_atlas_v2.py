"""Verifica dados, navegação e filtros do artefato final em navegador local."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tese/resultados-capitulo-3'
target = OUT / 'atlas-visual-capitulo-3-v2.html'
doc = BeautifulSoup(target.read_text(encoding='utf-8'), 'html.parser')
ids = [e['id'] for e in doc.select('[id]')]
assert len(ids) == len(set(ids)), 'IDs duplicados'
for link in doc.select('a[href]'):
    href = link['href']
    if href.startswith('#'):
        assert href[1:] in ids, href
    elif not href.startswith('https:'):
        assert (OUT / href).exists(), href
for script in doc.select('script'):
    script.decompose()
assert '??' not in doc.get_text(), 'Texto corrompido'

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(target.as_uri(), wait_until='load')
    page.wait_for_function("document.querySelector('#explorer').data?.length === 2")
    assert page.locator('.js-plotly-plot').count() == 15
    for metric in ['Lift', 'Excedente_pp', 'Cobertura_competitiva_pct', 'Lift_competitivo', 'NECr']:
        page.select_option('#metric', metric)
        page.wait_for_function('(m) => document.querySelector("#scope").textContent.includes(LABELS[m])', arg=metric)
        assert page.locator('#stats .card').count() == 2
    page.select_option('#uf', 'SP')
    page.select_option('#party', 'PT')
    assert '2 nominatas' in page.locator('#scope').inner_text()
    page.select_option('#mag', label='Pequeno (8–12)')
    assert 'Não há observações válidas' in page.locator('#empty').inner_text()
    page.select_option('#uf', '')
    page.select_option('#party', '')
    page.select_option('#mag', '')
    page.screenshot(path=str(OUT / 'atlas-v2-preview.png'))
    page.locator('#focalizacao').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT / 'atlas-v2-focalizacao-preview.png'))
    page.set_viewport_size({'width': 390, 'height': 844})
    page.evaluate('window.scrollTo(0,0)')
    page.wait_for_timeout(500)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 2'), 'Overflow mobile'
    page.screenshot(path=str(OUT / 'atlas-v2-mobile-preview.png'))
    assert not errors, errors
    browser.close()
result = {'status': 'OK', 'nominatas': 1570, 'graficos_narrativos': 14, 'explorador': True,
          'links_locais': 'OK', 'filtros_e_recorte_vazio': 'OK', 'mobile_390px': 'OK', 'erros_javascript': errors}
(OUT / 'v2_verificacao_interface.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=True))
