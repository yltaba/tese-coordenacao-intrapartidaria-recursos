# Tese — Coordenação da competição intrapartidária via fundos públicos

Repositório da tese de doutorado de Yuri Lucatelli Taba (Ciência Política, Brasil).
Idioma de trabalho: **português (pt-BR)**. Toda saída de agente de revisão é escrita em pt-BR.

## Mapa do repositório

| Caminho | O que é |
|---|---|
| `tese/*.qmd` | Capítulos (Quarto book). `02-literatura`, `03-medindo-coordenacao-intrapartidaria` (Cap. 3), `04-mecanismo-causal-coordenacao` (Cap. 4). |
| `tese/03-formulas-propostas.qmd` (removida em 14/09/2026; pode voltar) | Nota formal do Cap. 3: reescreve as fórmulas para bater com o código e lista divergências texto × implementação. |
| `tese/references.bib` | Bibliografia (chaves `@cheibubsin2020`, `@laaksotaagepera1979`, `@thomsen2023`, `@fivaetal2024`, `@silvacodato2024`, `@cox1972` …). |
| `src/1_silver/gerar_rrd.py` | Constrói a base de candidaturas `rrd_df_novo.parquet`: histórico eleitoral, flags de competitividade, quociente eleitoral, recursos partidários. |
| `src/2_gold/cap3_*.py` | Cálculo das medidas do Cap. 3. Núcleo: `cap3_cobertura_top_necr.py` (NECr, k, cobertura), `cap3_cs_features.py` (definição de competitivo, tipo de partido), `cap3_taa_features.py` (`acertos_fracionarios`, empates), `cap3_survival_features.py` (Cap. 4). |
| `data/processed/` | Bases. `rrd_df_novo.parquet` (candidaturas 2014/2018/2022), `df_cobertura_top_necr_lista.parquet` e `df_cobertura_top_necr_resumo.csv` (Top-NECr por lista e nacional), `df_cox_survival.parquet` (Cox, Cap. 4; **output do modelo, não input** — regenerar via `tese/scripts/regenerar_figuras_cap4.py` sempre que `rrd_df_novo.parquet` mudar, senão fica desatualizado como ficou entre 19/06/2026 e 17/09/2026), `bancada_partido_uf.csv` (Mp). |
| `tese/reports/resultados-capitulo-3/` | Tabelas auditadas do Cap. 3 (`00_sintese.csv` … `26_fontes.csv`). **`19_notas_redacao.csv` lista divergências texto × código já conhecidas; `21_verificacoes.csv` lista checagens automáticas.** |
| `tese/reports/lift-magnitude-partido/` | *Lift* do Top-NECr por magnitude (`lift_por_magnitude.csv`, fonte das tabelas `tbl-cap3-01`/`tbl-cap3-02`) e por partido. |
| `tese/reports/regressao-fracionaria/` | AMEs (`ames.csv`), coeficientes e razões exp(β) (`coeficientes.csv`) razão da credencial por magnitude (`interacao_magnitude.csv`, fora da figura) e filtros de amostra (`amostra.csv`) do modelo fracionário de "prêmio" das credenciais eleitorais (`sec-premio-credenciais`). Desde 18/09/2026 é **intralista** (logit fracionário condicional, EF de lista; modelos R1 = flag `candidato_competitivo`, R2 = contagens por cargo); a versão de 16–17/09 (GLM agrupado com ln magnitude) fica só no git. Desde 19/09/2026 (I-3-001 do run-002) a parcela mantém o `R_l` da lista completa e a média é `m_l·p_il` (m_l = massa retida após exclusões) na Hessiana, escores e AMEs; a renormalização entre retidas é sensibilidade (`sensibilidade_massa.csv`). |
| `tese/reports/` | Só resultados em uso pela versão atual (limpo em 16/09/2026; versões anteriores — Top-X%/validações/alternativas/explorações com a definição pré-correção de competitivo — ficam apenas no histórico do git). |
| `tese/scripts/` | `regenerar_figuras_cap3.py` (único gerador das figuras de Top-NECr, Top-X%, amplitude e concentração do Cap. 3; também é a fonte dos números de Top-X%), `regressao_fracionaria_cap3.py` (logit fracionário condicional — softmax na lista, equivalente a PPML com EF de lista — do prêmio de credenciais eleitorais, `fig-reg-frac`; ver `notes/tecnico/cap3-plano-regressao-intralista.md`), `resultados_capitulo3.py` (gera `resultados-capitulo-3/`), `render_capitulos.py`, `regenerar_figuras_cap4.py` (único gerador das figuras de *timing*/KM/fluxo cumulativo do Cap. 4; requer `data/raw/finanças/receitas_candidatos_*` para 3 das 4 figuras). |
| `tese/reports/bootstrap-lift-cap3/` | IC 95% bootstrap (listas e, como sensibilidade, partidos; B=2000, seed 42) de cobertura, precisão e *lift* do Top-NECr no Cap. 3, nacional e por magnitude, para competitivos e eleitos (`ic_metricas.csv`), e das diferenças 2018−2022 e Grande−Pequeno (`ic_diferencas.csv`). Gerado por `tese/scripts/bootstrap_lift_cap3.py`. |
| `tese/reports/lift-semanal/` | Lift do Top-NECr semana a semana (Cap. 4): `lift_semanal.csv` (lift, IC bootstrap, cobertura, precisão por eleição × semana) e `reconciliacao.csv` (última semana × Cap. 3). Gerado por `src/2_gold/cap4_lift_semanal.py` via `regenerar_figuras_cap4.py --so-lift`; figura `figs/cap4_lift_semanal.png` (`fig-lift-semanal`). |
| `figs/` | PNGs referenciados pelos capítulos (`cap3_*`, `cap4_*`). Cap. 3: `cap3_fig_top_necr.png` (Resultados), `cap3_fig_top_necr_eleicao.png`, `cap3_fig_topx_*.png` (Robustez), `cap3_regressao_fracionaria.png` (prêmio das credenciais, `fig-reg-frac`). Cap. 4: `cap4_survival_km_primeiro.png`/`cap4_survival_km_maior.png` (Kaplan-Meier), `cap4_fluxo_cumulativo_prop.png`/`cap4_fluxo_cumulativo_abs.png` (fluxo cumulativo) — desde 17/09/2026 só por candidato competitivo/não-competitivo (o corte por tipo de partido foi removido, era exploratório). |
| `notes/daily/` | Diário de decisões do autor. |
| `revisoes/` | Versões renderizadas e anteriores dos capítulos. |
| `thesis-review/` | **Sistema de revisão por agentes.** Estado persistente: rubrica, ledger de afirmações, runs, fila de revisão. |

## Objetos centrais da tese (vocabulário)

- **Lista / nominata** `l`: partido × UF × eleição. Candidatura `i` dentro da lista.
- **Recursos partidários** `R_il`: `vr_receita_recursos_partidos` (origem "Recursos de partido político"; não é filtrado por fonte FEFC/FP).
- **NECr**: número efetivo de candidaturas em recursos, `1/Σ s²`, só definido se `R_l > 0`.
- **Top-NECr**: núcleo priorizado; `k_l = floor(NECr + 0,5)`; empates na fronteira recebem peso fracionário (`acertos_fracionarios`).
- **Top-X%**: menor conjunto do topo que acumula τ ∈ {50,…,95}% dos recursos (robustez).
- **Competitivo (ex-ante)**: `candidato_competitivo` = vitória prévia (exceto vereador) OU ≥10% do QE em disputa anterior. `candidato_forte_cs` é a versão ex-post de Cheibub & Sin; **não** deve ser usada nas análises.
- **Cobertura / Precisão / Lift**: razões de somas nacionais; referência aleatória analítica `G_l·k_l/C_l` (hipergeométrica). Lift de cobertura ≡ lift de precisão no agregado.
- **Mp**: bancada pré-eleitoral do partido na UF. **Tipo de partido**: competitivo se ≥ 20 cadeiras nacionais.
- Cap. 4: *timing* dos repasses; Kaplan-Meier; Cox PH (`df_cox_survival.parquet`), HR. **Todos os cálculos usam a origem "Recursos de partido político", independentemente da fonte**, dentro da janela de campanha (decisão do autor em 19/09/2026). Usar `selecionar_receitas_partido` de `cap3_survival_features.py`; não filtrar por `FONTES_PARTIDO`/FEFC+FP. Em 2018, normalizar PATRIOTA → PATRI nas receitas. O gerador oficial recalcula o primeiro repasse na cópia de trabalho (a base RRD contém 218 falsos censurados dessa legenda); por isso **todas as cinco figuras e o Cox agora requerem os CSVs brutos**. `regenerar_figuras_cap4.py` salva também o fluxo em `tese/reports/fluxo-semanal/` e a conferência do primeiro repasse e dos totais em `tese/reports/harmonizacao-cap4/`. A diferença residual de recursos em relação ao Cap. 3 deve ser integralmente explicada pelos registros fora da janela; ver `tese/reports/harmonizacao-cap4/README.md`.

## Ambiente

Python 3.13 com pandas 2.2, numpy, pyarrow. Os agentes **podem e devem** recomputar números a partir de `data/processed/` quando isso decidir uma dúvida (use `python -c` ou scripts em `thesis-review/runs/<run>/evidence/`). Não rodar `gerar_rrd.py` (pesado e reconstrói a base).

## Sistema de revisão (`thesis-review/`)

Leia `thesis-review/PROTOCOL.md` e `thesis-review/rubric.yaml` antes de qualquer revisão. Resumo:

1. **Revisor ≠ autor.** Agentes de revisão **nunca editam** `tese/*.qmd`, `src/` ou `data/`. Escrevem apenas em `thesis-review/`.
2. **Regra de ouro.** Nenhuma crítica substantiva sem apontar o objeto que a sustenta: passagem citada literalmente + arquivo/linha, tabela, CSV, figura ou recomputação.
3. **Contrato > persona.** Cada agente tem escopo fechado e formato de saída fixo (ver `.claude/agents/`).
4. **Duas escalas.** Pass 1 (macro: pergunta → teoria → hipótese → desenho → medida → resultado → conclusão) antes de Pass 2 (micro: parágrafo, número, figura, citação).
5. **Fluxo de um run**: especialistas em paralelo → chair (agrupa/deduplica) → adversarial (tenta derrubar) → chair (arbitra, `final_review.md`, `issues.yaml`, `priority_queue.yaml`).
6. **Runs são numerados** (`thesis-review/runs/run-NNN/`) e comparáveis; `thesis-review/history.md` registra a evolução.

Comandos: `/review-ch3`, `/review-chapter <n>`, `/synthesize-review <run>`, `/adversarial-review <run>`, `/review-claim <id>`, `/review-diff <runA> <runB>`.
