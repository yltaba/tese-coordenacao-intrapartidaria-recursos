# Snapshot pré-correção I-3-001/D1+D3 (2026-09-14)

Cópia de `tese/reports/resultados-capitulo-3/` após I-3-002 + D2 (zfill), mas
**antes** de D1 (chave de ligação de CPF por cargo/município) e D3
(desempate pelo registro APTO em substituições de candidato).

Correção: `src/1_silver/gerar_rrd.py` ganhou `ligar_cpf`/`_preparar_candidatos_cpf`,
substituindo os antigos `drop_duplicates(["ano","uf","numero"], keep="first")`
em `construir_base`, `_construir_resultados_select` e `_gerar_resultados_cpf`.
A chave agora inclui o cargo e, em Prefeito/Vereador, também o município;
entre CPFs distintos sob o mesmo número (substituição), prioriza
`ds_situacao_candidatura == "APTO"`. Ver `thesis-review/runs/run-001/synthesis/
final_review.md`, achado I-3-001, D1 e D3.

Efeito sobre `candidato_competitivo` (Deputado Federal), acumulado sobre
I-3-002 + D2:
- 2018: 938/7.630 (12,3%) → 973/7.630 (12,75%)
- 2022: 1.275/9.675 (13,2%) → 1.354/9.675 (13,99%)

Progressão completa desde a base original:
| Etapa | 2018 | 2022 |
|---|---|---|
| Original | 886 (11,61%) | 1.287 (13,30%) |
| + I-3-002 (10% QE só proporcional) | 879 (11,52%) | 1.261 (13,03%) |
| + D2 (zfill CPF 2012/2014) | 938 (12,29%) | 1.275 (13,18%) |
| + D1+D3 (agora) | 973 (12,75%) | 1.354 (13,99%) |

Checagens do próprio relatório de revisão, confirmadas após a correção:
- Dos 378 deputados federais eleitos em 2014 que concorreram em 2018: 377/377
  contam como competitivos (era 353/378 na base original).
- "2022 MG AVANTE 7025" caiu de 46 para 1 vitória de prefeito.
- Os 3 casos de identidade trocada citados na revisão (Pauderney Avelino,
  Andréia Zemuner, José Arnon Bezerra) têm CPF/gênero corrigidos.

Bases intermediárias para auditoria:
- `data/processed/archive/pre-i3-002_2026-09-14/` — original
- `data/processed/archive/pre-i3-001-d2-zfill_2026-09-14/` — só I-3-002
- `data/processed/archive/pre-i3-001-d1d3_2026-09-14/` — I-3-002 + D2, sem D1/D3

Residual conhecido: o casamento de município usa normalização de acentos,
mas não recupera nomes já corrompidos na origem (mojibake em ~0,7% das linhas
de Prefeito entre 2012-2022, ex.: "OLHO D'ÁGUA..." gravado com caractere de
substituição). Essas poucas candidaturas municipais ficam sem CPF ligado
(tratadas como sem histórico ali, não como ligação errada).
