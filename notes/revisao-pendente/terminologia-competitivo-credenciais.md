# Terminologia: "candidatura competitiva" → "candidatura com credenciais eleitorais prévias"

Varredura de 19/09/2026 em `tese/*.qmd` (linhas conforme a árvore de trabalho nesta data).
Objetivo: localizar onde o texto ainda chama de "competitivo/competitiva" o grupo definido por
`candidato_competitivo` (vitória prévia, exceto vereador, OU ≥10% do QE em disputa anterior), que
a tese hoje chama de **candidaturas com credenciais eleitorais prévias**.

Esta nota não traz frases de substituição. Nos casos simples a troca é de termo; nos demais,
só aponto o problema.

## Critério de triagem

| Tipo de ocorrência | Ação |
|---|---|
| "competitivo(a/s)" = o indicador **da tese** (`candidato_competitivo`) | **Trocar** por "com credenciais (eleitorais prévias)" / "sem credenciais" |
| "competitivo" = conceito ou classificação **de @cheibubsin2020** (que inclui resultado da própria eleição) | **Manter.** É o termo dos autores, e a diferença para a medida da tese é justamente o argumento |
| "partidos (mais/menos) competitivos", "contexto competitivo", "vantagem competitiva", "eleição competitiva" | **Manter.** É outro conceito, fora do escopo desta troca |
| Rótulos Quarto (`#sec-competitivos`, `#eq-competitivo`, …) e nomes de arquivo | Opcional: não aparecem no texto renderizado |
| Dentro de `<!-- -->` (notas de revisão, rascunhos de Introdução e Considerações finais) | Fora do corpo. Não entra na contagem |

## Resumo

| Arquivo | Trocas no corpo | Ocorrências a manter | Observação |
|---|---|---|---|
| `01-introducao.qmd` | 0 | – | O texto está todo em comentário (l. 18–52) e já usa "credenciais" |
| `02-literatura.qmd` | 0 | 9 | Todas se referem a C&S, a partidos ou ao contexto. Só há o rótulo `@sec-competitivos` (l. 202) |
| `03-medindo-coordenacao-intrapartidaria.qmd` | **~24 em 15 parágrafos/nota + tabela** | 2 (l. 39 e l. 74, esta a decidir) | Concentra o problema. A nota de rodapé que declara os termos intercambiáveis precisa ser reavaliada |
| `04-mecanismo-causal-coordenacao.qmd` | **~24 em 7 parágrafos + 2 legendas** | 0 | Texto e legendas dizem "competitivos"; as figuras já dizem "Com/Sem credencial eleitoral prévia" |
| `05-consideracoes-finais.qmd` | 0 | – | O texto está em comentário (l. 19–53) e já usa "credenciais" |
| `apendice-a-formalizacao.qmd` | **1 (equação)** | – | $\text{Competitivo}_{iy}$ aparece renderizado e diverge da notação $g_{il}$ |
| Figura `cap3_fig_amplitude_barras.png` | **1 rótulo** | – | Eixo "Candidaturas competitivas". Precisa regenerar |

---

## 1. Capítulo 3 — `tese/03-medindo-coordenacao-intrapartidaria.qmd`

### 1.1 Definição (seção `sec-competitivos`). Resolver isto primeiro

- **l. 35**: "propõe-se um indicador binário que classifica uma *candidatura competitiva*[^…-1], mas o faz considerando algum sinal positivo de desempenho anterior."
  → A frase apresenta o indicador como uma variante de "competitiva". Se o termo único passa a ser
  "credencial", a frase precisa ser reestruturada, não só ter o termo trocado. **Reescrever (autor).**
  Vale manter uma única menção explícita de que o indicador adapta a noção de "competitivo" de
  @cheibubsin2020. Isso liga o termo ao nome da variável no código (`candidato_competitivo`) e à literatura.
- **l. 37, nota de rodapé**: "os termos 'candidaturas com credenciais eleitorais prévias' e 'candidaturas competitivas' se referem ao mesmo conjunto de concorrentes e são usados de maneira intercambiada."
  → Com a padronização, a nota deixa de valer do jeito que está. **Remover ou reescrever (autor).**
  O comentário já existente em `02-literatura.qmd:200`, item (d), pede o mesmo: definir "credencial" uma vez.
- **l. 39**: "Os autores consideraram também como **competitivos** os candidatos que atingiram…"
  → **Manter** (classificação de C&S).
  "…deliberadamente descarta-se como **competitivos** os candidatos novatos…"
  → **Trocar**. Aqui a classificação é da tese.

### 1.2 Descrição dos dados (amplitude)

- **l. 66**: "foram classificados como **"competitivos"** pelos critérios adaptados de @cheibubsin2020", "1.354 (13,99%) **competitivas**", "grupo de candidaturas **competitivas**", "o total de **competitivas** cresceu 39%"
  → **Trocar** as 4 ocorrências.
- **l. 68**: "a mediana de candidaturas **competitivas** por lista é igual a um candidato"
  → **Trocar**. A mesma passagem já diz "candidaturas com credenciais eleitorais prévias" na frase anterior.
- **l. 74**: "um afunilamento de candidatos **competitivos** segundo o histórico eleitoral"
  → **Trocar**: "segundo o histórico eleitoral" é a medida da tese.
  "ao lançarem poucas candidaturas **competitivas** em suas nominatas"
  → **Decidir.** A frase parafraseia o argumento de C&S, então o termo deles é defensável.
- **l. 76**: "o NECr seja maior que as candidaturas **competitivas** na média e mediana"
  → **Trocar**. Compara com o dado da tese (fig-amplitude).
- **l. 82**: "quando se considera a **competitividade prévia**"
  → **Trocar** por "credenciais eleitorais prévias".
- **Figura `fig-amplitude`** (`figs/cap3_fig_amplitude_barras.png`): o eixo diz "Candidaturas competitivas".
  → A origem é `tese/scripts/regenerar_figuras_cap3.py:116`, `("F", "Candidaturas\ncompetitivas")`.
  Trocar o rótulo e rodar o gerador de novo. É alteração de script, portanto decisão do autor.

### 1.3 Resultados do Top-NECr

- **l. 88**: "Entre as candidaturas **competitivas**, mais de 80%…", "cobre 4/5 dos candidatos classificados como **competitivos**", "parte majoritária dos candidatos **competitivos**"
  → **Trocar** as 3.
- **l. 90**: "estão entre os classificados como **competitivos**", "conteria 17,9 e 15,4% de **competitivos**"
  → **Trocar** as 2.
- **l. 94**: "quase 90% mais candidaturas **competitivas** do que seria esperado ao acaso"
  → **Trocar**.
- **l. 123, cabeçalho de `tbl-cap3-01-lift-magnitude`**: `| Magnitude | Competitivos 2018 | Competitivos 2022 |`
  → **Trocar** (aparece renderizado). A legenda da tabela está vazia (`: {#tbl-cap3-01-lift-magnitude}`),
  então o cabeçalho é o único lugar onde o leitor vê o que o *lift* mede.

### 1.4 Robustez (Top-X%)

- **l. 214**: "cobertura do núcleo priorizado entre os candidatos classificados como **competitivos**", "acabam selecionando mais candidatos **competitivos** também"
  → **Trocar** as 2.
- **l. 216**: "candidaturas previamente definidas como **competitivas**"
  → **Trocar**.
- **l. 218**: "Sistematicamente há mais candidaturas **competitivas** dentro do núcleo priorizado"
  → **Trocar**.
- **l. 222**: "do que quando se considera as candidaturas **competitivas** como referência"
  → **Trocar**.
- A legenda da figura na l. 220 já diz "credenciais eleitorais prévias". Os rótulos internos das
  figuras Top-NECr e Top-X% não mencionam "competitivo".

### 1.5 Opcional (não aparece renderizado)

- `{#sec-competitivos}` (l. 33): referenciado em `02-literatura.qmd:202`, `03-…:150` e `01-introducao.qmd:38` (este em comentário). Renomear exige atualizar todas as referências.
- `{#fig-cap3-04-topx-competitividade}` e o arquivo `figs/cap3_fig_topx_competitividade.png` (l. 214, 220): renomear exige mudar também `regenerar_figuras_cap3.py:359`.
- Comentários de revisão que citam "competitivo" (l. 43, 113, 132, 164) ficam fora do corpo.

---

## 2. Capítulo 4 — `tese/04-mecanismo-causal-coordenacao.qmd`

Todo o capítulo ainda compara "competitivos × não-competitivos (ex-ante)". As figuras, porém, já
foram regeneradas com as legendas **"Com credencial eleitoral prévia" / "Sem credencial eleitoral prévia"**
(`regenerar_figuras_cap4.py:63–65`). Hoje, portanto, **o texto e as legendas não batem com o que a figura mostra**.

- **l. 21** (fig-semana-campanha): "distinguindo candidatos **competitivos** de **não-competitivos** (ex-ante)", "mais acentuado para candidaturas **competitivas**", "entre os concorrentes **não-competitivos**"
  → **Trocar** as 4. Com "credenciais prévias", o "(ex-ante)" fica redundante (avaliar).
- **l. 23**: "candidatos **competitivos** já acumulam 21,8%", "ante 11,6% dos **não-competitivos**", "contra 39,8% dos **não-competitivos**", "favorável aos **competitivos**"
  → **Trocar** as 4.
- **l. 27** (fig-semana-abs): "candidatos **competitivos** tiveram um salto", "entre os **não-competitivos**" (2×), "O acréscimo entre os **competitivos**"
  → **Trocar** as 4.
- **l. 29**: "para candidatos **competitivos**", "pelos **não-competitivos**", "antecipação para candidaturas **competitivas**"
  → **Trocar** as 3.
- **l. 53** (Kaplan-Meier): "candidaturas **competitivas** e **menos competitivas**"
  → **Trocar**. Além do termo, "menos competitivas" sugere uma gradação que não existe: o indicador é binário.
- **l. 55**: "recursos para candidaturas **competitivas**", "um candidato **competitivo**", "entre os **não-competitivos**", "entre **competitivos** e **não-competitivos**"
  → **Trocar** as 5.
- **l. 57, legenda de `fig-km-cs`**: "por grupo de **competitividade** (ex-ante)"
- **l. 59, legenda de `fig-km-maior-cs`**: "por grupo de **competitividade** (ex-ante)"
  → **Trocar** nas duas legendas (a figura mostra "Com/Sem credencial eleitoral prévia").
- **l. 65** (transição para Cox): "recursos controlados pelos partidos para candidaturas **competitivas**"
  → **Trocar**.
- A seção do *lift* semanal (l. 31 em diante, em comentário) e o eixo de `fig-lift-semanal` já usam "credenciais".
- Opcional: os rótulos `fig-km-cs` e `fig-km-maior-cs` carregam o sufixo "-cs" (Cheibub & Sin). Não aparecem renderizados.

---

## 3. Apêndice — `tese/apendice-a-formalizacao.qmd`

- **l. 48–53**: a seção "Credenciais eleitorais prévias" define
  $\text{Competitivo}_{iy} = 1$ se, antes de $y$, $i$ satisfez (i) ou (ii).
  → O nome aparece renderizado. **Trocar.** Além disso, a notação diverge do resto do apêndice: a l. 27 define o mesmo indicador como $g_{il}$,
  que é o símbolo usado em $G_l$ e $H_l$ (l. 60), e os índices diferem ($iy$ × $il$). Vale unificar em
  um único símbolo. O rótulo `#eq-competitivo` (l. 53, citado nos comentários das l. 11 e 19) é opcional.
- Observação lateral: a l. 27 diz "credenciais eleitorais prévias estabelecidas **na seção anterior**", mas no apêndice a seção de credenciais (l. 45) vem **depois** de "Notação". A definição de (i)/(ii), por sua vez, está no Cap. 3 (l. 35).

---

## 4. Capítulo 2 — `tese/02-literatura.qmd` (nada a trocar)

Conferido. Todas as ocorrências no corpo usam "competitivo" em outro sentido:

| Linha | Trecho | Por que manter |
|---|---|---|
| 45 | "contexto competitivo" | Contexto eleitoral (Marsh) |
| 61 | "número de candidaturas competitivas próximo ao número de cadeiras" | Achado de @cheibubsin2020, no termo dos autores |
| 79 | "Quanto mais competitiva a eleição" | Competição entre e dentro de listas |
| 97, 99, 101 | "grau de competitividade", "ambiente competitivo", "capacidade competitiva" | Conceito geral |
| 147 (2×) | "partidos eleitoralmente mais/menos competitivos" | @fivaetal2024, partidos |
| 149 | "vantagem competitiva" | Conceito geral |
| 192 | "número de candidaturas competitivas inferior ao total" | Argumento de @cheibubsin2020 |
| 202 | "A classificação de competitividade de @cheibubsin2020" | É a classificação ex-post que a tese contrasta com a sua. Manter |

Único ponto de atenção: o comentário da l. 200, item (d), já registra a pendência de terminologia. Ele
pode ser apagado depois que a nota de rodapé do Cap. 3 (l. 37) for resolvida.

---

## 5. Fora de `tese/` (só para registro)

- `regenerar_figuras_cap3.py:116`: rótulo "Candidaturas competitivas" da `fig-amplitude` (ver 1.2).
- Nomes de variáveis (`candidato_competitivo`, `lift_competitivos`, `competitivo` em `regressao_fracionaria_cap3.py`) e colunas dos CSVs: são internos e não precisam mudar. `regressao_fracionaria_cap3.py:107` já rotula a variável como "Credencial eleitoral prévia".
