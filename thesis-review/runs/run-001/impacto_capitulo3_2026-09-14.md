# Impacto das correções I-3-002 e I-3-001 nos números do Capítulo 3

Compara cada número do capítulo que depende de `candidato_competitivo` (Deputado Federal, 2018 e
2022) antes e depois das correções de código de 2026-09-14 (I-3-002; I-3-001 D1+D2+D3 — ver
`implementacao_2026-09-14.md`). "Original" = base antes de qualquer correção
(`data/processed/archive/pre-i3-002_2026-09-14/rrd_df_novo.parquet`); "Atual" =
`data/processed/rrd_df_novo.parquet` (todas as correções aplicadas).

**Método.** As linhas marcadas ✅ **verificado** foram recomputadas com a mesma fórmula do
capítulo (Seção "Cobertura, precisão e lift", @eq-indicadores) diretamente sobre a base, e o valor
"Original" reproduziu exatamente o número já publicado no `.qmd` — confirma que a fórmula usada
aqui é a mesma do capítulo. As linhas marcadas ⚠️ **aproximado** não reproduziram exatamente o
número publicado ao recomputar diretamente (provável diferença de universo/script que não foi
localizado); a direção da mudança é confiável, o valor exato não. As linhas marcadas ⏳ **não
recomputado** dependem de pipelines não executados nesta rodada (ver §4 de
`implementacao_2026-09-14.md`).

## 1. Universo de competitivos (l. 115)

> "Dos 7.630 candidatos a Deputado Federal em 2018, 886 (11,6%) foram classificados como
> 'competitivos'... Em 2022, foram 9.675 candidaturas com 1.287 (13,3%) competitivas... o total de
> competitivas cresceu 45% no período."

✅ **verificado** (reproduz exatamente 886/1.287 na base original)

| | 2018 | 2022 |
|---|---|---|
| Original | 886 / 7.630 (11,61%) | 1.287 / 9.675 (13,30%) |
| **Atual** | **973 / 7.630 (12,75%)** | **1.354 / 9.675 (13,99%)** |
| Crescimento 2018→2022 | 45,3% | **39,2%** |

O total de candidatos lançados (27%) não muda — não depende de `candidato_competitivo`.

## 2. Amplitude por lista, só competitivos (l. 117)

> "Em 2018 e 2022, a mediana de candidaturas competitivas por lista é igual a um candidato. A
> média, respectivamente, é de 1,11 e 1,98 candidato."

✅ **verificado** (média reproduz exatamente 1,11/1,98 na base original, listas com recursos > 0)

| | 2018 | 2022 |
|---|---|---|
| Mediana (financiadas) | 1 (Original e Atual) | 1 (Original e Atual) |
| Média (financiadas), Original | 1,113 | 1,980 |
| **Média (financiadas), Atual** | **1,223** | **2,086** |

A mediana não muda; só a média.

## 3. Top-NECr × competitivos: cobertura, precisão, lift (l. 139-143, @fig-cap3-03-top-necr)

> "Entre as candidaturas com credenciais eleitorais prévias, mais de 80% compõem o núcleo... cobre
> 4/5 dos candidatos classificados como competitivos... referência: 43,2 e 43,7%... A precisão...
> 30,9 e 27,8%... Um núcleo... conteria 16,5 e 14,7% de competitivos... *lift*... 1,87 em 2018 e
> 1,89 em 2022."

✅ **verificado** (reproduz exatamente os cinco números da base original: cobertura, referência
aleatória, precisão, precisão aleatória e lift, nos dois anos)

| Indicador | 2018 Original | 2018 Atual | 2022 Original | 2022 Atual |
|---|---|---|---|---|
| Cobertura (%) | 80,90 | **80,86** | 82,68 | **80,89** |
| Cobertura aleatória (%) | 43,19 | **42,76** | 43,75 | **43,60** |
| Precisão (%) | 30,92 | **33,94** | 27,83 | **28,64** |
| Precisão aleatória (%) | 16,51 | **17,95** | 14,72 | **15,44** |
| **Lift** | **1,873** | **1,891** | **1,890** | **1,855** |

**Leitura.** A afirmação central sobrevive sem qualificação: cobertura continua acima de 80%
(ainda "cerca de 4/5") nos dois anos; lift continua entre 1,85 e 1,89 (o padrão "perto de 1,9" que
a l. 173 já generaliza como "sempre superior a um" permanece válido). A maior mudança é 2022, cuja
cobertura cai de 82,7% para 80,9% — a diferença entre 2018 e 2022 (que a revisão discute em
I-3-004) fica ainda mais parecida depois da correção, não menos.

## 4. Top-X% × competitivos (l. 157-161, @fig-cap3-04-topx-competitividade)

> "Mesmo no Top-95%, o corte mais permissivo calculado, ele [o lift] é 1,53 em 2018 e 1,38 em
> 2022."

✅ **verificado** (τ = 95%; reproduz exatamente 1,53/1,38 na base original)

| | 2018 | 2022 |
|---|---|---|
| Lift Top-95%, Original | 1,53 | 1,38 |
| **Lift Top-95%, Atual** | **1,55** | **1,37** |
| Cobertura Top-95%, Original | 86,97% | 93,18% |
| **Cobertura Top-95%, Atual** | **87,32%** | **92,66%** |

Não recomputados os demais limiares (50-90%) nem os painéis por magnitude da @fig-cap3-04; a
variação no limiar mais permissivo (95%) é pequena e nas duas direções, o que sugere que os
demais limiares também mudam pouco, mas isso não está confirmado.

## 5. Cotas de gênero e competitividade (l. 179)

> "Em 2018, 4,68% das mulheres no universo são classificadas como competitivas, contra 15,83% dos
> homens; em 2022, as proporções são 5,79% e 17,20%, respectivamente."

⚠️ **aproximado** — a recomputação direta (mesma base original, `mulher == 1`/`0`, universo
completo) deu 4,47%/14,93% (2018) e 5,96%/17,29% (2022), próximo mas não igual ao publicado
(4,68%/15,83%; 5,79%/17,20%). A diferença (0,1-0,9 p.p.) sugere que o script original usa um
recorte ou tratamento de `NaN` ligeiramente diferente que não foi localizado nesta rodada. Direção
e ordem de grandeza da mudança são o que se pode afirmar com confiança:

| | 2018 mulheres | 2018 homens | 2022 mulheres | 2022 homens |
|---|---|---|---|---|
| Original (recomputado, aproximado) | 4,47% | 14,93% | 5,96% | 17,29% |
| **Atual (recomputado, aproximado)** | **4,84%** | **16,42%** | **6,08%** | **18,31%** |

Ambos os grupos sobem de forma parecida (mulheres +0,3/+0,1 p.p.; homens +1,5/+1,0 p.p.); a razão
mulher/homem (o ponto do parágrafo — mulheres muito menos competitivas) não se altera
qualitativamente. Recomenda-se conferir com o script original antes de publicar um número exato.

## 6. Não recomputado nesta rodada

- **@fig-cap3-05-topx-eleicao** (l. 165): usa o resultado eleitoral (`eleito`) como referência, não
  `candidato_competitivo` — a variável `eleito` não depende das correções de 2026-09-14, então a
  figura em princípio não muda. Isto foi confirmado para a cobertura/precisão/lift do Top-NECr
  (`cap3_cobertura_top_necr.py` usa só `eleito`); não foi confirmado para o pipeline específico que
  gera a figura 05 (Top-X% × eleitos), que não foi localizado/executado nesta rodada.
- **@fig-amplitude** (`figs/cap3_fig_amplitude_barras.png`, l. 117): a figura em si (só os números
  de texto acima foram recomputados à parte).
- Painéis por magnitude/tipo de partido nas @fig-cap3-03/04 (só os totais nacionais foram
  recomputados aqui).

## 7. Síntese para a redação

Nenhuma correção do texto é urgente por invalidar o argumento — o núcleo do capítulo (partidos
priorizam candidaturas competitivas e eleitas muito além do acaso) sobrevive com folga em todas as
métricas recomputadas. O que precisa de atualização são os números específicos:

- l. 115: `886 (11,6%)` → `973 (12,75%)`; `1.287 (13,3%)` → `1.354 (13,99%)`; `cresceu 45%` →
  `cresceu ~39%`.
- l. 117: `1,11 e 1,98` → `1,22 e 2,09` (mediana continua `um`).
- l. 139: `mais de 80%` continua correto; `43,2 e 43,7%` → `42,8 e 43,6%`.
- l. 141: `30,9 e 27,8%` → `33,9 e 28,6%`; `16,5 e 14,7%` → `17,9 e 15,4%`.
- l. 143: `1,87 em 2018 e 1,89 em 2022` → `1,89 em 2018 e 1,86 em 2022`.
- l. 159: `1,53 em 2018 e 1,38 em 2022` → `1,55 em 2018 e 1,37 em 2022` (conferir os demais
  limiares antes de trocar).
- l. 179: manter cautela — os quatro percentuais mudam, mas o valor exato não foi confirmado
  (ver §5).

Estas trocas são independentes de I-3-004 (síntese "1,9") e das demais issues MODERATE/MINOR da
fila, que continuam pendentes.
