"""Auditoria read-only do capítulo 3; escreve apenas evidências deste run."""
from pathlib import Path
import importlib.util
import json
import re
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('cap3_fig_audit', ROOT/'tese/scripts/regenerar_figuras_cap3.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
listas = mod.carregar_listas()
rows=[]
for alvo in ['competitividade','eleicao']:
    for corte in ['topnecr', *mod.TAUS]:
        k='k_arredondado' if corte=='topnecr' else f'k_{corte}'
        for ano, vals in mod.nacional(listas, alvo, k, f'H_{alvo}_{corte}').items():
            rows.append(dict(ano=ano,alvo=alvo,corte=corte,**vals))
pd.DataFrame(rows).to_csv(OUT/'res_metricas_recomputadas.csv',index=False)
fund=listas[listas.Recursos>0]
summary=[]
for ano,g in listas.groupby('ano_eleicao'):
    f=fund[fund.ano_eleicao==ano]
    summary.append(dict(ano=int(ano),candidatos=int(g.C.sum()),competitivos=int(g.F.sum()),listas=len(g),listas_financiadas=len(f),sem_recursos=int((g.Recursos<=0).sum()),eleitos_sem_recursos=float(g.loc[g.Recursos<=0,'E'].sum()),C_mediana=f.C.median(),F_mediana=f.F.median(),F_media=f.F.mean(),NECr_mediana=f.NECr.median(),C_NECr_mediana=(f.C/f.NECr).median(),NECr_C_mediana=100*(f.NECr/f.C).median()))
(OUT/'res_resumo_recomputado.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
qmd=ROOT/'tese/03-medindo-coordenacao-intrapartidaria.qmd'
lines=qmd.read_text(encoding='utf-8').splitlines()
numbers=[dict(linha=i,trecho=line,numeros='; '.join(re.findall(r'\b\d+(?:[.,]\d+)*(?:%|/\d+)?',line))) for i,line in enumerate(lines,1) if re.search(r'\d',line)]
pd.DataFrame(numbers).to_csv(OUT/'res_inventario_tokens_numericos.csv',index=False)
allqmd='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'tese').glob('*.qmd'))
refs=sorted(set(re.findall(r'@((?:sec|fig|tbl|eq)-[\w-]+)', '\n'.join(lines))))
defs=set(re.findall(r'\{#([\w-]+)',allqmd))
(OUT/'res_referencias.json').write_text(json.dumps({'referencias':refs,'nao_definidas':[r for r in refs if r not in defs]},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print(pd.DataFrame(rows).to_string(index=False))
print('Referencias nao definidas:',[r for r in refs if r not in defs])
