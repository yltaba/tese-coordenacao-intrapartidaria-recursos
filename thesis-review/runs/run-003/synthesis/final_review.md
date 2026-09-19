# Parecer — Capítulo 2 — run-003

Arquivo avaliado: `tese/02-literatura.qmd` (sha256 `f4ba3b00…`, igual no início e no fim do run). Agentes: theory, literature, methodology, writing, thesis-chair (pass 1 e 2), adversarial. Data: 19/09/2026.

## Veredito

```         
THESIS REVIEW — run-003 — Capítulo 2
CRITICAL 0 | MAJOR 3 | MODERATE 19 | MINOR 6
Measurement n/a · Statistics n/a · Results n/a · Theory WARN · Literature WARN · Writing PASS · Internal validity WARN
OVERALL: ⚠ Revision required
```

-   Measurement, statistics e results não se aplicam: o capítulo é de revisão e argumento, e esses agentes não rodaram. As recomputações deste run (methodology e adversarial) só servem para testar as expectativas do Cap. 2.
-   **Nada neste parecer invalida os resultados empíricos dos Caps. 3 e 4.** Os três MAJOR pedem mudança no que o Cap. 2 diz que esses resultados mostram e no que ele reivindica como contribuição.

**Três fatos de processo que o autor precisa saber:**

1.  **A Introdução e as Considerações mudaram durante o run.** `tese/01-introducao.qmd` e `tese/05-consideracoes-finais.qmd` foram modificados em 19/09 às 00:18. Os especialistas terminaram entre 00:07 e 00:10, e o rascunho de issues é das 00:16. Os dois arquivos adotam a leitura "compatível com" e admitem as rivais e a prontidão administrativa. O Cap. 2 não mudou. **Nenhuma severidade deste parecer foi decidida com base nesses dois textos.** A pergunta sobre eles está em I-2-024.
2.  **O writing-reviewer leu o `issues_draft.yaml` antes de revisar**, por instrução do orquestrador. Isso desvia da regra de independência (PROTOCOL §1.6). O efeito foi limitado: ele deixou de polir as passagens condenadas e não emitiu juízo substantivo. Os achados WRI-2-\* foram tratados como independentes só no que diz respeito à redação.
3.  **Usei no pass 2 textos-fonte que já estavam no repositório** (`revisoes/fontes-discussao-capitulo3/janusz.txt`, `bolognesi.txt`, `fiva.txt`, `cheibub.txt`). Nenhum especialista nem o adversarial os consultou. Eles decidiram a condição que o adversarial deixou em aberto no I-2-005 e elevaram a confiança de I-2-018 e I-2-023.

## A cadeia do capítulo (macro) — elo mais fraco

| Elo | Onde | Estado após arbitragem | Issues |
|------------------|------------------|------------------|------------------|
| Pergunta: como os partidos alocam o dinheiro que controlam | L129, L133 | Sólido | — |
| Incentivo: a sobrevivência financeira depende do desempenho na Câmara | L157-169, L174 | Sólido como incentivo. A dispersão é rejeitada pelos dados (NECr/C mediano de 0,47/0,52). A direção 2018→2022 não é prevista | I-2-002, I-2-009 |
| **Mecanismo: credencial como sinal sob incerteza** | **L204** | **ELO MAIS FRACO.** (a) Não é separado das rivais que a L178 nomeia, e entre mandatários o padrão é o que a captura prevê. (b) Não é original: é a Hipótese 1 de Janusz et al., testada em 2014 com a mesma justificativa e o mesmo recorte intralista | **I-2-001, I-2-005** |
| Expectativa E1: sobrerrepresentação em relação ao acaso | L204 | Enunciada, com o contrafactual nomeado. Faltam o tamanho do núcleo e o conjunto de referência | I-2-008 |
| Expectativas auxiliares: *timing*, magnitude, partido, 2018×2022 | L214, L25, L121, L81-101 | *Timing* sem derivação e com uma rival não testável. Magnitude e partido sem expectativa. A literatura citada (Cheibub & Sin) prevê o gradiente de magnitude oposto ao encontrado | I-2-003, I-2-006, I-2-007, I-2-009 |
| Desenho: ex-ante, intralista | L212-214 | **Sólido** | — |
| Conclusão: "coordenação intrapartidária" | L176, título | Defensável sob uma definição comportamental (Cox 1997; Cheibub & Sin), que o capítulo não dá | I-2-004 |

Mudança em relação ao pass 1: o elo mais fraco continua no mecanismo, mas o diagnóstico mudou. No pass 1 o problema parecia ser que o incentivo não implica concentração. O adversarial mostrou que essa parte é resolvida pelos dados e pelo próprio texto da L204. O que sobra tem dois lados: o mecanismo não é discriminado das rivais (I-2-001) e não é da tese (I-2-005). **O capítulo ganha em ser reenquadrado como reexame, sob o FEFC e com medidas novas, de uma hipótese já existente, e em anunciar o único teste que discrimina sinal de captura, que já existe: a votação sem vitória.**

## Issues arbitrados

### MAJOR

**I-2-005 — A contribuição não é delimitada frente a precedentes que testaram a mesma hipótese (Janusz et al., 2014) e já construíram um número efetivo de financiados (Bolognesi et al., 2014).** MAJOR → **MAJOR**, confiança alta (era média). - *Adversarial:* sugeriu MODERATE. Os argumentos: a diferença frente a Cheibub & Sin é coerente entre os capítulos, Bolognesi seria coberto pelo critério institucional (L153) e o capítulo não reivindica nada falso sobre Janusz. Mas deixou uma condição explícita para voltar a MAJOR: Janusz et al. fazerem comparação intralista, com classificação ex-ante, no período do FEFC. - *Decisão:* **não sigo o adversarial.** O texto-fonte cumpre duas das três partes da condição. Janusz et al. usam dados de 2014, com efeitos fixos de partido estadual (= lista) e variáveis de experiência ex-ante (incumbente, ex-ocupante, candidatura anterior) (`janusz.txt` L418-462). A Hipótese 1 deles é a da L204, com a mesma justificativa: chances incertas, experiência como sinal de potencial eleitoral, maximização de cadeiras, citando inclusive Cheibub & Sin (`janusz.txt` L180-213). Bolognesi et al. operacionalizam um "número efetivo de financiados" para os deputados federais de 2014 (`bolognesi.txt` L1434-1509). O próprio `mapa-evidencias.md` do autor (L9) já avisa: "Não atribuir à tese a invenção do número efetivo em recursos". Mesmo assim, `bolognesietal2020` não é citado em nenhum capítulo. A L204 abre com "O argumento desta tese é…". O defeito não é uma citação ausente, e sim o enquadramento da contribuição. - *Recomendação:* reescrever o fecho do Argumento como delimitação. A hipótese e sua justificativa são de Janusz et al. e da literatura norte-americana que eles citam (Jacobson; Damore & Hansford; Herrnson). A tese as reexamina sob o regime pós-ADI 4650/FEFC, em 2018 e 2022, e acrescenta: o núcleo de tamanho endógeno por lista (em vez do nível em R\$ ou da correlação agregada NEF × bancada), as parcelas por cargo, o teste da votação sem vitória e o *timing*. Citar Bolognesi et al. como antecedente do número efetivo em recursos. Na L151, dizer que Janusz et al. analisam 2014. Corrigir o "novamente" do Cap. 4 L13. **A relação NEF × NECr também tem de entrar no próximo run do Cap. 3.**

**I-2-001 — A expectativa central não discrimina a sinalização das rivais que o próprio Argumento nomeia.** MAJOR → **MAJOR**, confiança alta. - *Adversarial:* crítica válida, e a recomputação dele a reforça. Entre ex-eleitos para DF, a parcela não cresce com a votação anterior (Spearman −0,13 em 2018 e 0,06 em 2022). Em 2018, o quartil mais votado recebe menos que o Q3 (mediana s·C de 1,99 contra 3,38). Um perfil plano entre mandatários é o que a captura por posição prevê. Por outro lado, fora dos mandatários a parcela cresce com a votação prévia (Spearman 0,43/0,47), e a captura não prevê isso. - *Decisão:* mantido. A L204 afirma um "porque" que o desenho não separa de captura, barganha, ameaça de saída e força do candidato. Essa última sobrevive ao controle pelas credenciais: a correlação parcial entre parcela partidária e não partidária fica em 0,32/0,25 (`adv_rivais_cap2.out`, bloco A). O atenuante da Introdução L36 não foi usado (ver I-2-024). - *Recomendação:* tirar o "porque" como tese demonstrada. Para cada rival, dar a implicação que a separa da sinalização. Anunciar o teste que já existe: prêmio a quem teve ≥ 10% do QE sem vitória (Cap. 3 L157: 2,89/1,70) e gradiente fora dos mandatários. Declarar o que o desenho não separa.

**I-2-003 — A frente (iii), *timing*, não tem expectativa derivada no Cap. 2, e a rival da prontidão administrativa não aparece.** MAJOR → **MAJOR**, confiança alta. - *Adversarial:* parcialmente válido. Caem duas partes: a troca núcleo → credencial (uma palavra, já justificada pela circularidade) e a leitura de que Fiva et al. prevêem o contrário (sem apoio na L91). Fica o núcleo do problema: não há expectativa temporal, e a prontidão administrativa é uma rival que a base não permite testar, porque não há data de habilitação de conta/CNPJ. - *Decisão:* sigo o adversarial. O problema limita a interpretação de um capítulo inteiro: o Cap. 4 L47 conclui intenção ("partidos políticos consideram a vantagem…"). O custo no Cap. 2 é baixo, porque a justificativa substantiva já existe no Cap. 4 L29. - *Recomendação:* derivar a expectativa temporal no Cap. 2 (mais tempo de campanha; ligar à L77, "e quando os recebem"), reescrever a frente (iii) em termos de credencial, nomear a prontidão como rival não testável e rever as L47 e L49 do Cap. 4.

### MODERATE rebaixados pelo adversarial

**I-2-002 — E1 não distingue foco em marginais de concentração em credenciados; não há direção prevista para 2018→2022; falta a literatura de alocação partidária.** MAJOR → **MODERATE**, confiança alta. - *Adversarial:* parcialmente válido. O elo incerteza → sinal está na L204 (conferi o trecho). A divisão igualitária é rejeitada pelo desenho (NECr/C mediano de 0,466/0,519; só 8,2%/11,7% das listas com NECr/C ≥ 0,9; lift 1,89/1,86). O Cap. 4 L25 trata de grau de concentração, não de composição. - *Decisão:* sigo o adversarial. Não é preciso mudar a interpretação. Falta dizer o que E1 não distingue. A literatura que falta está citada dentro de Janusz et al. (Damore & Hansford 1999; Herrnson 2009).

**I-2-004 — "Coordenação intrapartidária" não é definida, muda de sentido e é afirmada como fato ("constitui").** MAJOR → **MODERATE**, confiança alta. - *Adversarial:* parcialmente válido. Há uma definição comportamental disponível, e a parte "objetivos coletivos" duplica o I-2-001. - *Decisão:* sigo o adversarial. A condição do pass 1 se cumpre com fontes que não dependem da Introdução: a nota do autor de 11/09 ("não é concentração, mas priorização de um conjunto competitivo") e Cheibub & Sin, que usam "coordinated" no sentido de Cox (1997) (`cheibub.txt` L71-72, L712). Resta definir o termo uma vez e trocar "constitui" por "pode operar como" na L176.

### Novos issues (omissões do adversarial e do writing)

-   **I-2-023 (ADV-2-001) — Janusz et al. sobre mulheres × vantagem intralista das mulheres no Cap. 3.** MODERATE, confiança alta. O texto-fonte fecha a dúvida do adversarial: o dado é de 2014, antes do piso da ADI 5617, e a medida é o nível em R$. Não há contradição, e sim dois regimes e duas medidas (M/H em R$ de 0,74/0,86; parcela intralista das mulheres maior dentro de cada estrato de credencial). Datar a L151 e acrescentar uma frase de reconciliação.
-   **I-2-024 (ADV-2-002) — O Cap. 2 está dessincronizado da Introdução e das Considerações, alteradas durante o run.** MODERATE, confiança alta. A pergunta ao autor está abaixo.
-   **I-2-025 (WRI-2-001/002/004) — Estrutura.** A abertura não anuncia o Argumento, a ideia central é aberta três vezes (L95, L176, L204) e a tese só aparece no 7º parágrafo do Argumento. MODERATE. São três achados do mesmo problema, logo um issue. Executar depois da reescrita substantiva.
-   **I-2-026, I-2-027 e I-2-028 (demais WRI) — polimento.** MINOR. Clareza e transições; gramática; tradução de citações e rótulos. O WRI-2-003 (L103, ponte sem referente) foi rebaixado de MODERATE para MINOR: a seção seguinte deixa o assunto claro, e o próprio writing registra o claim como sustentado.

### Demais MODERATE e MINOR (sem mudança de severidade)

| Issue | Título curto | Final | Conf. | Observação da arbitragem |
|---------------|---------------|---------------|---------------|---------------|
| I-2-008 | Núcleo e referência aleatória não definidos | MODERATE | alta | O lift com R \> 0 (1,70/1,82) é sensibilidade, não a referência correta |
| I-2-010 | Cotas: nível do piso e viés | MODERATE | média | Ligado ao I-2-023 |
| I-2-012 | "Não ocorre" → residual; recursos privados | MODERATE | alta | Falar em comovimento, não em "força do candidato" como fato |
| I-2-009 | Comparabilidade 2018×2022 | MODERATE | alta | Absorve o Cap. 4 L25 (previsão sem base no Cap. 2) |
| I-2-006 | Magnitude sem expectativa | MODERATE | alta | **Achado do chair:** Cheibub & Sin encontram coordenação mais difícil em distritos grandes (`cheibub.txt` L70-73), e a priorização financeira do Cap. 3 é mais forte neles. É preciso dizer como as duas se relacionam (o dinheiro como substituto?) |
| I-2-018 | Fiva et al.: "p. 100" | MODERATE | alta (era média) | O artigo é o nº 105133, com 13 páginas de PDF, e não tem "p. 100". A previsão da L93 **existe** (resumo; §4) |
| I-2-007 | Heterogeneidade partidária sem teste | MODERATE | alta | Premissa confirmada em Fiva et al. e em Cheibub & Sin ("larger parties") |
| I-2-011 | Financiamento sem fontes | MODERATE | alta | — |
| I-2-015 | André/Crisp não sustentam o pós-convenção | MODERATE | alta | Janusz et al. sustentam ("party gatekeeping does not end at the nomination stage") |
| I-2-019 | Ausências canônicas | MODERATE | alta | — |
| I-2-014 | Pooling brasileiro (L33) | MODERATE | média | Codificação de Carey & Shugart não conferida |
| I-2-017 | Ferree/Mershon e as "gerações" | MODERATE | média | Sem texto-fonte no repositório |
| I-2-016 | Desposato possivelmente invertido | MODERATE | baixa | O mais frágil do run; cai se o autor confirmar |
| I-2-013 | Dilema do *gatekeeper* só pela proteção | MODERATE | média | — |
| I-2-020 | Ação do partido como pressuposto | MINOR | média | — |
| I-2-021 | Paráfrases esticadas | MINOR | média | — |
| I-2-022 | Formalidades de citação/.bib | MINOR | alta | Completar a entrada de Janusz et al. |

Ordem de trabalho: `runs/run-003/priority_queue.yaml`.

## O que está sólido (não mexer)

-   **Desenho ex-ante (L212-214).** Validado pelos quatro agentes e pelo código (`cap3_cs_features.py` L97-116: `candidato_competitivo` usa só o histórico, e a versão ex-post fica segregada). Resolve a reversão voto → recurso para a hipótese de composição.
-   **Números que o Cap. 2 antecipa ou dos quais depende, recomputados:** lift Top-NECr × competitivos de 1,891/1,855 e cobertura de 81,9%/81,0% (methodology). Recursos de origem partidária = 75,3%/87,9% da receita de DF; FEFC = 80,4%/90,7% do recurso partidário (L147, L157).
-   **A divisão igualitária é rejeitada pelo próprio desenho** (NECr/C, lift \> 1). O capítulo não precisa de teste novo para isso, só de uma frase.
-   **Não há substituição entre dinheiro privado e partidário.** A correlação intralista é positiva, o que responde à provocação de 11/09.
-   **Citações:** as 51 chaves existem no `.bib`. Os localizadores de Carey & Shugart, Samuels 2001, Scarrow & Webb, Silva & Cervi e Cheibub & Sin caem dentro do intervalo de páginas (o de Fiva et al. é exceção). Chang × Kselman e Cox & Thies × Samuels mostram a evidência contrária de forma equilibrada.
-   **Atribuições conferidas na fonte primária:** Janusz et al. sustentam o *resource gatekeeping* pós-convenção, os três instrumentos (número, dinheiro, TV) e a orientação ex-ante (L65, L212). Fiva et al. sustentam a previsão sobre partidos mais competitivos (L93). A caracterização ex-post de Cheibub & Sin (L212) é coerente.
-   **Forma:** as pontes entre seções existem (L69, L103, L129, L169), as referências cruzadas `@sec-*` resolvem e o itálico de estrangeirismos é consistente.

## Conflitos não resolvidos

1.  **Pergunta ao autor (I-2-024, ADV-2-002). Não presumo a resposta.** Os textos atuais de `tese/01-introducao.qmd` e `tese/05-consideracoes-finais.qmd` foram alterados em 19/09 às 00:18, não estão commitados e abrem com um bloco "Roteiro para a redação" de 12 itens. São versão sua, a ser mantida? O repositório não registra a autoria, e o contrato de autoria do projeto torna a pergunta relevante. Se forem seus, alinhar o Cap. 2 a eles fecha boa parte de I-2-001 e I-2-004. Se não forem, eles não servem de referência para a reescrita do Cap. 2, e a formulação do mecanismo fica em aberto na tese inteira.
2.  **Severidade de I-2-005: chair (MAJOR) × adversarial (MODERATE).** Decidi com base em fonte primária que o adversarial não leu, dentro da condição que ele mesmo fixou. Se o autor entender que a tese já se apresenta como reexame de Janusz et al. em outro lugar (por exemplo, na Introdução, se for sua), o issue pode cair para MODERATE no próximo run, desde que o Cap. 2 diga isso.
3.  **Atribuições sem texto-fonte no repositório:** Desposato (I-2-016), a codificação de Carey & Shugart (I-2-014), Mershon/Ferree (I-2-017) e Tavits (I-2-021). A confiança continua como declarada até o autor conferir.

## Próximo run: o que reavaliar

-   **Cap. 2 (depois da reescrita):** L204 (enquadramento e "porque"), L176 ("constitui"), L214 (frente iii), L151 (data de Janusz et al.), L188 (cotas), L147 ("não ocorre"). Incluir `01-introducao.qmd` e `05-consideracoes-finais.qmd` nos insumos do manifest e checar a coerência do mecanismo entre os três. Pôr os PDFs de Desposato, Carey & Shugart, Mershon e Tavits em `revisoes/fontes-discussao-capitulo3/` (ou equivalente) para fechar as atribuições de confiança baixa/média.
-   **Cap. 3:** antecedente NEF (Bolognesi et al.) × NECr; lift por magnitude com teto ou lift normalizado (MET-2-004, conflicts C2); lift com R \> 0 como sensibilidade (C3); L118 ("mais discriminante"); L171 (mulheres, ligado a I-2-023).
-   **Cap. 4 (nunca revisado por agentes):** L13 ("novamente"), L25 (previsão de desconcentração sem base no Cap. 2), L47 (intenção × prontidão), L49 (atribuição a Fiva et al.).