# Síntese (pass 1) — Capítulo 3 — run-001

Chair: thesis-chair. Insumos: `agents/measurement.md` (11 achados), `agents/statistics.md` (9), `agents/results.md` (9), evidências em `evidence/`.
Saída paralela: `../issues_draft.yaml` (20 issues).

## 0. Estado do repositório e comparabilidade do run

- **Reorganização durante o run.** Às 17:01 (run iniciado 16:55) o autor moveu `tese/resultados-capitulo-3/`, `relatorio-consolidado-capitulo-3/`, `sensibilidade-top-x/`, `resultados-validacao-top-necr/`, `alternativas-top-necr/`, `old/` e outras para `tese/reports/`. Os três agentes detectaram e contornaram. Citações a `tese/<pasta>/…` nos relatórios devem ser lidas como `tese/reports/<pasta>/…`.
- **Hashes conferidos pelo chair** (sha256 sobre os caminhos atuais): o capítulo `.qmd`, os três `src/2_gold/cap3_*.py`, `reports/resultados-capitulo-3/15_cobertura_nacional.csv`, `reports/resultados-capitulo-3/00_sintese.csv`, `reports/sensibilidade-top-x/resumo_nacional.csv` e `data/processed/df_cobertura_top_necr_resumo.csv` são **idênticos** aos do `manifest.yaml`. O conteúdo que os agentes auditaram é o mesmo; só mudaram os caminhos.
- **`tese/03-formulas-propostas.qmd` está ausente.** `find . -name "03-formulas*"` na raiz do repositório não retorna nada, e não há cópia em `tese/reports/old/`, `revisoes/` ou `notes/`. É insumo do manifesto (sha `48981b07…`) e fica registrado como **ausência**. MEA e STA o leram antes da remoção. Nenhum achado depende só dele, porque todos têm também código, CSV ou recomputação. Mas as afirmações sobre *o que a nota formal diz* ficam **não verificáveis pelo chair** neste run: MEA-3-004 e STA-3-001 ("decisão em aberto 2"), MEA-3-006 e STA-3-005 ("não ler como confirmação recíproca"), MEA-3-007 ("o capítulo também reporta piso e teto", l. 104-106 da nota), MEA-3-009, MEA-3-010, MEA-3-011 e STA-3-006.
- **Figuras quebradas.** O `.qmd` não mudou, então as l. 149, 163 e 167 ainda apontam para `relatorio-consolidado-capitulo-3/figuras/*.png`, caminho relativo a `tese/`. O chair conferiu: os três arquivos estão MISSING no caminho citado e OK em `tese/reports/relatorio-consolidado-capitulo-3/figuras/`. As Figuras 1 e 2 (`../figs/`) resolvem. O problema é real, porque o capítulo não renderiza as figuras centrais; `_quarto.yml` gera PDF via lualatex, onde imagem ausente costuma interromper a compilação (inferência, sem renderizar). A causa é a movimentação de pastas, não um erro de redação. Vira o issue I-3-013.
- `CLAUDE.md` e `manifest.yaml` ainda listam os caminhos antigos. Estão fora de `thesis-review/` ou são insumos do run, então não foram editados; fica a recomendação ao autor.

## 1. Triagem

### 1.1 Campos obrigatórios

Todos os 29 achados têm `id, titulo, escala, localizacao{arquivo, linha, secao, trecho}, afirmacao_do_autor, problema, evidencia{tipo, fontes, detalhe}, severidade, confianca, recomendacao`.

Ressalvas que **não** levam a descarte:
- RES-3-004: o `trecho` junta dois fragmentos literais da l. 173 com "…". Cada fragmento existe no arquivo, então foi aceito como citação com elisão.
- RES-3-005: `afirmacao_do_autor: "—"`, o que é aceitável para um defeito de formatação.
- Fontes com caminho antigo (`tese/resultados-capitulo-3/…` etc.): resolvidas em `tese/reports/…` com o mesmo hash.
- Fontes que citam `tese/03-formulas-propostas.qmd`: ver §0. Cada uma tem pelo menos uma fonte adicional verificável.

### 1.2 Descartes

**Nenhum achado descartado (0 de 29).**

### 1.3 Verificação por amostragem (10 achados, 7 deles MAJOR)

| Achado | Trecho no `.qmd` | Fonte diz o que o achado afirma? | Como o chair conferiu |
|---|---|---|---|
| MEA-3-001 (MAJOR) | l. 68, literal ✓ | **Sim.** `gerar_rrd.py:61-63` faz `drop_duplicates(["ano_eleicao","sg_uf","nr_candidato"], keep="first")` sobre candidatos, e o merge em `:511-524` usa a mesma chave. Recomputação do chair em `rrd_df_novo.parquet` (2018+2022): `n_eleicoes_prefeito` assume {…, 13: 2, 25: 1, 28: 1, 41: 1, 46: 1}. A candidatura 2022/MG/AVANTE/7025 tem 46 "vitórias de prefeito", o que é impossível entre 1998 e 2020. `n_eleicoes_vereador` máx. = 34. `mea_02_output.txt` reproduz 7.625/7.630 e 9.671/9.675 flags com o merge keep-first. | código + recomputação |
| MEA-3-002 (MAJOR) | l. 64, literal ✓ | **Sim.** `gerar_rrd.py:137-145`: lista de cargos com DISTRITAL e sem PRESIDENTE. `:178-179`: janelas `2016` e `2020`. `:686-692`: `CARGOS_FORTE` inclui GOVERNADOR, SENADOR e PREFEITO. `19_notas_redacao.csv` l. 6-7 registra "Histórico de vitórias" e "Cargos elegíveis". | código + artefato |
| MEA-3-003 (MODERATE) | l. 31 ✓ | **Sim.** `gerar_rrd.py:205-209` classifica por `ds_origem_receita`. `mea_04_output.txt`: R$ 12,42 mi (2018) e R$ 56,11 mi (2022) de "Outros recursos" na origem partidária. `19_notas_redacao.csv` l. 5. | código + evidência |
| STA-3-001 (MAJOR) | l. 107 ✓ | **Sim, e com artefato do próprio autor.** `reports/resultados-validacao-top-necr/validade_expost.csv`, linha "Apenas recebedores positivos": lift 1,782 (2018) e 2,048 (2022), contra 1,982 e 2,117 para "Todos os candidatos". | artefato |
| STA-3-002 (MAJOR) | l. 147 ✓ | **Parcialmente.** Os números batem (`sta_bootstrap_diferencas.csv`: lift eleitos 2022−2018 = +0,136 [−0,067; +0,342]). Mas `afirmacao_do_autor` exagera: a l. 147 diz "cerca do dobro, em ambos os ciclos" e não lê 1,98 → 2,12 como movimento. Ver conflito C4. | artefato + leitura do texto |
| STA-3-003 (MAJOR) | l. 173 ✓ | **Sim.** `validade_interna.csv`: "Núcleo = lista inteira" 207 / 100 e "Fronteiras comparáveis" 579 / 548. `sta_media_razoes_vs_razao_somas.csv`: participação em A0 de 27,4 % / 2,1 % (competitivos); lift sem essas listas 2,204 / 1,909. | artefato + evidência |
| STA-3-004 (MAJOR) | l. 179 ✓ | **Números sim, inferência não.** `sta_lift_por_sexo.csv` confere (homens 1,633 / 1,755). O chair contesta que a estratificação implemente o contrafactual "sem cotas". Ver conflito C2. | evidência + análise |
| RES-3-001 (MAJOR) | l. 179, placeholder literal ✓ | **Sim.** 4,47 % vs 14,93 % (2018) e 5,96 % vs 17,29 % (2022). Triangulado: o mesmo valor aparece em `res_recompute_cap3.out`, `sta_nucleo_por_sexo.csv` e `mea_03_output.txt` (d). | 3 recomputações independentes |
| RES-3-004 (MAJOR) | l. 173 (com elisão) ✓ | **Sim.** Pivot do chair em `reports/sensibilidade-top-x/resumo_nacional.csv`: lifts Top-X% entre 1,375 e 3,599; só 2 de 24 em [1,8; 2,0] (Top-80% competitivos: 1,926 e 1,980). Cobertura de eleitos em 2018 = 86,74 %, logo "acima de 87 %" é falso. | recomputação |
| RES-3-003 (MODERATE) | l. 149, literal ✓ | **Sim.** Teste de caminho a partir de `tese/`: 3 MISSING e 2 OK. | teste de arquivo |
| MEA-3-007 (MODERATE) | l. 155 ✓ | **Sim na parte verificável.** `grep -ci "piso\|teto"` no capítulo = 0. Piso/arredondado/teto estão em `mea_03_output.txt` (c), a partir de `df_cobertura_top_necr_resumo.csv`. A frase atribuída à nota formal não é verificável (§0). | grep + artefato |

## 2. Agrupamento: finding → issue

| Finding | Agente | Sev. agente | Issue | Problema comum do issue (1 frase) |
|---|---|---|---|---|
| MEA-3-001 | measurement | MAJOR | **I-3-001** | O histórico eleitoral municipal é ligado ao CPF pela chave (ano, UF, número), que não é única, e isso corrompe a flag competitiva, a referência ex-ante de todo o capítulo. |
| MEA-3-002 | measurement | MAJOR | **I-3-002** | A definição de "competitivo" no texto (l. 64 × l. 68) é contraditória e não é a implementada (Presidente, Distrital, 10 % em majoritárias, janela 2020). |
| STA-3-001 | statistics | MAJOR | **I-3-003** | O universo do sorteio de referência (todas as C_l, inclusive quem recebeu zero) não é declarado nem justificado. Entre recebedores, o lift de 2018 cai para 1,69 / 1,78. |
| MEA-3-004 | measurement | MODERATE | I-3-003 | idem |
| RES-3-004 | results | MAJOR | **I-3-004** | A síntese "1,9 se repete em 2018 e 2022 … e em quase todos os limiares" não corresponde à evidência: Top-X% vai de 1,38 a 3,60; a igualdade entre eleições depende da composição; "acima de 87 %" é falso em 2018. |
| STA-3-003 | statistics | MAJOR | I-3-004 | idem (listas com k = C pesam 27 % de A0 em 2018 e 2 % em 2022) |
| RES-3-001 | results | MAJOR | **I-3-005** | "Estimativa conservadora" por efeito das cotas é afirmada sem cálculo e com placeholder vazio. A única versão computável não sustenta a direção para o lift. |
| MEA-3-008 | measurement | MODERATE | I-3-005 | idem |
| STA-3-004 | statistics | MAJOR | I-3-005 | idem |
| STA-3-002 | statistics | MAJOR | **I-3-006** | Nenhum indicador ou comparação tem faixa de variabilidade (permutação, bootstrap por lista ou por partido), embora o autor já tenha 10.000 sorteios. |
| STA-3-008 | statistics | MODERATE | I-3-006 | idem (nível de cluster: lista × partido) |
| MEA-3-006 | measurement | MODERATE | **I-3-007** | Lift, razão de coberturas e razão de precisões são o mesmo número por identidade, mas o texto os apresenta como três confirmações. |
| STA-3-005 | statistics | MODERATE | I-3-007 | idem |
| MEA-3-003 | measurement | MODERATE | **I-3-008** | "Fundos públicos" rotula uma variável definida por origem partidária, não por fonte FEFC/FP. |
| MEA-3-005 | measurement | MODERATE | **I-3-009** | A unidade "lista/nominata" é partido × UF, mas em 2018 a lista eleitoral era a coligação (85 %) e em 2022 a federação (25 %). A convenção não é declarada. |
| MEA-3-007 | measurement | MODERATE | **I-3-010** | A seção de robustez apresenta o Top-X% (outro construto) como teste da arbitrariedade do Top-NECr e omite piso/teto, a robustez do próprio Top-NECr. |
| STA-3-007 | statistics | MODERATE | **I-3-011** | A monotonia acumulada do Top-X% é lida como "assinatura de camadas", mas a evidência direta são os lifts marginais por faixa (< 1 acima de ~80 % da massa), que existem e não são reportados. A parte (c) foi absorvida em I-3-004. |
| STA-3-006 | statistics | MODERATE | **I-3-012** | Razões de somas nacionais ponderam pelas listas grandes. Nem a convenção nem a dispersão entre listas são declaradas (mediana do lift por lista 2,0 / 1,9). |
| RES-3-003 | results | MODERATE | **I-3-013** | As Figuras 3–5 não resolvem porque os PNGs foram movidos para `tese/reports/`. A nota formal também sumiu. |
| RES-3-002 | results | MODERATE | **I-3-014** | Números da Discussão (l. 175–177) seguem provisórios ou imprecisos: colchetes, "candidaturas" onde são posições (Σk), "entre 4 e 7 vezes" quando o valor é 7,45. |
| MEA-3-011 | measurement | MINOR | I-3-014 | idem |
| RES-3-008 | results | MINOR | I-3-014 | idem |
| MEA-3-009 | measurement | MINOR | **I-3-015** | Convenções de denominador não declaradas: listas sem recursos continuam em ΣG; o grupo competitivo usa N e k válidos. |
| MEA-3-010 | measurement | MINOR | I-3-015 | idem |
| RES-3-006 | results | MINOR | **I-3-016** | O universo das médias de competitivos por lista (financiadas: 1,11 / 1,98; todas: 1,03 / 1,81) não é declarado. |
| RES-3-007 | results | MINOR | **I-3-017** | "Listas dobraram" vale para a mediana (×2,25), não para a média (×1,53) nem para o total (+27 %). |
| RES-3-009 | results | MINOR | **I-3-018** | As legendas das Figuras 1–5 omitem universo, painéis e o significado das linhas de referência. |
| RES-3-005 | results | MODERATE | **I-3-019** | Cabeçalho "## Discussão" duplicado e vazio (l. 169). |
| STA-3-009 | statistics | MINOR | **I-3-020** | "Núcleos maiores elevam por construção a cobertura" só vale para cortes aninhados. |

Por que alguns agrupamentos não foram feitos:
- **I-3-001 × I-3-002** tratam do mesmo objeto (flag competitiva), mas são defeitos distintos: um bug de ligação CPF ↔ resultado, que existe sob qualquer definição, e uma divergência de construto entre texto e código. Correções distintas, uma única regeneração. Recomenda-se que o pass 2 registre **I-3-002 → I-3-001** como dependência: decidir o construto antes de regenerar a base.
- **I-3-003 × I-3-004**: ambos mexem no denominador do lift, mas por mecanismos diferentes (quem pode ser sorteado × listas em que o núcleo é a lista inteira) e com ações diferentes (declarar o nulo × reescrever a síntese e reportar a variante com fronteira comparável). Juntos, mostram que o nível do lift em 2018 vai de 1,69 a 2,20 conforme convenções não declaradas, e isso reforça que a "estabilidade do 1,9" não é um fato robusto.
- **I-3-010 × I-3-011**: o primeiro trata do *que* a robustez testa; o segundo, do *que o gradiente prova*. Ações diferentes.
- **I-3-006 × I-3-004**: o bootstrap de STA-3-002 (diferença de lift entre anos com IC contendo zero) é compatível com "da mesma ordem". Não contradiz a síntese: ajuda a reescrevê-la. Ficam separados porque I-3-006 pede um acréscimo de método (faixas) e I-3-004 pede correção de interpretação.

## 3. Conflitos e decisões provisórias

### C1. Severidade do universo do sorteio (MEA-3-004 MODERATE/micro × STA-3-001 MAJOR/macro) → I-3-003
- **Diagnóstico:** idêntico nos dois, com os mesmos números (1,98 → 1,78; 1,87 → 1,69 em 2018). O autor já tem a variante em `validade_expost.csv`.
- **Leitura do chair:** o nulo define o que o lift mede. Com todas as C_l, parte do excesso é "receber × não receber", não ordenação entre financiados. "Quase 90 % mais" (l. 143) vira ~69 % em 2018 sob o nulo exigente. A conclusão "lift > 1" sobrevive, porque o observado está fora da faixa de permutação nos dois nulos. A leitura quantitativa da l. 143 e da l. 175, não.
- **Decisão provisória: MAJOR, confiança alta.** Pela rubrica, a mudança é de especificação/interpretação, não só de redação.

### C2. Cotas e "estimativa conservadora" (RES-3-001 MAJOR × MEA-3-008 MODERATE × STA-3-004 MAJOR, confiança média) → I-3-005
- **Divergência de diagnóstico:**
  - RES diz que "a direção afirmada se confirma", mas se refere só à premissa (mulheres menos competitivas: 4,5 % × 14,9 %).
  - MEA diz que a premissa se sustenta e o contrafactual não foi computado, logo o claim é *unsupported*.
  - STA diz que o claim é *contradicted* para o lift, porque o lift estratificado entre homens (1,63 / 1,75) é menor que o agregado (1,87 / 1,89).
- **Evidência lida pelo chair:** `sta_lift_por_sexo.csv`, `sta_nucleo_por_sexo.csv`, `mea_03_output.txt` (d). Três pontos:
  - A estratificação por sexo **não** implementa "retirar as cotas". Ela elimina o componente entre sexos do lift, mas não simula a realocação que o partido faria sem a obrigação legal. Por isso não prova o sinal oposto.
  - Ainda assim, dois fatos enfraquecem a premissa operacional do autor ("uma fração do núcleo é ocupada por candidaturas que o partido financia porque a lei manda, e isso puxa a precisão para baixo"). Primeiro, a participação das mulheres nas posições do núcleo (32,9 % / 36,2 %) é quase igual à participação delas nas candidaturas (31,7 % / 35,2 %). Segundo, o lift *entre mulheres* (1,63 / 1,81) é igual ou maior que o *entre homens*, ou seja, as mulheres no núcleo não são alocadas ao acaso quanto à competitividade.
  - "Puxa a precisão para baixo" é verdade só no sentido trivial de que a taxa-base de competitivas entre mulheres é menor. A precisão não é "o número que interessa" (l. 175), e o lift não mostra o viés alegado.
- **Decisão provisória: MAJOR, confiança média; claim C3.9.07 = `unsupported`** (e não `contradicted`). A frase qualifica o resultado central como limite inferior sem cálculo e com placeholder vazio. Precisa ser retirada ou testada, o que é mudança de interpretação. A confiança fica média porque o contrafactual admite mais de uma operacionalização.
- **Para o adversarial:** decidir se a estratificação de STA-3-004 justifica `contradicted`. A regra do pass 2 ("status mais conservador") levaria a `contradicted`; o chair propõe `unsupported` pelo motivo acima.

### C3. Validade dos números de competitivos (RES e STA "supported" × MEA "partially_supported") → I-3-001, I-3-002
- **Divergência:** RES (C3.6.01, C3.7.01–03) e STA (C3.5.01–02) dão *supported* a 886 / 1.287, "> 80 %", 30,9 % e 1,87. MEA dá *partially_supported*.
- **Leitura do chair:** não há contradição factual. RES e STA replicaram a flag a partir de `cap3_cs_features.py` sobre `rrd_df_novo.parquet`, isto é, reproduziram a variável da base. MEA auditou a *construção* dessa variável a partir dos brutos. O chair confirmou a anomalia (`n_eleicoes_prefeito` = 46 etc.). Reproduzir um número não valida a medida.
- **Decisão provisória:** status *partially_supported* para C3.6.01, C3.7.01, C3.7.02 e C3.7.03. As "verificações que passaram" de RES e STA sobre competitivos devem ser lidas como "o texto reproduz a base", não como "a medida está correta". A faixa de variação sob definições alternativas fica documentada: cobertura 75,4–81,2 %, lift 1,77–1,89.

### C4. Severidade da ausência de variabilidade (STA-3-002 MAJOR) → I-3-006
- **Tensão:** STA lê que o texto trata 1,98 → 2,12 como movimento. Na l. 147 o texto diz "Isto é, cerca do dobro, em ambos os ciclos", que é uma leitura de igualdade aproximada, e RES valida exatamente isso. A única diferença entre anos que o texto afirma e explica é a queda da precisão (19,2 → 12,4 %), atribuída ao crescimento de Σk, o que é aritmética.
- **Leitura do chair:** o teste que importa (lift ≠ 1) é esmagador (p < 0,0005 na permutação; IC por lista longe de 1). A falta de faixas é uma lacuna de apresentação e não muda nenhuma conclusão escrita. As afirmações de igualdade entre anos que realmente excedem a evidência já estão em I-3-004.
- **Decisão provisória: MODERATE, confiança alta.** STA-3-008 (cluster por partido) foi incorporado aqui como especificação de *como* reportar as faixas.

### C5. Status da síntese "1,9" (RES `contradicted` × STA e MEA `partially_supported`) → I-3-004
- **Leitura do chair:** a frase da l. 173 tem quatro partes:
  1. "1,9 no Top-NECr": 1,87–2,12. É aproximadamente verdade; para eleitos, "cerca de 2" é mais exato.
  2. "se repete em 2018 e 2022": descritivamente sim sob o universo completo, mas sensível à composição (2,20 × 1,91 sem listas k = C; 1,69 × 1,85 sob nulo de recebedores). A direção da mudança não é identificável.
  3. "em quase todos os limiares do Top-X%": falso, 2 de 24.
  4. "acima de 87 % dos eleitos": falso em 2018.
- **Decisão provisória: claim C3.9.01 = `contradicted`** (a frase como escrita), C3.9.02 = `partially_supported`. Issue MAJOR, confiança alta: é a síntese-título do capítulo.

### C6. Severidade de RES-3-005 (MODERATE) → I-3-019
- Um cabeçalho vazio duplicado é formatação sem efeito no argumento. **Decisão provisória: MINOR.**

### C7. MEA-3-007 × o próprio texto (conflito interno ao capítulo, registrado pelo chair)
- A l. 155 apresenta o Top-X% como teste da "arbitrariedade do recorte … pelo Top-NECr". A l. 177 diz que "a robustez ao limiar importa menos como defesa do Top-NECr do que como evidência de que a estrutura existe independentemente de onde se corta". O autor já concede parte do diagnóstico de MEA na Discussão. Isso vai para o `problema` de I-3-010 e não altera a severidade (MODERATE).

### C8. Colisão de IDs de claims (procedimental)
Os três agentes numeraram `C3.{secao}.{seq}` de formas diferentes:
- MEA contou `##`/`###` com a Discussão = 9.
- RES contou também o cabeçalho vazio da l. 169, com a Discussão = 10.
- STA renumerou as seções à parte (Amplitude = 4, Priorização = 5, Top-X% = 6, Discussão = 7).

Resultado: o mesmo ID designa claims diferentes; por exemplo, C3.7.01 é "> 80 %" em MEA e RES e "1,9 resume" em STA. RES-3-003 cita `C3.8.06`, que não existe em nenhum relatório.

**Numeração canônica adotada** (PROTOCOL §4: ordem dos `##`/`###` com conteúdo; o cabeçalho vazio da l. 169 não conta, para o ID não mudar quando I-3-019 for corrigido): 1 = `## Dados…`, 2 = Universo, 3 = Seleção do núcleo (inclui Top-NECr e Top-X%), 4 = Validação (competitivos e métricas), 5 = `## Resultados`, 6 = Amplitude, 7 = Priorização Top-NECr, 8 = Robustez, 9 = Discussão.

| Canônico | Linha | Claim | MEA | STA | RES |
|---|---|---|---|---|---|
| C3.2.01 | 25 | 7.630 / 9.675 candidaturas | C3.2.01 | — | C3.2.01 (parte) |
| C3.2.02 | 27 | 859 / 711 listas; 73 / 63 sem recursos; 3 / 0 eleitos | C3.2.02 | — | C3.2.01 (parte) |
| C3.3.01 | 38 | NECr = 1/Σs² | C3.3.01 | — | — |
| C3.3.02 | 49 | k = ⌊NECr+0,5⌋; empates; k = 0 | C3.3.02 | — | — |
| C3.3.03 | 56 | k^τ do Top-X% | C3.3.03 | — | — |
| **C3.3.04** | 31 | "exclusivamente … fundos públicos" | **C3.2.03** (seção errada) | — | — |
| C3.4.01 | 68 | definição de competitivo | C3.4.01 | — | — |
| C3.4.02 | 68 | janela 1998–2016 / 1998–2018 | C3.4.02 | — | — |
| C3.4.03 | 98 | fórmulas cobertura/precisão/lift | C3.4.03 | — | — |
| C3.4.04 | 107 | referência analítica G k / C | C3.4.04 | — | — |
| C3.6.01 | 115 | 886 / 1.287; +27 % / +45 % | C3.6.01 | **C3.4.01** | C3.6.01 |
| C3.6.02 | 117 | mediana C 4 / 9; competitivos por lista: mediana 1, média 1,11 / 1,98 | C3.6.02 | — | **C3.6.02 + C3.6.03** |
| C3.6.03 | 121 | NECr mediano 1,88 / 4,81 | C3.6.03 | — | **C3.6.04** |
| C3.6.04 | 127–131 | C/NECr e NECr/C (medianas e médias) | C3.6.04 | — | **C3.6.05** |
| C3.7.01 | 139 | > 80 % competitivos; acaso 43,2 / 43,7 | C3.7.01 | **C3.5.01** | C3.7.01 |
| C3.7.02 | 141 | precisão 30,9 / 27,8; acaso 16,5 / 14,7 | C3.7.02 | **C3.5.02** | C3.7.02 |
| C3.7.03 | 143 | lift 1,87 / 1,89; "quase 90 % mais" | C3.7.03 | **C3.5.04** | C3.7.03 |
| C3.7.04 | 145 | 86,7 / 92,6 % dos eleitos; "o dobro" | C3.7.04 | **C3.5.05** | C3.7.04 |
| C3.7.05 | 147 | precisão eleitos 19,2 / 12,4; lift 1,98 / 2,12; "cerca do dobro" | C3.7.05 | **C3.5.06 + C3.5.07** | C3.7.05 |
| C3.8.01 | 157 | Top-50 % > 50 % cobertura; cresce com limiar | C3.8.01 | **C3.6.01** | C3.8.01 |
| C3.8.02 | 159 | lift > 1 em todos os limiares; 1,53 / 1,38 no Top-95 % | C3.8.02 | **C3.6.03** | C3.8.02 |
| C3.8.03 | 161 | mais competitivos dentro que fora | — | **C3.6.04** | C3.8.03 |
| C3.8.04 | 165 | eleitos: cobertura maior; lifts > 1 (Fig. 5) | — | **C3.6.05** | C3.8.04 (e o "C3.8.06" de RES-3-003) |
| C3.9.01 | 173 | "1,9 … se repete … quase todos os limiares" | **C3.9.03** | **C3.7.01** | **C3.10.01** |
| C3.9.02 | 173 | cobertura > 80 % competitivos e > 87 % eleitos | — | — | **C3.10.02** |
| C3.9.03 | 175 | ~2,3 mil / 3,8 mil; 4–7× cadeiras | **C3.9.01** | — | **C3.10.03** |
| C3.9.04 | 175 | queda da precisão 19,2 → 12,4; "acerta o dobro"; médias 1,1 / 2,0 × NECr 3,0 / 5,9 | — | **C3.7.02** | **C3.10.04** |
| C3.9.05 | 177 | Top-50 %: precisão e lift sobem, cobertura cai; gradiente monotônico | — | **C3.7.04** | **C3.10.05** |
| C3.9.06 | 177 | "assinatura de distribuição em camadas" | — | **C3.7.05** | — |
| C3.9.07 | 179 | cotas → "estimativa conservadora" | **C3.9.02** | **C3.7.06** | **C3.10.06** |
| C3.9.08 | 181 | NECr/C estável, "listas dobraram"; "mudou de forma" | — | **C3.7.07** | **C3.10.07** |

Os `claims` de `issues_draft.yaml` já usam os IDs canônicos. O pass 2 deve usar esta tabela ao mesclar em `claims/claims.yaml`.

**Status provisório dos claims com divergência entre agentes:**

| Claim | MEA | STA | RES | Provisório (chair) |
|---|---|---|---|---|
| C3.6.01 | partially | supported | supported | partially_supported (C3) |
| C3.7.01 | partially | supported | supported | partially_supported (C3) |
| C3.7.02 | partially | supported | supported | partially_supported (C3) |
| C3.7.03 | partially | partially | supported | partially_supported (C1, C3) |
| C3.7.04 | supported* | supported* | supported | supported, com concerns (identidade com o lift; nulo) |
| C3.7.05 | supported* | partially | supported | partially_supported (C1) |
| C3.6.02 | supported* | — | partially (C3.6.03) | partially_supported (universo não declarado) |
| C3.9.01 | partially | partially | contradicted | contradicted (C5) |
| C3.9.04 | — | supported (média) | supported | partially_supported ("acerta o dobro" depende do nulo; C1) |
| C3.9.07 | unsupported | contradicted (média) | unsupported | unsupported (C2) |
| C3.9.08 | — | partially | partially | partially_supported |

\* supported com concerns que apontam para outro issue.

## 4. Avaliação macro consolidada

Cadeia do capítulo, com o estado de cada elo segundo os três agentes e a checagem do chair:

| Elo | Conteúdo | Estado |
|---|---|---|
| Pergunta | Os partidos priorizam candidaturas na alocação intralista dos recursos (*gatekeeping*)? (l. 5–11) | Clara. |
| Teoria → hipótese | Priorização estratégica: o núcleo financiado deve concentrar credenciais prévias e sucesso posterior. | Enunciada, sem hipóteses alternativas que gerariam a mesma associação (p.ex. capacidade própria de arrecadação, incumbência como regra de alocação). **Não avaliado neste run**: não houve theory ou methodology reviewer. |
| Desenho | Núcleo endógeno (Top-NECr; Top-X% como alternativa) comparado a uma referência ex-ante (competitivos) e uma ex-post (eleitos) contra um sorteio intralista. | Adequado para rejeitar "alocação ao acaso". Convenções não declaradas mudam o *nível* do resultado: universo do sorteio (I-3-003), unidade partido × UF sob coligações/federações (I-3-009), listas com núcleo = lista (I-3-004). |
| Medida — núcleo | NECr, k, empates fracionários, Top-X%, H, cobertura, precisão, lift. | **Sólido.** Reproduzido lista a lista (1.570 listas) por MEA e nos agregados por STA e RES. |
| Medida — referência ex-ante | Flag `candidato_competitivo`. | **Frágil.** Não é a definição do texto (I-3-002) e está corrompida pela ligação CPF ↔ histórico municipal (I-3-001). Rótulo "fundos públicos" impreciso (I-3-008). |
| Resultado | Lift 1,87–2,12; cobertura 81–93 %; muito fora da faixa de permutação. | **Robusto no sinal.** O nível varia com convenções: 1,69–2,20 (2018) conforme nulo e composição; 1,77–1,89 conforme a flag. Sem faixas de variabilidade (I-3-006). |
| Conclusão | "Partidos priorizam, e a priorização é observável antes do voto" (l. 183). Síntese "1,9 se repete" (l. 173); "estimativa conservadora" (l. 179); "mudou de forma" (l. 181). | O núcleo da conclusão sobrevive em todas as variantes recomputadas. As três qualificações da Discussão excedem a evidência (I-3-004, I-3-005) e há números provisórios (I-3-014). |

**Elo mais fraco: a medida da referência ex-ante (flag "competitivo").** É o único elo em que o objeto medido não é o objeto definido no texto, e em que a própria base está corrompida por um bug de ligação. É justamente esse elo que sustenta a parte distintiva da conclusão ("a priorização é observável antes do voto"). As recomputações indicam que a conclusão numérica sobrevive (lift 1,77–1,89; cobertura 75–81 %), mas "> 80 %" e "4/5" deixam de valer sob as regras do próprio código com CPF correto.

Segundo elo mais fraco: resultado → conclusão na Discussão (I-3-004, I-3-005).

## 5. Encaminhamento ao adversarial

Issues MAJOR para ataque: I-3-001, I-3-002, I-3-003, I-3-004, I-3-005. Pontos específicos:
- **I-3-001:** a severidade deveria ser CRITICAL, dado que "> 80 %" (l. 139, 173) e "4/5" deixam de valer com CPF correto sob as regras do código (75,4 / 76,5 %)? Ou MODERATE, dado que a flag como escrita no texto dá 80,7 / 81,2 %? A reconstrução de MEA (QE estadual = válidos/eleitos; 94–97 % de CPFs localizados) é confiável o bastante?
- **I-3-002:** a correção pode ser só textual? Nesse caso, MODERATE.
- **I-3-003:** sortear entre todas as C_l é defensável como o nulo teoricamente certo (a decisão de não financiar também é *gatekeeping*)? Nesse caso, basta declarar.
- **I-3-005:** `unsupported` ou `contradicted` (C2).
- **I-3-006** (rebaixado de MAJOR para MODERATE, C4): confirmar ou reverter.
