# measurement-reviewer — Capítulo 3 — run-001

## Escopo e método

- Arquivos lidos: `tese/03-medindo-coordenacao-intrapartidaria.qmd` (185 linhas, sha do manifesto); `tese/03-formulas-propostas.qmd`; `tese/resultados-capitulo-3/19_notas_redacao.csv`, `21_verificacoes.csv`, `00_sintese.csv`, `01_universos.csv`, `02_competitivos_ano.csv`, `05_concentracao_ano.csv`, `15_cobertura_nacional.csv`, `14_sem_eleitos.csv`, `26_fontes.csv`; `tese/sensibilidade-top-x/analisar.py` e `resumo_nacional.csv`; `tese/alternativas-top-necr/analisar.py`; `tese/relatorio-consolidado-capitulo-3/construir.py` e `manifesto-figuras.csv`; `tese/scripts/resultados_capitulo3.py`, `exploracao_composicao_nucleo.py`, `financiamento_alternativo_top_necr.py` (`membership`); `src/2_gold/cap3_cobertura_top_necr.py`, `cap3_cs_features.py`, `cap3_taa_features.py`; `src/1_silver/gerar_rrd.py` (linhas 1-260, 380-531, 677-892); `data/processed/df_cobertura_top_necr_resumo.csv`.
- Recomputações executadas (scripts e saídas em `thesis-review/runs/run-001/evidence/`):
  - `mea_01_recompute_listas.py` → `mea_01_output.txt`, `mea_01_listas_recomputadas.csv`: NECr, k, pesos w, H, benchmark para todas as 1.570 listas com implementação independente; três listas em detalhe (empate na fronteira: 2018 SP PSOL; sem recursos: 2018 MS PSL; E > k: 2018 RJ PSL); casos-limite.
  - `mea_02_competitivo_como_escrito.py` → `mea_02_output.txt`, `mea_02_resumo.csv`, `mea_02_flags_2018.csv`, `mea_02_flags_2022.csv`: flag competitiva recalculada a partir de `resultados.parquet` + `candidatos.parquet` (a) com a definição do texto tal como escrita, (b) com as regras do código e CPF corretamente atribuído, (c) reproduzindo o merge de `gerar_rrd.py`; comparação com `candidato_competitivo`.
  - `mea_03_benchmark_e_convencoes.py` → `mea_03_output.txt`: benchmark com universo = recebedores; candidaturas fracionárias; piso/teto; competitivos por sexo; denominadores válidos vs integrais.
  - `mea_04_origem_vs_fonte.py` → `mea_04_output.txt`: origem "Recursos de partido político" × fonte FEFC/FP em `receitas.parquet`.
  - `mea_05_impacto_flags.py` → `mea_05_output.txt`, `mea_05_metricas_por_flag.csv`: cobertura/precisão/lift do Top-NECr sob as três definições de competitivo; médias de competitivos por lista; coligações (2018) e federações (2022) por lista partido × UF.
- Não foi possível verificar: (i) `gerar_rrd.py` não foi executado (pesado); a reprodução do merge foi feita à parte e reproduz 7.625/7.630 e 9.671/9.675 flags, o que basta para atribuir a causa. (ii) Não há `data/raw/vagas`; o QE de Deputado Estadual foi reconstruído como votos válidos / eleitos; para Deputado Federal usou-se `quociente_eleitoral.csv`. (iii) Durante o run, os diretórios `tese/resultados-capitulo-3/`, `tese/relatorio-consolidado-capitulo-3/`, `tese/sensibilidade-top-x/`, `tese/alternativas-top-necr/` e `tese/03-formulas-propostas.qmd` foram movidos para `tese/reports/` (17:01); as citações abaixo usam os caminhos do manifesto do run.

### Tabela texto ↔ código

| # | Definição | O texto diz (linha) | O código faz | Situação |
|---|---|---|---|---|
| 1 | Universo | 7.630 / 9.675 candidaturas; 859 / 711 listas; 73 / 63 sem recursos; 3 / 0 eleitos nelas (l. 25-27) | `rrd_df_novo.parquet` filtrado 2018/2022; listas = ano × UF × `sg_partido_norm` | Igual (mea_01) |
| 2 | Recursos R_il | "recursos de campanha provenientes dos fundos públicos" (l. 5, 31, 125, 183); "recursos controlados por partidos" (l. 45) | `vr_receita_recursos_partidos` = origem "Recursos de partido político", qualquer fonte (`gerar_rrd.py:205-209`) | Diferente: 1,22 % / 1,96 % da medida não é FEFC/FP; R$ 26 mi de fundos públicos chegam via outros candidatos e ficam fora (mea_04) |
| 3 | NECr | eq-necr, definido se R_l > 0 (l. 37-43) | `cap3_cobertura_top_necr.py:41-43` | Igual |
| 4 | k_l | ⌊NECr + 0,5⌋; k = 0 sem recursos (l. 49) | `:46` `max(1, floor(necr+0.5))`; 0 sem recursos | Igual (o `max(1,·)` nunca atua: NECr ≥ 1) |
| 5 | Empates | posições restantes divididas igualmente (l. 49, 88) | `acertos_fracionarios`: restantes × média do bloco (`cap3_taa_features.py:97-135`) | Igual (mea_01: 121 / 185 listas com empate na fronteira, todos em valor positivo) |
| 6 | Universo do ranking | "candidaturas de cada nominata com recursos partidários positivos" (l. 47) | ordena todas as C_l; NaN → 0 | Equivalente: k ≤ recebedores em todas as listas (mea_01) |
| 7 | Top-X% | menor k com acumulado ≥ τ (l. 55-58) | `grupo_acumulado` (Decimal, empates fracionários, aninhado) | Igual |
| 8 | Competitivo: cargos de vitória | Presidente, Governador, Senador, Dep. Federal, Dep. Estadual, Prefeito (l. 68) | Prefeito, Dep. Estadual + **Distrital**, Dep. Federal, Governador, Senador; **não existe Presidente** em `resultados.parquet` (`gerar_rrd.py:137-160`) | Diferente |
| 9 | Competitivo: critério QE | "10 % do QE em disputa proporcional para Dep. Federal ou Dep. Estadual" (l. 68); mas l. 64 diz "nas disputas que concorreram, exceto vereador" | ≥ 10 % de votos válidos/vagas em Dep. Federal, Dep. Estadual, **Governador, Senador, Prefeito** (`:686-692`) | Diferente; texto contraditório entre l. 64 e l. 68 |
| 10 | Competitivo: janela | 1998-2016 para 2018; 1998-2018 para 2022 (l. 68) | vitórias ≤ 2016 / ≤ **2020** (`:178-179`); QE < ano (inclui 2020) | Diferente para 2022 (7 vitórias de prefeito em 2020) |
| 11 | Competitivo: atribuição do histórico | por candidato (l. 25, 68) | merge candidatos↔resultados por (ano, UF, nº) com `drop_duplicates(keep="first")` (`:61-78`, `:506-524`): chave não única para prefeito/vereador | **Implementação defeituosa** (MEA-3-001) |
| 12 | Competitivo ex-ante | l. 66, 78 | `candidato_competitivo` (não `candidato_forte_cs`) em `01_universos.csv` e `competitivo_previo` nas figuras | Igual |
| 13 | H_l, cobertura, precisão, lift | eq-acerto, eq-indicadores sobre C_l, k_l, G_l (l. 88-103) | idem; para competitivos, N e k **válidos** (4 / 3 perfis ausentes) | Convenção não declarada; efeito ≤ 0,03 p.p. (mea_03 e) |
| 14 | Referência aleatória | E[H] = G_l k_l / C_l, sorteio entre as C_l (l. 107) | `n_eleitos * k / len(g)` | Igual; universo do sorteio não justificado (MEA-3-004) |
| 15 | Listas sem recursos nas métricas | k = 0 (l. 49) | permanecem em ΣG_l (`cap3_cobertura_top_necr.py:10, 74-77`) | Não declarado no texto |
| 16 | Unidade "lista/nominata" | partido × UF × eleição (l. 25) | idem; coligações 2018 e federações 2022 não agregadas | Não declarado (MEA-3-005) |
| 17 | Piso/teto | não mencionados | calculados (`df_cobertura_top_necr_resumo.csv`) | Ausente no capítulo, embora `03-formulas-propostas.qmd:104-106` afirme que o capítulo os reporta |

### Divergências de `19_notas_redacao.csv` e `03-formulas-propostas.qmd` que continuam no texto

- "Origem partidária e fonte pública" (nota 19, l. 5) — continua (l. 5, 31, 125, 183).
- "Histórico de vitórias" (nota 19, l. 6) — parcialmente corrigida: 2018 agora encerra em 2016 (bate com o código); 2022 continua em 2018 contra 2020 do código.
- "Cargos elegíveis: a redação inclui Presidente; a classificação não contém coluna de vitórias presidenciais; inclui deputado distrital" (nota 19, l. 7) — continua integralmente (l. 68).
- `03-formulas-propostas.qmd`: arredondamento, peso fracionário e k = 0 foram incorporados (l. 49, 88). Não incorporados: declaração de que listas sem recursos permanecem em ΣG_l (l. 264-270 da nota); perfil não observado e denominadores válidos (l. 276-283); aviso de que lift de cobertura ≡ lift de precisão (l. 247-258); "Decisões em aberto" 2 (universo do sorteio) e 3 (núcleo ponderado vs binário).
- Itens da nota 19 sobre Mp, bancada, tipo de partido e NECr ≤ Mp + 1 não se aplicam: o capítulo atual não usa Mp nem tipo de partido.

## Avaliação macro

Dentro do escopo de mensuração, a cadeia do capítulo é: hipótese de *gatekeeping* → núcleo priorizado operacionalizado pelo Top-NECr sobre os repasses de origem partidária → validação contra (i) credenciais prévias e (ii) eleição → conclusão de que o partido prioriza e de que a priorização é observável antes do voto. As peças de medida do núcleo (NECr, k, empates, Top-X%, H, cobertura, precisão, lift, referência analítica) estão hoje corretamente descritas no texto e reproduzem exatamente o código e os CSVs auditados, lista a lista. O elo frágil é a **referência ex-ante**: a flag "competitivo" não é a que o texto define (cargos, critério de QE, janela) e, mais grave, o pipeline atribui o histórico municipal a CPFs errados — 132 (2018) e 218 (2022) ex-prefeitos não são reconhecidos e 18 / 31 "vitórias de prefeito" são falsas. Recomputadas, as métricas centrais mudam pouco (cobertura de competitivos entre 75 % e 81 %; lift entre 1,77 e 1,88 conforme a definição), de modo que a conclusão substantiva sobrevive, mas o número reportado depende de uma medida que não corresponde nem ao texto nem à intenção do código. Três convenções que afetam a leitura ficam sem declaração: o rótulo "fundos públicos" para uma variável definida por origem; o universo do sorteio de referência (todas as candidaturas, incluindo as que não podem estar no núcleo — com recebedores apenas, o lift dos eleitos cai de 1,98 / 2,12 para 1,78 / 2,05); e a unidade "nominata" = partido × UF, quando 85 % das listas de 2018 estavam em coligações e 25 % das de 2022 em federações — o construto medido é concentração intrapartidária, não intralista. A seção de robustez troca de construto (Top-X% fixa o acúmulo, não varia o arredondamento do Top-NECr) e omite a robustez que existe para o mesmo construto (piso/teto).

## Achados

```yaml
id: MEA-3-001
titulo: "Histórico eleitoral municipal atribuído a CPFs errados: vitórias de prefeito (e vereador) e QE de prefeito estão corrompidos na flag competitiva"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 68
  secao: "#### Desempenho eleitoral prévio {#sec-competitivos}"
  trecho: "Uma candidatura à eleição do ano $y$ é classificada como competitiva se, em alguma eleição anterior a $y$, o candidato: (i) venceu a disputa para Presidente, Governador, Senador, Deputado Federal, Deputado Estadual ou Prefeito"
afirmacao_do_autor: "A classificação competitiva identifica, por candidato, vitórias prévias inclusive para Prefeito."
problema: "`gerar_rrd.py` liga resultados a CPF pela chave (ano, UF, nr_candidato) com `drop_duplicates(keep='first')` (`_construir_resultados_select`, l. 61-78; `_gerar_resultados_cpf`, l. 506-524). Para cargos municipais a chave não é única (em 2016, 17.220 candidaturas a prefeito cabem em 768 chaves; 22 CPFs por chave em média): todas as vitórias de prefeito com o número N na UF são somadas ao primeiro CPF do arquivo. Resultado em `rrd_df_novo.parquet`: `n_eleicoes_prefeito` assume 25, 28, 41 e 46 para candidatos que nunca foram prefeitos (p.ex. 2022 MG AVANTE 7025, 46 'vitórias'), enquanto os ex-prefeitos reais recebem 0. O mesmo vale para `n_eleicoes_vereador` (máx. 34) e para o critério de 10 % em prefeito. A flag competitiva é a referência ex-ante de todo o capítulo."
evidencia:
  tipo: recomputacao
  fontes: ["src/1_silver/gerar_rrd.py:61-78", "src/1_silver/gerar_rrd.py:506-524", "thesis-review/runs/run-001/evidence/mea_02_output.txt", "thesis-review/runs/run-001/evidence/mea_02_resumo.csv", "thesis-review/runs/run-001/evidence/mea_05_output.txt"]
  detalhe: "Vitória prévia de prefeito: base = 19 (2018) e 35 (2022); com CPF atribuído por (ano, UF, cargo, município, nº) = 133 e 222; das flags da base, 18/19 e 31/35 são falsas; 132 e 218 ex-prefeitos são perdidos. Reproduzindo o merge do pipeline obtêm-se 889/886 e 1.287/1.287 flags (7.625 e 9.671 iguais), o que confirma a causa. Com as regras do próprio código e CPF correto, competitivos = 1.017 (13,3 %) e 1.554 (16,1 %) em vez de 886 e 1.287; Top-NECr: cobertura 75,4 % / 76,5 % (texto: > 80 %), precisão 33,1 % / 31,1 %, lift 1,82 / 1,77 (texto: 1,87 / 1,89). Distribuição de `n_eleicoes_prefeito` na base: {1: 15, 2: 6, 3: 12, …, 25: 1, 28: 1, 41: 1, 46: 1}."
severidade: MAJOR
confianca: alta
recomendacao: "Corrigir o merge em `gerar_rrd.py` incluindo `ds_cargo` e o município (`cd_municipio`/`nm_municipio`) na chave para cargos municipais e `ds_cargo` para os demais (senador × suplente compartilham número); regenerar `rrd_df_novo.parquet` e todos os CSVs/figuras que dependem de `candidato_competitivo`; atualizar 886/1.287 e as métricas de competitivos no capítulo. Registrar em `21_verificacoes.csv` um teste de plausibilidade (n_eleicoes_prefeito ≤ 6)."
claims: [C3.4.01, C3.6.01, C3.7.01, C3.7.02, C3.7.03]
```

```yaml
id: MEA-3-002
titulo: "Definição textual de 'competitivo' não corresponde à implementada (Presidente, Distrital, QE em majoritárias, janela 2020) e é contraditória entre l. 64 e l. 68"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 64
  secao: "#### Desempenho eleitoral prévio {#sec-competitivos}"
  trecho: "candidatos competitivos como aqueles que já venceram alguma eleição prévia para qualquer cargo exceto vereador ou que tenham obtido ao menos 10% do quociente eleitoral nas disputas que concorreram, também exceto para vereador."
afirmacao_do_autor: "Competitivo = vitória prévia (Presidente, Governador, Senador, Dep. Federal, Dep. Estadual, Prefeito) ou ≥ 10 % do QE em disputa proporcional para Dep. Federal ou Dep. Estadual; histórico 1998-2016 (2018) e 1998-2018 (2022)."
problema: "(a) l. 64 aplica o critério de 10 % a 'disputas que concorreram, exceto vereador'; l. 68 restringe a Dep. Federal/Estadual — contradição interna. (b) O código aplica 10 % (votos válidos/vagas, vagas = 1 em majoritárias) a Governador, Senador e Prefeito: 335 (2018) e 610 (2022) candidaturas satisfazem isso; 103 e 214 são competitivas só por esse critério. (c) 'Presidente' não existe em `resultados.parquet` nem no código; 'Deputado Distrital' está no código (11 / 10 candidaturas; 7 / 3 competitivas só por isso) e não no texto. (d) Para 2022 o código usa vitórias ≤ 2020 (7 prefeitos eleitos em 2020) e o texto diz 1998-2018. Itens 'Histórico de vitórias' e 'Cargos elegíveis' de `19_notas_redacao.csv` seguem abertos."
evidencia:
  tipo: recomputacao
  fontes: ["src/1_silver/gerar_rrd.py:137-160", "src/1_silver/gerar_rrd.py:178-179", "src/1_silver/gerar_rrd.py:686-692", "src/1_silver/gerar_rrd.py:801-802", "tese/resultados-capitulo-3/19_notas_redacao.csv:6-7", "thesis-review/runs/run-001/evidence/mea_02_output.txt", "thesis-review/runs/run-001/evidence/mea_05_metricas_por_flag.csv"]
  detalhe: "Flag recalculada com a definição da l. 68 tal como escrita (CPF correto, QE federal de `quociente_eleitoral.csv`, QE estadual = válidos/eleitos): 907 (11,9 %) e 1.337 (13,8 %) competitivos contra 886 e 1.287 da base. Cruzamento: 29 / 52 candidaturas competitivas na base não o são pelo texto (11 / 20 por vitória falsa de prefeito, 7 / 3 por distrital, 0 / 19 por QE majoritário) e 50 / 102 competitivas pelo texto não estão na base (48 / 100 ex-prefeitos perdidos). Top-NECr com a flag do texto: cobertura 80,7 % / 81,2 %, precisão 31,6 % / 28,4 %, lift 1,88 / 1,86 — a conclusão sobrevive, o número não."
severidade: MAJOR
confianca: alta
recomendacao: "Decidir o construto e alinhar texto e código: se a intenção é 'credenciais em disputa proporcional' (l. 68), restringir o código a Dep. Federal/Estadual(+Distrital) e à janela declarada; se a intenção é a regra implementada, reescrever l. 64 e l. 68 ('Prefeito, Governador, Senador, Deputado Federal, Estadual ou Distrital'; '10 % do quociente eleitoral, ou dos votos válidos em disputa majoritária'; 'até 2016 para 2018 e até 2020 para 2022') e retirar 'Presidente'. Em qualquer caso, eliminar a contradição entre l. 64 e l. 68."
claims: [C3.4.01, C3.4.02, C3.6.01]
```

```yaml
id: MEA-3-003
titulo: "'Fundos públicos' rotula uma variável definida por origem partidária, não por fonte FEFC/FP"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 31
  secao: "### Seleção do núcleo de candidaturas priorizadas"
  trecho: "As operacionalizações da seleção do núcleo de priorizados usam exclusivamente as informações da distribuição de financiamento de campanha provenientes de fundos públicos."
afirmacao_do_autor: "R_il são recursos de fundos públicos (repetido em l. 5, 125 e 183: 'distribuição intralista dos fundos públicos')."
problema: "`vr_receita_recursos_partidos` é definida por `ds_origem_receita == 'Recursos de partido político'` sem filtro de fonte (`gerar_rrd.py:205-209`). Inclui R$ 12,42 mi (2018) e R$ 56,11 mi (2022) de 'Outros recursos' repassados por partidos (1,22 % e 1,96 % da medida; 957 e 1.108 candidaturas) e exclui R$ 26,0 mi por ano de FEFC/FP recebidos de outros candidatos. A nota 19 ('Origem partidária e fonte pública') já pedia a distinção e ela não foi incorporada. O construto medido é 'alocação decidida pelo partido' — mais adequado ao argumento do que 'fundos públicos' — e é isso que o texto deveria dizer."
evidencia:
  tipo: recomputacao
  fontes: ["src/1_silver/gerar_rrd.py:193-243", "tese/resultados-capitulo-3/19_notas_redacao.csv:5", "thesis-review/runs/run-001/evidence/mea_04_output.txt"]
  detalhe: "2018: origem partido R$ 1.019,22 mi; FEFC+FP R$ 1.032,88 mi; interseção R$ 1.006,80 mi. 2022: origem partido R$ 2.860,03 mi; FEFC+FP R$ 2.830,28 mi; interseção R$ 2.803,93 mi. Fonte pública fora da origem partidária: 'Recursos de outros candidatos' R$ 26,0 / 26,1 mi."
severidade: MODERATE
confianca: alta
recomendacao: "Definir R_il uma vez (l. 45) como 'repasses de origem partidária (Recursos de partido político), majoritariamente FEFC e Fundo Partidário: 98,8 % em 2018 e 98,0 % em 2022' e substituir 'fundos públicos' por 'recursos partidários' nas l. 5, 31, 125 e 183, ou filtrar a variável por fonte e recalcular."
claims: [C3.2.03]
```

```yaml
id: MEA-3-004
titulo: "Universo do sorteio de referência inclui candidaturas que não podem pertencer ao núcleo; alternativa com recebedores reduz o lift e não é declarada"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 107
  secao: "#### Cobertura, precisão e lift {#sec-metricas}"
  trecho: "se um subconjunto de tamanho $k_l$ fosse extraído ao acaso, sem reposição, entre as $C_l$ candidaturas da lista $l$, o número esperado de candidaturas no grupo de referência nele contidas seria $G_l\\,k_l/C_l$."
afirmacao_do_autor: "O lift compara o núcleo com um sorteio entre todas as C_l candidaturas; 'o núcleo acerta o dobro' (l. 175)."
problema: "O núcleo só pode conter recebedores (k ≤ recebedores em todas as listas), mas o sorteio inclui 2.046 (2018) e 1.086 (2022) candidaturas com R = 0, entre elas 32 / 8 eleitos e 75 / 36 competitivos. O benchmark mistura duas decisões do partido (dar ou não dar; quanto dar) e por isso é o mais fácil de superar. `03-formulas-propostas.qmd` (l. 346-349) lista a escolha como decisão em aberto a ser declarada; o texto não a declara nem justifica."
evidencia:
  tipo: recomputacao
  fontes: ["src/2_gold/cap3_cobertura_top_necr.py:68", "tese/03-formulas-propostas.qmd:346-349", "thesis-review/runs/run-001/evidence/mea_03_output.txt"]
  detalhe: "Eleitos: lift 1,98 / 2,12 com universo C_l; 1,78 / 2,05 com universo = recebedores. Competitivos: 1,87 / 1,89 → 1,69 / 1,85. Cobertura máxima alcançável (só recebedores podem estar no núcleo): 93,8 % / 98,4 % dos eleitos e 91,5 % / 97,2 % dos competitivos."
severidade: MODERATE
confianca: alta
recomendacao: "Declarar o universo do sorteio e o motivo; reportar em nota ou na figura o lift com universo restrito aos recebedores (1,7-2,0) como limite inferior. Ajustar a frase da l. 175 ('o núcleo acerta o dobro') para o intervalo."
claims: [C3.4.04, C3.7.03, C3.7.05, C3.9.03]
```

```yaml
id: MEA-3-005
titulo: "'Lista/nominata' = partido × UF, mas 85 % das listas de 2018 estavam em coligações e 25 % das de 2022 em federações: o construto é concentração intrapartidária, não intralista"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 25
  secao: "### Universo empírico e recursos partidários"
  trecho: "Para examinar a distribuição intrapartidária, essas observações são agregadas por partido, unidade da federação e eleição."
afirmacao_do_autor: "A unidade é a nominata partidária; o capítulo fala de 'candidaturas de uma mesma lista', 'competição intrapartidária em suas listas' (l. 5, 7, 35)."
problema: "Em 2018 a lista que disputa o quociente é a coligação; em 2022, a federação. O texto não declara que coligações e federações são desmembradas por partido, que o NECr e o núcleo são calculados dentro do partido e que 'candidaturas competitivas na lista' e o sorteio de referência ignoram os coligados. Isso é defensável (o dinheiro é alocado pelo partido), mas muda o que 'lista mediana com quatro candidatos' (l. 117) e 'fim das coligações' (l. 181) significam: em 2018 a lista de voto era em média muito maior que o partido × UF medido."
evidencia:
  tipo: recomputacao
  fontes: ["data/processed/resultados.parquet (ds_composicao_coligacao)", "tese/alternativas-top-necr/analisar.py:188", "thesis-review/runs/run-001/evidence/mea_05_output.txt"]
  detalhe: "2018: 731 de 859 listas partido × UF (85,1 %) em coligação com > 1 partido; 4.975 de 7.630 candidaturas. 2022: 178 de 711 (25,0 %) em federação; 1.435 de 9.675 candidaturas. O relatório de alternativas registra a convenção ('partidos de federações/coligações não são agregados'); o capítulo não."
severidade: MODERATE
confianca: alta
recomendacao: "Declarar na seção de dados que a unidade é o partido dentro da UF, mesmo quando integra coligação (2018) ou federação (2022), e que todas as medidas são intrapartidárias; usar 'nominata partidária' de forma consistente e reler a l. 181 à luz disso."
claims: [C3.2.02, C3.6.02]
```

```yaml
id: MEA-3-006
titulo: "Lift, razão de coberturas e razão de precisões são o mesmo número, apresentados como três confirmações"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 147
  secao: "### Priorização financeira pelo Top-NECr"
  trecho: "Estas taxas de precisão seguem duas vezes maiores quando comparadas ao seu *benchmark* aleatório. O *lift* confirma que essa diferença não vem do tamanho dos grupos selecionados pelo Top-NECr"
afirmacao_do_autor: "Cobertura 'o dobro do esperado' (l. 145), precisão 'duas vezes maior' (l. 147) e lift 'confirma' (l. 147) são evidências que se reforçam."
problema: "Com A_0 = ΣG_l k_l/C_l no denominador, Cobertura/Cobertura_acaso = Precisão/Precisão_acaso = Lift por identidade algébrica (`03-formulas-propostas.qmd`, l. 247-258, que pede que a coincidência 'não seja lida como confirmação recíproca'). O texto não declara a identidade e a redação sugere convergência independente."
evidencia:
  tipo: textual
  fontes: ["tese/03-formulas-propostas.qmd:247-258", "tese/sensibilidade-top-x/analisar.py:127", "thesis-review/runs/run-001/evidence/mea_01_output.txt"]
  detalhe: "2018 eleitos: 86,7/43,8 = 19,2/9,7 = 1,98; 2022: 92,6/43,7 = 12,4/5,9 = 2,12. A verificação 'Lift idêntico por cobertura e precisão' está no próprio script de sensibilidade."
severidade: MODERATE
confianca: alta
recomendacao: "Após eq-indicadores, uma frase: 'como o mesmo A_0 aparece nos denominadores, o lift é idêntico à razão entre cobertura observada e esperada e à razão entre precisão observada e esperada; é uma única medida de excesso.' Reescrever l. 145-147 para não somar três vezes o mesmo fato."
claims: [C3.7.04, C3.7.05]
```

```yaml
id: MEA-3-007
titulo: "Seção de robustez troca de construto (Top-X%) e omite a robustez do mesmo construto (piso/teto)"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 155
  secao: "#### Sensibilidade ao limiar Top-X%"
  trecho: "Para avaliar a sensibilidade dos achados deste capítulo sobre a arbitrariedade do recorte do núcleo de candidaturas priorizadas pelo Top-NECr, utiliza-se o número mínimo de candidatos que são necessários para alcançar a concentração de i% dos recursos da lista"
afirmacao_do_autor: "Top-X% testa a arbitrariedade do recorte do Top-NECr."
problema: "O elemento arbitrário do Top-NECr é a conversão de NECr em inteiro (⌊·+0,5⌋); Top-X% não varia isso — fixa o acúmulo e é, nas palavras do próprio texto, 'a segunda operacionalização' (l. 53). A robustez do mesmo construto (piso ⌊NECr⌋ e teto ⌈NECr⌉) está calculada em `df_cobertura_top_necr_resumo.csv` e `15_cobertura_nacional.csv`, `03-formulas-propostas.qmd` (l. 104-106) afirma que 'o capítulo também reporta as versões com piso e teto', e o capítulo não as menciona (0 ocorrências de 'piso'/'teto')."
evidencia:
  tipo: ausencia
  fontes: ["tese/03-formulas-propostas.qmd:104-106", "data/processed/df_cobertura_top_necr_resumo.csv", "thesis-review/runs/run-001/evidence/mea_03_output.txt"]
  detalhe: "Eleitos, 2018: piso k = 2.058, cobertura 82,6 %, lift 2,18; arredondado 2.318 / 86,7 % / 1,98; teto 2.618 / 87,7 % / 1,75. 2022: piso 3.520 / 91,6 % / 2,26; arredondado 3.824 / 92,6 % / 2,12; teto 4.119 / 93,5 % / 1,98. Nota: 'quase todos os limiares' (l. 173) — o lift Top-95% é 1,38-1,57."
severidade: MODERATE
confianca: alta
recomendacao: "Apresentar o Top-X% como operacionalização alternativa do núcleo (fixa o acúmulo), não como teste de arbitrariedade do Top-NECr; acrescentar uma linha/nota com piso e teto (a robustez do próprio Top-NECr); corrigir a afirmação da nota formal ou o capítulo."
claims: [C3.3.03, C3.8.01, C3.8.02]
```

```yaml
id: MEA-3-008
titulo: "Afirmação de 'estimativa conservadora' por cotas não é calculada e o parágrafo contém marcador de dado a inserir"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 179
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "[inserir: X% das mulheres no universo são classificadas como competitivas, contra Y% dos homens]. Uma fração do núcleo priorizado é, portanto, ocupada por candidaturas que o partido financia porque a lei manda"
afirmacao_do_autor: "As cotas forçam a inclusão de não competitivas no núcleo e puxam a precisão para baixo; sem elas a priorização medida seria maior — os indicadores são conservadores."
problema: "A premissa está com marcador vazio e o contrafactual ('se as cotas fossem retiradas do cálculo') não foi computado. O núcleo é definido pela ordem de valores; não é possível saber, sem cálculo, se as posições de mulheres/negros no núcleo derivam da cota ou de escolha. A direção do argumento é plausível, mas a conclusão 'estimativa conservadora' é uma afirmação sobre o construto sem evidência."
evidencia:
  tipo: recomputacao
  fontes: ["thesis-review/runs/run-001/evidence/mea_03_output.txt"]
  detalhe: "Competitivas: mulheres 4,5 % (2018) e 6,0 % (2022) vs homens 14,9 % e 17,3 %. Mulheres ocupam 32,9 % e 36,2 % das posições do núcleo; entre posições de mulheres no núcleo, 13,1 % / 13,0 % são competitivas, contra 39,7 % / 36,3 % entre homens. Os números preenchem X e Y, mas não demonstram o contrafactual."
severidade: MODERATE
confianca: alta
recomendacao: "Preencher X/Y com os valores acima (ou recalculados após MEA-3-001) e substituir 'estimativa conservadora' por uma versão testada — p.ex. reportar precisão e lift do núcleo restrito a homens ou excluindo posições com peso ≤ ao piso legal — ou rebaixar a frase a hipótese."
claims: [C3.9.02]
```

```yaml
id: MEA-3-009
titulo: "Listas sem recursos permanecem no denominador da cobertura; o texto não declara e a cobertura máxima em 2018 é 99,4 %"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 49
  secao: "#### Top-NECr"
  trecho: "Em listas sem recursos partidários, não há definição de NECr e atribui-se $k_l=0$."
afirmacao_do_autor: "k_l = 0 sem recursos."
problema: "Falta a segunda metade da convenção (pedida em `03-formulas-propostas.qmd`, l. 264-270 e 318-321): essas listas saem das estatísticas de concentração (786 / 648 listas) mas seus G_l continuam em ΣG_l das métricas (859 / 711). Os 3 eleitos de 2018 em listas sem recursos (l. 27) são citados sem que se diga que limitam a cobertura a 99,4 %."
evidencia:
  tipo: codigo
  fontes: ["src/2_gold/cap3_cobertura_top_necr.py:10", "src/2_gold/cap3_cobertura_top_necr.py:74-77", "tese/03-formulas-propostas.qmd:264-270"]
  detalhe: "Recomputado (mea_01): 2018 ΣG = 513 com 3 eleitos e 11 competitivos em listas sem recursos; 2022: 0 eleitos e 4 competitivos."
severidade: MINOR
confianca: alta
recomendacao: "Acrescentar à l. 49 a frase proposta na nota formal: 'Essas listas são excluídas das estatísticas de concentração, mas permanecem no universo nacional das métricas de cobertura: seus candidatos do grupo-alvo seguem no denominador.'"
claims: [C3.2.02, C3.4.03]
```

```yaml
id: MEA-3-010
titulo: "Perfil competitivo não observado (4 / 3 candidaturas) e denominadores 'válidos' não declarados"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 95
  secao: "#### Cobertura, precisão e lift {#sec-metricas}"
  trecho: "Os três indicadores são calculados nacionalmente, somando as listas:"
afirmacao_do_autor: "As somas correm sobre C_l, k_l e G_l integrais."
problema: "Para o grupo competitivo o código (`evaluate` em `alternativas-top-necr/analisar.py:68-72`, usado por `sensibilidade-top-x`) restringe as somas às candidaturas com CPF válido (7.626 / 9.672; posições 2.316 / 3.822 em vez de 2.318 / 3.824). O texto não menciona a exclusão nem que as 4 / 3 candidaturas com CPF '-4' contam como não competitivas na contagem 886 / 1.287."
evidencia:
  tipo: recomputacao
  fontes: ["tese/alternativas-top-necr/analisar.py:68-72", "tese/sensibilidade-top-x/resumo_nacional.csv", "tese/03-formulas-propostas.qmd:276-283", "thesis-review/runs/run-001/evidence/mea_03_output.txt"]
  detalhe: "Precisão de competitivos com Σk integral = 30,92 % vs 30,95 % reportado (2018); 27,83 % vs 27,84 % (2022); lift 1,8731 vs 1,8728. Efeito numérico desprezível; a convenção é que falta."
severidade: MINOR
confianca: alta
recomendacao: "Nota de rodapé em @sec-metricas com o parágrafo 'Perfil competitivo não observado' de `03-formulas-propostas.qmd`."
claims: [C3.4.03, C3.7.02]
```

```yaml
id: MEA-3-011
titulo: "Núcleo é conjunto de posições (226 / 477 candidaturas com pertencimento fracionário), mas o texto o trata alternadamente como conjunto de candidaturas"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 175
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "Somadas todas as listas, o Top-NECr seleciona [cerca de 2,3 mil] candidaturas em 2018 e [cerca de 3,8 mil] em 2022"
afirmacao_do_autor: "O Top-NECr seleciona 2.318 / 3.824 candidaturas; 'candidatos selecionados no núcleo' (l. 141)."
problema: "2.318 / 3.824 são posições (Σk). Candidaturas com w = 1: 2.216 / 3.589; com 0 < w < 1: 226 (49 listas) / 477 (108 listas), somando 102 / 235 posições. O texto declara o peso fracionário (l. 49, 88) mas depois fala em candidaturas selecionadas; a nota formal (l. 161-165 e decisão 3) pede que se diga que o núcleo não é uma lista fechada de pessoas. Há também os marcadores '[cerca de …]' não resolvidos e a notação R_i (l. 45) contra R_il (l. 40)."
evidencia:
  tipo: recomputacao
  fontes: ["thesis-review/runs/run-001/evidence/mea_03_output.txt", "tese/03-formulas-propostas.qmd:161-165"]
  detalhe: "Entre as fracionárias há 3 / 13 eleitas e 4 / 28 competitivas."
severidade: MINOR
confianca: alta
recomendacao: "Usar 'posições' onde o número é Σk (l. 141, 175) e registrar em uma frase que 226 / 477 candidaturas pertencem parcialmente ao núcleo; resolver os marcadores; indexar R_il na l. 45."
claims: [C3.9.01, C3.3.02]
```

## Claims

```yaml
claim_id: C3.2.01
capitulo: 3
secao: "### Universo empírico e recursos partidários"
claim: "O universo reúne 7.630 candidaturas em 2018 e 9.675 em 2022."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 25}
evidencia: {tipo: csv, referencia: "tese/resultados-capitulo-3/01_universos.csv; evidence/mea_01_output.txt"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: measurement-reviewer
```

```yaml
claim_id: C3.2.02
capitulo: 3
secao: "### Universo empírico e recursos partidários"
claim: "859 listas em 2018 e 711 em 2022; 73 e 63 sem recursos partidários; 3 e 0 eleitos nelas."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 27}
evidencia: {tipo: csv, referencia: "01_universos.csv; evidence/mea_01_output.txt"}
assessment: {status: supported, confidence: alta}
concerns: ["Unidade partido × UF não declarada como desmembramento de coligações/federações (MEA-3-005)", "Permanência dessas listas em ΣG_l não declarada (MEA-3-009)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.2.03
capitulo: 3
secao: "### Seleção do núcleo de candidaturas priorizadas"
claim: "As operacionalizações usam exclusivamente recursos provenientes de fundos públicos."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 31}
evidencia: {tipo: codigo, referencia: "src/1_silver/gerar_rrd.py:205-209; evidence/mea_04_output.txt"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["Variável é por origem partidária; 1,2-2,0 % não é FEFC/FP e R$ 26 mi/ano de fundos públicos via outros candidatos ficam fora (MEA-3-003)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.3.01
capitulo: 3
secao: "#### Top-NECr"
claim: "NECr_l = 1/Σ s_il², s_il = R_il/R_l, definido se R_l > 0."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 38}
evidencia: {tipo: codigo, referencia: "src/2_gold/cap3_cobertura_top_necr.py:41-43; evidence/mea_01_output.txt (1.570 listas iguais)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: measurement-reviewer
```

```yaml
claim_id: C3.3.02
capitulo: 3
secao: "#### Top-NECr"
claim: "k_l = ⌊NECr_l + 0,5⌋; empates na posição k_l dividem as posições restantes igualmente; k_l = 0 sem recursos."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 49}
evidencia: {tipo: codigo, referencia: "cap3_cobertura_top_necr.py:44-51; cap3_taa_features.py:97-135; evidence/mea_01_output.txt"}
assessment: {status: supported, confidence: alta}
concerns: ["Núcleo é conjunto de posições; 226 / 477 candidaturas fracionárias (MEA-3-011)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.3.03
capitulo: 3
secao: "#### Top-X%"
claim: "k^τ_l = menor k com Σ_{j≤k} s_(j)l ≥ τ, τ ∈ {0,50 … 0,95}."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 56}
evidencia: {tipo: codigo, referencia: "tese/alternativas-top-necr/analisar.py:36-51 (grupo_acumulado); sensibilidade-top-x/analisar.py:72-78, 93-97"}
assessment: {status: supported, confidence: alta}
concerns: ["Apresentado na robustez como teste da arbitrariedade do Top-NECr, mas é outro construto (MEA-3-007)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.4.01
capitulo: 3
secao: "#### Desempenho eleitoral prévio"
claim: "Competitivo = vitória prévia para Presidente, Governador, Senador, Dep. Federal, Dep. Estadual ou Prefeito, ou ≥ 10 % do QE em disputa proporcional para Dep. Federal ou Dep. Estadual."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 68}
evidencia: {tipo: codigo, referencia: "gerar_rrd.py:137-160, 686-692; cap3_cs_features.py:83-100; evidence/mea_02_output.txt"}
assessment: {status: contradicted, confidence: alta}
concerns: ["Código: sem Presidente, com Distrital, QE em Gov/Sen/Pref (MEA-3-002)", "Histórico municipal atribuído a CPFs errados (MEA-3-001)", "l. 64 contradiz l. 68"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.4.02
capitulo: 3
secao: "#### Desempenho eleitoral prévio"
claim: "Histórico de 1998 a 2016 para 2018 e de 1998 a 2018 para 2022."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 68}
evidencia: {tipo: codigo, referencia: "gerar_rrd.py:178-179, 801-802"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["2018: bate (≤ 2016). 2022: código usa vitórias ≤ 2020 e QE < 2022 (MEA-3-002)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.4.03
capitulo: 3
secao: "#### Cobertura, precisão e lift"
claim: "Cobertura = ΣH/ΣG; Precisão = ΣH/Σk; Lift = ΣH/Σ(G k/C), com H_l = Σ w g."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 98}
evidencia: {tipo: codigo, referencia: "cap3_cobertura_top_necr.py:63-98; alternativas-top-necr/analisar.py:68-72, 142-145; evidence/mea_01_output.txt"}
assessment: {status: supported, confidence: alta}
concerns: ["Para competitivos, somas sobre N/k válidos (MEA-3-010)", "Listas sem recursos ficam em ΣG (MEA-3-009)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.4.04
capitulo: 3
secao: "#### Cobertura, precisão e lift"
claim: "O valor de referência é analítico: sorteio de k_l entre as C_l candidaturas dá esperança G_l k_l/C_l."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 107}
evidencia: {tipo: codigo, referencia: "cap3_cobertura_top_necr.py:68; evidence/mea_03_output.txt"}
assessment: {status: supported, confidence: alta}
concerns: ["Universo do sorteio inclui candidaturas sem recursos, que não podem estar no núcleo; com recebedores o lift cai (MEA-3-004)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.6.01
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "886 (11,6 %) competitivos em 2018 e 1.287 (13,3 %) em 2022; candidatos +27 %, competitivos +45 %."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 115}
evidencia: {tipo: csv, referencia: "01_universos.csv; evidence/mea_02_resumo.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["Números reproduzem `candidato_competitivo`, mas a flag não implementa a definição do texto (907 / 1.337) nem as regras do código com CPF correto (1.017 / 1.554) — MEA-3-001, MEA-3-002"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.6.02
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "Lista mediana com 4 e 9 candidatos; competitivos por lista: mediana 1, média 1,11 e 1,98."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 117}
evidencia: {tipo: csv, referencia: "05_concentracao_ano.csv; evidence/mea_05_output.txt (financiadas: 1,113 / 1,980)"}
assessment: {status: supported, confidence: alta}
concerns: ["Médias referem-se às listas financiadas (786 / 648); em todas as listas são 1,03 / 1,81 — o texto não diz qual universo"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.6.03
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "NECr mediano 1,88 (2018) e 4,81 (2022)."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 121}
evidencia: {tipo: csv, referencia: "05_concentracao_ano.csv (1,8781; 4,8144)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: measurement-reviewer
```

```yaml
claim_id: C3.6.04
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "C/NECr mediano 1,95 e 1,86; NECr/C mediano 51,36 % e 53,65 %; médias C/NECr 3,29 → 2,67."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 127}
evidencia: {tipo: csv, referencia: "05_concentracao_ano.csv (Q mediana 1,9469 / 1,8641; média 3,2949 / 2,6668)"}
assessment: {status: supported, confidence: alta}
concerns: ["Média de NECr/C (56,18 % / 55,40 %) não verificada aqui (results-reviewer)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.7.01
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Mais de 80 % dos competitivos estão no Top-NECr; referência 43,2 % e 43,7 %."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 139}
evidencia: {tipo: csv, referencia: "sensibilidade-top-x/resumo_nacional.csv (80,90 / 82,68; 43,18 / 43,75); evidence/mea_05_metricas_por_flag.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["Reproduz a flag da base; com a definição do texto 80,7 / 81,2 %; com regras do código e CPF correto 75,4 / 76,5 % (MEA-3-001)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.7.02
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Precisão 30,9 % e 27,8 %; aleatória 16,5 % e 14,7 %."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 141}
evidencia: {tipo: csv, referencia: "sensibilidade-top-x/resumo_nacional.csv (30,95 / 27,84; 16,52 / 14,73)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["Mesma ressalva de C3.7.01; 31,6 / 28,4 % pela definição do texto"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.7.03
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Lift 1,87 em 2018 e 1,89 em 2022."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 143}
evidencia: {tipo: csv, referencia: "sensibilidade-top-x/resumo_nacional.csv (1,8737 / 1,8900); evidence/mea_05_metricas_por_flag.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["1,88 / 1,86 pela definição do texto; 1,82 / 1,77 pelas regras do código com CPF correto; 1,69 / 1,85 com sorteio entre recebedores"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.7.04
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "86,7 % dos eleitos em 2018 e 92,6 % em 2022 estão no Top-NECr; o dobro do esperado."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 145}
evidencia: {tipo: csv, referencia: "15_cobertura_nacional.csv; evidence/mea_01_output.txt (445,0/513; 475,19/513; A0 224,57 / 224,42)"}
assessment: {status: supported, confidence: alta}
concerns: ["'O dobro' é o mesmo número que o lift (MEA-3-006); com sorteio entre recebedores é 1,78 / 2,05 (MEA-3-004)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.7.05
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Precisão de eleitos 19,2 % e 12,4 %; lift 1,98 e 2,12; 513 deputados."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 147}
evidencia: {tipo: csv, referencia: "15_cobertura_nacional.csv; evidence/mea_01_output.txt"}
assessment: {status: supported, confidence: alta}
concerns: ["Três formulações do mesmo excesso (MEA-3-006)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.8.01
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "No Top-50 % há mais de 50 % de cobertura dos competitivos; a cobertura cresce com o limiar."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 157}
evidencia: {tipo: csv, referencia: "sensibilidade-top-x/resumo_nacional.csv (57,3 % / 52,8 %; trajetórias não decrescentes verificadas no script)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: measurement-reviewer
```

```yaml
claim_id: C3.8.02
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "Lift acima de 1 em todos os limiares; no Top-95 % é 1,53 (2018) e 1,38 (2022)."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 159}
evidencia: {tipo: csv, referencia: "sensibilidade-top-x/resumo_nacional.csv (1,5338 / 1,3754)"}
assessment: {status: supported, confidence: alta}
concerns: ["Depende da flag competitiva (MEA-3-001/002); não recomputado para as definições alternativas"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.9.01
capitulo: 3
secao: "## Discussão"
claim: "O Top-NECr seleciona cerca de 2,3 mil candidaturas em 2018 e 3,8 mil em 2022."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 175}
evidencia: {tipo: csv, referencia: "15_cobertura_nacional.csv (Σk = 2.318 / 3.824)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["São posições, não candidaturas: 2.216 / 3.589 inteiras + 226 / 477 fracionárias (MEA-3-011)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.9.02
capitulo: 3
secao: "## Discussão"
claim: "As cotas puxam a precisão para baixo sem refletir escolha; os indicadores são estimativa conservadora da priorização."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 179}
evidencia: {tipo: nenhuma, referencia: "marcador '[inserir: X% …]' no texto; evidence/mea_03_output.txt (d)"}
assessment: {status: unsupported, confidence: alta}
concerns: ["Contrafactual não calculado (MEA-3-008)"]
agent: measurement-reviewer
```

```yaml
claim_id: C3.9.03
capitulo: 3
secao: "## Discussão"
claim: "A razão 1,9 se repete em 2018 e 2022, para competitivos e eleitos, no Top-NECr e em quase todos os limiares do Top-X%."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 173}
evidencia: {tipo: csv, referencia: "sensibilidade-top-x/resumo_nacional.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["Lifts vão de 1,38 (Top-95 %) a 3,60 (Top-50 %, eleitos 2022); 'se repete' descreve só o Top-NECr e o Top-80 %", "Com sorteio entre recebedores: 1,69-2,05"]
agent: measurement-reviewer
```

## Verificações que passaram

- NECr, k (arredondado), pesos w, H de eleitos e valor esperado recomputados de forma independente para as 1.570 listas: idênticos a `df_cobertura_top_necr_lista.parquet` (mea_01).
- Agregados nacionais reproduzidos: 2018 Σk = 2.318, H = 445,0, A_0 = 224,57, cobertura 86,74 %, precisão 19,20 %, lift 1,982; 2022 Σk = 3.824, H = 475,19, A_0 = 224,42, 92,63 %, 12,43 %, 2,117. Tabela "Valores que as fórmulas produzem" de `03-formulas-propostas.qmd` confere.
- Universo: 7.630 / 9.675 candidaturas; 859 / 711 listas; 73 / 63 sem recursos; 3 / 0 eleitos nelas; 513 eleitos por ano; nenhuma candidatura com situação de registro anômala na base (só ELEITO*/NÃO ELEITO/SUPLENTE).
- Regra de empate do texto (l. 49, 88) ≡ `acertos_fracionarios` ≡ `membership`; Σw = k em toda lista; 121 / 185 listas com empate na fronteira, nenhum em valor zero; todos os valores monetários são múltiplos de R$ 0,01 (a "igualdade monetária" da nota formal não gera ambiguidade).
- k ≤ número de recebedores em todas as listas; `max(1,·)` nunca atua; listas com 1 candidato (163 / 33) e k = C (207 / 100) tratadas sem erro; E > k em 10 / 4 listas (39 / 22 eleitos) contabilizadas corretamente; nenhum eleito com 0 votos; nenhum recebedor com 0 votos.
- NaN de recursos (2.046 / 1.086) tratados como 0 de forma idêntica em `gerar_features`, `_preparar` e na sensibilidade; recursos ≥ 0.
- A flag usada nas contagens (886 / 1.287) e nas figuras é `candidato_competitivo`/`competitivo_previo` (ex-ante); `candidato_forte_cs` (ex-post) não é usada.
- Janela do histórico para 2018 (≤ 2016) confere com o texto; a nota 19 "Histórico de vitórias" foi parcialmente atendida.
- Top-X%: definição, mínimo, aninhamento, invariância à ordem e empates verificados no script de sensibilidade; Top-NECr canônico reproduzido lá.
- Lift de cobertura ≡ lift de precisão (identidade verificada no script e na recomputação).
- Medianas e médias das l. 117, 121, 127, 131 (C, NECr, C/NECr) conferem com `05_concentracao_ano.csv`; médias de competitivos 1,11 / 1,98 correspondem às listas financiadas.
- Marcadores numéricos da Discussão (2,3 mil / 3,8 mil; 26 % e 20 %; 2,4 e 3,6; 66 % e 70 %; 1,1 e 2,0; 3,0 e 5,9) correspondem aos artefatos.

## Limites desta revisão

- `gerar_rrd.py` não foi executado; a causa de MEA-3-001 foi estabelecida reproduzindo o merge à parte (7.625 / 7.630 e 9.671 / 9.675 flags iguais) e por recomputação com chave correta. A taxa de CPF localizável por cargo na reconstrução foi 94-97 %; candidaturas não localizadas não puderam ser atribuídas em nenhuma das versões.
- Sem `data/raw/vagas`, o QE de Deputado Estadual foi reconstruído como votos válidos / eleitos; para Federal usou-se `quociente_eleitoral.csv`. Isso afeta apenas a flag "como escrita" na margem (critério ii).
- Não recomputei as figuras Top-X% sob as definições alternativas de competitivo, nem os números de médias de NECr/C (l. 131) — results-reviewer.
- Mp, bancada e tipo de partido não aparecem no capítulo atual; não foram avaliados.
- Durante o run (17:01) os diretórios `tese/resultados-capitulo-3/`, `tese/relatorio-consolidado-capitulo-3/`, `tese/sensibilidade-top-x/`, `tese/alternativas-top-necr/`, `tese/resultados-exploracao-nucleo/` e `tese/resultados-validacao-top-necr/` foram movidos para `tese/reports/`. Os caminhos citados são os do manifesto; as figuras referenciadas nas l. 149, 163 e 167 (`relatorio-consolidado-capitulo-3/figuras/…`, relativas a `tese/`) passaram a não existir nesse caminho — registro para o results-reviewer/chair.
