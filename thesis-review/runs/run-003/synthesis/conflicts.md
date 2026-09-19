# Síntese pass 1 — run-003 — Capítulo 2 (`tese/02-literatura.qmd`)

Insumos: `agents/theory.md` (10 achados), `agents/literature.md` (17), `agents/methodology.md` (11). Total: 38 achados, 22 issues.
O writing-reviewer ainda não rodou; os achados WRI-2-* entram no pass 2 (agrupar em issues novos ou nos existentes).

## 1. Triagem

**Descartes: nenhum.** Os 38 achados têm `localizacao.linha`, `trecho` e `evidencia.fontes`.

**Achado fora do capítulo:** MET-2-004 aponta para o Cap. 3 (`03-medindo…qmd:118`). Fica, porque a expectativa confrontada nasce no Cap. 2 (L25, L121). Foi agrupado com THE-2-007 no I-2-006. A parte que é só do Cap. 3 segue para o próximo run do Cap. 3 (ver §4, C2).

**Conferência dos trechos.** Li o `.qmd` inteiro (219 linhas). Os 38 `trecho`s existem literalmente nas linhas indicadas, inclusive MET-2-004 na L118 do Cap. 3.

**Conferência das fontes** (amostra de 12, todos os MAJOR+ incluídos):

| Achado | Fonte conferida | Resultado |
|---|---|---|
| THE-2-001 / MET-2-001 | Cap. 3 L157; `coeficientes.csv` linhas 9 e 22 (`qe_sem_vitoria`, R2) | Confere: 2,886 [2,185–3,812] em 2018 e 1,701 [1,476–1,961] em 2022 |
| THE-2-002 / MET-2-002 | Cap. 4 L25 | Confere: "incentivos adicionais para que os partidos alocassem recursos de forma mais desconcentrada" |
| THE-2-002 / MET-2-002 | Cap. 2 L167 (comentário do autor) | Confere: "35% do FEFC e 95% do FP seguem VOTOS, o que pode incentivar dispersão" |
| THE-2-003 | Cap. 4 L49 | Confere: atribui a Fiva et al. uma previsão sobre o FEFC ("prevê que partidos, ao controlarem a distribuição do FEFC…") |
| MET-2-003 | Cap. 4 L9, L47, L61, L63 | Confere: o corte é competitivo/não competitivo; L47 afirma intenção ("partidos políticos consideram a vantagem…") |
| THE-2-004 / MET-2-005 | Cap. 3 L76 | Confere: "'contaminados' pelo resultado eleitoral" |
| THE-2-005 | Cap. 4 L13; Cap. 3 L100 | Confere: "se diferencia novamente de @cheibubsin2020"; "os resultados reforçam o argumento de @cheibubsin2020" |
| THE-2-006 | Cap. 3 L86, L90 | Confere: mediana de competitivos = 1; NECr mediano 1,88/4,81 |
| LIT-2-001 | `references.bib:43-49` | Confere: `bolognesietal2020` existe e não é citado (`evidence/lit_cruzamento_citacoes.out`) |
| LIT-2-007 | `references.bib:188-196` | Confere: `pages = {105133}` (número de artigo). "p. 100" é implausível |
| MET-2-004 | `evidence/met_cap2_alternativas.out` bloco H; `lift_por_magnitude.csv` | *Lift* e teto conferem. **A conclusão "o gradiente se inverte" não se sustenta com a normalização do próprio repositório** (ver C2) |
| MET-2-007 | `evidence/met_cap2_alternativas.out` bloco D | Confere: *lift* com R>0 de 1,697 (2018) e 1,824 (2022). Ressalva de interpretação em C3 |
| THE-2-008 / MET-2-011 | grep em Caps. 3 e 4 por "tipo de partido", "lift_partido", "por partido" | Confere: nenhuma ocorrência no corpo |

## 2. Reconciliação de IDs de claim (colisões entre agentes)

Os três agentes numeraram as seções da mesma forma (1 Primeira/segunda gerações; 2 Cânone; 3 Segunda geração; 4 Partidos heterogêneos; 5 Competição e gastos; 6 Financiamento; 7 Argumento), mas os `seq` colidem nas seções 4, 6 e 7. IDs canônicos para o pass 2 e para `claims/claims.yaml`:

| Canônico | Linha | Claim | IDs de origem | Status proposto (o mais conservador) |
|---|---|---|---|---|
| C2.4.01 | 75 | Aldrich: partidos resolvem ação coletiva | LIT C2.4.01 | supported |
| C2.4.02 | 77 | Cox & McCubbins: controle de recursos escassos | LIT C2.4.02 | partially_supported |
| C2.4.03 | 89 | Fiva et al.: menor esforço agregado (p. 100) | LIT C2.4.03 | partially_supported |
| C2.4.04 | 93 | Fiva et al.: partidos competitivos lidam melhor com o *trade-off* | LIT C2.4.04 ≡ THE C2.4.03 | unverifiable |
| C2.4.05 | 97 | Guarnieri: comissões provisórias | LIT C2.4.05 | supported |
| C2.4.06 | 97/101 | Tavits: *inactive branches*; RBV | LIT C2.4.06 | unverifiable |
| C2.4.07 | 95 | A distribuição é instrumento de vantagem competitiva | THE C2.4.01 | partially_supported |
| C2.4.08 | 95 | *Gatekeeping* também após as nominatas | THE C2.4.02 | supported (não original) |
| C2.6.01 | 133 | Mancuso: três vertentes | LIT C2.6.01 | supported |
| C2.6.02 | 139 | Thomsen: recursos mais concentrados que votos | LIT C2.6.02 | supported |
| C2.6.03 | 145 | Silva & Cervi: números de 2014 | LIT C2.6.03 | unverifiable |
| C2.6.04 | 159-165 | Regras FEFC/FP/cláusula (sem fonte) | LIT C2.6.04 | unsupported |
| C2.6.05 | 157 | FEFC deu centralidade aos partidos (Silva & Codato) | LIT C2.6.05 | partially_supported |
| C2.6.06 | 151 | Janusz et al.: incumbentes; mulheres | LIT C2.6.06 | supported |
| C2.6.07 | 169 | Eleição para DF é crucial à sobrevivência → seletividade | THE C2.6.01 ≡ MET C2.6.04 | partially_supported |
| C2.6.08 | 147 | Confundimento pela intermediação "não ocorre" em 2018/2022 | MET C2.6.01 | partially_supported |
| C2.6.09 | 157 | Partidos distribuem a maior parte dos recursos | MET C2.6.02 | supported |
| C2.7.01 | 174 | Vínculo desempenho–recursos → distribuição seletiva | THE C2.7.01 ≡ MET C2.7.01 | partially_supported |
| C2.7.02 | 176 | Alocação é instrumento de coordenação | THE C2.7.02 (unsupported) ≡ MET C2.7.02 (partially) | **unsupported** |
| C2.7.03 | 204 | E1: sobrerrepresentação de credenciados em relação ao acaso | THE C2.7.03 (partially) ≡ MET C2.7.08 (supported) | **partially_supported** |
| C2.7.04 | 214 | Frente (i): núcleo priorizado | THE C2.7.04 | partially_supported |
| C2.7.05 | 214 | Frente (ii): desagregação por cargo | THE C2.7.05 | partially_supported |
| C2.7.06 | 214 | Frente (iii): priorização temporal ao núcleo | THE C2.7.06 (unsupported) ≡ MET C2.7.11 (contradicted) | **contradicted** |
| C2.7.07 | 212 | Silva & Cervi e Cheibub & Sin usam a eleição corrente; a tese usa só resultados anteriores | THE C2.7.07 ≡ LIT C2.7.01 ≡ MET C2.7.09 | supported (media) |
| C2.7.08 | 218 | Cap. 3 → (i)/(ii); Cap. 4 → (iii) | THE C2.7.08 ≡ MET C2.7.12 | partially_supported |
| C2.7.09 | 178 | Rivais: captura, barganha, ameaça de saída | LIT C2.7.02 (unsupported) ≡ MET C2.7.03 (supported) | **unsupported** (sem literatura; reconhecidas, mas não testadas) |
| C2.7.10 | 204 | Credencial como sinal; "porque" | LIT C2.7.03 (unsupported) ≡ MET C2.7.07 (partially) | **unsupported** |
| C2.7.11 | 188 | Cotas não fixam a parcela | LIT C2.7.04 (unsupported) ≡ MET C2.7.05 (partially) | **unsupported** |
| C2.7.12 | 212 | Segue a orientação ex-ante de Janusz et al. | LIT C2.7.05 | partially_supported |
| C2.7.13 | 180 | Ação sempre atribuível ao partido | MET C2.7.04 | partially_supported |
| C2.7.14 | 196 | Financiamento público não eliminou a desigualdade | MET C2.7.06 | supported |
| C2.7.15 | 214 | Separação ex-ante permite testar associação sem usar sucesso posterior | MET C2.7.10 | supported |

As seções 1, 2, 3 e 5 não têm colisão: valem os IDs de `literature.md` (C2.1.01; C2.2.01–04; C2.3.01–08; C2.5.01–02).

## 3. Agrupamento (finding → issue)

| Achados | Issue | Problema comum (uma frase) |
|---|---|---|
| THE-2-001, MET-2-001, LIT-2-009 | **I-2-001** (MAJOR) | A implicação testada (L204) é prevista também pelas rivais que a L178 nomeia (e por "força do candidato"/inércia), e o Argumento não diz que observação as separaria nem as ancora na literatura. |
| THE-2-002, MET-2-002, LIT-2-002 | **I-2-002** (MAJOR) | O Argumento passa de "incentivo por votos/cadeiras" (L174) a "concentrar em credenciados" (L204) sem o elo que descarta dispersão ou foco em marginais, e sem a literatura de alocação partidária que trata exatamente disso. Consequência: não há direção prevista para 2018→2022, e o Cap. 4 (L25) deriva a oposta. |
| THE-2-003, MET-2-003 | **I-2-003** (MAJOR) | A frente (iii) não tem hipótese temporal derivada e promete "núcleo priorizado", mas o Cap. 4 testa credencial (e usar o núcleo seria circular). |
| THE-2-004, MET-2-005 | **I-2-004** (MAJOR, conflito de severidade) | "Coordenação" é reivindicada (L176, título), mas o desenho só observa priorização. Não há definição operacional nem implicação sobre o efeito coletivo. |
| THE-2-005, LIT-2-001, LIT-2-016 | **I-2-005** (MAJOR, confiança média) | O capítulo não delimita o que a tese acrescenta aos precedentes diretos sobre alocação partidária de dinheiro (Janusz et al., cujo período/fonte não é dito; Bolognesi et al. 2020, no .bib e não citado). A diferença em relação a Cheibub & Sin muda entre os Caps. 2, 3 e 4. |
| THE-2-007, MET-2-004 | **I-2-006** (MODERATE) | A magnitude é teorizada na revisão (L25, L121), mas não gera expectativa. O gradiente do Cap. 3 é lido *post hoc*, e parte do gradiente do *lift* é mecânica. |
| THE-2-008, MET-2-011 | **I-2-007** (MODERATE) | A heterogeneidade partidária (L81-101) implica variação entre partidos que o Argumento não formula e os Caps. 3/4 não testam, embora os artefatos existam. |
| THE-2-006, MET-2-007 | **I-2-008** (MODERATE) | O "núcleo priorizado" e o contraste "em relação ao acaso" não são definidos no Argumento: nem tamanho, nem conjunto de referência (que inclui candidaturas sem recurso algum). |
| MET-2-006 | **I-2-009** (MODERATE) | As diferenças de regra 2018×2022 (coligações, cláusula crescente, cota racial) não são discutidas; o *pooling* é descrito como se valesse a regra de 2022 nos dois anos. |
| MET-2-008, THE-2-010 | **I-2-010** (MODERATE) | A frase das cotas (L188) não diz em que nível o piso opera nem o sentido do viés (teste conservador). |
| LIT-2-008 | **I-2-011** (MODERATE) | Afirmações institucionais e empíricas de Financiamento (L143-165, L188) sem fonte, embora o .bib já tenha as fontes. |
| MET-2-009 | **I-2-012** (MODERATE) | L147 diz que o confundimento "não ocorre" (é residual, ~1–2%), e o Argumento ignora os recursos não partidários (24,7%/12,1% da receita de DF). |
| THE-2-009 | **I-2-013** (MODERATE) | A analogia com o dilema do *gatekeeper* toma só o lado da proteção. O custo em esforço e a divisibilidade do dinheiro não geram implicação, e "gatekeeping" muda de sentido. |
| LIT-2-003 | **I-2-014** (MODERATE) | A classificação do *pooling* brasileiro (L33) contradiz a própria definição da L21 (e, provavelmente, a codificação de Carey & Shugart). |
| LIT-2-004 | **I-2-015** (MODERATE) | André et al./Crisp et al. não mostram *gatekeeping* pós-convenção: a recompensa ocorre na lista seguinte. |
| LIT-2-005 | **I-2-016** (MODERATE, confiança baixa) | O achado de Desposato (2006) pode estar reportado de forma invertida. |
| LIT-2-006 | **I-2-017** (MODERATE) | Ferree et al. usados como definição da "segunda geração"; o vocabulário de "gerações" em Mershon não foi verificado. |
| LIT-2-007 | **I-2-018** (MODERATE) | Fiva et al.: "p. 100" incompatível com um artigo de paginação por número; a previsão da L93 (base da heterogeneidade) está sem localizador. |
| LIT-2-010, LIT-2-011 | **I-2-019** (MODERATE) | Faltam obras canônicas que um examinador esperaria: Pereira & Mueller 2003 (objeção direta na arena eleitoral), Samuels 2002, Cain et al., Nicolau, Katz & Mair, Panebianco. |
| MET-2-010 | **I-2-020** (MINOR) | A atribuição da ação ao partido (L180) é justificada por observabilidade e deve ser declarada como pressuposto (vários níveis de diretório agregados em R_il). |
| LIT-2-012, LIT-2-013, LIT-2-014, LIT-2-015 | **I-2-021** (MINOR) | Paráfrases que esticam o que a obra sustenta (Tavits, Avelino et al./Ames, Braga & Amaral/Kselman, Cox & McCubbins). Cada uma é pontual e não afeta a cadeia. |
| LIT-2-017 | **I-2-022** (MINOR) | Formalidades de citação e do .bib (localizador manual, chaves com ano divergente, duplicata, metadados). |

Os 38 achados estão mapeados, nenhum em dois issues.

**Três agrupamentos que não fiz, e por quê:**
- LIT-2-009 (rivais sem literatura) entrou no I-2-001 e não virou issue próprio. É a mesma lacuna (rivais sem implicação e sem âncora). Isolado, seria MODERATE; o MAJOR do I-2-001 vem de THE-2-001/MET-2-001.
- LIT-2-002 foi para o I-2-002, e não para o I-2-001. A obra que falta (alocação a marginais × credenciados; PVEA de Shugart et al.) resolve o elo incentivo → estratégia, não a discriminação das rivais.
- Mantive LIT-2-004/005/006 (MODERATE) separados do I-2-021 (MINOR). Os três afetam a moldura "primeira × segunda geração" ou a tese de *gatekeeping* pós-convenção, que sustentam o Argumento; os do I-2-021 não.

## 4. Conflitos e decisões provisórias

**C1 — Severidade de I-2-004 (coordenação × priorização).** THE-2-004 diz MAJOR; MET-2-005 diz MODERATE (seria correção de definição e redação: "constitui" → "pode operar como").
Decisão provisória: **MAJOR**. "Coordenação" é o conceito do título da tese. A L176 afirma que a alocação "constitui um instrumento de coordenação intrapartidária". Nenhuma frente mede efeito sobre a competição ou o resultado coletivo, e o Cap. 3 (L76) descarta a validação ex-post. Mudar a reivindicação central de "coordenação" para "priorização compatível com coordenação" é mudança de interpretação (definição de MAJOR na rubrica), mesmo que a execução seja textual. O adversarial deve testar se uma definição de coordenação *como* alocação orientada por sinal (sem exigir efeito) bastaria. Nesse caso cai para MODERATE.

**C2 — MET-2-004 (MAJOR) × THE-2-007 (MODERATE): gradiente por magnitude.** Divergem no diagnóstico. THE-2-007 diz que o gradiente, se previsto, seria um teste do mecanismo (a credencial vale mais quando a informação piora). MET-2-004 diz que o gradiente do *lift* é "majoritariamente mecânico" e que, normalizado, "se inverte levemente".
Verifiquei (CHAIR). O teto `Σmin(G,k)/ΣGk/C` de fato cresce com M (2018: 1,57→2,99). Mas MET-2-004 normaliza por `lift/teto`, e o repositório define `lift_normalizado = (H−E)/(Hmax−E)` (`tese/scripts/regenerar_figuras_cap3.py:282`; `notes/tecnico/cap3-lift-partido.md:26`). Aplicada aos mesmos números do bloco H, a normalização do repositório dá **0,70 / 0,79 / 0,76 (2018)** e **0,60 / 0,73 / 0,74 (2022)**: o gradiente se atenua, mas não se inverte, e em 2022 continua crescente. A frase "o gradiente se inverte" depende da métrica escolhida. O ponto de fundo (o *lift* bruto por magnitude precisa vir com o teto) e a razão intralista (4,76→13,48, sem teto) continuam de pé.
Decisão provisória: **I-2-006 MODERATE**. Para o Cap. 2, o problema é a ausência de expectativa, e nisso os dois concordam. A parte do Cap. 3 (reportar teto/normalizado; moderar "mais discriminante" na L118) segue para o próximo run do Cap. 3 como MODERATE, não MAJOR.

**C3 — MET-2-007 × "verificações que passaram" de theory.md** ("E1… tem o contrafactual explícito, coerente com a referência aleatória do Cap. 3").
Não é contradição: theory confere que o contrafactual é *nomeado*; MET questiona *qual* conjunto de referência. Ressalva do chair: restringir a referência a R>0 condiciona em parte da variável de resultado, porque não repassar nada também é uma decisão de alocação. O *lift* com R>0 (1,70/1,82) é uma sensibilidade, não a referência "correta". A inversão 2018×2022 que MET aponta só existe nessa sensibilidade.
Decisão provisória: **I-2-008 MODERATE**, restrito a "especificar o contraste no Argumento e reconhecer o papel das candidaturas sem campanha financiada (Hott & Menezes)". A leitura 2018×2022 segue para o Cap. 3.

**C4 — Severidade de I-2-010 (cotas).** THE-2-010 diz MINOR; MET-2-008 diz MODERATE.
Decisão provisória: **MODERATE**. MET recomputou que, no nível DF, as mulheres receberam 25,6% dos recursos partidários em 2018, com mediana por partido de 27,8% (bloco F). Logo, o piso não opera lista a lista, e a L188 não diz em que nível opera. Além disso, o Cap. 3 (L171) usa o piso legal para interpretar a razão 1,44 das mulheres, o que depende de o Cap. 2 ter dito isso.

**C5 — LIT-2-001 classificado como MAJOR por uma citação ausente.** Isolada, uma omissão bibliográfica seria MODERATE. Agrupada ao THE-2-005 (contribuição não delimitada), o MAJOR do I-2-005 vem da falta de delimitação frente a precedentes que estudam o mesmo objeto, e não da citação em si.
Decisão provisória: **I-2-005 MAJOR, confiança média**. A confiança depende de Janusz et al. (2021) cobrirem ou não o período do FEFC. O `.bib` (L610-616) só traz título, periódico e DOI, e nenhum agente leu a obra.

**C6 — Achados que dependem de memória do revisor sobre obras fora do repositório** (LIT-2-002, 003, 005, 006, 009, 010, 011, 012, 013, 015). A *ausência* é verificável (grep no .bib); o *conteúdo* das obras não.
Decisão: mantidos. A confiança fica como declarada pelo agente, e nenhum MAJOR repousa só nisso: o MAJOR do I-2-002 se ancora em THE-2-002/MET-2-002, no texto do Cap. 2 e nos comentários do próprio autor (L167, L183, L208). I-2-016 (Desposato, confiança baixa) é o mais frágil: se o autor conferir o resumo e o achado estiver correto, o issue cai.

**C7 — Status de claims divergentes** (C2.7.02, 03, 06, 09, 10, 11; ver §2). Regra: fica o mais conservador, e os `concerns` se unem no pass 2.

**Sem conflito, com convergência forte:** I-2-001, I-2-002 e I-2-003 foram encontrados de forma independente por theory e methodology, com o mesmo trecho, a mesma severidade (MAJOR) e recomendações compatíveis. MET-2-003 acrescenta a rival da prontidão administrativa (Cap. 4 L9), que complementa THE-2-003.

## 5. Cadeia macro consolidada

| Elo | Onde | Estado | Issues |
|---|---|---|---|
| Pergunta: como os partidos alocam o dinheiro que controlam | L129, L133 | Sólido | — |
| Teoria/incentivo: sobrevivência financeira depende do desempenho na Câmara | L157-169, L174 | Sólido como incentivo; **indeterminado quanto à direção** | I-2-002, I-2-009 |
| **Mecanismo: credencial como sinal sob incerteza → concentração em credenciados** | L204 | **ELO MAIS FRACO.** Não derivado do incentivo (por que não dispersão ou marginais?) e não discriminado das rivais que o próprio texto nomeia (L178) | **I-2-002, I-2-001** |
| Hipótese/expectativa: sobrerrepresentação em relação ao acaso | L204 | Enunciada, com contrafactual nomeado, mas conjunto de referência e tamanho do núcleo indefinidos | I-2-008 |
| Expectativas auxiliares: magnitude, heterogeneidade partidária, 2018×2022, *timing* | L25, L121, L81-101, L214 | Ausentes (magnitude, partido, 2018×2022) ou sem derivação (*timing*) | I-2-006, I-2-007, I-2-009, I-2-003 |
| Desenho: ex-ante, comparação intralista | L212-214 | **Sólido**: validado pelos três agentes e pelo código (`cap3_cs_features.py:97-116`) | — |
| Conclusão reivindicada: "coordenação intrapartidária" | L176, título | Além do que o desenho licencia (licencia priorização associativa com precedência temporal) | I-2-004, I-2-005 |

Elo mais fraco: **incentivo → mecanismo (L174 → L204)**. O capítulo não diz por que o incentivo leva à concentração em credenciados, e a implicação testada é compartilhada com as rivais. Os três agentes chegam a este elo por caminhos distintos: theory (derivação), methodology (identificação) e literature (a obra que falta é justamente a da alocação a marginais × credenciados). O próprio autor o marcou nos comentários [A2] e [A7] e na L167. Nada disso invalida os resultados empíricos dos Caps. 3/4. Exige mudar o que o Cap. 2 promete que eles mostram.

## 6. Dependências (para a fila do pass 2)

- I-2-002 primeiro: define a direção do incentivo e desbloqueia I-2-001 (implicações diferenciais), I-2-009 (expectativa 2018×2022), I-2-006 (magnitude) e I-2-007 (partidos).
- I-2-004 (definir coordenação × priorização) desbloqueia I-2-003 (*timing*), I-2-013 (dilema do *gatekeeper*) e I-2-005 (contribuição).
- I-2-018 (localizador de Fiva et al., L93) precede I-2-007 se a heterogeneidade for derivada de Fiva et al.
