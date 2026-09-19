# Revisão pendente: "Financiamento de campanhas no Brasil" e "Argumento"

-   **Data da análise:** 18/09/2026.
-   **Arquivo analisado:** [tese/02-literatura.qmd](../../tese/02-literatura.qmd), linhas 129–193 (versão lida nesta data; as linhas podem mudar depois de edições).
-   **Escopo:** estrutura argumentativa, consistência interna, fatos institucionais, números e estilo. Também confere as afirmações que podem ser checadas em `data/processed/rrd_df_novo.parquet`. As obras citadas **não** foram relidas. O que depende delas está marcado como *conferir na fonte*.
-   **O que esta nota não faz:** não traz parágrafos reescritos. As correções pontuais ficam no nível da palavra ou da frase curta. Nos problemas de argumento, a nota descreve o que falta e deixa a redação com o autor.
-   **Complementa:** [02-literatura-revisao-de-estilo-e-autoria.md](02-literatura-revisao-de-estilo-e-autoria.md), que cobre o capítulo até a linha 131.

------------------------------------------------------------------------

## 1. Diagnóstico geral

As duas seções carregam o peso de ligar a revisão de literatura ao desenho empírico. **Financiamento** deveria entregar três coisas: (a) o lugar da tese na literatura sobre financiamento; (b) a mudança institucional que torna o objeto novo; (c) o incentivo partidário que motiva a alocação seletiva. **Argumento** deveria transformar isso em um mecanismo, uma expectativa observável e um desenho de teste.

As peças estão presentes, mas há três problemas estruturais:

1.  **Ordem e redundância.** O contexto institucional aparece duas vezes em Financiamento (l. 135–137 e l. 149–151). Os mesmos estudos e números de @silvacervi2017 e @janusz_barreiro_cintron_2021 voltam em Argumento (l. 141 ≈ l. 177; l. 143 ≈ l. 185). Por isso, o Argumento parece recomeçar a revisão em vez de avançar a partir dela.
2.  **Falta de ligação entre as seções.** Financiamento termina com o argumento da *sobrevivência* organizacional (l. 164–166: votos e cadeiras em *t* definem os fundos até *t+4*). O Argumento, porém, abre com a primeira e a segunda geração do voto preferencial (l. 173) e não retoma a sobrevivência. O melhor gancho teórico da seção anterior fica sem uso.
3.  **Mecanismo subespecificado.** O Argumento afirma que credenciais prévias sinalizam "capacidade de contribuir para o desempenho coletivo" (l. 187). Não explica por que o partido maximiza esse desempenho concentrando recursos em quem tem credenciais, e não em outras estratégias. Também não apresenta as explicações rivais para o mesmo padrão observável. Ver a seção 3.

Há ainda dois problemas de acabamento que precisam ser resolvidos antes de qualquer outra revisão: a linha 137 tem um marcador de rascunho, e as linhas 181–183 têm uma frase quebrada. Ver a seção 2.

------------------------------------------------------------------------

## 2. Correções pontuais

### 2.1 Erros e marcas de rascunho

| Linha | Trecho | Problema | Correção sugerida |
|------------------|------------------|------------------|------------------|
| 137 | "**Mas isso não é novidade...**" | Marcador de rascunho em negrito no corpo do texto. | Remover e escrever a transição para o modelo anterior (l. 139). |
| 175 | "Essa interpretação teórica orienta **o** tese." | Concordância. | "orienta **a** tese". |
| 181–183 | "Nestes termos, ⏎⏎ Interessa verificar…" | A frase termina em "Nestes termos," e um novo parágrafo começa com "Interessa". Sobrou de uma edição. | Juntar os dois trechos em uma frase ou apagar "Nestes termos,". |
| 169–171 | `<!-- Revisão pendente: texto melhorado por IA a partir de rascunho humano -->` | Pelo próprio comentário, o Argumento inteiro está marcado como texto melhorado por IA. Isso entra em conflito com o compromisso de autoria. | Prioridade máxima: reescrever a seção a partir do rascunho humano original, usando esta nota como checklist e não como texto-fonte. |
| 123 (vizinha) | "leva Samuels **à** uma conclusão semelhante **a** levantada" | Crase indevida antes de artigo indefinido; falta crase em "à levantada". | "a uma conclusão semelhante **à** levantada". |
| 133 | "enquanto os partidos se diferenciam significativamente" | "Significativamente" é ambíguo em um texto estatístico: pode significar "muito" ou "com significância estatística". | Usar "substancialmente" ou indicar o teste. |
| 141 | "estes recursos empresariais que são roteados pelas legendas" | "Roteados" é um anglicismo (*routed*). | "intermediados pelas legendas" (o termo já usado na l. 139). |
| 143 | "Este caráter de seletividade produziu desigualdade" | Atribui causalidade a um achado descritivo. | "Essa seletividade se traduz em desigualdade…", ou conferir se os autores fazem inferência causal. |
| 147 | "tratando as primárias partidárias" | Regência. | "ao tratar das primárias" ou "com dados das primárias". |
| 164 | "no ano `t`" / "`t+4`" | A fonte de código (crases) mistura notação matemática com código no PDF. | Usar `$t$`, `$t+4$` em LaTeX, como no Cap. 3. |

### 2.2 Fatos institucionais e números a conferir

| Linha | Trecho | Problema | Evidência / ação |
|------------------|------------------|------------------|------------------|
| **160** | "4 bilhões de reais foram distribuídos conforme o resultado \[…\] Os **900 milhões** restantes foram alocados segundo \[…\] Senado (735 milhões) e igualmente entre todos os partidos (98 milhões)." | **Erro aritmético.** 735 + 98 = **833 milhões**, não 900. Com FEFC = 4,9 bi: 83% = 4,067 bi; 15% = 735 mi; 2% = 98 mi. O "900 milhões" vem de 4,9 − 4,0, com o 4,0 já arredondado para baixo. Se o valor exato do FEFC 2022 for usado (≈ R\$ 4,96 bi, *conferir na fonte*), as parcelas mudam um pouco. | Recalcular as três parcelas a partir do mesmo valor-base e usar o mesmo arredondamento em todas. |
| 160 | "segundo o desempenho nas eleições para o Senado Federal **de 2018**" | O critério de 15% é o **tamanho da bancada no Senado**, não o resultado de uma eleição. Em 2022, a bancada reunia senadores eleitos em 2014 (1/3) e em 2018 (2/3). | Reformular como "bancada no Senado". *Conferir* a data de referência da bancada na redação vigente em 2022 (art. 16-D da Lei 9.504/97, alterado pela Lei 13.877/2019). |
| 155–160 | "48% proporcionalmente ao número de representantes \[…\] na Câmara" → "83% \[…\] desempenho partidário nas eleições para a Câmara" | Os 48% dependem do número de representantes. Se a base for a bancada em certa data, e não o número de eleitos, as migrações partidárias entram no cálculo e os 83% deixam de ser puramente "desempenho eleitoral". A Lei 13.877/2019 passou a usar os eleitos na última eleição geral, com ressalvas. | *Conferir* o critério aplicável em 2018 e em 2022. Se forem diferentes, dizer isso: a tese analisa os dois pleitos. |
| 137 | "Por definição da **própria legislação que criou o FEFC**, \[…\] respeitando critérios legais de cotas para candidaturas de mulheres, **pessoas negras e pardas**." | \(i\) As cotas de recursos não vieram da lei que criou o FEFC (Leis 13.487 e 13.488/2017). Vieram de decisões posteriores do STF e do TSE: ADI 5617 e consulta ao TSE de 2018 para mulheres; consulta de 2020 e ADPF 738 para candidaturas negras. Depois foram constitucionalizadas (EC 117/2022). (ii) "Negras e pardas" é redundante: pela classificação do IBGE usada pelo TSE, "negras" = pretas + pardas. A l. 179 já descreve isso corretamente com @tse2018financiamentofeminino e @tse2022criteriosfefc. | Corrigir a origem normativa e usar "pessoas negras (pretas e pardas)". |
| 162 | "Desde 2007, 95% dos valores do Fundo Partidário \[…\] são distribuídos conforme os votos" | Correto em linhas gerais (art. 41-A da Lei 9.096/95, na redação da Lei 11.459/2007). Mas omite a **cláusula de desempenho** (EC 97/2017): desde 2019, só têm acesso ao Fundo Partidário os partidos que superam o limiar. Esse é o argumento mais forte para a tese da "sobrevivência" (l. 166), e ele não aparece. | Incluir a EC 97/2017 e a escada de limiares (1,5% em 2018; 2% em 2022). Isso fortalece a l. 166. *Conferir* os percentuais na fonte. |
| 149 | "Desde as eleições de 2018, candidaturas a deputado federal não podem receber recursos de pessoas jurídicas" | Correto, mas a proibição vale para todas as candidaturas desde 2016. A formulação sugere uma regra específica para deputados. | Dizer que 2018 foi a primeira eleição **geral** sob a proibição (ADI 4650/2015; Lei 13.165/2015). |
| 141 | "dos R\$ 428 milhões repassados pelos partidos \[…\] em 2014, 89,6% \[…\] pessoas jurídicas e \[…\] 7,5% \[…\] Fundo Partidário" | **Batem com a base da tese.** Em `rrd_df_novo.parquet`, a soma de `vr_receita_recursos_partidos` em 2014 dá **R\$ 433,8 mi**, e `vr_receita_fp` dá **R\$ 31,9 mi (7,35%)**. A pequena diferença é compatível com diferenças de extração. | Nada a corrigir. Se quiser, uma nota de rodapé pode registrar que a base da tese reproduz a ordem de grandeza. |
| 177 | "em 2014, os partidos se tornaram a principal origem imediata das receitas" | Não dá para checar na base: `vr_receita_outros` (R\$ 736,9 mi em 2014) junta várias origens. | *Conferir na fonte* (página em @silvacervi2017). |

### 2.3 Citações ausentes (afirmações empíricas sem referência)

-   **l. 133:** "A vinculação à base governista também está associada a maiores volumes de doações, enquanto os partidos se diferenciam…" não tem citação.
-   **l. 133:** "A literatura identifica, ainda, associações entre o custo das campanhas e fatores como a magnitude do distrito, o PIB municipal, o grau de urbanização e a desigualdade de renda." Nenhuma referência sustenta a frase, embora "a literatura" seja o sujeito.
-   **l. 151:** "Essa mudança conferiu às lideranças partidárias maior centralidade na estruturação das condições de competição" é uma afirmação empírica sem citação (candidatos: @silvacodato2024 e trabalhos sobre o FEFC).
-   **l. 135:** "que se tornou a principal fonte de recursos": a base confirma. Os recursos de partido com origem no FEFC somam R\$ 809 mi em 2018 e R\$ 2.584 mi em 2022, contra R\$ 327 mi e R\$ 394 mi de "outros". Mesmo assim, falta citação ou remissão à base.

------------------------------------------------------------------------

## 3. Buracos argumentativos

### 3.1 O Argumento não usa o incentivo construído em Financiamento

> l.  166: "argumenta-se que as eleições para deputado federal são cruciais para \[…\] a sua sobrevivência. Por este motivo, partidos possuem incentivos para distribuir os recursos que controlam de maneira seletiva e estratégica."

> l.  173: "Para a primeira geração de estudos sobre o voto preferencial…"

A l. 166 anuncia que "este é o argumento da tese que será detalhado na seção seguinte". A seção seguinte, porém, não detalha o argumento da sobrevivência: volta ao debate das gerações e à noção de coordenação (@fivaetal2024). O leitor fica com dois argumentos soltos: (a) sobrevivência financeira; (b) coordenação intrapartidária. Falta a frase-ponte que mostre que (a) é a *razão* pela qual o partido busca (b).

### 3.2 Votos vs. cadeiras: o incentivo aponta em duas direções

As regras descritas nas l. 155–162 **não recompensam só cadeiras**. Os 35% do FEFC e os 95% do Fundo Partidário são proporcionais a **votos**. Os 48% do FEFC são proporcionais a **cadeiras**. Em lista aberta com transferência de votos dentro da lista, todo voto nominal soma para a legenda. Um incentivo baseado em votos pode favorecer a **dispersão** (muitos candidatos trazendo votos para a lista), e não a concentração em poucos credenciados.

O texto não trata essa tensão. Ela é importante porque a hipótese (l. 187) prevê concentração em credenciados, e a própria seção de Financiamento fornece uma razão para esperar o contrário, pelo menos em parte. O argumento precisa dizer qual incentivo domina e por quê: cadeiras como condição da cláusula de desempenho? Ganho marginal decrescente de votos para candidatos sem chance? Também precisa dizer o que isso implica para listas de partidos pequenos, que precisam de votos para superar a cláusula, em comparação com partidos grandes. Isso se liga ao "tipo de partido" do Cap. 3.

### 3.3 O mecanismo não descarta explicações rivais

> l.  175: "demonstrar que uma distribuição de recursos é seletiva não basta para estabelecer que ela foi produzida para atender a este objetivo."

A ressalva é correta, mas fica abstrata: não diz **quais** outros objetivos produziriam o mesmo padrão. Candidatas óbvias:

-   **Poder interno / autofavorecimento.** Incumbentes e ex-eleitos costumam controlar os diretórios que decidem a alocação. Credenciais prévias podem prever recursos porque quem decide se beneficia, sem relação com maximizar cadeiras. O *resource gatekeeping* de @janusz_barreiro_cintron_2021 (l. 185) é compatível com as duas leituras.
-   **Poder de barganha e risco de saída.** Candidatos com votos próprios podem ameaçar trocar de partido. Financiá-los pode ser uma forma de retê-los, não de coordenar a lista.
-   **Custo de campanha.** Incumbentes podem ter custos maiores (mais bases, mais municípios). Nesse caso, a alocação reflete necessidade e não prioridade.

O texto não precisa refutar cada uma no Cap. 2, mas deveria nomeá-las no vocabulário da própria seção, sem antecipar as medidas dos capítulos empíricos. Opcionalmente, pode indicar onde as previsões divergem em termos substantivos (ex.: o autofavorecimento de quem ocupa mandato ou direção não prevê prioridade para quem teve votação expressiva e perdeu; a busca de desempenho coletivo prevê). Dizer qual teste (Top-NECr, regressão intralista, *timing*) distingue qual rival cabe à discussão/limitações dos Caps. 3 e 4. Se nenhum distinguir, a conclusão deve admitir isso. (Revisto em 18/09/2026: a versão anterior pedia essa discussão de testes já no Cap. 2.) Isso também dá conteúdo à frase das l. 175, que hoje é genérica ("padrões que se adequam às expectativas de uma leitura direcionada pelo argumento teórico citado").

### 3.4 A definição de "priorização" é fraca demais para a medida

> l.  181: "Nesta tese, a priorização financeira é definida como a destinação de parcelas maiores dos recursos partidários a um subconjunto de candidaturas de uma mesma nominata."

Quase qualquer distribuição desigual atende a essa definição. Ela não diz qual subconjunto nem quão maior. A medida do Cap. 3 é bem mais específica: um núcleo de tamanho ≈ NECr, arredondado (`k = floor(NECr + 0,5)`). O argumento deveria indicar **por que o tamanho do núcleo é dado pelo número efetivo**, formulado em termos teóricos (quantas candidaturas o partido de fato financia com peso relevante), sem antecipar NECr ou `k`, que ficam para o Cap. 3. O elo natural é @cheibubsin2020 (l. 185: competição organizada em torno de um número de competitivos menor que o total). Esse elo aparece como "aproximação de duas contribuições", mas não é usado para justificar o *tamanho* do núcleo.

### 3.5 @thomsen2023 fica solta

As l. 145–149 apresentam a perspectiva de Thomsen: ver a competição pela distribuição de recursos, e não de votos. Essa é, na prática, a justificativa conceitual do **NECr**, que aplica o número efetivo de @laaksotaagepera1979 ao dinheiro. O Argumento não volta a citar Thomsen, e Financiamento não diz que essa perspectiva vira uma medida. Hoje a autora serve de apoio geral ("o interesse central… decorre, portanto…", l. 149). Poderia ser a ponte explícita para a mensuração.

### 3.6 A frente iii (*timing*) não tem justificativa teórica

> l.  191: "iii) a identificação de uma priorização temporal ao núcleo de priorizados da lista."

Nada no Argumento explica por que o **momento** do repasse importaria. Não se fala em custo de oportunidade do tempo de campanha, em dinheiro cedo como sinal para eleitores e doadores, ou em restrição de fluxo de caixa. O Cap. 4 fica sem hipótese derivada no Cap. 2. Basta uma passagem que diga qual padrão temporal o argumento prevê.

### 3.7 Linguagem causal vs. ressalva observacional

-   

    l.  175 diz que os testes são observacionais e só "permitem constatar padrões".

-   

    l.  191 anuncia "a análise desagregada por cargos do **impacto** das credenciais eleitorais sobre a parcela intralista".

-   

    l.  187 usa "porque" em sentido causal ("priorizam \[…\] porque estas são sinais…").

"Impacto" contradiz a ressalva. A regressão intralista estima associações condicionais à lista (razões de parcelas). "Associação" ou "prêmio", o termo do Cap. 3 (`sec-premio-credenciais`), é mais coerente.

### 3.8 A medida é mais ampla que o texto

O Argumento (l. 179) fala só do FEFC. A variável da tese (`vr_receita_recursos_partidos`) inclui **todas** as receitas com origem "Recursos de partido político", inclusive o Fundo Partidário. Na base:

| Ano  | Recursos de partido | FEFC           | FP           | FP / total partidário |
|------|---------------------|----------------|--------------|-----------------------|
| 2018 | R\$ 1.005,3 mi      | R\$ 809,4 mi   | R\$ 183,7 mi | **18,3%**             |
| 2022 | R\$ 2.847,3 mi      | R\$ 2.583,9 mi | R\$ 207,5 mi | 7,3%                  |

(Recomputado em 18/09/2026 com `groupby('ano_eleicao').sum()` em `rrd_df_novo.parquet`.)

Em 2018, quase 1/5 dos recursos partidários vem do Fundo Partidário. Convém dizer no argumento, ou em nota, que "recursos controlados pelo partido" inclui o FP. Isso reforça o argumento: os dois fundos são discricionários do partido e dependem do resultado na Câmara.

### 3.9 Quem decide a alocação?

A unidade de análise é a lista partido × UF. O argumento fala "do partido" como ator unitário. O FEFC é recebido pelo diretório **nacional**, que distribui aos estaduais e aos candidatos segundo critérios aprovados pela executiva nacional. Se a coordenação é nacional, ela aparece nas listas estaduais? Se a decisão é estadual, os incentivos de sobrevivência (nacionais) chegam até lá? Uma frase sobre o nível decisório evita a objeção na banca. Isso também se liga à literatura de partidos como organizações heterogêneas (l. 75–105, @ribeiro2013_organizacao sobre centralização).

### 3.10 As cotas trabalham contra a hipótese

A l. 179 diz que as cotas "não fixam uma parcela igual", o que deixa espaço para priorizar. Falta o outro lado: as cotas **obrigam** a destinar ≥ 30% a mulheres (e, em 2022, uma proporção a candidaturas negras). Esses grupos têm, em média, menos credenciais prévias. As cotas empurram recursos para fora do grupo credenciado e, portanto, **tornam o teste mais conservador**. Dizer isso transforma a ressalva em argumento a favor da robustez do achado. A menção a Janusz et al. sobre mulheres (l. 185, "embora essa experiência não explique as desvantagens…") hoje está deslocada: não fica claro que papel ela cumpre no argumento.

### 3.11 A relação com @silvacervi2017 e @cheibubsin2020 (l. 189) precisa de página

> "Em @silvacervi2017, os grupos comparados são definidos pelo desempenho na eleição cujo financiamento é analisado. A classificação de competitividade de @cheibubsin2020 também incorpora resultados da eleição sob análise."

As duas afirmações sustentam a originalidade *ex ante* da tese. Merecem a página ou a tabela exata da fonte, porque a banca vai testar exatamente isso. No código, a versão *ex post* de Cheibub & Sin é `candidato_forte_cs`, que não é usada. Isso está coerente com a afirmação.

------------------------------------------------------------------------

## 4. Sugestões de estrutura

### Financiamento (l. 129–166): ordem proposta

> **Aplicada em 18/09/2026**, a pedido do autor. A ordem dos parágrafos foi mudada no `.qmd` sem reescrever nenhuma frase. Os pontos de costura e as correções de conteúdo ficaram em comentários HTML numerados \[1\]–\[5\] na própria seção. Só houve dois cortes: o marcador "**Mas isso não é novidade...**" e a divisão do antigo parágrafo "O interesse central…" em duas partes (a 1ª frase ficou com Thomsen; o resto foi para o bloco da ruptura). Thomsen ficou logo depois de Mancuso, e não no fim (ver \[2\]). As linhas citadas nas seções 2–3 desta nota se referem à versão **anterior** à reestruturação.

A ordem atual é: vertentes (Mancuso) → distinção pela origem do dinheiro → FEFC → "não é novidade" → modelo anterior → Silva & Cervi, Janusz → Thomsen → volta ao contexto institucional → regras do FEFC → Fundo Partidário → sobrevivência.

A seção vai e volta: o contexto institucional aparece nas l. 135–137, some e reaparece nas l. 149–151. Uma ordem linear seria:

1.  As vertentes de Mancuso e o lugar da tese na terceira (l. 131–133).
2.  **O regime anterior:** doações empresariais e intermediação partidária (l. 139–143). Mostra que o papel dos partidos já existia, mas com autonomia limitada.
3.  **A ruptura:** ADI 4650, FEFC, cotas (l. 135–137 + 149–151, fundidas e sem repetição).
4.  **Regras de repasse aos partidos e incentivo de sobrevivência:** FEFC, FP, cláusula de desempenho (l. 153–166).
5.  Thomsen pode ir para o fim desta seção, como passagem para a medida, ou para o Argumento (ver 3.5).

### Argumento (l. 168–193): esqueleto lógico que falta explicitar

> **Comentários inseridos em 18/09/2026**, a pedido do autor. A seção 3 desta nota virou comentários HTML \[A0\]–\[A10\], um depois de cada parágrafo do Argumento no `.qmd`. \[A0\], logo abaixo do título, traz o roteiro geral. O texto da seção não foi alterado. Os comentários já consideram o que o autor mudou em Financiamento e no Argumento no mesmo dia: "associação" no lugar de "impacto", fontes das cotas e anúncio da medida de Thomsen.

A seção deveria deixar visível, em qualquer redação, esta cadeia:

**incentivo** (sobrevivência depende de votos e cadeiras na Câmara) → **restrição informacional** (o partido aloca antes de conhecer os votos) → **sinal** (credenciais prévias) → **estratégia** (concentrar recursos num núcleo de tamanho ≈ número efetivo de competitivos) → **implicações observáveis** (i) composição do núcleo; ii) prêmio intralista por credencial; iii) antecipação temporal) → **rivais** (o que mais geraria i–iii e o que os testes conseguem ou não distinguir).

Hoje os elos "restrição informacional" e "sinal" estão presentes (l. 187). "Incentivo" está na seção anterior e não é retomado. "Tamanho do núcleo" e "rivais" estão ausentes. A implicação iii está sem justificativa.

### Redundâncias a cortar

| Onde aparece primeiro | Onde se repete | Sugestão |
|------------------------|------------------------|------------------------|
| l\. 141: Silva & Cervi, 89,6% empresarial | l\. 177: mesmo número e mesma ressalva sobre candidaturas indicadas pelos doadores | Manter em um só lugar. No Argumento, basta remeter. |
| l\. 143: Janusz et al., seletividade, incumbentes, mulheres | l\. 185: *resource gatekeeping*, experiência, mulheres | Idem. Em Financiamento, o achado. No Argumento, só o conceito que é usado. |
| l\. 135: FEFC como distinção do objeto | l\. 149: "o objeto da tese se distingue \[…\] em razão do contexto institucional" | Fundir. |
| l\. 173–175: primeira e segunda gerações | seção 2.1 inteira (l. 5–71) | No Argumento, uma frase de retomada basta. |

------------------------------------------------------------------------

## 5. Revisão de estilo

Os padrões abaixo aparecem com frequência nas duas seções, sobretudo no Argumento, que o comentário da l. 169 marca como melhorado por IA. São os mesmos padrões descritos em [02-literatura-revisao-de-estilo-e-autoria.md](02-literatura-revisao-de-estilo-e-autoria.md).

**a) Frase-síntese ou anúncio que repete o parágrafo.** - l. 149: "O interesse central desta tese pelo financiamento eleitoral decorre, portanto, do papel…" - l. 147: "Em síntese, a autora mostra que…" repete a frase anterior do mesmo parágrafo. - l. 187: "Em resumo, o argumento desta tese é que…" A frase é necessária (é a tese!), mas chega depois de "Essa expectativa aproxima duas contribuições…" (l. 185), que por sua vez vem depois de "Interessa verificar…" (l. 183). Há três aberturas para a mesma ideia. A formulação central deveria aparecer uma vez, cedo.

**b) Contraste "não X, mas Y" / "Ainda assim… não basta".** - l. 175, 177 ("Essa intermediação, porém, não assegurava…"), 179 ("mas não fixam…"), 181 ("Constatar essa desigualdade, entretanto, ainda deixa em aberto…"), 189 ("mas não isolam…"). Cinco ressalvas adversativas em sete parágrafos criam um ritmo previsível. Algumas podem virar afirmação direta.

**c) Pronomes demonstrativos em cadeia no início das frases.** - "Essa capacidade…" (l. 175), "Essa interpretação…", "Essa intermediação…" (l. 177), "Essa prerrogativa…" (l. 179), "Essas regras…", "Essa expectativa…" (l. 185), "Essa separação…" (l. 191). Quase toda frase do Argumento começa retomando a anterior com "Essa/Esse". Isso dá coesão mecânica e soa artificial. Variar a estrutura ou retomar pelo substantivo.

**d) Período longo com condicional encaixada.** - l. 187: "Se a distribuição partidária busca favorecer candidaturas capazes de contribuir para o desempenho coletivo da legenda, com as credenciais sendo um sinal observável mais direto dessa capacidade antes de termos o resultado eleitoral em mãos, espera-se encontrar…" Numa frase só: condicional, gerúndio ("com as credenciais sendo"), primeira pessoa do plural ("termos") e coloquialismo ("em mãos"). É a frase mais importante do capítulo e deveria ser a mais limpa.

**e) Oscilação de registro.** - Coloquial: "Mas isso não é novidade..." (l. 137), "a ideia desta tese é verificar" (l. 127), "o que dirá de" (l. 119), "em mãos" (l. 187). - Formal e abstrato: "a organização procura orientar a competição entre seus candidatos para objetivos eleitorais coletivos" (l. 175). - A voz do autor está nas passagens de Financiamento sobre as regras (l. 153–166): diretas, com números e com uma afirmação própria ("argumenta-se que…"). É esse o registro a manter no Argumento.

**f) Frase autorreferente vazia.** - l. 175: "Os dados e testes observacionais utilizados permitem constatar padrões que se adequam às expectativas de uma leitura direcionada pelo argumento teórico citado." A frase não diz quais padrões nem quais expectativas. Ou ela ganha conteúdo (ver 3.3), ou sai.

**g) Terminologia instável.** - "Nominata" / "lista" / "lista partidária" alternam sem critério. O CLAUDE.md usa "lista / nominata" como sinônimos, mas convém fixar um termo principal. - "Credenciais eleitorais prévias" (l. 183, 187), "atributos eleitorais observáveis" (l. 191), "sinais eleitorais anteriores" (l. 189), "competitivo" (Cap. 3). Definir "credencial" uma vez e dizer que ela corresponde a `candidato_competitivo`. - "Núcleo priorizado" (l. 191) vs. "núcleo de priorizados" (l. 191, mesma frase). - "Recursos partidários" / "recursos do FEFC" / "dinheiro de campanha controlado por eles" (l. 127). Ver 3.8.

**h) Minúcias.** - "capítulo 3" → "@sec-…" ou "Capítulo 3" com maiúscula, conforme o padrão do livro Quarto (l. 193). - Listas "i) … ii) … iii)" dentro do parágrafo (l. 191): o padrão ABNT mais comum é "(i)", "(ii)", "(iii)". - l. 155–158: a lista em bloco de citação (`>`) formata as regras como citação literal da lei. Se não for transcrição literal, usar uma lista comum ou uma tabela com a fonte (art. 16-D da Lei 9.504/97).

------------------------------------------------------------------------

## 6. Checklist de prioridade

**Antes de qualquer outra coisa** - \[ \] l. 137: remover o marcador "**Mas isso não é novidade...**". - \[ \] l. 181–183: consertar a frase quebrada ("Nestes termos,"). - \[ \] l. 160: corrigir a aritmética (833 mi, não 900 mi) e a descrição dos 15% (bancada, não eleição de 2018). - \[ \] l. 137: corrigir a origem normativa das cotas e "negras e pardas". - \[ \] l. 169: decidir como reescrever o Argumento sem texto de IA (compromisso de autoria).

**Argumento (substância)** - \[ \] Retomar o incentivo de sobrevivência (3.1) e tratar a tensão entre votos e cadeiras (3.2). - \[ \] Nomear as explicações rivais e dizer o que os testes distinguem (3.3). - \[ \] Justificar o tamanho do núcleo ≈ NECr com Cheibub & Sin e Thomsen (3.4, 3.5). - \[ \] Derivar a expectativa de *timing* (3.6). - \[ \] Trocar "impacto" por "associação"/"prêmio" (3.7). - \[ \] Dizer que "recursos partidários" inclui o FP (3.8). - \[ \] Uma frase sobre o nível decisório (3.9) e sobre as cotas como viés conservador (3.10). - \[ \] Páginas para as afirmações sobre Silva & Cervi e Cheibub & Sin (3.11).

**Financiamento (estrutura e fontes)** - \[ \] Reordenar conforme a seção 4 e eliminar a repetição do contexto institucional. - \[ \] Citações para as afirmações da l. 133 e da l. 151. - \[ \] Incluir a cláusula de desempenho (EC 97/2017) no argumento da sobrevivência.

**Estilo** - \[ \] Reduzir as cadeias de "Essa/Esse" e as ressalvas adversativas (5b, 5c). - \[ \] Simplificar a frase central da l. 187 (5d). - \[ \] Fixar a terminologia: lista/nominata, credencial, núcleo (5g).