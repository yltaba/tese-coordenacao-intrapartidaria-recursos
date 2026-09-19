"""Checagem mecânica de evidências e integridade dos relatórios; não arbitra mérito."""
from pathlib import Path
import hashlib
import json
import re
import yaml

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / 'thesis-review/runs/run-002'
required = ['id', 'titulo', 'escala', 'localizacao', 'afirmacao_do_autor', 'problema', 'evidencia', 'severidade', 'confianca', 'recomendacao']
results = []
for report in sorted((RUN / 'agents').glob('*.md')):
    entries = []
    for block in re.findall(r'```yaml\s*\n(.*?)```', report.read_text(encoding='utf-8'), re.S):
        try:
            content = yaml.safe_load(block)
        except yaml.YAMLError as err:
            entries.append({'error_yaml': str(err)})
            continue
        for finding in content if isinstance(content, list) else [content]:
            if not isinstance(finding, dict) or 'id' not in finding:
                continue
            missing = [key for key in required if key not in finding]
            loc = finding.get('localizacao', {})
            path = ROOT / loc.get('arquivo', '')
            quote = loc.get('trecho', '')
            line = loc.get('linha')
            source = path.read_text(encoding='utf-8-sig') if path.is_file() else ''
            literal = bool(quote) and quote in source
            lines = source.splitlines()
            at_line = isinstance(line, int) and 0 < line <= len(lines) and quote in '\n'.join(lines[line-1:line+5])
            entries.append({'id': finding['id'], 'missing': missing, 'literal': literal, 'line_matches': at_line, 'sources_present': bool(finding.get('evidencia', {}).get('fontes'))})
    results.append({'report': report.name, 'findings': entries})
manifest = yaml.safe_load((RUN / 'manifest.yaml').read_text(encoding='utf-8'))
changed = []
for entry in manifest['insumos']:
    path = ROOT / entry['arquivo']
    current = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else 'AUSENTE'
    if current != entry['sha256']:
        changed.append(entry['arquivo'])
output = {'reports': results, 'inputs_changed': changed}
(RUN / 'evidence/validacao_relatorios.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(output, ensure_ascii=False, indent=2))
