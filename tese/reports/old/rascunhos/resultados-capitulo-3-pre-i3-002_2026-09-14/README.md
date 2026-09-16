# Snapshot pré-correção I-3-002 (2026-09-14)

Cópia de `tese/reports/resultados-capitulo-3/` (00_sintese.csv … 26_fontes.csv,
resultados-capitulo-3.html, verificacao.json) **antes** de regenerar com o
`candidato_competitivo` corrigido.

Correção: `src/1_silver/gerar_rrd.py::adicionar_alcancou_10pct_qe_hist` restringiu
o critério (ii) de "competitivo" (10% do quociente eleitoral) a Deputado
Federal e Deputado Estadual, removendo Governador/Senador/Prefeito — conforme
`tese/03-medindo-coordenacao-intrapartidaria.qmd` l. 68 e a recomendação
I-3-002 de `thesis-review/runs/run-001/synthesis/final_review.md`.

Impacto observado em `candidato_competitivo` (Deputado Federal):
- 2018: 886/7.630 (11,6%) → 879/7.630 (11,5%)
- 2022: 1.287/9.675 (13,3%) → 1.261/9.675 (13,0%)

A base pré-correção correspondente está em
`data/processed/archive/pre-i3-002_2026-09-14/rrd_df_novo.parquet`.

Somente as tabelas que dependem de `candidato_competitivo`/`candidato_competitivo_nom`
mudam de valor (seção 2 "Candidaturas competitivas...": 02, 03, 04, 09, e os
agregados que os usam em 22/23/24/25). Cobertura/precisão/lift do Top-NECr
(seções 5–6; tabelas 11–18) usam `eleito`, não `candidato_competitivo`, e não
mudam.
