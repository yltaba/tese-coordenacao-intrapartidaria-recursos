# results-reviewer — Capítulo 3 — run-001

## Escopo e método

- Arquivos lidos:
  - `tese/03-medindo-coordenacao-intrapartidaria.qmd` (sha256 `0aec63e5…`, igual ao `manifest.yaml`), integral, com números de linha.
  - `tese/03-formulas-propostas.qmd` (lido no início do run; **no fim do run o arquivo não existe mais em nenhum caminho do repositório** — ver RES-3-003).
  - `tese/resultados-capitulo-3/`: `00_sintese`, `01_universos`, `02_competitivos_ano`, `05_concentracao_ano`, `11`–`17`, `19_notas_redacao`, `20_confronto_scripts`, `21_verificacoes`, `26_fontes`, `verificacao.json`.
  - `tese/relatorio-consolidado-capitulo-3/`: `03-top-necr-dados.csv`, `manifesto-figuras.csv`, `resumo_nacional.csv`, `universo.csv`, `tamanhos_top_x.csv`, `descritivos.csv`, `faixas_incrementais.csv`, `auditoria.json`, `verificacao.json`, `figuras-para-tese.qmd`.
  - `tese/sensibilidade-top-x/`: `resumo_nacional.csv`, `tamanhos.csv`, `trajetorias.csv`, `interpretacao.json`, `verificacao.json`.
  - `data/processed/df_cobertura_top_necr_resumo.csv`; `data/processed/rrd_df_novo.parquet` (esquema e recomputação).
  - Código: `src/2_gold/cap3_cs_features.py`, `cap3_cobertura_top_necr.py`, `cap3_taa_features.py`, `tese/scripts/exportar_amplitude_barras.py`.
  - PNGs abertos: `figs/cap3_fig_amplitude_barras.png`, `figs/cap3_fig_concentracao_barras.png`, `relatorio-consolidado-capitulo-3/figuras/03-top-necr.png`, `04-topx-competitividade.png`, `05-topx-eleicao.png`.
- Recomputações executadas (`evidence/res_recompute_cap3.py` → `evidence/res_recompute_cap3.out`): universos e contagens; competitivos por ano e por gênero; descritivos por lista (C, F, NECr, C/NECr, NECr/C; universos "todas" e "financiadas"); Σk do Top-NECr; cobertura/precisão/lift nacionais para competitivos e eleitos com empates fracionários (replicando `acertos_fracionarios` e `norm_partido`); lifts e monotonia do Top-X%; razões de crescimento 2018→2022.
- Mudança de estado do repositório durante o run: às 17:01:37 (run iniciado 16:55:50) as pastas `tese/resultados-capitulo-3/`, `tese/relatorio-consolidado-capitulo-3/`, `tese/sensibilidade-top-x/`, `tese/alternativas-top-necr/`, `tese/old/` foram movidas para `tese/reports/`. Os CSVs relocados têm os mesmos sha256 do `manifest.yaml` (conferido: `15_cobertura_nacional.csv`, `00_sintese.csv`, `resumo_nacional.csv`), portanto o conteúdo usado abaixo é o auditado. Os caminhos de figura do `.qmd` (l. 149, 163, 167) deixaram de resolver.
- Não foi possível verificar: nada de numérico ficou sem conferência. A norma legal citada na l. 179 (30% do FEFC; cotas raciais) está fora do escopo deste agente.

### Tabela de números do capítulo

| linha | trecho | número | artefato-fonte | valor no artefato | bate? |
|---|---|---|---|---|---|
| 25 | "7.630 candidaturas em 2018 e 9.675 em 2022" | 7.630 / 9.675 | `01_universos.csv`; recompute | 7630 / 9675 | sim |
| 27 | "859 listas em 2018 e 711 em 2022" | 859 / 711 | `01_universos.csv`; recompute | 859 / 711 | sim |
| 27 | "73 não receberam recursos … 63 nominatas em 2022" | 73 / 63 | `01_universos.csv`; recompute | 73 / 63 | sim |
| 27 | "três candidatos foram eleitos em 2018 e nenhum em 2022" | 3 / 0 | `01_universos.csv`; `df_cobertura_top_necr_resumo.csv` | 3 / 0 | sim |
| 115 | "886 (11,6%) … competitivos" | 886; 11,6% | `01_universos.csv`; recompute | 886; 11,61% | sim |
| 115 | "1.287 (13,3%) competitivas" | 1.287; 13,3% | idem | 1287; 13,30% | sim |
| 115 | "total de candidatos lançados aumentou 27%" | 27% | recompute | 26,8% | sim |
| 115 | "competitivas cresceu 45%" | 45% | recompute | 45,3% | sim |
| 117 | "lista partidária mediana possuiu quatro candidatos em 2018 e nove em 2022" | 4 / 9 | `descritivos.csv` (ambos universos) | 4,0 / 9,0 | sim |
| 117 | "A média de candidaturas foi maior" | — | `descritivos.csv` | 9,41 / 14,42 (financiadas) | sim |
| 117 | "mediana de candidaturas competitivas por lista é igual a um" | 1 / 1 | `descritivos.csv` | 1,0 / 1,0 | sim |
| 117 | "A média … 1,11 e 1,98" | 1,11 / 1,98 | `descritivos.csv` (Listas financiadas) | 1,113 / 1,980 | sim — universo financiadas (todas: 1,03 / 1,81), não declarado no texto |
| 121 | "na mediana … 1,88 candidato efetivo … 4,81" | 1,88 / 4,81 | `00_sintese.csv`; recompute | 1,878 / 4,814 | sim |
| 127 | "1,95 e 1,86 candidato formal para cada candidato efetivo" | 1,95 / 1,86 | `05_concentracao_ano.csv` mediana Q | 1,947 / 1,864 | sim |
| 127 | "proporção mediana … 51,36% e 53,65%" | 51,36 / 53,65 | `descritivos.csv` NECr/C | 51,36 / 53,65 | sim |
| 131 | "média de C/NECr caiu de 3,29 para 2,67" | 3,29 / 2,67 | `00_sintese.csv` | 3,295 / 2,667 | sim |
| 131 | "média de NECr/C passou de 56,18% para 55,40%" | 56,18 / 55,40 | `descritivos.csv` | 56,18 / 55,40 | sim |
| 139 | "mais de 80% compõem o núcleo" | >80% | `03-top-necr-dados.csv`; recompute | 80,90 / 82,68 | sim |
| 139 | "43,2 e 43,7% em 2018 e 2022" | 43,2 / 43,7 | idem | 43,18 / 43,75 | sim |
| 141 | "precisão … 30,9 e 27,8%" | 30,9 / 27,8 | idem | 30,95 / 27,84 | sim |
| 141 | "conteria 16,5 e 14,7% de competitivos" | 16,5 / 14,7 | idem | 16,52 / 14,73 | sim |
| 143 | "lift … 1,87 em 2018 e 1,89 em 2022" | 1,87 / 1,89 | idem | 1,874 / 1,890 | sim |
| 143 | "quase 90% mais candidaturas competitivas" | ~90% | derivado | 87% / 89% | sim |
| 145 | "86,7% dos eleitos em 2018 e 92,6% … 2022" | 86,7 / 92,6 | `15_cobertura_nacional.csv` (arredondado); recompute | 86,74 / 92,63 | sim |
| 145 | "o dobro daquelas esperadas aleatoriamente" | ~2× | 86,7/43,8; 92,6/43,7 | 1,98 / 2,12 | sim |
| 147 | "precisão é de 19,2 e 12,4%" | 19,2 / 12,4 | `15_cobertura_nacional.csv` | 19,20 / 12,43 | sim |
| 147 | "elegem 513 deputados" | 513 | `01_universos.csv` | 513 / 513 | sim |
| 147 | "duas vezes maiores … benchmark aleatório" | ~2× | 19,2/9,69; 12,4/5,87 | 1,98 / 2,12 | sim |
| 147 | "1,98 vez … 2018 e 2,12 vez em 2022" | 1,98 / 2,12 | `03-top-necr-dados.csv`; recompute | 1,982 / 2,117 | sim |
| 155 | limiares "50, 60, 70, 80, 90 e 95%" | 6 limiares | `resumo_nacional.csv` | 6 | sim |
| 157 | "Top-50% … mais de 50% de cobertura" | >50% | `resumo_nacional.csv` | 57,3 / 52,8 | sim |
| 159 | "acima de um em todos os limiares" | lift > 1 | `interpretacao.json` | 24/24 > 1; mín. 1,375 | sim |
| 159 | "Top-95% … 1,53 em 2018 e 1,38 em 2022" | 1,53 / 1,38 | `resumo_nacional.csv` | 1,534 / 1,375 | sim |
| 161 | "mais candidaturas competitivas dentro do núcleo … do que fora" | — | recompute (precisão vs `proporcao_perfil_fora`) | verdadeiro em 12/12 limiares | sim |
| 165 | "cobertura de eleitas … mais alta do que … competitivas" | — | recompute | verdadeiro em 12/12 limiares | sim |
| 165 | "valores de lift … sempre … acima de um" | — | `interpretacao.json` | 24/24 | sim |
| 173 | "resumido em um número: 1,9 … se repete … em quase todos os limiares do Top-X%" | 1,9 | `resumo_nacional.csv` | lifts Top-X% de 1,38 a 3,60; só 2/24 em [1,8; 2,0] | **não** |
| 173 | "cobertura acima de 80% dos competitivos" | >80% | `03-top-necr-dados.csv` | 80,9 / 82,7 | sim |
| 173 | "acima de 87% dos eleitos" | >87% | `15_cobertura_nacional.csv` | 86,74 / 92,63 | **não** em 2018 (86,7%) |
| 175 | "[cerca de 2,3 mil] … [cerca de 3,8 mil]" | 2,3 mil / 3,8 mil | `universo.csv` Posicoes_Top_NECr; recompute | 2.318 / 3.824 | sim, mas placeholder |
| 175 | "entre quatro e sete vezes o número de cadeiras" | 4–7× | 2318/513; 3824/513 | 4,52 / 7,45 | parcial (7,45 > 7) |
| 175 | "queda da precisão … de 19,2% para 12,4%" | 19,2 / 12,4 | `15_cobertura_nacional.csv` | 19,20 / 12,43 | sim |
| 175 | "média de competitivos por lista … 1,1 e 2,0" | 1,1 / 2,0 | `descritivos.csv` (financiadas) | 1,113 / 1,980 | sim (financiadas) |
| 175 | "NECr médio de 3,0 e 5,9" | 3,0 / 5,9 | `00_sintese.csv` | 2,962 / 5,902 | sim |
| 177 | "Top-50% … precisão … [26% e 20%]" | 26 / 20 | `resumo_nacional.csv` eleicao top_50 | 26,10 / 20,32 | sim, mas placeholder |
| 177 | "lift … [2,4 e 3,6]" | 2,4 / 3,6 | idem | 2,380 / 3,599 | sim, mas placeholder |
| 177 | "cobertura cai para [66% e 70%]" | 66 / 70 | idem | 66,40 / 70,41 | sim, mas placeholder |
| 177 | "gradiente é monotônico nas duas eleições e nas duas referências" | — | `trajetorias.csv`; recompute | cobertura não-decrescente, precisão e lift não-crescentes em 4/4 séries | sim |
| 179 | "[inserir: X% das mulheres … contra Y% dos homens]" | X / Y | recompute (`rrd_df_novo`, `ds_genero`) | 2018: 4,47% vs 14,93%; 2022: 5,96% vs 17,29% | **placeholder vazio** |
| 181 | "1,9 candidatura por lista em 2018 e 4,8 em 2022" | 1,9 / 4,8 | `00_sintese.csv` | 1,878 / 4,814 | sim |
| 181 | "proporção … estável, em torno de metade" | ~50% | `descritivos.csv` NECr/C mediana | 51,4 / 53,6 | sim |
| 181 | "enquanto as listas dobraram" | ×2 | recompute | mediana C 4→9 (×2,25); média 9,4→14,4 (×1,53); candidaturas +27% | parcial |

### Figuras

| ref. | linha | arquivo citado | existe? | o que o PNG mostra | legenda vs `manifesto-figuras.csv` |
|---|---|---|---|---|---|
| `@fig-amplitude` | 119 | `../figs/cap3_fig_amplitude_barras.png` | sim | Barras horizontais, painéis Média e Mediana, séries 2018/2022: Candidaturas totais 9,41/14,42 e 4/9; competitivas 1,11/1,98 e 1/1; NECr 2,96/5,90 e 1,88/4,81. Universo financiadas (N=786/648). | Não é a figura do manifesto (`01-amplitude`, dot-plot Q1–Q3); gerada de `amplitude-proposta-2.plotly.json` por `exportar_amplitude_barras.py`. Legenda do `.qmd` não diz painéis nem N. |
| `@fig-concentracao` | 129 | `../figs/cap3_fig_concentracao_barras.png` | sim | Barras: C/NECr média 3,29/2,67, mediana 1,95/1,86; NECr/C média 56,18%/55,40%, mediana 51,36%/53,65%. | Não é `02-concentracao` do manifesto (que inclui k/C). Valores batem com `descritivos.csv`. |
| `@fig-cap3-03-top-necr` | 149 | `relatorio-consolidado-capitulo-3/figuras/03-top-necr.png` | **não resolve desde 17:01** (arquivo em `tese/reports/…`) | 2×3 painéis; linha 1 Competitivos prévios (80,9→82,7; 30,9→27,8; 1,87→1,89), linha 2 Eleitos (86,7→92,6; 19,2→12,4; 1,98→2,12); pontilhado cinza = acaso intralista (43,2/43,7; 16,5/14,7; 43,8/43,7; 9,7/5,9). | Legenda do `.qmd` é versão truncada (omite "linha preta: observado; cinza pontilhada: benchmark"). Texto (l. 137, 145) descreve corretamente linha 1 / linha 2. |
| `@fig-cap3-04-topx-competitividade` | 163 | `…/04-topx-competitividade.png` | **não resolve desde 17:01** | 2×3 painéis por ano (2018, 2022) × cobertura, precisão, lift; eixo 50–95%; tracejado = Top-NECr; Top-80% destacado. Valores conferem com `resumo_nacional.csv`. | Legenda omite "Top-80% destacado" e "referência horizontal = Top-NECr", que o leitor precisa para ler o tracejado. |
| `@fig-cap3-05-topx-eleicao` | 167 | `…/05-topx-eleicao.png` | **não resolve desde 17:01** | Mesmo layout para eleitos; lift 2022 vai de 3,60 (Top-50%) a 1,46 (Top-95%). | Idem. |

Tabelas: o capítulo não contém tabelas nem código inline. Referências cruzadas: `@fig-amplitude`, `@fig-concentracao`, `@fig-cap3-03-top-necr`, `@fig-cap3-04-topx-competitividade`, `@fig-cap3-05-topx-eleicao`, `@sec-metricas` — todas definidas. `#sec-validacao`, `#sec-competitivos`, `#sec-discussao-cap3` e as equações `#eq-*` são definidos e nunca referenciados (sem efeito).

## Avaliação macro

Dentro do escopo deste agente — o texto diz o que a evidência mostra? — a cadeia resultado → conclusão se sustenta nos números centrais. Todos os valores das seções de Resultados (universos, competitivos, medianas e médias de C, NECr, C/NECr, NECr/C, cobertura/precisão/lift do Top-NECr para competitivos e eleitos, lifts do Top-95%) batem com os CSVs auditados e foram reproduzidos independentemente a partir de `rrd_df_novo.parquet` com a mesma regra de empates. As cinco figuras existem, mostram o que o texto descreve e os valores rotulados coincidem com os CSVs de dados.

O que não está fechado é a Discussão. Ela contém seis números entre colchetes (dos quais cinco estão corretos, mas seguem marcados como provisórios) e um placeholder vazio (`X%` / `Y%` de mulheres e homens competitivos) que sustenta o argumento de que os indicadores são "uma estimativa conservadora da priorização". A síntese "o resultado do capítulo pode ser resumido em um número: 1,9 … que se repete … em quase todos os limiares do Top-X%" afirma mais do que a Figura 4/5 mostra: os lifts Top-X% vão de 1,38 a 3,60 e só ficam em [1,8; 2,0] em 2 de 24 pontos; o que se repete é "acima de 1", não "1,9". Há ainda um cabeçalho `## Discussão` duplicado e vazio. Por fim, os três caminhos de figura da seção de resultados deixaram de resolver após a movimentação dos relatórios para `tese/reports/` ocorrida durante este run.

Nenhum achado invalida uma conclusão; um exige mudança de interpretação (a síntese do 1,9) e um bloqueia o fechamento do capítulo (placeholder vazio na Discussão).

## Achados

```yaml
id: RES-3-001
titulo: "Placeholder vazio na Discussão sustenta o argumento da 'estimativa conservadora'"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 179
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "[inserir: X% das mulheres no universo são classificadas como competitivas, contra Y% dos homens]"
afirmacao_do_autor: "As cotas forçam o partido a financiar candidaturas que, pelo critério do histórico eleitoral, raramente são competitivas; logo os indicadores são uma estimativa conservadora da priorização."
problema: "O número que sustenta a premissa ('raramente são competitivas') não está no texto. O parágrafo inteiro — e a conclusão de que a precisão é puxada para baixo pela lei, não por escolha — depende dele."
evidencia:
  tipo: recomputacao
  fontes: ["thesis-review/runs/run-001/evidence/res_recompute_cap3.py", "thesis-review/runs/run-001/evidence/res_recompute_cap3.out", "data/processed/rrd_df_novo.parquet"]
  detalhe: "Universo de candidaturas, flag candidato_competitivo replicada de cap3_cs_features.py. 2018: FEMININO 108/2414 = 4,47%; MASCULINO 778/5212 = 14,93%. 2022: FEMININO 203/3404 = 5,96%; MASCULINO 1084/6268 = 17,29%. (4 e 3 registros 'não divulgável', nenhum competitivo.) A direção afirmada se confirma: razão homens/mulheres ≈ 3,3× em 2018 e 2,9× em 2022."
severidade: MAJOR
confianca: alta
recomendacao: "Substituir o colchete por: 'em 2018, 4,5% das mulheres e 14,9% dos homens no universo são classificados como competitivos; em 2022, 6,0% e 17,3%'. Declarar o universo (todas as candidaturas, N = 7.630 e 9.675) e registrar o cálculo em tese/resultados-capitulo-3/ (não há CSV com esse cruzamento)."
claims: [C3.10.06]
```

```yaml
id: RES-3-002
titulo: "Cinco números da Discussão permanecem entre colchetes, embora corretos"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 175
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "o Top-NECr seleciona [cerca de 2,3 mil] candidaturas em 2018 e [cerca de 3,8 mil] em 2022"
afirmacao_do_autor: "O núcleo não é pequeno (2,3 mil / 3,8 mil posições); no Top-50% a precisão sobe para [26% e 20%], o lift para [2,4 e 3,6] e a cobertura cai para [66% e 70%]."
problema: "Os seis valores entre colchetes (l. 175 e l. 177) são placeholders de redação não fechados. Todos conferem com os artefatos, mas o capítulo não está finalizado enquanto estiverem marcados como provisórios, e os colchetes vão para o texto renderizado."
evidencia:
  tipo: artefato
  fontes: ["tese/relatorio-consolidado-capitulo-3/universo.csv", "tese/sensibilidade-top-x/resumo_nacional.csv", "thesis-review/runs/run-001/evidence/res_recompute_cap3.out"]
  detalhe: "Posicoes_Top_NECr = 2318 (2018) e 3824 (2022); recompute Σk = 2318 / 3824. Top-50%, desfecho eleicao: precisão 26,10% / 20,32%; lift 2,380 / 3,599; cobertura 66,40% / 70,41%. Todos batem com o que está nos colchetes."
severidade: MODERATE
confianca: alta
recomendacao: "Remover os colchetes e fixar: '2.318 candidaturas em 2018 e 3.824 em 2022'; 'no Top-50% dos recursos, a precisão sobe para 26,1% e 20,3%, o lift para 2,4 e 3,6, e a cobertura cai para 66,4% e 70,4%'. Indicar que os valores do Top-50% se referem ao grupo-alvo eleitos (para competitivos: 38,9%/38,2%; 2,1/2,7; 57,3%/52,8%)."
claims: [C3.10.03, C3.10.05]
```

```yaml
id: RES-3-003
titulo: "Os três caminhos de figura da seção Top-NECr/Robustez não resolvem após a movimentação dos relatórios para tese/reports/"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 149
  secao: "### Priorização financeira pelo Top-NECr"
  trecho: "](relatorio-consolidado-capitulo-3/figuras/03-top-necr.png){#fig-cap3-03-top-necr"
afirmacao_do_autor: "As Figuras 3, 4 e 5 estão em relatorio-consolidado-capitulo-3/figuras/ (caminho relativo a tese/)."
problema: "Às 17:01:37 de 2026-09-14 (durante o run-001) as pastas tese/resultados-capitulo-3/, tese/relatorio-consolidado-capitulo-3/, tese/sensibilidade-top-x/ etc. foram movidas para tese/reports/. O .qmd (inalterado, sha256 igual ao manifesto) referencia os PNGs pelo caminho antigo nas l. 149, 163 e 167; a renderização do capítulo perderá as três figuras centrais. tese/03-formulas-propostas.qmd (insumo do manifesto) também não existe mais em nenhum caminho. As Figuras 1 e 2 (../figs/) continuam resolvendo."
evidencia:
  tipo: ausencia
  fontes: ["tese/03-medindo-coordenacao-intrapartidaria.qmd:149", "tese/03-medindo-coordenacao-intrapartidaria.qmd:163", "tese/03-medindo-coordenacao-intrapartidaria.qmd:167", "tese/reports/relatorio-consolidado-capitulo-3/figuras/03-top-necr.png", "thesis-review/runs/run-001/manifest.yaml"]
  detalhe: "Teste a partir de tese/: MISSING relatorio-consolidado-capitulo-3/figuras/03-top-necr.png, 04-topx-competitividade.png, 05-topx-eleicao.png; OK ../figs/cap3_fig_amplitude_barras.png e cap3_fig_concentracao_barras.png. find . -name '03-formulas*' → nenhum resultado. Os CSVs relocados mantêm os sha256 do manifest.yaml (15_cobertura_nacional, 00_sintese, resumo_nacional)."
severidade: MODERATE
confianca: alta
recomendacao: "Se a reorganização for definitiva: atualizar os três caminhos para reports/relatorio-consolidado-capitulo-3/figuras/… ou, como já feito para as Figuras 1–2, copiar os PNGs para figs/ (cap3_fig_top_necr.png etc.) e referenciar ../figs/. Atualizar CLAUDE.md, o contrato deste agente e o manifest.yaml para os novos caminhos, e restaurar (ou registrar a remoção de) tese/03-formulas-propostas.qmd."
claims: [C3.7.01, C3.8.01, C3.8.06]
```

```yaml
id: RES-3-004
titulo: "A síntese 'um número: 1,9 … se repete em quase todos os limiares do Top-X%' não corresponde à Figura 4/5"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 173
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "O resultado do capítulo pode ser resumido em um número: 1,9. … e ela se repete em 2018 e 2022, para candidaturas competitivas e para eleitas, no Top-NECr e em quase todos os limiares do Top-X%."
afirmacao_do_autor: "O lift ≈ 1,9 é estável entre anos, grupos-alvo e limiares."
problema: "No Top-NECr o lift é 1,87/1,89 (competitivos) e 1,98/2,12 (eleitos) — 'cerca de 2' já é mais exato que 1,9 para eleitos. No Top-X% o lift varia de 1,38 (Top-95%, competitivos 2022) a 3,60 (Top-50%, eleitos 2022); só 2 dos 24 pontos ficam em [1,8; 2,0] e 9 em [1,7; 2,1]. O próprio parágrafo seguinte (l. 177) descreve um gradiente monotônico de 3,6 a 1,5. O que se repete é 'acima de 1' com o valor ~1,9–2,3 no Top-80%, não 1,9. Na mesma frase, 'cobertura … acima de 87% dos eleitos' é falso para 2018 (86,7%)."
evidencia:
  tipo: artefato
  fontes: ["tese/sensibilidade-top-x/resumo_nacional.csv", "tese/relatorio-consolidado-capitulo-3/03-top-necr-dados.csv", "thesis-review/runs/run-001/evidence/res_recompute_cap3.out"]
  detalhe: "Lifts Top-X% — competitivos 2018: 2,08 2,05 2,02 1,93 1,73 1,53; 2022: 2,65 2,44 2,20 1,98 1,61 1,38; eleitos 2018: 2,38 2,35 2,22 2,03 1,79 1,57; 2022: 3,60 3,17 2,77 2,34 1,78 1,46. Em [1,8; 2,0]: 2/24. Cobertura eleitos Top-NECr 2018 = 86,74%."
severidade: MAJOR
confianca: alta
recomendacao: "Reescrever a síntese para o que a evidência mostra, p.ex.: 'entre 1,9 e 2,1 no Top-NECr, nos dois anos e nos dois grupos-alvo; acima de 1 em todos os 24 cortes do Top-X%, com valores próximos aos do Top-NECr no Top-80% e maiores quanto mais restrito o corte'. Trocar 'acima de 87%' por 'acima de 86%' ou '86,7% e 92,6%'."
claims: [C3.10.01, C3.10.02]
```

```yaml
id: RES-3-005
titulo: "Cabeçalho '## Discussão' duplicado e vazio"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 169
  secao: "## Discussão"
  trecho: "## Discussão"
afirmacao_do_autor: "—"
problema: "A l. 169 abre uma seção '## Discussão' sem conteúdo, imediatamente seguida por '## Discussão {#sec-discussao-cap3}' na l. 171. O sumário e a numeração renderizados terão duas seções 'Discussão', uma vazia."
evidencia:
  tipo: textual
  fontes: ["tese/03-medindo-coordenacao-intrapartidaria.qmd:169", "tese/03-medindo-coordenacao-intrapartidaria.qmd:171"]
  detalhe: "Linhas 169–171: '## Discussão' / (vazia) / '## Discussão {#sec-discussao-cap3}'."
severidade: MODERATE
confianca: alta
recomendacao: "Apagar a l. 169."
claims: []
```

```yaml
id: RES-3-006
titulo: "Universo das médias de competitivos por lista (1,11 / 1,98) não é declarado; o CSV de síntese traz 1,03 / 1,81"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 117
  secao: "### Amplitude das nominatas e concentração dos recursos"
  trecho: "Em 2018 e 2022, a mediana de candidaturas competitivas por lista é igual a um candidato. A média, respectivamente, é de 1,11 e 1,98 candidato."
afirmacao_do_autor: "Média de competitivos por lista = 1,11 (2018) e 1,98 (2022); repetido na l. 175 como 1,1 e 2,0."
problema: "Os valores correspondem às listas financiadas (N = 786 / 648). Sobre todas as listas (N = 859 / 711), que é o universo em que o parágrafo anterior conta 886 e 1.287 competitivos, a média é 1,03 / 1,81 (00_sintese.csv). O texto não diz qual universo usa; só a legenda da figura diz 'financiadas'. As medianas de C (4 / 9) coincidem nos dois universos, o que esconde a diferença."
evidencia:
  tipo: artefato
  fontes: ["tese/relatorio-consolidado-capitulo-3/descritivos.csv", "tese/resultados-capitulo-3/00_sintese.csv", "thesis-review/runs/run-001/evidence/res_recompute_cap3.out"]
  detalhe: "descritivos.csv: F média — Todas as listas 1,031 / 1,810; Listas financiadas 1,113 / 1,980. Recompute idêntico. C média: todas 8,88 / 13,61; financiadas 9,41 / 14,42 (a figura mostra 9,41 / 14,42)."
severidade: MINOR
confianca: alta
recomendacao: "Acrescentar na l. 117 'entre as 786 e 648 listas com recursos partidários' (ou reportar os dois universos), e manter a mesma escolha na l. 175."
claims: [C3.6.03, C3.10.04]
```

```yaml
id: RES-3-007
titulo: "'Listas dobraram' vale para a mediana (×2,25), não para a média (×1,53) nem para o total de candidaturas (+27%)"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 181
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "a proporção de candidaturas efetivas ficou estável, em torno de metade da nominata, enquanto as listas dobraram."
afirmacao_do_autor: "O tamanho das listas dobrou entre 2018 e 2022."
problema: "A lista mediana foi de 4 para 9 (×2,25); a média foi de 9,4 para 14,4 (×1,53); o total de candidaturas cresceu 27% (l. 115). 'Dobraram' sem qualificador contrasta com o 27% dito no mesmo capítulo; o efeito é composição (menos listas, 859→711)."
evidencia:
  tipo: recomputacao
  fontes: ["thesis-review/runs/run-001/evidence/res_recompute_cap3.out", "tese/relatorio-consolidado-capitulo-3/descritivos.csv"]
  detalhe: "Financiadas: razão de medianas C = 2,25; razão de médias = 1,53. Todas: idem. Candidaturas 7.630→9.675 (+26,8%); listas 859→711 (−17%)."
severidade: MINOR
confianca: alta
recomendacao: "'enquanto a lista mediana mais que dobrou (de 4 para 9 candidaturas), com menos listas e 27% mais candidaturas'."
claims: [C3.10.07]
```

```yaml
id: RES-3-008
titulo: "'Entre quatro e sete vezes o número de cadeiras' subestima 2022 (7,45×)"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 175
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "entre quatro e sete vezes o número de cadeiras em disputa"
afirmacao_do_autor: "Σk / 513 está entre 4 e 7."
problema: "2318/513 = 4,52; 3824/513 = 7,45. O limite superior fica acima de sete."
evidencia:
  tipo: recomputacao
  fontes: ["thesis-review/runs/run-001/evidence/res_recompute_cap3.out", "tese/relatorio-consolidado-capitulo-3/universo.csv"]
  detalhe: "k/513 = 4,52 (2018) e 7,45 (2022)."
severidade: MINOR
confianca: alta
recomendacao: "'entre quatro e meia e sete vezes e meia' ou 'cerca de 4,5 e 7,5 vezes'."
claims: [C3.10.03]
```

```yaml
id: RES-3-009
titulo: "Legendas das Figuras 1–5 no .qmd omitem o que o manifesto declara (universo, painéis, significado das linhas de referência)"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 163
  secao: "#### Sensibilidade ao limiar Top-X%"
  trecho: "![Sensibilidade da cobertura, precisão e lift de competitivos prévios ao limiar Top-X%, por eleição.]"
afirmacao_do_autor: "—"
problema: "As Figuras 4 e 5 têm três séries (observado, acaso intralista, tracejado Top-NECr) e o ponto Top-80% destacado; a legenda do .qmd não explica o tracejado nem o destaque, que o manifesto explica ('Benchmark intralista; Top-80% destacado. A referência horizontal indica o resultado do Top-NECr'). A Figura 3 perde 'linha preta: observado; cinza pontilhada: benchmark intralista'. As Figuras 1–2 são versões em barras (amplitude-proposta-2 / concentracao-barras) distintas de 01-amplitude/02-concentracao do manifesto, com legenda que não informa os painéis (Média/Mediana) nem N = 786/648; Figura 1 diz 'formal e efetiva' mas inclui também a série 'competitivas'."
evidencia:
  tipo: artefato
  fontes: ["tese/relatorio-consolidado-capitulo-3/manifesto-figuras.csv", "tese/scripts/exportar_amplitude_barras.py", "figs/cap3_fig_amplitude_barras.png", "tese/relatorio-consolidado-capitulo-3/figuras/04-topx-competitividade.png"]
  detalhe: "PNG 04: legenda interna 'Top-X% observado / Acaso intralista / Top-NECr'; ponto 80% maior. Legenda .qmd: 22 palavras, sem essas três informações. exportar_amplitude_barras.py gera figs/cap3_fig_amplitude_barras.png de amplitude-proposta-2.plotly.json, não de 01-amplitude."
severidade: MINOR
confianca: alta
recomendacao: "Adotar as legendas do manifesto (ou versão reduzida que preserve: universo, o que é cada linha, o que é o ponto destacado). Para as Figuras 1–2, dizer 'listas com recursos partidários (N = 786 e 648); painéis: média e mediana por lista'."
claims: [C3.6.01, C3.6.02, C3.8.01]
```

## Claims

```yaml
claim_id: C3.2.01
capitulo: 3
secao: "### Universo empírico e recursos partidários"
claim: "7.630 candidaturas em 2018 e 9.675 em 2022; 859 e 711 listas; 73 e 63 sem recursos partidários; 3 e 0 eleitos em listas sem recursos."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 25}
evidencia: {tipo: csv, referencia: "tese/resultados-capitulo-3/01_universos.csv; evidence/res_recompute_cap3.out §1"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.6.01
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "886 (11,6%) competitivos em 2018 e 1.287 (13,3%) em 2022; candidaturas +27%, competitivas +45%."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 115}
evidencia: {tipo: csv, referencia: "01_universos.csv; res_recompute_cap3.out §1 (26,8% / 45,3%)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.6.02
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "Lista mediana com 4 (2018) e 9 (2022) candidatos; média maior; Figura 1 (amplitude) mostra isso."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 117}
evidencia: {tipo: figura, referencia: "figs/cap3_fig_amplitude_barras.png; descritivos.csv"}
assessment: {status: supported, confidence: alta}
concerns: ["Legenda não declara universo (financiadas) nem painéis — RES-3-009"]
agent: results-reviewer
```

```yaml
claim_id: C3.6.03
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "Mediana de competitivos por lista = 1; média 1,11 (2018) e 1,98 (2022)."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 117}
evidencia: {tipo: csv, referencia: "descritivos.csv (Listas financiadas); 00_sintese.csv dá 1,03/1,81 para todas as listas"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["Universo não declarado no texto — RES-3-006"]
agent: results-reviewer
```

```yaml
claim_id: C3.6.04
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "NECr mediano 1,88 (2018) e 4,81 (2022)."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 121}
evidencia: {tipo: csv, referencia: "00_sintese.csv; res_recompute_cap3.out §2 (1,878 / 4,814)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.6.05
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "C/NECr mediano 1,95 e 1,86; NECr/C mediano 51,36% e 53,65%; médias C/NECr 3,29→2,67 e NECr/C 56,18%→55,40% (Figura 2)."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 127}
evidencia: {tipo: figura, referencia: "figs/cap3_fig_concentracao_barras.png; descritivos.csv; 05_concentracao_ano.csv"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.7.01
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Cobertura de competitivos pelo Top-NECr 80,9% e 82,7% (>80%, '4/5'); referência aleatória 43,2% e 43,7% (Figura 3, linha 1)."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 139}
evidencia: {tipo: figura, referencia: "relatorio-consolidado-capitulo-3/figuras/03-top-necr.png; 03-top-necr-dados.csv; res_recompute_cap3.out §3"}
assessment: {status: supported, confidence: alta}
concerns: ["Caminho do PNG não resolve desde a movimentação para tese/reports/ — RES-3-003"]
agent: results-reviewer
```

```yaml
claim_id: C3.7.02
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Precisão de competitivos 30,9% e 27,8%; ao acaso 16,5% e 14,7%."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 141}
evidencia: {tipo: csv, referencia: "03-top-necr-dados.csv; res_recompute_cap3.out §3 (30,92 / 27,83; 16,51 / 14,73)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.7.03
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Lift de competitivos 1,87 (2018) e 1,89 (2022): 'quase 90% mais'."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 143}
evidencia: {tipo: csv, referencia: "03-top-necr-dados.csv; res_recompute_cap3.out §3 (1,873 / 1,890)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.7.04
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Cobertura de eleitos 86,7% e 92,6%, 'o dobro' do esperado ao acaso (43,8% / 43,7%)."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 145}
evidencia: {tipo: csv, referencia: "15_cobertura_nacional.csv (arredondado); df_cobertura_top_necr_resumo.csv; res_recompute_cap3.out §3"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.7.05
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Precisão de eleitos 19,2% e 12,4%; 513 cadeiras; lift 1,98 e 2,12 ('cerca do dobro')."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 147}
evidencia: {tipo: csv, referencia: "15_cobertura_nacional.csv; 03-top-necr-dados.csv; res_recompute_cap3.out §3 (19,20 / 12,43; 1,982 / 2,117)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.8.01
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "Figura 4: padrão consistente 2018/2022; Top-50% cobre mais de 50% dos competitivos; cobertura cresce com o limiar."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 157}
evidencia: {tipo: figura, referencia: "relatorio-consolidado-capitulo-3/figuras/04-topx-competitividade.png; sensibilidade-top-x/resumo_nacional.csv (57,3% / 52,8%); trajetorias.csv"}
assessment: {status: supported, confidence: alta}
concerns: ["Caminho do PNG não resolve — RES-3-003; legenda incompleta — RES-3-009"]
agent: results-reviewer
```

```yaml
claim_id: C3.8.02
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "Precisão cresce quanto mais restrito o corte, nos dois ciclos; lift acima de 1 em todos os limiares; Top-95%: 1,53 e 1,38."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 159}
evidencia: {tipo: csv, referencia: "sensibilidade-top-x/resumo_nacional.csv; interpretacao.json (24/24 > 1; mín. 1,375); res_recompute_cap3.out §5"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.8.03
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "Sistematicamente há mais competitivos dentro do núcleo do que fora."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 161}
evidencia: {tipo: csv, referencia: "resumo_nacional.csv (precisao > proporcao_perfil_fora em 12/12 cortes); res_recompute_cap3.out §5"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: results-reviewer
```

```yaml
claim_id: C3.8.04
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "Cobertura de eleitos é maior que a de competitivos em todos os limiares; lifts sempre acima de 1 (Figura 5)."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 165}
evidencia: {tipo: figura, referencia: "figuras/05-topx-eleicao.png; resumo_nacional.csv; res_recompute_cap3.out §5 (12/12; 24/24)"}
assessment: {status: supported, confidence: alta}
concerns: ["Caminho do PNG não resolve — RES-3-003"]
agent: results-reviewer
```

```yaml
claim_id: C3.10.01
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "O resultado se resume a 1,9, que se repete em 2018 e 2022, competitivos e eleitos, Top-NECr e quase todos os limiares do Top-X%."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 173}
evidencia: {tipo: csv, referencia: "sensibilidade-top-x/resumo_nacional.csv: lifts Top-X% 1,38–3,60; 2/24 em [1,8; 2,0]"}
assessment: {status: contradicted, confidence: alta}
concerns: ["RES-3-004"]
agent: results-reviewer
```

```yaml
claim_id: C3.10.02
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "Cobertura acima de 80% dos competitivos e acima de 87% dos eleitos."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 173}
evidencia: {tipo: csv, referencia: "03-top-necr-dados.csv (80,9 / 82,7); 15_cobertura_nacional.csv (86,74 / 92,63)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["86,7% em 2018 não é 'acima de 87%' — RES-3-004"]
agent: results-reviewer
```

```yaml
claim_id: C3.10.03
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "Top-NECr seleciona cerca de 2,3 mil (2018) e 3,8 mil (2022) candidaturas, entre 4 e 7 vezes as 513 cadeiras."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 175}
evidencia: {tipo: csv, referencia: "universo.csv Posicoes_Top_NECr 2318 / 3824; res_recompute_cap3.out §2 (4,52× / 7,45×)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["Placeholder entre colchetes — RES-3-002", "7,45 > 7 — RES-3-008"]
agent: results-reviewer
```

```yaml
claim_id: C3.10.04
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "Queda da precisão de 19,2% para 12,4%; média de competitivos por lista 1,1 e 2,0 contra NECr médio 3,0 e 5,9."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 175}
evidencia: {tipo: csv, referencia: "15_cobertura_nacional.csv; descritivos.csv (financiadas 1,113 / 1,980); 00_sintese.csv (2,962 / 5,902)"}
assessment: {status: supported, confidence: alta}
concerns: ["Universo das médias de competitivos não declarado — RES-3-006"]
agent: results-reviewer
```

```yaml
claim_id: C3.10.05
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "No Top-50%: precisão 26% e 20%, lift 2,4 e 3,6, cobertura 66% e 70%; gradiente monotônico nas duas eleições e nas duas referências."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 177}
evidencia: {tipo: csv, referencia: "resumo_nacional.csv top_50 eleicao (26,10 / 20,32; 2,380 / 3,599; 66,40 / 70,41); trajetorias.csv (0 reversões em 4/4 séries)"}
assessment: {status: supported, confidence: alta}
concerns: ["Valores entre colchetes — RES-3-002; texto não diz que são os do grupo-alvo eleitos"]
agent: results-reviewer
```

```yaml
claim_id: C3.10.06
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "Mulheres são raramente competitivas pelo histórico eleitoral: X% contra Y% dos homens; por isso as cotas puxam a precisão para baixo e os indicadores são conservadores."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 179}
evidencia: {tipo: nenhuma, referencia: "placeholder; recompute em res_recompute_cap3.out §4: 4,47% vs 14,93% (2018); 5,96% vs 17,29% (2022)"}
assessment: {status: unsupported, confidence: alta}
concerns: ["Número ausente no texto — RES-3-001; a direção se confirma na recomputação"]
agent: results-reviewer
```

```yaml
claim_id: C3.10.07
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "NECr mediano 1,9 → 4,8; proporção de candidaturas efetivas estável em torno de metade, enquanto as listas dobraram."
localizacao: {arquivo: "tese/03-medindo-coordenacao-intrapartidaria.qmd", linha: 181}
evidencia: {tipo: csv, referencia: "00_sintese.csv; descritivos.csv NECr/C mediana 51,4 / 53,6; res_recompute_cap3.out §2 (mediana C ×2,25; média ×1,53)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["'Dobraram' só vale para a mediana — RES-3-007"]
agent: results-reviewer
```

## Verificações que passaram

- Universos (l. 25, 27): 7.630 / 9.675 candidaturas; 859 / 711 listas; 73 / 63 sem recursos; 3 / 0 eleitos em listas sem recursos — CSV e recomputação.
- Competitivos (l. 115): 886 (11,6%) / 1.287 (13,3%); +27% / +45% — recomputação com a flag replicada de `cap3_cs_features.py` (4 e 3 perfis não observados não alteram nenhum valor reportado a duas casas).
- Descritivos por lista (l. 117, 121, 127, 131, 175, 181): medianas de C 4 / 9; NECr 1,88 / 4,81 (média 2,96 / 5,90); C/NECr 1,95 / 1,86 (média 3,29 / 2,67); NECr/C 51,36% / 53,65% (média 56,18% / 55,40%) — CSV, PNGs e recomputação idênticos.
- Top-NECr nacional (l. 139–147; Figura 3): Σk 2.318 / 3.824; competitivos 80,90% / 30,95% / 1,874 e 82,68% / 27,84% / 1,890; eleitos 86,74% / 19,20% / 1,982 e 92,63% / 12,43% / 2,117; referências 43,2 / 43,7 / 16,5 / 14,7 / 43,8 / 43,7 / 9,7 / 5,9 — reproduzidos com empates fracionários a partir de `rrd_df_novo.parquet`; PNG rotula exatamente esses valores; linha 1 = competitivos, linha 2 = eleitos como o texto diz.
- Top-X% (l. 157–165; Figuras 4–5): Top-50% cobertura 57,3% / 52,8%; Top-95% lift 1,53 / 1,38; 24/24 lifts > 1; cobertura não-decrescente e precisão/lift não-crescentes em todas as 4 séries; precisão > incidência fora do núcleo em 12/12 cortes; cobertura de eleitos > de competitivos em 12/12 cortes.
- "O dobro" (l. 145, 147) e "quase 90% mais" (l. 143): razões 1,98 / 2,12 e 1,87 / 1,89 — dentro do que o texto afirma.
- Referências cruzadas `@fig-*` e `@sec-metricas` resolvem; nenhum `TODO`; nenhum `@tbl-`/`@eq-` referenciado e ausente.
- `03-top-necr-dados.csv` ≡ `resumo_nacional.csv` (top_necr) ≡ `15_cobertura_nacional.csv` (arredondado) ≡ `df_cobertura_top_necr_resumo.csv`; `auditoria.json` e `verificacao.json` com status OK; os CSVs relocados para `tese/reports/` mantêm os sha256 do `manifest.yaml`.

## Limites desta revisão

- Não julguei a validade da medida (definição de competitivo, benchmark hipergeométrico, universo do sorteio) nem a adequação inferencial — escopo de measurement e statistics. Registrei como `partially_supported` apenas onde o número bate mas o universo difere do declarado.
- A recomputação da cobertura de competitivos restringe as somas às candidaturas com perfil observado (7.626 / 9.672), como `03-formulas-propostas.qmd` descreve; a variante NA=False dá os mesmos valores a duas casas. Não reproduzi `df_cobertura_top_necr_lista.parquet` linha a linha, só os agregados.
- A afirmação legal da l. 179 (30% do FEFC desde 2018; cotas raciais desde 2022) não foi verificada.
- O estado do repositório mudou durante o run (movimentação para `tese/reports/` às 17:01; `03-formulas-propostas.qmd` ausente). Se a mudança for revertida ou concluída pelo autor, RES-3-003 deve ser reavaliado pelo chair; os demais achados não dependem dela.
- Os PNGs foram inspecionados visualmente; a coincidência de valores foi conferida pelos rótulos impressos nas figuras e pelos CSVs de dados, não por extração de pixels.
