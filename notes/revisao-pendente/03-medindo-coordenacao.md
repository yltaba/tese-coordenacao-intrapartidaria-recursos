# Revisão pendente: Cap. 3 — Priorização na alocação de recursos partidários

- **Data da análise:** 18/09/2026.
- **Arquivo:** [tese/03-medindo-coordenacao-intrapartidaria.qmd](../../tese/03-medindo-coordenacao-intrapartidaria.qmd), do início até "## Discussão" (exclusive).
- **Fora do escopo:** a Discussão (`@sec-discussao-cap3`), que você está redigindo.
- **Diferença deste capítulo em relação a Financiamento/Argumento (Cap. 2):** já existe um run de revisão por agentes arbitrado — `thesis-review/runs/run-002/` (18/09/2026) — com achados verificados por recomputação (measurement, statistics, results, theory, writing → chair → adversarial). Esta nota **não repete** essa análise: cruza os achados já arbitrados (issues `I-3-001` a `I-3-007`, todos com `status: open`) com a leitura direta do capítulo, cita o run como fonte nos comentários HTML, e acrescenta pontos de coerência estrutural que o run-002 não cobre (ele analisa achado por achado, não a costura entre parágrafos).
- **Checagens próprias feitas nesta revisão** (além de retomar o run-002): contagens de listas/candidaturas em `data/processed/rrd_df_novo.parquet` (Dados); valores de lift por magnitude em `tese/reports/lift-magnitude-partido/lift_por_magnitude.csv`; razões da regressão intralista em `tese/reports/regressao-fracionaria/{coeficientes,ames}.csv`; cobertura/precisão nacional dos eleitos em `tese/reports/resultados-capitulo-3/15_cobertura_nacional.csv`.
- **Como ler:** os comentários HTML no `.qmd` usam rótulos `[3.0]`…`[3.8]` e sublabels `[3.x-n]`. Quando um comentário cita `I-3-00n` ou `STA/MEA/THE/WRI-3-00n`, a fonte completa está em `thesis-review/runs/run-002/issues.yaml` e `thesis-review/runs/run-002/agents/*.md`.

---

## 1. Diagnóstico geral

Este capítulo é o mais maduro dos três em termos de rigor quantitativo: cada número tem uma fonte auditável (`tese/reports/`), e a maior parte das afirmações que verifiquei nesta revisão bateu exatamente com os CSVs de origem. Os problemas encontrados são de três tipos:

1. **Um problema metodológico MAJOR, já identificado e ainda aberto** (`I-3-001`): a regressão fracionária intralista (`sec-premio-credenciais`) calcula as parcelas $s_{il}$ antes de excluir candidaturas sem CPF ligado, o que quebra a soma unitária em 2 listas de 2018 e 12 de 2022. O efeito estimado nos casos testados é pequeno, mas o método precisa ser corrigido e os artefatos regenerados antes de fechar a versão final. Ver `[3.7]`.
2. **Precisão na descrição da agregação nacional.** Cobertura, precisão e *lift* nacionais são razões de somas ponderadas, não a média das métricas por lista — a diferença chega a 7,7 pontos percentuais na precisão de 2018 (`I-3-003`/`STA-3-003`). A seção `sec-metricas` não declara essa regra de agregação. Ver `[3.4]` e `[3.6-1]`.
3. **Precisão na descrição de variáveis e escopo.** "Recursos de partido" não é estritamente FEFC/FP (`I-3-004`); "todos os cargos" na regressão inclui, na leitura literal, Presidente, que não é estimado (`I-3-005`); a robustez da desvantagem racial em 2022 depende do nível de cluster escolhido (`I-3-002`). Todos MODERATE, todos com correção de redação simples.

Nenhum desses pontos exige refazer a análise: a recomendação do próprio run-002, que concordo ao reler o capítulo, é de correção pontual de método (para `I-3-001`) e de redação (para os demais).

## 2. Cruzamento com o run-002 (issues abertos)

| Issue | Severidade | Onde no `.qmd` | Resumo | Rótulo do comentário |
|---|---|---|---|---|
| `I-3-001` | **MAJOR** | Prêmio intralista | Massa não unitária na regressão fracionária; corrigir Hessiana/escores ou renormalizar. | `[3.7]` |
| `I-3-002` | MODERATE | Prêmio intralista (negra, 2022) | Significância da desvantagem racial não resiste a cluster por partido. | `[3.7-9]` |
| `I-3-003` | MODERATE | Composição do núcleo (sec-metricas) | Agregação nacional é razão de somas, não média por lista; declarar a regra. | `[3.4]`, `[3.6-1]` |
| `I-3-004` | MODERATE | Dados | "Recursos de partido" ≠ exclusivamente FEFC/FP. | `[3.1-1]` |
| `I-3-005` | MODERATE | Prêmio intralista | "Todos os cargos" excede os cargos de fato estimados (sem Presidente). | `[3.3-1]`, `[3.7-3]`, `[3.7-4]` |
| `I-3-006` | MODERATE | Introdução do capítulo | Formular o mecanismo como associação compatível, não como causa demonstrada. | `[3.0]` |
| `I-3-007` | MINOR | Tabelas/figuras de magnitude | Legendas sem título; chave visual das figuras Top-X incompleta. | `[3.8-1]`, `[3.8-3]` |

## 3. Achados novos desta revisão (não cobertos pelo run-002)

- **`[3.2]`** — A escolha de arredondar $NECr$ (em vez de piso ou teto) nunca é justificada no texto. A tabela `15_cobertura_nacional.csv` mostra que ela fica no meio das três regras (82,6% / 86,7% / 87,7% de cobertura de eleitos em 2018) — uma frase explicando por que o meio-termo é a escolha certa fortaleceria a seção.
- **`[3.1-2]`** — "Retroagindo até 1998" (Dados) e a lista de cargos em `sec-competitivos` (que inclui Presidente) já estavam registrados como divergência em `19_notas_redacao.csv`, mas não tinham chegado ao run-002 como achado formal. Incluí como `[3.1-2]`/`[3.3-1]`, citando a nota existente.
- **`[3.5-1]`** — Repetição: a proporção de candidaturas "efetivas" (1/Q ≈ 51%/54%) aparece duas vezes seguidas, em parágrafos consecutivos.
- **`[3.8-2]`** — Falta uma frase conectando por que o Top-X% (que testa limiares de 50% a 95%) produz núcleos tipicamente maiores que o Top-NECr, o que ajuda a entender a curva de cobertura crescente da robustez.

## 4. Verificações que bateram (sem necessidade de ação)

- Universo de candidaturas: 7.630 (2018) e 9.675 (2022) — confere.
- Listas: 859/711; sem recursos: 73/63; eleitos nessas listas: 3/0 — confere exatamente.
- Competitivos: 973/7.630 = 12,75%; 1.354/9.675 = 13,99%; crescimento 27%/39% — confere.
- Lift por magnitude (competitivos e eleitos), tabelas `tbl-cap3-01` e `tbl-cap3-02` — todos os seis valores conferem contra `lift_por_magnitude.csv`.
- Cobertura/precisão nacional dos eleitos (86,7%/92,6% e 19,2%/12,4%) — confere exatamente contra `15_cobertura_nacional.csv` (regra "arredondado").
- Razões da regressão intralista para vitórias por cargo, mulher e o indicador de credencial binário (2018) — todas conferidas contra `coeficientes.csv`.

## 5. Checklist de prioridade

- [ ] **Resolver `I-3-001` antes de fechar a versão final** (correção de método na regressão fracionária; ver `thesis-review/runs/run-002/agents/statistics.md`, achado `STA-3-001`, com o código de correção sugerido).
- [ ] Declarar a regra de agregação nacional em `sec-metricas` (`I-3-003`).
- [ ] Ajustar a frase sobre origem dos recursos em Dados (`I-3-004`).
- [ ] Ajustar "todos os cargos" na regressão, ou listar os cargos estimados (`I-3-005`).
- [ ] Qualificar a robustez da desvantagem racial em 2022 por nível de cluster (`I-3-002`).
- [ ] Formular o mecanismo causal como associação compatível na introdução (`I-3-006`).
- [ ] Legendas descritivas nas três tabelas de magnitude e chave visual nas figuras Top-X (`I-3-007`).
- [ ] Justificar a escolha do arredondamento do NECr (`[3.2]`).
- [ ] Cortar a repetição da proporção de candidaturas efetivas (`[3.5-1]`).
