# Síntese pass 1 — run-002

Os relatórios convergem em que os números do Top-NECr, Top-X e da figura da regressão batem com os artefatos atuais. A ausência da discussão foi excluída conforme `ESCOPO.md`.

## Agrupamento

| Achados | Issue |
|---|---|
| STA-3-001 | I-3-001 — estimando e massa não unitária após filtros da regressão |
| STA-3-002 | I-3-002 — sensibilidade da inferência racial ao cluster |
| STA-3-003, STA-3-004 | I-3-003 — convenções de agregação e AME precisam ser declaradas |
| MEA-3-001 | I-3-004 — origem partidária versus fundos específicos |
| MEA-3-002 | I-3-005 — cargos definidos versus cargos estimados |
| THE-3-001 | I-3-006 — alcance associativo do mecanismo |
| WRI-3-001, WRI-3-002, RES-3-001, RES-3-002 | I-3-007 — legendas e chaves visuais |

## Conflitos e decisão provisória

O problema da massa não unitária é MAJOR por atingir a especificação, embora as recomputações indiquem alteração pequena nos coeficientes. A sensibilidade racial é MODERATE. Os demais são correções de declaração, interpretação ou polimento. O elo mais fraco da cadeia é a especificação da regressão após filtros; a cadeia substantiva Top-NECr → robustez permanece coerente.
