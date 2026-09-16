# Snapshot pré-correção I-3-001/D2 (2026-09-14)

Cópia de `tese/reports/resultados-capitulo-3/` **após** a correção I-3-002
(critério (ii) restrito a Dep. Federal/Estadual) mas **antes** da correção
D2 (zfill dos CPFs de 2012/2014).

Correção D2: `src/1_silver/gerar_rrd.py::carregar_dados` passou a normalizar
`nr_cpf_candidato` com `zfill(11)` (preservando sentinelas "-1"/"-4") na
leitura de `candidatos.parquet`. Em 2012 e 2014, 28,6% e 26,4% dos CPFs
haviam sido gravados sem zeros à esquerda (8–10 dígitos); o merge por
CPF-string usado para computar histórico eleitoral e %QE histórico não
ligava essas candidaturas ao seu próprio histórico de 2012/2014. Ver
`thesis-review/runs/run-001/synthesis/final_review.md`, achado I-3-001/D2.

Efeito sobre `candidato_competitivo` (Deputado Federal), em cima do estado
já corrigido para I-3-002:
- 2018: 879/7.630 (11,5%) → 938/7.630 (12,3%)
- 2022: 1.261/9.675 (13,0%) → 1.275/9.675 (13,2%)

Checagem do próprio relatório de revisão (dos 378 deputados federais eleitos
em 2014 que concorreram em 2018): antes, 52 apareciam com zero vitórias
federais na base e 25 não eram competitivos (todos com CPF iniciado em "0").
Depois da correção: 0 e 0.

A base intermediária (só I-3-002, sem D2) está em
`data/processed/archive/pre-i3-001-d2-zfill_2026-09-14/rrd_df_novo.parquet`.
A base original (antes de tudo) está em
`data/processed/archive/pre-i3-002_2026-09-14/rrd_df_novo.parquet`.

Esta correção NÃO inclui os outros dois defeitos de ligação de CPF do mesmo
achado I-3-001 (D1 — chave de merge não única entre cargos/municípios; D3 —
desempate arbitrário na identidade da candidatura de Dep. Federal). Esses
permanecem como estavam.
