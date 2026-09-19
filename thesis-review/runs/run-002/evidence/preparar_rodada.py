"""Preserva os insumos e o escopo da revisão pré-discussão do capítulo 3."""
from pathlib import Path
from hashlib import sha256
import shutil
import yaml

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / 'thesis-review/runs/run-002'
manifest_path = RUN / 'manifest.yaml'
manifest = yaml.safe_load(manifest_path.read_text(encoding='utf-8'))
manifest['escopo'] = {
    'objetivo': 'Avaliar coerência e estrutura do capítulo 3 antes da escrita final da discussão.',
    'exclusoes': ['Ausência ou incompletude da discussão deliberadamente fora dos achados e gates.'],
    'alteracao_do_capitulo': False,
    'fluxo': 'measurement/statistics/results; theory; chair pass 1; writing; chair complemento pass 1; adversarial; chair pass 2',
}
additional = [
    'tese/02-literatura.qmd', 'tese/04-mecanismo-causal-coordenacao.qmd',
    'tese/scripts/regressao_fracionaria_cap3.py', 'tese/scripts/regenerar_figuras_cap3.py',
    'tese/scripts/resultados_capitulo3.py', 'tese/references.bib',
]
additional += [str(p.relative_to(ROOT)).replace('\\', '/') for p in (ROOT / 'tese/reports/regressao-fracionaria').glob('*.csv')]
additional += [str(p.relative_to(ROOT)).replace('\\', '/') for p in (ROOT / 'figs').glob('cap3_*.png')]
existing = {i['arquivo'] for i in manifest['insumos']}
for rel in additional:
    if rel not in existing:
        p = ROOT / rel
        manifest['insumos'].append({'arquivo': rel, 'sha256': sha256(p.read_bytes()).hexdigest() if p.exists() else 'AUSENTE'})
for source, target in [
    ('tese/03-medindo-coordenacao-intrapartidaria.qmd', 'capitulo3_snapshot.qmd'),
    ('thesis-review/claims/claims.yaml', 'claims_antes_run002.yaml'),
]:
    dest = RUN / 'evidence' / target
    if not dest.exists():
        shutil.copyfile(ROOT / source, dest)
manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding='utf-8')
print('Escopo, hashes e snapshots registrados.')
