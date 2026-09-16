# Implementação — I-3-002 e I-3-001 (run-001)

Registro do que foi feito em código/dados fora do fluxo de revisão (autor, não agente de
revisão), seguindo a ordem 1-2 de `priority_queue.yaml`. Ver também
`thesis-review/revisions/accepted_changes.md` (registro curto, usado por `/review-diff`) e
`thesis-review/runs/run-001/impacto_capitulo3_2026-09-14.md` (efeito nos números do capítulo).

Data: 2026-09-14. Não houve novo run de revisão (não há run-002); isto documenta a implementação
das recomendações do run-001, não uma nova rodada de avaliação.

## 1. I-3-002 — critério (ii) de "competitivo" restrito a disputa proporcional

**Decisão do autor:** seguir a recomendação (l. 68 do capítulo — 10% do quociente eleitoral só em
disputa proporcional Dep. Federal/Dep. Estadual).

**Código.** `src/1_silver/gerar_rrd.py::adicionar_alcancou_10pct_qe_hist`: `CARGOS_FORTE` e
`UF_CARGOS` reduzidos de `[DEPUTADO FEDERAL, DEPUTADO ESTADUAL, GOVERNADOR, SENADOR, PREFEITO]`
para `[DEPUTADO FEDERAL, DEPUTADO ESTADUAL]`. Removido o ramo de cálculo do QE municipal
(Prefeito, `qt_vaga = 1`). O critério (i) (vitória prévia) não foi alterado.

**Dados.** `data/processed/rrd_df_novo.parquet` recomputado (só as colunas
`alcancou_10pct_qe_hist`/`_nom`) sem rodar o pipeline pesado `gerar_rrd.py::main()` — script
ad-hoc que reaplica a função corrigida sobre os insumos já processados. `qt_vaga` histórico de
Dep. Federal/Estadual foi reconstruído a partir dos eleitos em `resultados.parquet` (todas as
vagas proporcionais são sempre preenchidas), porque `data/raw/vagas/` não está disponível neste
ambiente; validado sem divergência (0/189) contra `vagas_deputado_federal.parquet`.

**Backup:** `data/processed/archive/pre-i3-002_2026-09-14/rrd_df_novo.parquet` (base original).

## 2. I-3-001 — ligação de CPF (D1, D2, D3)

**Decisão do autor:** implementar as três correções recomendadas, em dois passos.

### 2.1 D2 — zfill no CPF de 2012/2014

**Código.** Nova função `gerar_rrd.py::_normalizar_cpf` (zfill(11), preservando sentinelas
`-1`/`-4`), aplicada em `carregar_dados()` logo após ler `candidatos.parquet`.

**Dados.** Recomputadas `n_eleicoes_*` (via `adicionar_historico_eleitoral`) e
`alcancou_10pct_qe_hist*` (via `adicionar_alcancou_10pct_qe_hist`, já com o critério de I-3-002),
sobre a base já corrigida para I-3-002.

**Backup:** `data/processed/archive/pre-i3-001-d2-zfill_2026-09-14/rrd_df_novo.parquet`.

**Checagem do próprio achado:** dos 378 deputados federais eleitos em 2014 que concorreram em
2018, os que tinham `n_eleicoes_deputado_federal = 0` na base (52 antes da correção) e os não
competitivos (25 antes) foram reduzidos — a correção completa só fecha com D1/D3 (§2.2).

### 2.2 D1 + D3 — chave de ligação por cargo/município e desempate pelo registro APTO

**Código.** Novas funções em `gerar_rrd.py`: `_chave_cargo_municipio`, `_texto_ascii` (normaliza
acento, vetorizado), `_preparar_candidatos_cpf` e `ligar_cpf`. Substituem os três
`drop_duplicates(["ano_eleicao","sg_uf","nr_candidato"], keep="first")` em `construir_base`,
`_construir_resultados_select` e `_gerar_resultados_cpf`. A chave agora é (ano, UF, cargo, número)
para cargos de UF e (ano, UF, cargo, município, número) para Prefeito/Vice-Prefeito/Vereador
(`CARGOS_MUNICIPAIS`). Quando há mais de um CPF sob a mesma chave (substituição de candidato),
prioriza `ds_situacao_candidatura == "APTO"` em vez do primeiro registro do arquivo.

**Dados.** Recomputados, nesta ordem: identidade da candidatura de Dep. Federal
(`nr_cpf_candidato`, `ds_genero`, `ds_cor_raca`, `mulher`, `negra`, via `construir_base`) →
`n_eleicoes_*` (via `_construir_resultados_select` + `adicionar_historico_eleitoral`) →
`alcancou_10pct_qe_hist*` (via `_gerar_resultados_cpf` + `adicionar_alcancou_10pct_qe_hist`).

**Backup:** `data/processed/archive/pre-i3-001-d1d3_2026-09-14/rrd_df_novo.parquet`.

**Checagens do próprio achado, confirmadas:**
- Dos 378 deputados federais eleitos em 2014 que concorreram em 2018: **377/377** contam como
  competitivos (era 353/378 na base original; a recomendação previa "hoje 353/378", meta 378/378).
- "2022 MG AVANTE 7025": 46 → **1** vitória de prefeito (era o exemplo citado do defeito D1).
- Os 3 casos de identidade trocada citados na revisão têm CPF/gênero corrigidos: 2022 AM 4444
  (Pauderney Avelino, FEMININO→MASCULINO), 2022 DF 4545 (Andréia Zemuner, MASCULINO→FEMININO),
  2022 CE 1251 (José Arnon Bezerra, CPF trocado).
- 24 (2018) e 24 (2022) candidaturas de Dep. Federal tiveram CPF de fato distinto por D3 (a
  revisão havia contado 61/76 grupos com >1 CPF em `candidatos.parquet`; o número menor aqui é só
  as candidaturas cujo CPF resultante mudou depois do desempate por APTO).

**Residual conhecido, não corrigido:** o casamento de município usa normalização de acentos
(NFKD), mas não recupera nomes já corrompidos na origem (mojibake, caractere de substituição
`�`) em ~0,7% das linhas de Prefeito entre 2012-2022 (ex.: "OLHO D'ÁGUA..."). Essas poucas
candidaturas municipais ficam sem CPF ligado (tratadas como sem histórico ali, não como ligação
errada — falha segura, não silenciosa).

## 3. Atualização de 2026-09-14 (mesmo dia): texto e figuras

O autor atualizou o texto do capítulo usando `impacto_capitulo3_2026-09-14.md` (l. 115, 117, 127,
139, 141, 143, 157-161 corrigidas; l. 177/quotas por gênero deixada como estava, corretamente,
porque o relatório marcava aquele número como não confirmado). Em seguida foram regeneradas as 5
figuras do capítulo que dependem de `candidato_competitivo`:

- `figs/cap3_fig_amplitude_barras.png`, `figs/cap3_fig_concentracao_barras.png`
- `tese/reports/relatorio-consolidado-capitulo-3/figuras/03-top-necr.png`,
  `04-topx-competitividade.png`, `05-topx-eleicao.png`

**Decisão do autor:** em vez de consertar a cadeia legada (`tese/reports/resultados-exploracao-
nucleo` → `alternativas-top-necr` → `sensibilidade-top-x` → `relatorio-consolidado-capitulo-3/
construir.py` — caminhos obsoletos da reorganização de 14/09 e asserts de regressão com os
números antigos), optou por um gerador novo e direto: `tese/scripts/regenerar_figuras_cap3.py`,
que recomputa da base (mesma fórmula do capítulo) e reproduz o leiaute/cores das figuras
originais sem depender da cadeia legada. Números conferidos batendo com
`impacto_capitulo3_2026-09-14.md` (screenshots revisados manualmente).

Backup das figuras anteriores: `tese/reports/old/rascunhos/figuras-cap3-pre-correcoes_2026-09-14/`.

Corrigidos também 3 caminhos de imagem obsoletos no `.qmd` (referenciavam
`relatorio-consolidado-capitulo-3/...` sem o prefixo `reports/`, e sem `../tese/` — necessário
porque `tese/scripts/render_capitulos.py` renderiza a partir de `revisoes/`, fora de `tese/`).
PDF renderizado com sucesso: `revisoes/2026-09-14_03-medindo-coordenacao-intrapartidaria.pdf`.

**Ainda não regenerado/tocado:**
- Os CSVs/painéis da cadeia legada (`sensibilidade-top-x`, `alternativas-top-necr`,
  `resultados-exploracao-nucleo`, `resultados-validacao-top-necr`) — as figuras que dependiam
  deles foram substituídas pelo gerador direto, mas esses CSVs continuam com os números antigos
  e os caminhos obsoletos, e não foram usados nesta atualização.
- **Cap. 4** (`src/2_gold/cap3_survival_features.py`, covariável `candidato_competitivo` do Cox)
  também é afetado (a mesma flag), mas não foi tocado.
- **I-3-004** (síntese "1,9") e as demais issues MODERATE/MINOR da fila (`priority_queue.yaml`,
  ordem 3+) seguem abertas; várias delas (`depende_de: [I-3-001]`) agora estão desbloqueadas:
  I-3-005, I-3-006, I-3-011, I-3-012, I-3-015, I-3-016, I-3-018.

## 4. Regenerado (auditado)

`tese/reports/resultados-capitulo-3/` (00-26 CSVs + HTML + `verificacao.json`), via
`tese/scripts/resultados_capitulo3.py` — corrigido também o caminho de saída, que apontava para
`tese/resultados-capitulo-3/` (pasta que não existe mais após a reorganização de 14/09). Rodado
três vezes (após I-3-002; após D2; após D1+D3), com backup de cada versão anterior em
`tese/reports/old/rascunhos/resultados-capitulo-3-pre-*_2026-09-14/`. As 9 verificações internas
do script passaram nas três rodadas.
