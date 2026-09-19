# Adversarial review — run-003 — Capítulo 2 (`tese/02-literatura.qmd`)

## Escopo e método

- Li `CLAUDE.md`, `PROTOCOL.md`, `rubric.yaml`, `issues_draft.yaml`, `synthesis/conflicts.md`, `agents/theory.md`, `agents/methodology.md` e os achados LIT-2-001/002/009/016 de `agents/literature.md`. Li também o Cap. 2 inteiro, o corpo e o rascunho [3.D] do Cap. 3, o Cap. 4 (L1-70), `tese/01-introducao.qmd`, `tese/05-consideracoes-finais.qmd`, `notes/daily/2026-09-11.md`, `2026-09-13.md` e `2026-09-18.md`, e as entradas `.bib` de Janusz et al., Bolognesi et al., Cox (1997), Fiva et al. e Cheibub & Sin.
- Recomputação: `evidence/adv_rivais_cap2.py` → `evidence/adv_rivais_cap2.out`. Blocos: A (força do candidato), B (dispersão), C/C2 (marginais × credenciados e gradiente da votação prévia), E (mulheres).
- **Fato de processo que afeta vários vereditos.** `tese/01-introducao.qmd` e `tese/05-consideracoes-finais.qmd` foram modificados em 19/09 às 00:18. Os especialistas escreveram entre 00:07 e 00:10, e o chair terminou o `issues_draft.yaml` às 00:16. O Cap. 2 não mudou: o sha256 `f4ba3b00…` é igual ao do manifest. Os dois arquivos novos têm texto no corpo (fora de comentários) que trata de parte dos issues. Não estão commitados (`git status`: `M` e `??`), e o repositório não diz se são do autor ou se são versão final. Por isso, **nenhum veredito abaixo depende só deles**. Onde os cito, é como evidência de que a decisão de interpretação já foi tomada fora do Cap. 2. Uma consequência direta: a frase de `agents/theory.md` (Escopo) "a introdução ainda não formula a contribuição" era verdadeira quando o agente fez o grep e hoje está desatualizada (Intro L32, L52).
- Não consegui verificar o conteúdo de Janusz, Barreiro & Cintron (2021), cujo período e fonte não estão no `.bib`, nem o de Cox (1997) além do título. Onde uso memória sobre essas obras, digo isso.

## Vereditos (issues MAJOR)

```yaml
issue_id: I-2-001
steelman: "L204 afirma, como tese, que os partidos priorizam credenciados PORQUE a credencial sinaliza contribuição ao desempenho coletivo. A única implicação enunciada (sobrerrepresentação em relação ao acaso) também decorre das rivais que a própria L178 nomeia (captura, barganha, ameaça de saída) e da força do candidato. O Cap. 2 não diz que observação as separa, então o 'porque' não é falseável pelos testes planejados."
assessment: valid
evidencia_contra:
  - fonte: "tese/01-introducao.qmd:36; tese/05-consideracoes-finais.qmd (parágrafo 'Há limites para a interpretação do mecanismo proposto')"
    detalhe: "Texto posterior ao run já adota a formulação recomendada: 'a pesquisa procura identificar padrões compatíveis com o argumento proposto, preservando a distinção entre a prioridade observada e as motivações que a produziram' e 'sem separar integralmente essas explicações'. A decisão de interpretação existe na tese, mas o Cap. 2 (L204, 'porque') não a acompanha."
  - fonte: "tese/03-medindo-coordenacao-intrapartidaria.qmd:157; evidence/adv_rivais_cap2.out (bloco C2)"
    detalhe: "Há evidência discriminante contra a captura pura por mandatários, e ela é mais forte do que os especialistas registraram. Além de qe_sem_vitoria (2,89/1,70), a parcela normalizada s·C cresce com a votação anterior no grupo formado por candidaturas sem credencial e credenciadas só por votação, sem vitória para DF (Spearman 0,43 em 2018 e 0,47 em 2022). A captura por quem ocupa mandato ou direção não prevê esse gradiente."
  - fonte: "evidence/adv_rivais_cap2.out (blocos A e C2), a favor da crítica"
    detalhe: "Tentei derrubar a rival 'força do candidato' residualizando a correlação intralista entre parcela partidária e não partidária pelas credenciais (contagens por cargo, 10% QE, votos t-1, mulher, negra). Não caiu: vai de 0,407 para 0,324 em 2018 e de 0,337 para 0,250 em 2022. Dentro de cada estrato fica em 0,28/0,23 (credenciados/sem credencial, 2018) e 0,21/0,24 (2022). Entre os ex-eleitos para DF, a parcela não cresce com a votação anterior (Spearman −0,13 em 2018, n=296; 0,06 em 2022, n=499), e em 2018 o quartil mais votado recebe menos (mediana s·C 1,99 contra 3,38 no Q3). Um perfil plano entre mandatários é o que a captura por posição prevê. A direção da correlação com o dinheiro privado continua ambígua: o dinheiro do partido pode atrair doadores. A rival não é demonstrada, mas também não é excluída."
severidade_sugerida: MAJOR
razao: "A crítica se sustenta para o Cap. 2 como está escrito. A L204 enuncia o mecanismo como tese demonstrável, e a L178 nomeia rivais que o capítulo abandona. Minha recomputação reforça a crítica: entre mandatários, o padrão é compatível com a captura. O atenuante é real, mas externo ao capítulo: a Intro e as Considerações já adotam 'compatível com'. Se o Cap. 2 alinhar a L204 a essa formulação e anunciar o teste discriminante que já existe (votação sem mandato), cai para MODERATE."
o_que_o_autor_pode_responder: "Os testes não separam sinalização de barganha, mas separam sinalização de captura por mandatários: candidaturas sem mandato recebem mais quanto maior foi sua votação anterior (Cap. 3, votação ≥10% do QE sem vitória), padrão que a captura não prevê."
```

```yaml
issue_id: I-2-002
steelman: "As regras que o próprio capítulo descreve (35% do FEFC e 95% do FP por votos; pooling) são compatíveis com dispersão e com foco em candidatos marginais. O Argumento passa de 'seletivamente' (L174) a 'credenciados' (L204) sem excluir essas estratégias, não cita a literatura de alocação partidária e não prevê a direção 2018→2022, que o Cap. 4 (L25) deriva no sentido oposto."
assessment: partially_valid
evidencia_contra:
  - fonte: "tese/02-literatura.qmd:204"
    detalhe: "O elo que a recomendação pede ('sob incerteza, a credencial é o único sinal ex-ante') já está no texto: 'Quando os recursos são distribuídos, a votação ainda é incerta. Vitórias anteriores e votações expressivas oferecem sinais observáveis da capacidade de organizar uma campanha e atrair eleitores.' O passo incerteza → sinal → credenciados existe. Falta dizer o que ele não exclui."
  - fonte: "evidence/adv_rivais_cap2.out (bloco B); tese/03-medindo-coordenacao-intrapartidaria.qmd:96"
    detalhe: "A dispersão como rival é rejeitada pelos dados. Uma alocação igualitária dá NECr/C = 1 e lift = 1 por construção. Observado nas listas financiadas com C>1: NECr/C mediano de 0,466 (2018) e 0,519 (2022). Só 8,2% e 11,7% das listas ficam com NECr/C ≥ 0,9. O lift é 1,89/1,86. O teste E1 já discrimina concentração de dispersão, então o que falta é uma frase, não um teste."
  - fonte: "tese/02-literatura.qmd:61; evidence/adv_rivais_cap2.out (bloco C2)"
    detalhe: "O foco em marginais não é rival da expectativa testada (E1). Ex-ante, o partido só identifica marginais pelos mesmos sinais de histórico, e as candidaturas sem credencial são em grande parte fracas (Hott & Menezes, L61). Nos quintis inferiores de votação anterior, s·C médio fica em 0,40 e 1,75 (2018). Uma estratégia de marginais também produz lift > 1 para credenciados. Ela só diverge da concentração nos 'mais fortes' DENTRO do grupo credenciado, e a L204 não faz essa afirmação."
  - fonte: "tese/04-mecanismo-causal-coordenacao.qmd:25; rascunho [3.D] em tese/03-medindo-coordenacao-intrapartidaria.qmd:248"
    detalhe: "'Direção oposta' é exagero. O Cap. 4 L25 fala do GRAU de concentração entre 2018 e 2022 (desconcentração). A L204 fala da COMPOSIÇÃO do topo em relação ao acaso. Os dois valem ao mesmo tempo nos dados: o NECr médio vai de 2,96 para 5,90 e o lift fica em 1,89→1,86. O Cap. 4 L25 é uma previsão auxiliar não derivada (pertence a I-2-009), não uma contradição com a tese central."
  - fonte: "tese/01-introducao.qmd:36, :50 (texto posterior ao run)"
    detalhe: "'Tampouco se pressupõe que financiar candidaturas com histórico seja necessariamente a estratégia que maximiza votos ou cadeiras'. Sobre 2018×2022: 'a comparação descreve essas mudanças sem permitir atribuí-las isoladamente a uma reforma institucional'. Na Intro, o autor já escolheu a opção 'declarar que a tese não distingue essas lógicas'."
  - fonte: "evidence/adv_rivais_cap2.out (bloco C2), a favor da crítica"
    detalhe: "Entre os ex-eleitos para DF de 2018, o quartil de maior votação anterior recebe menos que o Q3 (s·C médio 3,26 contra 5,89; mediana 1,99 contra 3,38). Isso é compatível com retorno marginal decrescente ou foco em marginais dentro do grupo credenciado. O Cap. 2 não deve sugerir que o dinheiro vai aos 'mais fortes'. A frase atual ('capazes de contribuir') não sugere isso, mas o texto também não o exclui."
severidade_sugerida: MODERATE
razao: "Três das quatro partes da crítica não se sustentam como MAJOR. O elo incerteza → sinal está na L204. A dispersão já é rejeitada pelo teste E1 e pelo NECr/C. A 'direção oposta' do Cap. 4 confunde grau com composição. Resta um problema real de redação: o Argumento não diz que o foco em marginais e a concentração em credenciados são indistinguíveis no nível de E1, nem que a tese não prevê direção para 2018→2022. A lacuna bibliográfica (LIT-2-002) é MODERATE por si só. Nada disso exige mudar a interpretação: o autor já a fixou (Intro L36) e o teste já existe."
o_que_o_autor_pode_responder: "A tese não afirma que concentrar em credenciados maximiza cadeiras. Afirma que, sob incerteza, o histórico é o sinal disponível para identificar candidaturas viáveis, e isso vale para quem busca puxadores e para quem busca marginais. O teste rejeita a divisão igualitária, que não produziria lift acima de 1."
```

```yaml
issue_id: I-2-003
steelman: "A frente (iii) sustenta um capítulo inteiro (Cap. 4) sem expectativa derivada no Cap. 2. Ela promete 'priorização temporal ao núcleo priorizado', mas o Cap. 4 testa credenciais (e usar o núcleo seria circular). A rival da prontidão administrativa, que o Cap. 4 L9 torna evidente, não aparece."
assessment: partially_valid
evidencia_contra:
  - fonte: "tese/04-mecanismo-causal-coordenacao.qmd:29; tese/01-introducao.qmd:32 (posterior ao run)"
    detalhe: "A justificativa substantiva existe na tese, fora do Cap. 2. Cap. 4 L29: 'O recebimento antecipado de recursos de campanha dá aos candidatos contemplados maior margem para aplicação deste dinheiro… \"colocar a campanha na rua\" mais cedo'. Intro L32: 'receber recursos mais cedo amplia o período disponível para sua aplicação'. Transpor isso para o Cap. 2 é trabalho de redação."
  - fonte: "tese/01-introducao.qmd:46; tese/05-consideracoes-finais.qmd (parágrafo 'A conexão entre os dois capítulos'); rascunho [3.D] Cap. 3 L258"
    detalhe: "A troca núcleo → credencial está justificada em três lugares (circularidade: o Top-NECr é calculado com o total ao fim da campanha). No Cap. 2 L214, a correção é de uma palavra. Essa parte é MINOR."
  - fonte: "tese/02-literatura.qmd:91"
    detalhe: "A sub-alegação de THE-2-003 ('a lógica de Fiva et al. pode prever o contrário: antecipar dinheiro aos protegidos agrava o risco moral') não tem apoio no próprio capítulo. A L91 localiza o custo em esforço nos 'candidatos não contemplados', e o momento do repasse aos protegidos não altera isso. É especulação sem página e deve sair do issue."
  - fonte: "tese/05-consideracoes-finais.qmd (parágrafo 'Outro limite…'), a favor da crítica"
    detalhe: "A rival administrativa é admitida como não resolvida: 'Diferenças de prontidão das campanhas constituem uma explicação adicional a investigar, e a persistência do padrão para o maior repasse não elimina essa possibilidade.' O Cap. 4 L47 continua concluindo intenção ('partidos políticos consideram a vantagem…'). Não há na base data de habilitação da conta ou do CNPJ que permita testar essa rival (colunas de `rrd_df_novo.parquet`: só `dt_receita`/`dias_desde_inicio` do repasse)."
severidade_sugerida: MAJOR
razao: "A parte núcleo × credencial e a leitura invertida de Fiva caem. O núcleo do issue fica de pé: a frente (iii) não tem expectativa no Cap. 2, e há uma rival específica do timing que a própria tese admite não ter eliminado nem poder testar com os dados atuais. Isso limita o que o Cap. 4 pode concluir (intenção × prontidão), e esse é o tipo de mudança de interpretação que a rubrica chama de MAJOR. O custo da correção no Cap. 2 é baixo (a justificativa já existe na Intro L32 e no Cap. 4 L29)."
o_que_o_autor_pode_responder: "O argumento prevê antecipação porque o dinheiro recebido cedo rende mais tempo de campanha. A tese documenta a antecipação, mas não a separa da prontidão administrativa das campanhas com histórico, e por isso a trata como padrão compatível com uma decisão partidária."
```

```yaml
issue_id: I-2-004
steelman: "'Coordenação intrapartidária' é o conceito do título. A L176 diz que a alocação 'constitui' um instrumento que 'orienta a competição para objetivos coletivos', mas nenhuma frente mede efeito sobre a competição ou o resultado coletivo, e o Cap. 3 L76 descarta a validação ex-post. O desenho mede priorização, não coordenação."
assessment: partially_valid
evidencia_contra:
  - fonte: "tese/02-literatura.qmd:63; tese/references.bib:180-186"
    detalhe: "A literatura que o capítulo mobiliza já usa 'coordenação' em sentido comportamental, sem exigir medida de efeito. Na L63, Cheibub & Sin tratam como 'coordenação intralista' o número de competitivos próximo às cadeiras, que é um padrão de estrutura da lista e não um efeito medido. O Cox (1997) citado na L121 tem como título 'Strategic Coordination'. Minha leitura da obra (memória, confiança média) é que a coordenação das elites se observa na concentração de recursos em concorrentes viáveis. Com essa definição, o que a tese mede é a implicação observável do conceito."
  - fonte: "notes/daily/2026-09-11.md:5"
    detalhe: "Definição do próprio autor: 'a definição de coordenação: não é concentração, mas priorização de um conjunto competitivo de candidaturas'. É exatamente o que as frentes (i)-(ii) medem. O defeito é que essa definição não chegou ao Cap. 2."
  - fonte: "tese/05-consideracoes-finais.qmd:20 (posterior ao run)"
    detalhe: "'compatível com o emprego do dinheiro partidário como instrumento de coordenação intrapartidária': é a troca 'constitui' → 'compatível com' que MET-2-005 recomenda."
  - fonte: "tese/02-literatura.qmd:139, :95"
    detalhe: "'Vantagem competitiva' (L95) é uma premissa ancorada em Thomsen (L139: os recursos 'condicionam a capacidade das campanhas'), não uma afirmação de efeito que a tese precise testar. Dar dinheiro a alguém é dar capacidade de competir."
  - fonte: "issues_draft.yaml I-2-001"
    detalhe: "O que sobra de 'para objetivos coletivos' é a MOTIVAÇÃO da alocação, e isso é exatamente o I-2-001 (as rivais não são discriminadas). Manter o I-2-004 como MAJOR conta o mesmo defeito duas vezes."
severidade_sugerida: MODERATE
razao: "A condição que o chair pôs em conflicts.md C1 se cumpre. Existe uma definição comportamental de coordenação, ancorada em obras já citadas (Cheibub & Sin L63; Cox 1997 no .bib) e já adotada pelo autor (nota de 11/09; Considerações). Sob ela, a medida corresponde ao conceito. A parte que exige interpretação ('objetivos coletivos') duplica o I-2-001. Resta um defeito de definição e redação: o termo não é definido no Cap. 2, muda de sentido (L55, L63, L176) e a L176 diz 'constitui'."
o_que_o_autor_pode_responder: "Nesta tese, coordenação designa a priorização sistemática de recursos escassos a candidaturas identificadas como viáveis, no sentido comportamental de Cox (1997) e de Cheibub & Sin (2020). A tese não mede o efeito dessa coordenação sobre o resultado da legenda."
```

```yaml
issue_id: I-2-005
steelman: "Pelo que o Cap. 2 diz, Janusz et al. já mostram resource gatekeeping pós-convenção, privilégio a incumbentes e ex-ocupantes de cargo, e usam classificação ex-ante: praticamente a E1/E2 da tese. O capítulo não diz o que a tese acrescenta, omite Bolognesi et al. (2020) e muda entre os capítulos a diferença frente a Cheibub & Sin."
assessment: partially_valid
evidencia_contra:
  - fonte: "tese/02-literatura.qmd:212; tese/03-medindo-coordenacao-intrapartidaria.qmd:100; tese/04-mecanismo-causal-coordenacao.qmd:13"
    detalhe: "'Muda entre capítulos' é exagero. São três eixos compatíveis: diferença de mensuração (ex-ante × ex-post, Cap. 2), convergência substantiva com o afunilamento ('reforçam', Cap. 3) e diferença de momento (pós-lista, Cap. 4). Concordar com um achado e divergir da medida não é contraditório. O defeito real é só o 'novamente' do Cap. 4 L13, que pressupõe uma diferença de momento que o Cap. 2 nunca atribui aos autores."
  - fonte: "tese/references.bib:43-49; tese/02-literatura.qmd:153"
    detalhe: "Bolognesi et al. (2020) trata de '2014 no Brasil' (título no .bib), antes do FEFC e com dinheiro empresarial. O capítulo já tem o critério que distingue a tese desses estudos: 'O objeto da tese se distingue… em razão do contexto institucional' (L153). Contra Bolognesi, o que falta é a citação (MODERATE isolado, como o próprio chair nota em C5), não uma delimitação nova."
  - fonte: "tese/02-literatura.qmd:212"
    detalhe: "O capítulo não reivindica novidade sobre Janusz et al.: declara que 'segue a orientação ex-ante de @janusz_barreiro_cintron_2021'. Nada no texto afirma uma prioridade que precise ser retirada. O problema é de ausência de delimitação, não de reivindicação falsa."
  - fonte: "evidence/adv_rivais_cap2.out (bloco E), a favor da crítica e útil ao autor"
    detalhe: "Há um ponto substantivo de diferença (ou tensão) com Janusz et al. que ninguém registrou: ver ADV-2-001. Ele pode servir à delimitação."
severidade_sugerida: MODERATE
razao: "As partes Cheibub & Sin e Bolognesi não se sustentam como MAJOR. O que fica é a falta de duas ou três frases que delimitem a contribuição frente a Janusz et al., e o capítulo não faz afirmação falsa sobre eles. Condição explícita para voltar a MAJOR: se Janusz et al. analisam a eleição de 2018 com recursos partidários do FEFC e comparação entre candidaturas da mesma lista, a novidade das frentes (i)-(ii) precisa ser reescrita. Nenhum agente leu a obra, e o .bib não traz período nem páginas. O autor deve conferir antes da arbitragem final."
o_que_o_autor_pode_responder: "Janusz et al. mostram que o dinheiro partidário favorece incumbentes; a tese acrescenta a delimitação endógena do núcleo por lista, a comparação intralista por componente do histórico, o timing dos repasses e duas eleições sob o FEFC (a confirmar conforme o período analisado por eles)."
```

## Omissões dos especialistas

```yaml
id: ADV-2-001
titulo: "A L151 relata, via Janusz et al., que mulheres recebem menos 'mesmo controlando' a experiência, e os dados da própria tese mostram vantagem intralista das mulheres. O capítulo não reconcilia as duas coisas."
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 151
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "a análise desagregada dos resultados mostra que mulheres receberam sistematicamente menos recursos que homens, mesmo controlando-se a \"qualidade da candidatura\" medida por sua experiência prévia."
afirmacao_do_autor: "A distribuição partidária penaliza mulheres, condicional à experiência (Janusz et al.)."
problema: "No corpo do Cap. 3 (L171), ser mulher está associado a parcela intralista MAIOR (razões de 1,44 e 1,32) com as credenciais controladas. Recomputei (bloco E): a parcela normalizada s·C das mulheres é igual à dos homens no bruto (M/H 1,01 em 2018; 0,95 em 2022) e maior dentro de cada estrato de credencial (1,26/1,46 em 2018; 1,20/1,25 em 2022, credenciados/sem credencial). O valor médio em R$ é menor (M/H 0,74/0,86). A desvantagem, portanto, está ENTRE listas (as mulheres se concentram em listas com menos recursos por candidatura), não DENTRO delas. O Cap. 2 reporta o achado de Janusz et al. sem data nem medida e não o confronta com o resultado da tese. Se Janusz et al. tratam de 2014, há uma mudança associada às cotas de financiamento (ADI 5617, L155) que reforça o argumento de I-2-010. Se tratam de 2018, há uma contradição de medida (nível × parcela; entre × dentro da lista) que precisa ser explicada. Nenhum dos três agentes cruzou a L151 com o Cap. 3 L171."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-003/evidence/adv_rivais_cap2.py (bloco E)"
    - "thesis-review/runs/run-003/evidence/adv_rivais_cap2.out"
    - "tese/03-medindo-coordenacao-intrapartidaria.qmd:171"
    - "tese/02-literatura.qmd:151, :155, :188"
    - "thesis-review/runs/run-003/evidence/met_cap2_alternativas.out (bloco F: mulheres = 31,7% das candidaturas e 25,6% dos recursos DF em 2018)"
  detalhe: "Listas financiadas. 2018: bruto M/H=1,01 (R$ médio 0,74); credenciados 1,26 (nM=116, nH=845); sem credencial 1,46 (nM=2.231, nH=4.203). 2022: 0,95 (0,86); 1,20 (207/1.145); 1,25 (3.075/4.916)."
severidade: MODERATE
confianca: media
recomendacao: "Na L151, informar a eleição e a medida de Janusz et al. e dizer em uma frase como o achado se relaciona com o da tese (desvantagem em nível e entre listas × vantagem intralista condicional). Usar a diferença na delimitação da contribuição (I-2-005) e no argumento das cotas (I-2-010)."
claims: [C2.6.06, C2.7.11]
nota: "Confiança média: a recomputação é inequívoca; o período e a especificação de Janusz et al. não foram verificados."
```

```yaml
id: ADV-2-002
titulo: "Depois do run, a Introdução e as Considerações passaram a adotar a leitura 'compatível com', e o Cap. 2 ficou dessincronizado delas"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 204
  secao: "## Argumento"
  trecho: "O argumento desta tese é que os partidos priorizam financeiramente candidaturas com credenciais eleitorais prévias porque estas constituem sinais da capacidade destes candidatos em contribuir para o desempenho coletivo da legenda."
afirmacao_do_autor: "O mecanismo é enunciado como tese (Cap. 2) e como padrão compatível (Intro L36; Considerações)."
problema: "`tese/01-introducao.qmd` e `tese/05-consideracoes-finais.qmd` (mtime 19/09 00:18, depois dos especialistas e do issues_draft) dizem: 'padrões compatíveis com o argumento proposto'; 'Tampouco se pressupõe que financiar candidaturas com histórico seja necessariamente a estratégia que maximiza'; 'compatível com o emprego do dinheiro partidário como instrumento de coordenação'; e admitem as rivais e a prontidão administrativa. O Cap. 2 continua com 'porque' (L204), 'constitui' (L176) e sem rivais para o timing. A tese hoje sustenta duas posições sobre o próprio mecanismo. Além disso, o manifest do run só registra o hash do Cap. 2 e do .bib, então as checagens dos agentes sobre a Intro ('não formula a contribuição') não valem para a versão atual."
evidencia:
  tipo: textual
  fontes:
    - "tese/01-introducao.qmd:32, :36, :46, :50, :52"
    - "tese/05-consideracoes-finais.qmd:20 e parágrafos 'Há limites…' e 'Outro limite…'"
    - "tese/02-literatura.qmd:176, :204, :214"
    - "thesis-review/runs/run-003/manifest.yaml (insumos)"
  detalhe: "ls --time-style=full-iso: 01-introducao 00:18:48; 05-consideracoes 00:18:52; agents/*.md 00:07-00:10; issues_draft.yaml 00:16. sha256 do Cap. 2 igual ao manifest (f4ba3b00…)."
severidade: MODERATE
confianca: alta
recomendacao: "Chair: (1) registrar em final_review.md que a Intro e as Considerações mudaram durante o run e que I-2-001/002/003/004 têm atenuante fora do capítulo. (2) Pedir ao autor que confirme se esses textos são versão sua; o repositório não diz, e o contrato de autoria (memória 'no AI text in thesis body') torna isso relevante. (3) Tratar o alinhamento do Cap. 2 à Intro como a ação que fecha I-2-001 e I-2-004. Em um run futuro, incluir 01 e 05 nos insumos do manifest."
claims: [C2.7.02, C2.7.03, C2.7.10]
```

## Observações sobre recomputações que tocam issues MODERATE

- **I-2-012 (força do candidato / recursos não partidários).** A correlação +0,41/+0,34 que MET-2-009 usa **sobrevive** ao controle pelas credenciais (parcial 0,32/0,25), então a recomendação de nomear a rival se sustenta. A direção causal, porém, não é identificável: o dinheiro do partido também pode atrair doadores. O texto deve falar em comovimento, não em "força do candidato" como fato.
- **I-2-010 (cotas).** O bloco E indica que a desigualdade de gênero em R$ está entre listas, e que dentro da lista as mulheres têm parcela maior. Isso reforça a leitura de que o piso opera no agregado do partido e afeta a alocação intralista a favor delas. O viés contra a hipótese (teste conservador) continua plausível.

## Resumo dos vereditos

| Issue | Assessment | Severidade inicial | Sugerida | Principal razão |
|---|---|---|---|---|
| I-2-001 | valid | MAJOR | MAJOR | L204 afirma o "porque". A recomputação reforça a rival da captura entre mandatários. Cai para MODERATE se o Cap. 2 se alinhar à Intro L36 e anunciar o teste da votação sem mandato |
| I-2-002 | partially_valid | MAJOR | MODERATE | O elo incerteza → sinal está na L204. A dispersão já é rejeitada (NECr/C mediano 0,47/0,52; lift 1,89/1,86). Marginais também preveem E1. O Cap. 4 L25 é sobre grau, não composição |
| I-2-003 | partially_valid | MAJOR | MAJOR | Sem expectativa no Cap. 2, e a rival da prontidão não é testável com a base. As partes núcleo × credencial e Fiva invertido caem |
| I-2-004 | partially_valid | MAJOR | MODERATE | Há definição comportamental disponível (Cheibub & Sin L63; Cox 1997; nota do autor de 11/09). A parte "objetivos coletivos" duplica o I-2-001 |
| I-2-005 | partially_valid | MAJOR | MODERATE (volta a MAJOR se Janusz et al. cobrirem 2018/FEFC intralista) | Cheibub & Sin: três eixos compatíveis. Bolognesi 2014 já coberto pelo critério da L153. Falta a delimitação frente a Janusz |
| ADV-2-001 | nova | — | MODERATE | L151 × Cap. 3 L171: vantagem intralista das mulheres não reconciliada |
| ADV-2-002 | nova | — | MODERATE | Intro e Considerações mudaram depois do run; o Cap. 2 ficou dessincronizado |
