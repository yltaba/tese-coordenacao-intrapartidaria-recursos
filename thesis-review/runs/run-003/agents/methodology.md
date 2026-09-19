# methodology-reviewer — Capítulo 2 — run-003

## Escopo e método
- Arquivos lidos: `CLAUDE.md`, `thesis-review/PROTOCOL.md`, `rubric.yaml`, `templates/agent_report.md`, `runs/run-003/manifest.yaml`; `tese/02-literatura.qmd` (integral, com foco em "Financiamento de campanhas no Brasil" e "Argumento" {#sec-argumento}; **não existe seção "Plano da tese"** — o plano está nas l. 214–218); `tese/03-medindo-coordenacao-intrapartidaria.qmd` e `tese/04-mecanismo-causal-coordenacao.qmd` (integrais, para o diálogo entre capítulos); `notes/daily/*.md` (28/08 a 18/09); `src/2_gold/cap3_cs_features.py` (definição de `candidato_competitivo`); `src/1_silver/gerar_rrd.py` l. 288–332 (origem/fonte das receitas); `tese/reports/regressao-fracionaria/{coeficientes,amostra}.csv`; `tese/reports/lift-magnitude-partido/{lift_por_magnitude,lift_por_partido_ano}.csv`.
- Recomputações (script `evidence/met_cap2_alternativas.py`, saída `evidence/met_cap2_alternativas.out`), sobre `data/processed/rrd_df_novo.parquet` e `receitas.parquet`:
  A. composição da receita dos candidatos a DF por origem; B. composição de "Recursos de partido político" por fonte; C. recursos não partidários por credencial e correlação intralista entre parcela partidária e parcela não partidária; D. candidaturas com R=0 em listas financiadas e *lift* do Top-NECr com referência restrita a quem recebeu algum recurso; F. parcela dos recursos partidários (DF) destinada a mulheres; G. composição do grupo com credencial; H. *lift* por magnitude contra o teto mecânico `min(G,k)`.
- Não foi possível verificar: páginas citadas de @silvacervi2017 (p. 85) e @cheibubsin2020 (p. 79); estrutura de coligações de 2018 (a base não tem coluna de coligação); data de abertura de conta/CNPJ das campanhas (Cap. 4); o locus decisório (diretório nacional × estadual) das transferências.

## Cadeia do capítulo (7 elos, registrada antes da crítica)
1. **Pergunta**: como os partidos alocam, entre as candidaturas da lista aberta, o dinheiro de campanha que controlam (l. 129) — e se essa alocação coordena a competição intralista.
2. **Argumento**: as regras do FEFC (83% por desempenho na Câmara), do FP (95% por votos) e a cláusula de desempenho amarram a sobrevivência financeira do partido à eleição para DF → incentivo à alocação "seletiva e estratégica" (l. 161–169, 174), entendida como instrumento de coordenação (l. 176).
3. **Hipótese**: os partidos priorizam candidaturas com credenciais eleitorais prévias *porque* são sinais de contribuição ao desempenho coletivo; implicação: presença desproporcional, "em relação ao acaso", de credenciados entre os que concentram recursos (l. 204).
4. **Desenho**: observacional, duas eleições (2018, 2022), comparação dentro da nominata, só informação anterior ao pleito (l. 212–214); a ação é atribuída ao partido por suposto (l. 180).
5. **Variável**: credencial ex-ante (vitória prévia ou ≥10% do QE em disputa anterior, adaptando Cheibub & Sin); R_il = recursos de origem partidária; núcleo definido pela própria distribuição.
6. **Teste**: (i) composição do núcleo vs. acaso; (ii) parcela intralista por cargo; (iii) "priorização temporal ao núcleo priorizado" (l. 214).
7. **Conclusão licenciada pelo desenho**: associação descritiva, com precedência temporal, entre credenciais e prioridade financeira. **Não** licencia o "porque" da l. 204, nem "coordenação" como efeito sobre o desempenho coletivo, nem a escolha entre as rivais que a própria l. 178 nomeia.

## Avaliação macro
A cadeia se sustenta até o elo 5 como **desenho descritivo com precedência temporal**, e essa é a principal virtude metodológica do Argumento: a separação ex-ante/ex-post (l. 212–214) está bem motivada, bem implementada no código (`cap3_cs_features.py` l. 97–100) e resolve a reversão temporal voto→recurso para a hipótese de composição. Há três rupturas. (1) **Elo 2→3**: o incentivo de sobrevivência não implica concentração em credenciados; com *pooling* e 35% do FEFC/95% do FP seguindo votos, ele é compatível também com dispersão ou foco em candidatos marginais, e o texto não diz por que prevalece a concentração. O Cap. 4 (l. 25) chega a derivar do mesmo contexto institucional a previsão oposta (desconcentração em 2022). (2) **Elo 3→6**: a l. 178 reconhece autofavorecimento, barganha e ameaça de saída como rivais, mas nenhuma das três frentes as discrimina; a implicação testada é comum a todas. O repositório já tem um teste parcialmente discriminante (votação ≥10% do QE sem vitória: razão 2,89/1,70) que o Argumento não enuncia. (3) **Elo 6 (frente iii)**: não há hipótese temporal derivada, e a frente promete "priorização temporal ao núcleo priorizado", enquanto o Cap. 4 testa credencial, não núcleo. Além disso, o conceito "coordenação" não é definido de modo observável, e o que se mede é priorização. Dois pontos de comparabilidade (coligações em 2018; referência aleatória inflada por candidaturas sem recurso) e um gradiente por magnitude que é, em boa parte, mecânico (recomputado) enfraquecem leituras que o Cap. 3 apoia nas expectativas do Cap. 2. O capítulo funciona como enquadramento de uma **evidência de padrão compatível com estratégia**, e não como teste de mecanismo; o texto do Argumento ainda não assume esse limite.

## Achados

```yaml
id: MET-2-001
titulo: "A implicação testada não discrimina o mecanismo proposto das rivais que o próprio Argumento nomeia"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 204
  secao: "## Argumento"
  trecho: "O argumento desta tese é que os partidos priorizam financeiramente candidaturas com credenciais eleitorais prévias porque estas constituem sinais da capacidade destes candidatos em contribuir para o desempenho coletivo da legenda."
afirmacao_do_autor: "A priorização de credenciados se explica pela busca do desempenho coletivo; a expectativa é presença desproporcional de credenciados entre os mais financiados."
problema: "A l. 178 admite que 'Esta seletividade pode refletir autofavorecimento, com captura de incumbentes sobre os diretórios que decidem a alocação, indicar simplesmente barganha, ou uma ameaça de sair do partido e levar votos consigo', mas a única implicação enunciada (l. 204) é prevista igualmente por todas essas rivais e ainda por duas não nomeadas: (a) inércia da alocação (quem foi financiado antes acumulou credencial e é financiado de novo) e (b) atração de recursos pelo próprio candidato (lado da demanda), que move dinheiro partidário e privado na mesma direção. Nenhuma das frentes (i)–(iii) (l. 214) é desenhada para separar essas explicações. A 'ameaça de sair e levar votos' é, além disso, observacionalmente equivalente ao mecanismo da tese: ela pressupõe que os votos do candidato valem para a legenda. O 'porque' da l. 204 fica, assim, além do que o desenho identifica. Há no repositório uma implicação parcialmente discriminante que o Argumento não enuncia: a captura por incumbentes/dirigentes não prevê prioridade a quem teve votação expressiva e perdeu; a busca de desempenho coletivo prevê. A nota do autor de 18/09 registra exatamente essa ideia, que não chegou ao texto."
evidencia:
  tipo: recomputacao
  fontes:
    - "tese/02-literatura.qmd:178"
    - "tese/02-literatura.qmd:204"
    - "tese/02-literatura.qmd:214"
    - "tese/reports/regressao-fracionaria/coeficientes.csv (variavel=qe_sem_vitoria, R2)"
    - "notes/daily/2026-09-18.md (última linha)"
    - "thesis-review/runs/run-003/evidence/met_cap2_alternativas.out (blocos C e G)"
  detalhe: "Candidaturas com credencial só por votação (≥10% QE, sem vitória acima de vereador): 235 de 973 em 2018 e 409 de 1.354 em 2022 (bloco G). Razão de parcelas intralista: 2,886 [IC 2,185–3,812] em 2018 e 1,701 [1,476–1,961] em 2022 (coeficientes.csv). É evidência contra a captura pura por mandatários, mas não contra barganha nem contra a atração de recursos pelo candidato. Correlação intralista entre a parcela de recursos partidários e a parcela de recursos não partidários da candidatura: +0,407 (2018, n=7.244) e +0,337 (2022, n=9.131) (bloco C). O dinheiro do partido e o dinheiro privado vão para as mesmas candidaturas, o que é compatível com um rival de 'força do candidato', que o Argumento não nomeia."
severidade: MAJOR
confianca: alta
recomendacao: "(1) Reformular a l. 204 como expectativa de padrão ('se a distribuição busca desempenho coletivo, espera-se...'), sem o 'porque' como tese demonstrável. (2) Acrescentar ao Argumento, para cada rival da l. 178, o que ela prevê de diferente: captura não prevê prêmio a perdedores bem votados; desempenho coletivo prevê. Apontar o coeficiente de `qe_sem_vitoria` do Cap. 3 como o teste que separa essas duas. (3) Declarar que barganha, ameaça de saída e atração de recursos pelo candidato não são separadas pelo desenho, e nomear a inércia da alocação como rival."
claims: [C2.7.03, C2.7.07]
```

```yaml
id: MET-2-002
titulo: "O incentivo de sobrevivência não implica concentração em credenciados; a direção da estratégia não é derivada"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 174
  secao: "## Argumento"
  trecho: "O vínculo entre desempenho eleitoral e recursos recebidos pelos partidos presente nas regras de financiamento gera os incentivos para que as legendas distribuam seus recursos seletivamente, visando a ampliação do quociente partidário"
afirmacao_do_autor: "As regras de financiamento geram incentivo à distribuição seletiva, e a seletividade favorece credenciados."
problema: "O capítulo documenta que 35% do FEFC e 95% do FP seguem votos (l. 159, 163), e que, com *pooling*, 'o voto depositado em cada candidatura individual beneficia o cálculo das cadeiras' (l. 33). Sob esse incentivo, a alocação ótima pode ser dispersa (muitos coletores de voto) ou concentrada em candidatos marginais, perto do corte, e não necessariamente em credenciados. O Argumento passa de 'incentivo' (l. 174) a 'priorizar credenciados' (l. 204) sem o elo que escolhe entre essas estratégias. O ponto já está registrado como comentário no próprio arquivo (l. 183 '[A2] (b) VOTOS x CADEIRAS'; l. 208 '[A7] (c) BURACO NO MECANISMO'), mas o texto do corpo segue inalterado. Consequência entre capítulos: o Cap. 4 (l. 25) afirma que o fim das coligações e a cláusula 'criaram incentivos adicionais para que os partidos alocassem recursos de forma mais desconcentrada', ou seja, deriva do mesmo contexto uma previsão que o Cap. 2 não formula e que tensiona a l. 204. Não há, portanto, expectativa ex-ante sobre a diferença entre 2018 e 2022. As leituras da queda 2018→2022 nos rascunhos de Discussão dos Caps. 3 e 4 ficam sem ancoragem teórica."
evidencia:
  tipo: textual
  fontes:
    - "tese/02-literatura.qmd:33"
    - "tese/02-literatura.qmd:159-169"
    - "tese/02-literatura.qmd:174"
    - "tese/02-literatura.qmd:183"
    - "tese/02-literatura.qmd:208"
    - "tese/04-mecanismo-causal-coordenacao.qmd:25"
  detalhe: "Nenhuma frase do corpo das seções 'Financiamento' e 'Argumento' diz por que a sobrevivência favorece concentração em quem tem histórico, em vez de dispersão. A única previsão comparativa 2018×2022 da tese está no Cap. 4, l. 25 ('de forma mais desconcentrada'), sem derivação no Cap. 2."
severidade: MAJOR
confianca: alta
recomendacao: "Incluir no Argumento o elo que falta: sob incerteza, a credencial é o único sinal ex-ante de retorno do recurso, e o retorno esperado de um real é maior onde a probabilidade de converter dinheiro em votos é maior. Ou, alternativamente, declarar que a tese não distingue concentração em credenciados de foco marginal. Enunciar também a expectativa (ou a ausência dela) para 2018×2022, para que Cap. 3 e Cap. 4 interpretem a queda à luz de algo dito antes."
claims: [C2.6.04, C2.7.01]
```

```yaml
id: MET-2-003
titulo: "A frente (iii) promete ao Cap. 4 um teste que ele não faz e não traz hipótese temporal"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 214
  secao: "## Argumento"
  trecho: "e (iii) a identificação de uma priorização temporal ao núcleo priorizado da lista."
afirmacao_do_autor: "O Cap. 4 identifica priorização temporal do núcleo priorizado."
problema: "(a) Unidade: o Cap. 4 compara candidaturas competitivas e não competitivas (l. 35, 61, 63; `figs/cap4_*` 'só por candidato competitivo/não-competitivo' segundo CLAUDE.md). Não usa o núcleo Top-NECr. O rascunho [3.D] do Cap. 3 (l. 258) argumenta que usar o núcleo seria circular, porque ele é definido pelo total recebido ao fim da campanha. Então a formulação da l. 214 promete um teste que, pelo próprio raciocínio do autor, não deve ser feito. (b) Hipótese: nada no Cap. 2 diz qual padrão temporal o argumento prevê, nem por quê. O comentário [A9] (l. 216) registra isso, e a nota de 18/09 também ('agentes dizem que a abordagem temporal não está embasada'). (c) Validade interna do evento: o Cap. 4 (l. 9) registra que o recebimento depende de registro, CNPJ e conta da campanha. A antecipação observada pode refletir a prontidão administrativa de campanhas com histórico, e não uma decisão do partido. Essa rival não aparece no Cap. 2, e o Cap. 4 conclui intenção ('os resultados indicam que partidos políticos consideram a vantagem que distribuir dinheiro antecipadamente constitui', l. 47)."
evidencia:
  tipo: textual
  fontes:
    - "tese/02-literatura.qmd:214-218"
    - "tese/02-literatura.qmd:216"
    - "tese/04-mecanismo-causal-coordenacao.qmd:9"
    - "tese/04-mecanismo-causal-coordenacao.qmd:35"
    - "tese/04-mecanismo-causal-coordenacao.qmd:47"
    - "tese/03-medindo-coordenacao-intrapartidaria.qmd:258 (comentário [3.D])"
    - "notes/daily/2026-09-18.md"
  detalhe: "Grep em 04-mecanismo-causal-coordenacao.qmd: 'Top-NECr' só aparece em comentários do revisor ([4.0], [4.1], [4.2-1], [4.1-4]), nunca no corpo. O corte usado no corpo é 'competitivos (ex-ante)'."
severidade: MAJOR
confianca: alta
recomendacao: "Reescrever a frente (iii) para o que o Cap. 4 testa ('antecipação dos repasses a candidaturas com credenciais prévias'), ou incorporar ao Cap. 4 o teste do núcleo. Derivar no Argumento uma expectativa temporal mínima (o momento do repasse como vantagem competitiva: tempo de campanha na rua, contratação), no ponto já indicado pelo comentário [2.2-2] (l. 77). Listar a prontidão administrativa como rival do *timing*, com a indicação de que o evento 'maior repasse' a atenua."
claims: [C2.7.11, C2.7.12]
```

```yaml
id: MET-2-004
titulo: "O gradiente do *lift* por magnitude é majoritariamente mecânico; o diálogo Cap. 2 ↔ Cap. 3 sobre magnitude se apoia em evidência que não o sustenta"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 118
  secao: "### Priorização financeira pelo Top-NECr"
  trecho: "Isso indica que, relativamente ao tamanho da nominata, o núcleo financiado pelo partido se torna mais discriminante nos distritos de maior magnitude."
afirmacao_do_autor: "O *lift* crescente com a magnitude mostra priorização mais discriminante nos distritos grandes, o que contraria a expectativa herdada de Carey & Shugart e de Samuels/Cox (Cap. 2, l. 25 e 121; rascunho [3.D], l. 250)."
problema: "Achado entre capítulos. A localização principal está no Cap. 3, mas a expectativa confrontada está no Cap. 2 (l. 25, 121), que não formula previsão própria sobre magnitude. Como H_l ≤ min(G_l, k_l), o *lift* agregado tem teto Σmin(G,k)/Σ(Gk/C), e esse teto cresce com o tamanho das listas. Recomputado: o teto sobe de 1,57 para 2,99 (2018) entre distritos pequenos e grandes. Normalizado pelo teto, o *lift* é plano ou levemente decrescente com a magnitude. O repositório já normaliza o *lift* por partido (`lift_por_partido_ano.csv` tem `teto_lift` e `lift_normalizado`), mas não o *lift* por magnitude (`lift_por_magnitude.csv` não tem essas colunas). A razão de parcelas da regressão intralista (4,76→13,48) não está sujeita a esse teto e continua sendo evidência do gradiente. A frase da l. 118, baseada no *lift*, não está."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-003/evidence/met_cap2_alternativas.out (bloco H)"
    - "tese/reports/lift-magnitude-partido/lift_por_magnitude.csv"
    - "tese/reports/lift-magnitude-partido/lift_por_partido_ano.csv (colunas teto_lift, lift_normalizado)"
    - "tese/02-literatura.qmd:25"
    - "tese/02-literatura.qmd:121"
  detalhe: "Lift observado reproduz a tabela tbl-cap3-01 exatamente (2018: 1,398/1,959/2,516; 2022: 1,367/1,999/2,372). Teto mecânico, 2018: 1,566/2,219/2,993; 2022: 1,608/2,376/2,855. Razão lift/teto, 2018: 0,893/0,883/0,841; 2022: 0,850/0,841/0,831. Normalizado, o gradiente se inverte levemente."
severidade: MAJOR
confianca: alta
recomendacao: "No Cap. 2: explicitar a expectativa da tese sobre magnitude (ou dizer que não há), para que o Cap. 3 não precise 'contrariar' a literatura com base em uma medida sem teto comparável. No Cap. 3 (encaminhar ao próximo run do capítulo): reportar o *lift* por magnitude junto de seu teto ou do *lift* normalizado, como já se faz por partido, e apoiar a afirmação de gradiente apenas na razão de parcelas intralista."
claims: []
nota: "Fora do capítulo em revisão; registrado porque a expectativa confrontada nasce no Cap. 2 e o rascunho [3.D] (l. 250) usa o resultado como diálogo com Carey & Shugart e Cox."
```

```yaml
id: MET-2-005
titulo: "'Coordenação' é afirmada, mas não definida de modo observável; o desenho mede priorização"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 176
  secao: "## Argumento"
  trecho: "Nesta leitura, a alocação de recursos partidários constitui um instrumento de coordenação intrapartidária, por meio do qual a organização procura orientar a competição entre seus candidatos para objetivos eleitorais coletivos."
afirmacao_do_autor: "A alocação de recursos é instrumento de coordenação intrapartidária."
problema: "O título da tese e a l. 176 usam 'coordenação' no sentido de orientar a competição para resultados coletivos. As implicações observáveis (l. 204, 214) dizem respeito à composição da prioridade financeira, isto é, a quem recebe. Nenhuma implicação trata do resultado coletivo da coordenação (por exemplo, menos votos desperdiçados, adequação do núcleo às cadeiras esperadas). O Cap. 3 (l. 76) declara que a referência ex-post aos eleitos é 'contaminada'. Resultado: o conceito fica em um patamar que o desenho não alcança, e o texto não distingue desigualdade, priorização e coordenação. O autor fez essa distinção em notas, mas ela não entrou no capítulo: 11/09 'definição de coordenação: não é concentração, mas priorização'; 13/09 'Distinga: desigualdade / priorização financeira / coordenação'. A l. 198 ([A5]) também aponta que 'parcelas maiores a um subconjunto' vale para quase qualquer distribuição desigual."
evidencia:
  tipo: textual
  fontes:
    - "tese/02-literatura.qmd:53"
    - "tese/02-literatura.qmd:176"
    - "tese/02-literatura.qmd:204"
    - "tese/02-literatura.qmd:214"
    - "tese/03-medindo-coordenacao-intrapartidaria.qmd:76"
    - "notes/daily/2026-09-11.md"
    - "notes/daily/2026-09-13.md (item 9)"
  detalhe: "Não há no Cap. 2 definição operacional de 'coordenação'. O termo aparece nas l. 53, 55, 63, 81 e 176, sempre como rótulo conceitual."
severidade: MODERATE
confianca: alta
recomendacao: "Definir no Argumento os três degraus (desigualdade → priorização → coordenação). Dizer que a tese observa a priorização orientada por sinais ex-ante e a interpreta como compatível com coordenação, sem medir o resultado coletivo. Ajustar a l. 176 de 'constitui' para 'pode operar como'."
claims: [C2.7.02]
```

```yaml
id: MET-2-006
titulo: "Comparabilidade 2018 × 2022: coligações proporcionais de 2018 ausentes do Argumento; o Cap. 3 remete a uma discussão que não existe"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 33
  secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
  trecho: "No Brasil, votos nominais em candidatos são somados para o cálculo do quociente partidário."
afirmacao_do_autor: "O pooling ocorre no nível do partido; a lista relevante é partido × UF."
problema: "Em 2018, as coligações proporcionais ainda existiam (Cap. 4, l. 25). O *pooling* e a ordenação dos eleitos ocorriam no nível da coligação, e a competição 'intralista' por cadeiras incluía candidatos de outros partidos. A unidade da tese (l = partido × UF × eleição) é a do tomador da decisão de repasse, o que se defende. Mas o Argumento (l. 174: 'ampliação do quociente partidário') e o *pooling* (l. 33) são formulados como se a regra de 2022 valesse nos dois pleitos. As palavras 'coligação/coligações' só aparecem no Cap. 2 na l. 49 (sobre Samuels 1999). O rascunho [3.D] do Cap. 3 (l. 248) diz que a pressão do fim das coligações foi 'discutida no capítulo anterior', o que não ocorre. A cota de repasse a candidaturas negras só vale em 2022 (l. 155), outra diferença de regra sem expectativa associada. O que é comparável entre os anos (a decisão intrapartidária de repasse) e o que não é (a unidade de *pooling*, a validação por eleitos, a competição intralista por cadeiras) não é dito."
evidencia:
  tipo: ausencia
  fontes:
    - "tese/02-literatura.qmd:33"
    - "tese/02-literatura.qmd:49"
    - "tese/02-literatura.qmd:174"
    - "tese/04-mecanismo-causal-coordenacao.qmd:25"
    - "tese/03-medindo-coordenacao-intrapartidaria.qmd:248 (comentário [3.D])"
  detalhe: "grep -i 'coliga' em 02-literatura.qmd: uma única ocorrência (l. 49). A base `rrd_df_novo.parquet` não tem coluna de coligação (33 colunas listadas), então a tese não pode condicionar a comparação a ela."
severidade: MODERATE
confianca: alta
recomendacao: "Acrescentar ao Cap. 2 (seção Financiamento ou Argumento) um parágrafo curto sobre as diferenças de regra 2018×2022 (coligações, cláusula crescente, cota racial), com o que cada uma implica para a alocação intrapartidária. Declarar que a unidade de decisão (partido) coincide com a unidade de *pooling* só em 2022. Isso dá base às leituras da queda 2018→2022 feitas nos Caps. 3 e 4."
claims: [C2.7.01]
```

```yaml
id: MET-2-007
titulo: "A referência 'em relação ao acaso' inclui candidaturas sem recurso algum e muda a comparação entre anos"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 204
  secao: "## Argumento"
  trecho: "a expectativa da tese é encontrar uma presença desproporcional, em relação ao acaso, de candidatos com credenciais entre os destinatários que concentram a maior parcela de recursos."
afirmacao_do_autor: "O contraste relevante é com o acaso dentro da lista."
problema: "O próprio Cap. 2 cita @hottmenezes2023 (l. 61: vagas adicionais vão para 'candidaturas fracas, com grande participação de novatos'), e as cotas de candidatura induzem nominatas com candidaturas não competitivas. O sorteio na lista inteira é, portanto, um contraste fraco: parte do *lift* vem de candidaturas que nenhuma estratégia financiaria. Recomputado: 24,5% das candidaturas de listas financiadas não receberam recurso partidário em 2018 (8,1% em 2022). Com a referência restrita a quem recebeu algum recurso, o *lift* fica em 1,70 (2018) e 1,82 (2022). Segue acima de 1, e a conclusão principal sobrevive, mas a comparação entre anos inverte: o rascunho [3.D] do Cap. 3 (l. 248) lê 1,89→1,86 como 'praticamente não muda'."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-003/evidence/met_cap2_alternativas.out (blocos D e E)"
    - "tese/02-literatura.qmd:61"
  detalhe: "2018: 786 listas, 7.395 candidaturas, 1.811 com R=0 (24,5%), H=786,8, lift (todos)=1,891, lift (R>0)=1,697, cobertura=0,819. 2022: 648 listas, 9.345 candidaturas, 756 com R=0 (8,1%), H=1.095,3, lift (todos)=1,855, lift (R>0)=1,824, cobertura=0,810. Entre não competitivos de listas financiadas, R=0: 27,2% (2018) e 9,0% (2022)."
severidade: MODERATE
confianca: alta
recomendacao: "No Argumento, especificar o contraste da expectativa ('em relação a um núcleo do mesmo tamanho sorteado entre as candidaturas da lista'). Reconhecer que candidaturas sem campanha financiada inflam esse contraste, com a ligação a Hott & Menezes. No Cap. 3, reportar o *lift* com referência restrita a R>0 como robustez e ajustar a leitura 2018×2022."
claims: [C2.7.08]
```

```yaml
id: MET-2-008
titulo: "Cotas: a frase 'não fixam a parcela' confunde o nível da restrição e omite o sentido do viés"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 188
  secao: "## Argumento"
  trecho: "As cotas que garantem financiamento de candidaturas negras e de mulheres condicionam as escolhas partidárias, mas não fixam a parcela que deve ser transferida."
afirmacao_do_autor: "As cotas deixam espaço para priorização dentro dos grupos."
problema: "As cotas fixam um piso agregado por partido, somando todos os cargos (a l. 155 as descreve como 'critérios de cotas de financiamento'), mas não a parcela de cada candidatura nem de cada cargo. O texto não diz em qual nível a restrição opera nem em que sentido ela afeta o teste. Como os grupos beneficiados têm muito menos credenciais, o piso empurra recurso para fora do grupo credenciado, o que torna o teste de composição conservador. O comentário [A4] (l. 192) aponta isso, sem reflexo no corpo. Recomputado, no nível DF o piso não se reproduz lista a lista: as mulheres receberam 25,6% dos recursos partidários de DF em 2018 (mediana por partido 27,8%; só 4 de 35 partidos entre 28% e 35%) e 31,7% em 2022. Isso é compatível com cumprimento da cota por outros cargos. Nenhum teste de composição (Top-NECr) estratifica por gênero ou raça. Só a regressão intralista controla `mulher`/`negra`."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-003/evidence/met_cap2_alternativas.out (bloco F)"
    - "tese/02-literatura.qmd:155"
    - "tese/02-literatura.qmd:192"
    - "tese/03-medindo-coordenacao-intrapartidaria.qmd:149"
  detalhe: "Credencial: mulheres 4,8% vs homens 16,4% (2018); 6,1% vs 18,3% (2022). Parcela dos recursos partidários de DF para mulheres: 25,6% (2018), 31,7% (2022); candidaturas femininas: 31,7% e 35,2%."
severidade: MODERATE
confianca: media
recomendacao: "Reescrever a l. 188 dizendo que o piso é agregado por partido (todos os cargos), que deixa livre a alocação entre candidaturas e cargos, e que, por recair sobre grupos com menos credenciais, tende a atenuar o padrão procurado (teste conservador). Indicar que o controle aparece na regressão intralista, não no Top-NECr."
claims: [C2.7.05]
```

```yaml
id: MET-2-009
titulo: "Financiamento privado e teto de gastos (provocação de 11/09) fora do Argumento; os dados indicam complementaridade, não substituição"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 147
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "O confundimento gerado pela intermediação partidária destes recursos não ocorre nas eleições que são objeto desta tese, visto que os dados de 2018 e 2022, refletem eleições que ocorreram já sob o financiamento público dominante."
afirmacao_do_autor: "Sem doações empresariais, o recurso partidário reflete decisão do partido sobre dinheiro público."
problema: "A afirmação sobre a intermediação de doações é quase integralmente sustentada: 'OUTROS RECURSOS' são só 1,2% (2018) e 2,0% (2022) do recurso de origem partidária. O Argumento, porém, ignora os recursos não partidários que continuam existindo: 24,7% da receita dos candidatos a DF em 2018 e 12,1% em 2022. A provocação registrada em 11/09 (candidato com arrecadação privada perto do teto recebe só a complementação e pode ficar fora do Top-NECr) não é reconhecida. Esse rival agiria contra a hipótese, reduzindo a parcela de credenciados. Os dados não mostram substituição: a correlação intralista entre parcela partidária e parcela não partidária é positiva (+0,41/+0,34), e 95%/89% dos credenciados têm alguma receita não partidária, contra 71%/54% dos demais. O rival mais relevante passa a ser o de MET-2-001 (força do candidato atrai as duas fontes). Resta também a fungibilidade descrita na nota de 31/08 (doação ao partido 'trocada' por FEFC indicado pelo doador), indetectável nos dados."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-003/evidence/met_cap2_alternativas.out (blocos A, B, C)"
    - "notes/daily/2026-09-11.md"
    - "notes/daily/2026-08-31.md"
  detalhe: "Receita DF por origem, 2018/2022: partido 75,27%/87,86%; pessoas físicas 12,32%/8,71%; próprios 9,58%/2,22%. Fonte do recurso partidário: FEFC 80,38%/90,72%; FP 18,40%/7,31%; outros 1,22%/1,96%. Parcela não partidária no total do grupo: não competitivos 36,3% (2018) e 11,3% (2022); competitivos 18,8% e 12,8%."
severidade: MODERATE
confianca: alta
recomendacao: "Trocar 'não ocorre' por 'é residual (≈1–2% do recurso partidário)' e mencionar a fungibilidade como limitação. No Argumento, nomear o financiamento privado e o teto como rival, com o sinal esperado (substituição → contra a hipótese), e registrar que os dados indicam complementaridade. Esse resultado cabe no Cap. 3 como robustez."
claims: [C2.6.01, C2.6.02]
```

```yaml
id: MET-2-010
titulo: "Atribuição da ação ao partido justificada pela observabilidade, não pela decisão"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 180
  secao: "## Argumento"
  trecho: "A ação será sempre atribuída ao partido, pois as transferências monetárias representam uma ação concreta que torna observável o resultado de um processo decisório da organização."
afirmacao_do_autor: "Toda transferência de origem partidária expressa uma decisão da organização."
problema: "Que a transferência seja observável não implica que ela resulte de uma decisão estratégica da organização, e não de negociação com o candidato, de indicação de doador (MET-2-009) ou de regra legal (cotas). O locus decisório também varia: a l. 180 diz que os recursos chegam ao diretório nacional e que 'a maneira como cada partido decide... pode variar'. A unidade de análise, porém, é partido × UF, e a origem 'Recursos de partido político' agrega repasses de diretórios nacional, estadual e municipal, sem filtro de fonte (CLAUDE.md). É um pressuposto legítimo, mas precisa ser declarado como pressuposto, com a consequência para a inferência: as conclusões valem para 'o partido' como agregado, sem identificar quem decide."
evidencia:
  tipo: textual
  fontes:
    - "tese/02-literatura.qmd:180"
    - "CLAUDE.md (definição de R_il: não é filtrado por fonte FEFC/FP)"
    - "src/1_silver/gerar_rrd.py:288-332"
  detalhe: "Em gerar_rrd.py, vr_receita_recursos_partidos agrega toda receita com ds_origem_receita == 'Recursos de partido político'. Não há variável de diretório de origem na base."
severidade: MINOR
confianca: media
recomendacao: "Reformular como pressuposto ('assume-se que...'), dizer que a decisão pode ocorrer em níveis diferentes da organização e que a tese não os distingue, e remeter à nota do Cap. 3 sobre agrupamento de erros por partido."
claims: [C2.7.04]
```

```yaml
id: MET-2-011
titulo: "A variação partidária é teorizada (Scarrow & Webb; Fiva et al.) sem expectativa derivada; os resultados por partido existem, mas não entram"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 93
  secao: "## Partidos como organizações heterogêneas"
  trecho: "@fivaetal2024, além de demonstrarem empiricamente o dilema, teorizam que partidos eleitoralmente mais competitivos conseguem transitar melhor pelo *trade-off* apresentado."
afirmacao_do_autor: "A capacidade de coordenação varia entre partidos."
problema: "A seção 'Partidos como organizações heterogêneas' (l. 81–101) constrói a expectativa de variação entre partidos, mas o Argumento não a converte em implicação. Nenhuma das frentes (i)–(iii) prevê diferença por tipo ou capacidade de partido. Os artefatos existem (`lift_por_partido_ano.csv`, `03_competitivos_magnitude_tipo.csv`, `24_por_magnitude_tipo.csv`, `figs/cap3_fig_lift_partido.png`), mas o corpo do Cap. 3 não os usa. Um elo teórico fica sem teste. O comentário [2.2-3] (l. 83) registra o ponto."
evidencia:
  tipo: ausencia
  fontes:
    - "tese/02-literatura.qmd:81-101"
    - "tese/02-literatura.qmd:214"
    - "tese/reports/lift-magnitude-partido/lift_por_partido_ano.csv"
    - "tese/reports/resultados-capitulo-3/03_competitivos_magnitude_tipo.csv"
  detalhe: "grep 'lift_partido|tipo de partido' em 03-*.qmd e 04-*.qmd: nenhuma ocorrência no corpo."
severidade: MODERATE
confianca: alta
recomendacao: "Escolher: (a) derivar uma expectativa auxiliar (partidos com mais cadeiras/recursos priorizam de forma mais nítida) e testá-la no Cap. 3 com o *lift* normalizado por partido já calculado; ou (b) apresentar a seção como contexto de heterogeneidade e dizer que a tese não a testa."
claims: []
```

## Claims

```yaml
claim_id: C2.6.01
capitulo: 2
secao: "Financiamento de campanhas no Brasil"
claim: "O confundimento pela intermediação partidária de doações não ocorre em 2018 e 2022."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 147}
evidencia: {tipo: csv, referencia: "evidence/met_cap2_alternativas.out bloco B (OUTROS RECURSOS 1,22%/1,96% da origem partidária)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["residual, não nulo; fungibilidade doação→FEFC indetectável (MET-2-009)"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.6.02
capitulo: 2
secao: "Financiamento de campanhas no Brasil"
claim: "Com o fundo público, os partidos passaram a distribuir a maior parte dos recursos de campanha."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 157}
evidencia: {tipo: csv, referencia: "evidence/met_cap2_alternativas.out bloco A (origem partidária 75,27%/87,86% da receita de DF)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: methodology-reviewer
```

```yaml
claim_id: C2.6.04
capitulo: 2
secao: "Financiamento de campanhas no Brasil"
claim: "Por a eleição para DF ser crucial à sobrevivência, partidos têm incentivos para distribuir recursos de maneira seletiva e estratégica."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 169}
evidencia: {tipo: nenhuma, referencia: "argumento teórico; direção da seletividade não derivada"}
assessment: {status: partially_supported, confidence: media}
concerns: ["MET-2-002: incentivo por votos é compatível com dispersão"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.01
capitulo: 2
secao: "Argumento"
claim: "O vínculo desempenho–recursos gera incentivo à distribuição seletiva visando ampliar o quociente partidário."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 174}
evidencia: {tipo: nenhuma, referencia: "tese/02-literatura.qmd:159-165"}
assessment: {status: partially_supported, confidence: media}
concerns: ["MET-2-002", "MET-2-006: em 2018 o quociente era da coligação"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.02
capitulo: 2
secao: "Argumento"
claim: "A alocação de recursos partidários constitui um instrumento de coordenação intrapartidária."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 176}
evidencia: {tipo: nenhuma, referencia: "sem definição operacional de coordenação"}
assessment: {status: partially_supported, confidence: media}
concerns: ["MET-2-005: o desenho observa priorização, não coordenação"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.03
capitulo: 2
secao: "Argumento"
claim: "Seletividade não basta para estabelecer maximização coletiva; pode refletir autofavorecimento, barganha ou ameaça de saída."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 178}
evidencia: {tipo: nenhuma, referencia: "reconhecimento textual; nenhuma frente discrimina as rivais"}
assessment: {status: supported, confidence: alta}
concerns: ["MET-2-001: reconhecida, mas não convertida em teste"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.04
capitulo: 2
secao: "Argumento"
claim: "A ação de transferir recursos é sempre atribuível ao partido."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 180}
evidencia: {tipo: codigo, referencia: "src/1_silver/gerar_rrd.py:288-332"}
assessment: {status: partially_supported, confidence: media}
concerns: ["MET-2-010: pressuposto justificado por observabilidade"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.05
capitulo: 2
secao: "Argumento"
claim: "As cotas condicionam as escolhas, mas não fixam a parcela a ser transferida."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 188}
evidencia: {tipo: csv, referencia: "evidence/met_cap2_alternativas.out bloco F"}
assessment: {status: partially_supported, confidence: media}
concerns: ["MET-2-008: piso agregado por partido; sentido do viés omitido"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.06
capitulo: 2
secao: "Argumento"
claim: "A predominância do financiamento público não eliminou a desigualdade de recursos entre candidaturas."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 196}
evidencia: {tipo: figura, referencia: "Cap. 3 fig-concentracao (NECr/C mediano 51,36%/53,65%)"}
assessment: {status: supported, confidence: media}
concerns: []
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.07
capitulo: 2
secao: "Argumento"
claim: "Partidos priorizam credenciados PORQUE as credenciais sinalizam capacidade de contribuir ao desempenho coletivo."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 204}
evidencia: {tipo: csv, referencia: "tese/reports/regressao-fracionaria/coeficientes.csv (qe_sem_vitoria 2,89/1,70); evidence bloco C"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["associação sustentada; motivo não identificado pelo desenho (MET-2-001)"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.08
capitulo: 2
secao: "Argumento"
claim: "Espera-se presença desproporcional, em relação ao acaso, de credenciados entre os que concentram recursos."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 204}
evidencia: {tipo: csv, referencia: "evidence/met_cap2_alternativas.out bloco D (lift 1,891/1,855; 1,697/1,824 com referência R>0)"}
assessment: {status: supported, confidence: alta}
concerns: ["MET-2-007: o contraste com o acaso é inflado por candidaturas sem recurso; direção 2018×2022 depende da referência"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.09
capitulo: 2
secao: "Argumento"
claim: "A tese usa exclusivamente vitórias e votações de eleições anteriores para classificar credenciais."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 212}
evidencia: {tipo: codigo, referencia: "src/2_gold/cap3_cs_features.py:97-100 (incumbente | alcancou_10pct_qe_hist)"}
assessment: {status: supported, confidence: media}
concerns: ["detalhes de horizonte e cargos são escopo do measurement-reviewer"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.10
capitulo: 2
secao: "Argumento"
claim: "A separação ex-ante permite verificar associação entre alocação e credenciais sem definir prioridade pelo sucesso posterior."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 214}
evidencia: {tipo: codigo, referencia: "src/2_gold/cap3_cs_features.py:97-116 (candidato_forte_cs ex-post segregado)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.11
capitulo: 2
secao: "Argumento"
claim: "Frente (iii): identificação de uma priorização temporal ao núcleo priorizado da lista."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 214}
evidencia: {tipo: figura, referencia: "Cap. 4 fig-semana-campanha, fig-km-cs (corte por competitivo, não por núcleo)"}
assessment: {status: contradicted, confidence: alta}
concerns: ["MET-2-003"]
agent: methodology-reviewer
```

```yaml
claim_id: C2.7.12
capitulo: 2
secao: "Argumento"
claim: "O Cap. 3 trata das frentes (i) e (ii); o Cap. 4 investiga (iii)."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 218}
evidencia: {tipo: tabela, referencia: "Cap. 3 fig-cap3-03-top-necr, fig-reg-frac; Cap. 4 tbl-cox"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["(i) e (ii) cumpridas; (iii) testada sobre credencial, não núcleo"]
agent: methodology-reviewer
```

## Verificações que passaram
- *Lift* nacional Top-NECr × competitivos recomputado de forma independente: 1,891 (2018) e 1,855 (2022); cobertura 81,9% e 81,0%. Batem com o Cap. 3 (1,89/1,86; "mais de 80%").
- *Lift* por magnitude reproduzido exatamente (`lift_por_magnitude.csv`).
- Princípio ex-ante (l. 212–214): `candidato_competitivo` usa só histórico. A versão ex-post (`candidato_forte_cs`) existe, segregada e marcada para não uso (`cap3_cs_features.py` l. 97–116). A reversão voto→recurso não afeta a hipótese de composição.
- "Financiamento público dominante" (l. 147) e "maior parte dos recursos" distribuída por partidos (l. 157): recurso de origem partidária = 75,3%/87,9% da receita de DF; FEFC = 80,4%/90,7% do recurso partidário.
- A substituição privado→partido (provocação do teto, 11/09) não aparece nos dados: a correlação intralista é positiva.

## Limites desta revisão
- Não avaliei a fidelidade das citações e paráfrases da literatura (theory/literature-reviewer), nem os números legais do FEFC/FP (l. 159–165).
- Sem coluna de coligação na base, a extensão do problema de 2018 (MET-2-006) não foi quantificada.
- O recálculo do Top-NECr em `evidence/` reimplementa a regra de empates fracionários e reproduz os números oficiais, mas não usa as funções de `cap3_taa_features.py`.
- MET-2-004 aponta um problema do Cap. 3 (l. 118). Ele é registrado aqui pela ligação com as expectativas do Cap. 2 e deve ser reavaliado no próximo run do Cap. 3.
- Os comentários HTML no `.qmd` (roteiros [A0]–[A10], [3.D], [4.D]) foram lidos como registro de pendências, não como texto do autor. Todas as passagens citadas como `trecho` nos achados são do corpo, exceto quando indicado.
