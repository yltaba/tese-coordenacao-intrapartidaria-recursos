# literature-reviewer — Capítulo 2 — run-003

## Escopo e método
- Arquivos lidos: `CLAUDE.md`, `thesis-review/PROTOCOL.md`, `thesis-review/rubric.yaml`, `thesis-review/templates/agent_report.md`, `thesis-review/runs/run-003/manifest.yaml`, `tese/02-literatura.qmd` (219 linhas, inteiro), `tese/references.bib` (inteiro, 73 entradas).
- Recomputações executadas: `evidence/lit_cruzamento_citacoes.sh` (extrai as chaves `@...` do capítulo, exclui `@sec-*`, cruza com as chaves do `.bib`, lista duplicatas no `.bib` e entradas do `.bib` que o capítulo não cita). Saída em `evidence/lit_cruzamento_citacoes.out`. Também chequei com `grep` quais entradas do `.bib` sem uso no Cap. 2 aparecem em outros capítulos.
- Resultado do cruzamento: 51 chaves distintas citadas; **todas existem** no `.bib`; 1 chave duplicada no `.bib` (`jonesmainwaring2003`, linhas 83 e 131); 21 entradas do `.bib` não citadas no Cap. 2, das quais 11 não aparecem em nenhum capítulo (`bolognesietal2020`, `horochovski2024`, `schaefer2024`, `fischmesquita2022`, `locatelli2022`, `crisp2007`, `zolnerkevic2025`, `tse2018financiamentofeminino`, `tse2022criteriosfefc`, `jacobson1978`, `guarnierisilva2025`).
- Citações dentro de comentários HTML (L79, L192, L198) não são renderizadas; foram registradas mas não avaliadas como citações do texto.
- Não foi possível verificar: conteúdo literal de páginas citadas (`p. 434`, `p. 100`, `p. 1`, `p. 85`, `p. 79`, `p.2`), números atribuídos a @marsh1985 (1% Áustria, 60% Suíça) e a @silvacervi2017 (R$ 428 milhões, 89,6%, 7,5%), e detalhes de desenho de @hottmenezes2023, @janusz_barreiro_cintron_2021, @fivaetal2024 e @kselman2011. Não tenho acesso aos PDFs; onde não tenho confiança, a tabela marca `unverifiable`.

### Tabela de citações

| chave | linha(s) | afirmação atribuída | no bib | avaliação |
|---|---|---|---|---|
| mershon2020 | 7, 41 | enquadra "duas gerações" de estudos sobre voto preferencial; "não há fronteira rígida" | sim | parcial: o artigo desafia a "sabedoria convencional" sobre RP preferencial (título); o vocabulário de "gerações" e a frase sobre fronteira: unverifiable |
| rae1971 | 13 | leis eleitorais traduzem votos e distribuem autoridade *entre* partidos | sim | consistente |
| katz1986 | 13, 15 | Rae supõe partidos coesos; candidatos podem valorizar sucesso próprio acima do partido; bases próprias, débitos e lealdades | sim | consistente (confiança média) |
| careyshugart1995 | 17–37 | 4 variáveis (ballot, pool, vote, magnitude), 3 níveis; efeito da magnitude se inverte entre lista fechada e aberta; "escândalos extraordinários de corrupção" (p. 434) | sim | variáveis e efeito da magnitude: consistente; p. 434 dentro de 417–439; citação literal: unverifiable; aplicação ao pooling brasileiro: ver LIT-2-003 |
| ames2001 | 27, 39 | clientelismo/bases localizadas; instabilidade pós-1988 | sim | consistente em linhas gerais (média) |
| chang2005 | 29 | lista aberta incentiva corrupção | sim | consistente |
| figueiredo_limongi_2002_incentivos | 33 | voto nominal soma para as cadeiras do partido | sim | consistente (média) |
| mainwaring1999 | 39, 127 | competição intrapartidária pode ser mais intensa que a interpartidária | sim | consistente (média) |
| ames1995 | 39 | partidos como agregados de individualistas que distribuem *pork* | sim | parcial: o artigo trata de estratégias espaciais de voto dos candidatos; é usado só para *pork* (ver LIT-2-013) |
| ferree2014 | 45 | "o que une a segunda geração" é o contexto moldar os efeitos das regras | sim | uso deslocado: a revisão trata de sistemas partidários, não de voto preferencial (LIT-2-006) |
| marsh1985 | 47 | variação no uso do voto preferencial; Áustria 1%, Suíça 60%; "agentes de mobilização" | sim | variação: consistente; números e conceito: unverifiable |
| samuels1999 | 49 | partidos/candidatos podem cultivar voto partidário sob lista aberta; recursos e coligações condicionam | sim | consistente |
| figueiredolimongi1999 | 51 | deputados votam com as lideranças | sim | consistente |
| desposato_2006_impact | 51 | partidos igualmente coesos na Câmara e no Senado | sim | dúvida sobre o achado reportado (LIT-2-005), confiança baixa |
| avelino_barone2012 | 55 | RDD em eleições apertadas; *coattail* reverso prefeito → deputado federal | sim | consistente (média); chave omite o coautor Biderman (sem efeito na renderização) |
| hagopian_gervasoni_moraes_2009_patronage | 57 | reformas de mercado reduzem patronagem e produzem legisladores orientados ao partido | sim | consistente |
| schmitt_carneiro_kuschnir_1999_estrategias | 57 | distribuição do HGPE entre candidaturas indica controle partidário | sim | consistente (média) |
| braga_amaral_2013_implicacoes | 57 | partidos não preenchiam o máximo das nominatas → controle | sim | dado: unverifiable; inferência frágil (LIT-2-014) |
| kselman2011 | 59 | lista aberta disciplina contra corrupção; menos corrupção que majoritário | sim | unverifiable no detalhe; posição da citação no argumento: LIT-2-014 |
| hottmenezes2023 | 61 | descontinuidade no tamanho da lista; vagas extras vão a candidatos fracos/novatos | sim | unverifiable no detalhe (média) |
| hazan_rahat_2010 | 61 | seleção de candidatos como arena de poder organizacional | sim | consistente |
| cheibubsin2020 | 63, 202, 212 | nº de candidaturas competitivas próximo ao nº de cadeiras; critério de competitividade usa a eleição corrente (p. 79) | sim | consistente (a natureza ex-post bate com `candidato_forte_cs` no CLAUDE.md); p. 79 dentro de 70–95 |
| avelinobidermansilva2011 | 63 | partidos reduzem sobreposição regional entre copartidários viáveis | sim | parcial: artigo de medidas de concentração (título) (LIT-2-013) |
| silotto2019 | 63 | estratégia regional na composição de listas (SP) | sim | consistente |
| cheibub_junqueira_moreira_2024 | 63 | *geographic sorting* em OLPR | sim | consistente com o título; working paper sem URL |
| janusz_barreiro_cintron_2021 | 65, 151, 202, 212 | *resource gatekeeping*; número de urna, TV e dinheiro; favorece incumbentes; mulheres subfinanciadas; orientação ex-ante | sim | gênero/incumbência: consistente (média); lista de instrumentos e rótulo: unverifiable (LIT-2-016) |
| andreetal2015 | 67 | voto preferencial usado como sinal para posição na lista seguinte | sim | consistente; uso inferencial problemático (LIT-2-004); chave 2015 × ano 2017 |
| crispetal2013 | 67 | Eslováquia; recompensa por posição de lista | sim | caso: consistente; inferência: LIT-2-004 |
| aldrich2011 | 75 | partidos resolvem problemas de ação coletiva | sim | consistente |
| cox_mccubbins_2005_setting | 77 | delegação a lideranças via "controle de recursos escassos" | sim | parcial: o recurso escasso da obra é a agenda do plenário (LIT-2-015) |
| scarrowwebb2017 | 81–87 | citação p. 1; estruturas, recursos, estratégias de representação | sim | consistente (as três dimensões estão no título); citação literal: unverifiable |
| fivaetal2024 | 89, 93, 176 | dilema do gatekeeper; menor esforço agregado (p. 100); partidos competitivos lidam melhor com o *trade-off* | sim | dilema: consistente; p. 100 e previsão sobre partidos competitivos: LIT-2-007 |
| silvacodato2024 | 95, 157, 196 | desigualdade persiste sob financiamento público; FEFC dá centralidade aos partidos | sim | consistente com o título (média) |
| guarnieri2011 | 97, 180 | comissões provisórias como centralização | sim | consistente |
| tavits2012 | 97, 101 | *inactive branches* pós-comunistas; *resource-based view* | sim | unverifiable; analogia forçada (LIT-2-012); chave 2012 × ano 2013 |
| ribeiro2013_organizacao | 99, 180 | inclusividade e centralização nos estatutos | sim | consistente |
| ribeiroetal2022 | 101 | partidos não homogêneos; citação p. 2; RBV | sim | tese geral: consistente; citação e RBV: unverifiable; "(p.2)" fora da sintaxe |
| webbkeith2017 | 101 | RBV aplicada a partidos | sim | parcial/unverifiable |
| cox_thies_1998_cost | 109–119 | diferenciação por posição × dinheiro; SNTV japonês; gastos sobem com competição | sim | consistente |
| samuels_2001_every_penny | 119–127 | nº de adversários não afeta gasto; qualidade dos colegas afeta; citação p. 100 | sim | consistente (média); p. 100 dentro de 89–102 |
| cox1997 | 121 | informação piora com a magnitude | sim | consistente |
| mancuso_2015_investimento | 133, 135, 153 | três vertentes da literatura | sim | consistente (média) |
| lemosmarcelinopederiva2010 | 135 | incumbentes recebem mais | sim | consistente (média) |
| marcelino2010 | 135 | idem | sim | consistente (média) |
| mancuso2012 | 135 | incumbentes; direita recebe mais | sim | consistente (média) |
| silvacervi2017 | 135, 145, 212 | base governista; partidos como principal origem em 2014; 89,6% PJ, 7,5% FP; grupos definidos ex-post (p. 85) | sim | números e "base governista": unverifiable; p. 85 dentro de 75–110 |
| samuels2001a | 135 | direita recebe mais | sim | consistente (média) |
| speck2011 | 135 | idem | sim | unverifiable; tipo de entrada inadequado |
| sacchetspeck2011 | 135 | mulheres subfinanciadas | sim | consistente |
| peixoto2010 | 135 | custo × magnitude, PIB, urbanização, desigualdade | sim | unverifiable |
| thomsen2023 | 137–139 | competição via dinheiro; recursos mais concentrados que votos; primárias; medida de concentração | sim | consistente (média) |

## Avaliação macro

A literatura sustenta de forma razoável os dois primeiros elos do capítulo: (a) o cânone do voto pessoal (Katz, Carey & Shugart, Ames, Mainwaring) e (b) a revisão que devolve agência aos partidos (Samuels 1999, Figueiredo & Limongi, Cheibub & Sin, Janusz et al., Fiva et al.). O uso é em geral justo: o capítulo apresenta Chang contra Kselman e Cox & Thies contra Samuels 2001 sem esconder resultados desfavoráveis.

O problema está no último elo. A hipótese central (L204: partidos priorizam candidaturas com **credenciais prévias** porque elas **sinalizam** capacidade de contribuir para o resultado coletivo) não se apoia em nenhuma literatura sobre *como organizações partidárias alocam recursos entre candidatos* nem sobre *atributos de candidatos como sinais*. Existem duas tradições diretamente aplicáveis que ficam de fora: a literatura sobre alocação partidária de dinheiro e de "bons candidatos" em posições marginais (EUA e RP de lista), que é justamente a rival "credenciados × marginais" que o próprio comentário [A7] identifica; e a literatura sobre *personal vote-earning attributes*. Há também um precedente brasileiro que está no `.bib` e não é citado: Bolognesi et al. (2020), sobre como os partidos distribuíram dinheiro em 2014 segundo sua estrutura organizacional.

Na seção de Financiamento, afirmações institucionais e empíricas (regras do FEFC/FP, cotas, peso das doações empresariais) aparecem sem fonte, embora o `.bib` já tenha entradas para isso (TSE 2018/2022, Fisch & Mesquita 2022, Schaefer 2025, Horochovski et al. 2024). Há ainda quatro usos pontuais que esticam o que a obra citada sustenta: a classificação de pooling de Carey & Shugart, a inferência a partir de André et al. e Crisp et al., Ferree et al. como definição da segunda geração, e possivelmente Desposato (2006). Nenhum desses usos invalida a cadeia do capítulo. Juntos, deixam a passagem da literatura para a hipótese mais fraca do que precisa ser.

## Achados

```yaml
id: LIT-2-001
titulo: "Precedente brasileiro direto sobre distribuição partidária de dinheiro (Bolognesi et al. 2020) está no .bib e não é citado"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 145
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "Alguns estudos estudaram estes recursos empresariais que são intermediados pelas legendas."
afirmacao_do_autor: "Os estudos sobre recursos intermediados pelos partidos são representados por Silva & Cervi (2017) e Janusz et al. (2021)."
problema: "`bolognesietal2020` ('Como os partidos distribuem o dinheiro. Estrutura organizacional e recursos eleitorais em 2014 no Brasil', Colombia International 104) trata exatamente do objeto da tese (distribuição partidária de recursos entre candidaturas) e o liga à estrutura organizacional, que é o tema da seção 'Partidos como organizações heterogêneas'. A obra está no .bib e não é citada em nenhum capítulo. Um examinador da área a esperaria nos dois pontos. O mesmo vale, em escala menor, para `horochovski2024` (efeitos da proibição de doações empresariais), que sustentaria a afirmação sem fonte da L147 sobre o fim do confundimento em 2018/2022."
evidencia:
  tipo: ausencia
  fontes: ["tese/references.bib:43-49", "tese/references.bib:19-25", "thesis-review/runs/run-003/evidence/lit_cruzamento_citacoes.out"]
  detalhe: "O cruzamento mostra bolognesietal2020 e horochovski2024 no .bib sem citação no Cap. 2; grep em tese/*.qmd não encontra nenhuma das duas em outro capítulo. Descrevo o conteúdo pelo título e pelo periódico; não li o texto."
severidade: MAJOR
confianca: alta
recomendacao: "Citar Bolognesi et al. (2020) em Financiamento (L145-151), ao lado de Silva & Cervi e Janusz et al., e relacioná-lo à seção de organização (L97-101): se a estrutura organizacional explica a distribuição, isso é uma hipótese auxiliar ou uma rival. Usar Horochovski et al. (2024) como fonte da L147."
claims: [C2.6.03]
```

```yaml
id: LIT-2-002
titulo: "A hipótese sobre credenciais como sinal não dialoga com a literatura sobre alocação partidária de recursos nem sobre atributos de candidatos"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 204
  secao: "## Argumento"
  trecho: "O argumento desta tese é que os partidos priorizam financeiramente candidaturas com credenciais eleitorais prévias porque estas constituem sinais da capacidade destes candidatos em contribuir para o desempenho coletivo da legenda."
afirmacao_do_autor: "Credenciais prévias são sinais que levam o partido a priorizar esses candidatos."
problema: "A frase central do capítulo não tem nenhuma citação que sustente o mecanismo (credencial como sinal; priorizar credenciados em vez de marginais). Três linhas da literatura, ausentes tanto do capítulo quanto do .bib, tratam disso diretamente: (1) alocação de recursos controlados pelo partido entre candidatos. Nos EUA, o padrão é priorizar disputas marginais (p.ex. Jacobson 1985, Political Science Quarterly, sobre a distribuição de recursos partidários em 1982; Damore & Hansford 1999, sobre recursos controlados pelos partidos nas eleições para a Câmara; confiança média nos detalhes bibliográficos). Em RP de lista: Galasso & Nannicini (2011, APSR, 'Competing on good politicians'; 2015, 'So closed: political selection in proportional systems') e Buisseret, Folke, Prato & Rickne (2022, AJPS, estratégias de nomeação em RP de lista). É a rival 'credenciados × marginais' que o próprio comentário [A7] (L208) aponta como buraco. (2) Atributos de candidatos como sinais: Shugart, Valdini & Suominen (2005, AJPS, 'Looking for locals') definem *personal vote-earning attributes*, conceito muito próximo de 'credencial'. (3) Qualidade de candidatura: Jacobson & Kernell (1981, Strategy and Choice in Congressional Elections), base do uso de cargo prévio como proxy, que o capítulo adota via Janusz et al. sem citar a origem. Folke, Persson & Rickne (2016, APSR, 'The primary effect') também seriam interlocutores naturais de André et al. e Crisp et al."
evidencia:
  tipo: ausencia
  fontes: ["tese/02-literatura.qmd:204", "tese/02-literatura.qmd:206-210", "tese/references.bib"]
  detalhe: "Nenhuma dessas obras está no .bib (grep por Galasso, Buisseret, Shugart+Valdini, Jacobson+Kernell não encontra nada; jacobson1978 existe, mas trata do efeito do gasto, não da alocação). Tenho confiança alta na existência e no tema de Galasso & Nannicini 2011, Shugart/Valdini/Suominen 2005, Buisseret et al. 2022, Folke/Persson/Rickne 2016 e Jacobson & Kernell 1981; confiança média nos detalhes de Jacobson 1985 e Damore & Hansford 1999."
severidade: MAJOR
confianca: media
recomendacao: "No Argumento (L202-204), incluir um parágrafo que situe a hipótese entre duas expectativas da literatura: priorizar marginais (EUA; Galasso & Nannicini) ou priorizar credenciados/puxadores (lógica de pooling). Ancorar 'credencial como sinal' em Shugart, Valdini & Suominen (2005) e em Jacobson & Kernell (1981). A forma de redigir cabe ao autor."
claims: [C2.7.03]
```

```yaml
id: LIT-2-003
titulo: "A classificação do pooling brasileiro contradiz a codificação do próprio Carey & Shugart"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 33
  secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
  trecho: "A aplicação relativa ao *pooling* dos votos não pode ser realizada diretamente em algum dos três níveis determinados por @careyshugart1995."
afirmacao_do_autor: "O pooling brasileiro não se encaixa nos três níveis e ficaria entre o nível de menor incentivo e o intermediário."
problema: "Em Carey & Shugart, Pool=0 corresponde a votos agregados no nível do partido inteiro, que é o caso brasileiro: votos nominais somam para o quociente da legenda (e, até 2018, da coligação, o que é agregação ainda maior). Pelo que sei, os autores codificam a RP de lista aberta como ballot=1, pool=0, vote=2. A frase 'não pode ser realizada diretamente' e a posição 'entre' (L33) não têm base na obra citada. O comentário [2.1-4] (L35) aponta a indecisão, mas não o fato de que o próprio texto-fonte a resolve."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:21", "tese/02-literatura.qmd:33", "tese/references.bib:198-207"]
  detalhe: "A própria L21 do capítulo define o nível de menor incentivo como aquele em que o resultado depende 'da votação que toda a legenda recebe', e a L33 reconhece que no Brasil 'o voto depositado em cada candidatura individual beneficia o cálculo das cadeiras que um partido como um todo receberá'. Pela definição dada no próprio texto, isso é pool=0. A codificação ballot=1/pool=0/vote=2 para lista aberta vem da minha memória da tabela de Carey & Shugart; não conferi a página."
severidade: MODERATE
confianca: media
recomendacao: "Conferir a tabela de codificação de Carey & Shugart (1995) e classificar o Brasil como pool=0, ou justificar explicitamente por que o autor diverge dos autores."
claims: [C2.2.03]
```

```yaml
id: LIT-2-004
titulo: "André et al. e Crisp et al. não mostram gatekeeping depois da convenção: a recompensa ocorre na formação da lista seguinte"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 67
  secao: "### A segunda geração e a agência partidária"
  trecho: "Estas são evidências corroborativas, em eleições sob outro sistema eleitoral, de que o *gatekeeping* partidário não termina no momento da convenção."
afirmacao_do_autor: "A recompensa por votos preferenciais em listas flexíveis mostra que o gatekeeping continua depois da convenção."
problema: "Pelo que o próprio parágrafo descreve, o partido usa o desempenho preferencial para 'melhorar sua posição na lista da eleição seguinte'. O instrumento continua sendo a formação da lista, só que num ciclo posterior. Isso não é controle exercido *durante* a campanha, depois de a nominata estar fechada, que é o que a tese estuda com recursos financeiros e o que Janusz et al. (L65) sustentam. A conclusão da L67 atribui a essas obras uma implicação que elas não carregam."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:65", "tese/02-literatura.qmd:67", "tese/references.bib:676-696"]
  detalhe: "L67: 'usam o desempenho relativo de um candidato em votos preferenciais como sinal para melhorar sua posição na lista da eleição seguinte [@andreetal2015]'."
severidade: MODERATE
confianca: alta
recomendacao: "Usar André et al./Crisp et al. para sustentar outra coisa: partidos usam sinais de desempenho eleitoral passado para decidir quem priorizar. Isso é análogo às 'credenciais prévias' da L204 e fortaleceria o Argumento. Retirar a conclusão sobre gatekeeping pós-convenção, que já está bem sustentada por Janusz et al. na L65."
claims: [C2.3.07]
```

```yaml
id: LIT-2-005
titulo: "O achado de Desposato (2006) pode estar reportado de forma invertida"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 51
  secao: "### A segunda geração e a agência partidária"
  trecho: "Entretanto, as evidências mostram que partidos atuam de maneira coesa em ambos."
afirmacao_do_autor: "Desposato encontra coesão partidária igual na Câmara e no Senado, contra a expectativa derivada das regras eleitorais."
problema: "Minha lembrança do artigo (JOP 68(4)) é que ele encontra diferenças atribuíveis às regras eleitorais, com partidos no Senado mais unidos que na Câmara. Nesse caso, o artigo apoiaria em parte a primeira geração, e não a segunda. Não tenho certeza. Se a lembrança estiver certa, a obra está sendo usada contra o que ela sustenta."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:51", "tese/references.bib:440-449"]
  detalhe: "Sem acesso ao texto. Registro como suspeita a ser conferida pelo autor no resumo e nas conclusões do artigo."
severidade: MODERATE
confianca: baixa
recomendacao: "Reler o resumo e a conclusão de Desposato (2006). Se o resultado for de diferença entre as casas, reescrever a frase e deslocar a citação para um ponto que reconheça evidência mista."
claims: [C2.3.04]
```

```yaml
id: LIT-2-006
titulo: "Ferree, Powell & Scheiner (2014) usados como definição da 'segunda geração' dos estudos sobre voto preferencial"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 45
  secao: "### A segunda geração e a agência partidária"
  trecho: "O que une os estudos da segunda geração é o entendimento de que o contexto social, econômico e político moldam a eficácia dos incentivos esperados das regras eleitorais [@ferree2014]."
afirmacao_do_autor: "O traço comum da segunda geração é o condicionamento contextual dos efeitos das regras, segundo Ferree et al."
problema: "Ferree et al. (Annual Review, 'Context, Electoral Rules, and Party Systems') tratam de como o contexto condiciona o efeito das regras sobre sistemas partidários (número de partidos). A obra não revisa a literatura sobre voto preferencial nem a divisão em gerações de Mershon. A citação sustenta a ideia geral de condicionamento contextual, mas não a afirmação de que isso é 'o que une' a segunda geração. Em seguida, a L41 atribui a Mershon a afirmação de que 'não há uma fronteira rígida entre primeira e segunda gerações'. Não consigo confirmar que Mershon use o vocabulário de 'gerações'."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:41", "tese/02-literatura.qmd:45", "tese/references.bib:584-592", "tese/references.bib:285-296"]
  detalhe: "O título e o periódico de ferree2014 indicam que o objeto são sistemas partidários. O agrupamento 'primeira/segunda geração' só aparece no capítulo atribuído a mershon2020."
severidade: MODERATE
confianca: media
recomendacao: "Atribuir a caracterização da segunda geração a Mershon (2020), se ela a fizer, ou assumi-la como síntese do autor. Usar Ferree et al. como apoio geral ('efeitos de regras dependem do contexto'), e não como definição do grupo."
claims: [C2.1.01, C2.3.01]
```

```yaml
id: LIT-2-007
titulo: "Fiva et al. (2024): localizador 'p. 100' incompatível com a paginação do artigo e previsão sobre partidos competitivos sem página"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 89
  secao: "## Partidos como organizações heterogêneas"
  trecho: "esta atribuição pode reduzir o esforço agregado de campanha dos candidatos, conforme evidência apresentada [@fivaetal2024, p. 100]."
afirmacao_do_autor: "Fiva et al. mostram menor esforço agregado (p. 100) e teorizam que partidos mais competitivos lidam melhor com o trade-off (L93)."
problema: "O .bib registra o artigo como Journal of Public Economics 234, artigo 105133, com paginação por número de artigo. Uma 'p. 100' é implausível para um artigo desse tipo e coincide com o localizador de Samuels 2001 na L127, o que sugere erro de cópia. Não consigo verificar a previsão da L93, de que partidos eleitoralmente mais competitivos 'conseguem transitar melhor'. Ela precisa de localizador porque o comentário [2.2-3] (L83) propõe apoiar nela o corte por tipo de partido do Cap. 3."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:89", "tese/02-literatura.qmd:93", "tese/02-literatura.qmd:127", "tese/references.bib:188-196"]
  detalhe: "bib: 'pages = {105133}'. Há dois 'p. 100' no capítulo: fivaetal2024 (L89) e samuels_2001_every_penny (L127, dentro de 89-102)."
severidade: MODERATE
confianca: media
recomendacao: "Corrigir o localizador (seção, proposição ou página do PDF). Localizar a passagem exata da L93 e citá-la com página antes de derivar dela qualquer hipótese auxiliar."
claims: [C2.4.03, C2.4.04]
```

```yaml
id: LIT-2-008
titulo: "Afirmações institucionais e empíricas sobre FEFC, FP, cotas e doações empresariais sem fonte, embora o .bib tenha fontes para elas"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 155
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "Decisões posteriores (STF ADI 5617 e consulta ao TSE (2018) para mulheres; consulta ao TSE (2020) e ADPF 738 para candidaturas negras; EC 117/2022) limitaram tal autonomia"
afirmacao_do_autor: "Cotas de financiamento, regras de repartição do FEFC e do FP, cláusula de desempenho e o peso das doações empresariais."
problema: "L143 ('Doações empresariais e de grandes conglomerados constituíam parcela expressiva dos recursos'), L147 (fim do confundimento em 2018/2022), L153-155 (FEFC, ADI 5617, consultas ao TSE, ADPF 738, EC 117), L159-161 (critérios da Lei 13.488 e valores de 2022), L163 (95% do FP por votos desde 2007) e L165 (EC 97/2017) não citam nenhuma fonte. Diplomas legais podem ser referidos pelo número, mas os valores de 2022 e a afirmação sobre 'parcela expressiva' são empíricos. O .bib já tem entradas que o autor criou para isso e não usa: tse2018financiamentofeminino e tse2022criteriosfefc (urldate 2026-09-18), fischmesquita2022 (reformas eleitorais e de financiamento), schaefer2024 (reformas do financiamento) e horochovski2024. A L188 ('não fixam a parcela que deve ser transferida') também não tem fonte e, lida isoladamente, conflita com a L155, porque as cotas fixam pisos por grupo, não por candidato."
evidencia:
  tipo: ausencia
  fontes: ["tese/02-literatura.qmd:143", "tese/02-literatura.qmd:147", "tese/02-literatura.qmd:153-165", "tese/02-literatura.qmd:188", "tese/references.bib:708-723", "tese/references.bib:274-283", "tese/references.bib:486-494", "thesis-review/runs/run-003/evidence/lit_cruzamento_citacoes.out"]
  detalhe: "Nenhuma chave @ entre as L143 e L165, exceto silvacervi2017, janusz, mancuso_2015 e silvacodato2024, que sustentam outras frases."
severidade: MODERATE
confianca: alta
recomendacao: "Citar as fontes legais e as entradas já existentes no .bib: tse2018 para a cota feminina, tse2022 para os critérios do FEFC, Fisch & Mesquita (2022) ou Schaefer (2025) para a sequência de reformas, e Horochovski et al. (2024) para L143/L147. Dar fonte (TSE/portaria) aos valores de 2022 e precisar a L188 ('pisos por grupo, sem critério por candidatura')."
claims: [C2.6.04, C2.7.04]
```

```yaml
id: LIT-2-009
titulo: "Explicações rivais (captura por incumbentes, barganha, ameaça de saída) sem literatura"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 178
  secao: "## Argumento"
  trecho: "Esta seletividade pode refletir autofavorecimento, com captura de incumbentes sobre os diretórios que decidem a alocação, indicar simplesmente barganha, ou uma ameaça de sair do partido e levar votos consigo."
afirmacao_do_autor: "Seletividade pode ter explicações alternativas ao objetivo coletivo."
problema: "As três rivais aparecem sem nenhuma citação, e cada uma tem literatura brasileira conhecida. Migração partidária como ameaça: Desposato (2006, AJPS, 'Parties for Rent? Ambition, Ideology, and Party Switching in Brazil's Chamber of Deputies') e Melo (2004, 'Retirando as cadeiras do lugar'). Força dos incumbentes e vantagem de mandato: Pereira & Rennó (2001, 'O que é que o reeleito tem?'). Captura organizacional: Guarnieri (2011), já citado, e Bolognesi et al. (2020), no .bib. Sem essa ancoragem, as rivais parecem ad hoc e não se sabe qual delas a literatura considera mais plausível."
evidencia:
  tipo: ausencia
  fontes: ["tese/02-literatura.qmd:178", "tese/references.bib"]
  detalhe: "Nenhuma das obras sugeridas está no .bib, exceto guarnieri2011 e bolognesietal2020. Confiança alta na existência de Desposato 2006 (AJPS) e Pereira & Rennó 2001; média nos detalhes de Melo 2004."
severidade: MODERATE
confianca: media
recomendacao: "Ancorar cada rival em uma referência e dizer qual implicação observável a distinguiria da hipótese de coordenação (isso é trabalho do Argumento, não da literatura; aqui só se pede a fonte)."
claims: [C2.7.02]
```

```yaml
id: LIT-2-010
titulo: "Ausências canônicas no debate sobre voto pessoal e partidos no Brasil"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 41
  secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
  trecho: "Esta cadeia de causalidade que liga os incentivos ao voto pessoal ao enfraquecimento dos partidos enquanto organizações representa a literatura canônica sobre o tema"
afirmacao_do_autor: "O cânone da primeira geração é Katz, Carey & Shugart, Ames e Mainwaring; a resposta brasileira é Figueiredo & Limongi e Samuels."
problema: "Faltam, no capítulo e no .bib: (a) Cain, Ferejohn & Fiorina (1987, The Personal Vote), origem do conceito que dá nome à seção; (b) Samuels (2002, JOP, 'Pork Barreling Is Not Credit Claiming or Advertising: Campaign Finance and the Sources of the Personal Vote in Brazil'), que liga *pork* a financiamento de campanha, exatamente a ponte entre as seções 'cânone' e 'financiamento'; (c) Pereira & Mueller (2003, Dados, 'Partidos fracos na arena eleitoral e partidos fortes na arena legislativa'), a posição intermediária mais conhecida entre Ames/Mainwaring e Figueiredo & Limongi, que afirma justamente que os partidos são fracos na arena eleitoral estudada pela tese; (d) Nicolau (2006, Dados, 'O sistema eleitoral de lista aberta no Brasil'), referência padrão para a descrição institucional das L31-37. Sem (c), a narrativa 'primeira geração refutada' fica seletiva: a tese precisa mostrar que a força partidária também existe na arena eleitoral, e Pereira & Mueller é a objeção direta."
evidencia:
  tipo: ausencia
  fontes: ["tese/02-literatura.qmd:11-41", "tese/02-literatura.qmd:51-53", "tese/references.bib"]
  detalhe: "grep no .bib: nenhuma entrada de Cain, Pereira, Nicolau ou Samuels 2002. Confiança alta na existência e no tema das quatro obras."
severidade: MODERATE
confianca: alta
recomendacao: "Incluir ao menos Pereira & Mueller (2003), como contraponto explícito na L51-53, e Samuels (2002), como ponte para o financiamento. Cain et al. e Nicolau fecham lacunas de referência básica."
claims: [C2.2.01, C2.3.05]
```

```yaml
id: LIT-2-011
titulo: "Financiamento público e poder da organização partidária sem a literatura de partido-cartel e de organização"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 157
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "Com a criação do fundo público de financiamento, as organizações partidárias passaram a deter a prerrogativa formal de distribuir internamente a maior parte dos recursos de campanha."
afirmacao_do_autor: "Fundos públicos centralizam nos partidos a distribuição de recursos."
problema: "A relação entre subsídio estatal e fortalecimento das direções partidárias é o núcleo da tese do partido-cartel, de Katz & Mair (1995, Party Politics, 'Changing Models of Party Organization and Party Democracy: The Emergence of the Cartel Party'). O controle de recursos financeiros como 'zona de incerteza' que dá poder às lideranças está em Panebianco (1988, Political Parties: Organization and Power). As duas obras, ausentes do capítulo e do .bib, são expectativa básica para a seção 'Partidos como organizações heterogêneas' e para a L157. No caso brasileiro, há literatura sobre Fundo Partidário e organização (p.ex. Braga & Bourdoukan 2009, Perspectivas; confiança média no detalhe). locatelli2022, sobre organização de base dos partidos e sistema eleitoral, está no .bib e não é usado."
evidencia:
  tipo: ausencia
  fontes: ["tese/02-literatura.qmd:71-101", "tese/02-literatura.qmd:157", "tese/references.bib:666-675"]
  detalhe: "grep no .bib: nenhuma entrada de Katz & Mair, Panebianco ou Braga & Bourdoukan."
severidade: MODERATE
confianca: alta
recomendacao: "Citar Katz & Mair (1995) na L157 e Panebianco (1988) na seção de organização, ao lado de Scarrow & Webb, para conectar controle de recursos e poder das lideranças."
claims: [C2.6.05]
```

```yaml
id: LIT-2-012
titulo: "Tavits (2013): analogia entre 'inactive branches' pós-comunistas e comissões provisórias, e atribuição da resource-based view, sem base verificável"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 97
  secao: "## Partidos como organizações heterogêneas"
  trecho: "como aponta @tavits2012 em análise comparada das organizações partidárias surgidas em nações pós-soviéticas do funcionamento das *inactive branches* dos partidos."
afirmacao_do_autor: "Tavits mostra que ramos inativos funcionam como ferramentas de mobilização, o que valeria para as comissões provisórias brasileiras. Tavits e Webb & Keith amparam a resource-based view (L101)."
problema: "Não consigo confirmar que Tavits trate de *inactive branches* nem que se filie à *resource-based view*. A obra argumenta, em termos gerais, que a força organizacional (filiais, membros, staff) importa para o desempenho eleitoral. A transposição para as comissões provisórias, que segundo Guarnieri são instrumento de centralização, não de mobilização, é do autor e deveria ser apresentada como tal. A chave `tavits2012` corresponde a uma obra de 2013."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:97", "tese/02-literatura.qmd:101", "tese/references.bib:554-561"]
  detalhe: "bib: year = {2013} sob a chave tavits2012."
severidade: MINOR
confianca: baixa
recomendacao: "Conferir o termo e a página em Tavits (2013). Apresentar a analogia como hipótese do autor e indicar qual das obras (Ribeiro et al. 2022?) introduz a RBV."
claims: [C2.4.06]
```

```yaml
id: LIT-2-013
titulo: "Coordenação territorial: Avelino, Biderman & Silva (2011) é um artigo de medidas; Ames (1995), origem da tipologia espacial, é usado só para pork"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 63
  secao: "### A segunda geração e a agência partidária"
  trecho: "partidos reduzem a sobreposição regional entre copartidários viáveis, organizando a competição no espaço do distrito eleitoral [@avelinobidermansilva2011; @silotto2019; @cheibub_junqueira_moreira_2024]."
afirmacao_do_autor: "Os três trabalhos mostram que partidos reduzem a sobreposição territorial entre copartidários."
problema: "'A Concentração Eleitoral nas Eleições Paulistas: Medidas e Aplicações' propõe e aplica medidas de concentração. Atribuir-lhe a conclusão de que os *partidos* reduzem a sobreposição vai além do que o título indica, e não tenho confiança de que o artigo afirme isso. Ames (1995, AJPS), citado na L39 apenas para *pork*, é a origem da tipologia de padrões espaciais de votação (concentrado/disperso, dominante/compartilhado), que é a base dessa literatura. zolnerkevic2025 (localismo nas proporcionais) está no .bib e não é usado."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:39", "tese/02-literatura.qmd:63", "tese/references.bib:235-245", "tese/references.bib:474-484", "tese/references.bib:222-233"]
  detalhe: "Avaliação feita pelo título e pelo periódico; não li o texto."
severidade: MINOR
confianca: media
recomendacao: "Reservar avelinobidermansilva2011 para a medida e citar Ames (1995) como origem do argumento espacial. Considerar Zolnerkevic (2025)."
claims: [C2.3.06]
```

```yaml
id: LIT-2-014
titulo: "Inferências fracas a partir de Braga & Amaral (2013) e Kselman (2011) na seção sobre agência partidária"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 57
  secao: "### A segunda geração e a agência partidária"
  trecho: "Controle também observado por @braga_amaral_2013_implicacoes, ao verificar que partidos em geral não preenchiam a capacidade máxima de suas nominatas."
afirmacao_do_autor: "Listas incompletas indicam controle partidário. Kselman (L59) é evidência da segunda geração."
problema: "Listas abaixo do teto também são compatíveis com escassez de candidatos, e o texto não diz se Braga & Amaral as interpretam como controle. Kselman (L59) descreve um mecanismo de disciplina por *competição entre candidatos*, não de agência partidária, e por isso destoa do título da subseção. Nos dois casos a obra é usada para uma tese que ela não sustenta diretamente."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:43", "tese/02-literatura.qmd:57", "tese/02-literatura.qmd:59"]
  detalhe: "L59: 'outro colega de partido pode estar dando atenção ao eleitorado e por isso posteriormente vencer uma eventual disputa intrapartidária com o político corrupto'. O agente do mecanismo é o candidato, não o partido."
severidade: MINOR
confianca: media
recomendacao: "Verificar se Braga & Amaral interpretam as listas incompletas como controle. Mover Kselman para o contraponto de Chang (2005), na L29, onde ele funciona como evidência contra o cânone."
claims: [C2.3.03]
```

```yaml
id: LIT-2-015
titulo: "Cox & McCubbins (2005): 'recursos escassos' é a agenda legislativa; a extensão para dinheiro é do autor"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 77
  secao: "## Partidos como organizações heterogêneas"
  trecho: "lideranças recebem autoridade para organizar a ação coletiva e proteger a reputação da legenda, sobretudo por meio do controle de recursos escassos."
afirmacao_do_autor: "Lideranças protegem a reputação da legenda controlando recursos escassos, o que teria análogo no dinheiro de campanha."
problema: "Em Setting the Agenda, o recurso escasso é o tempo e a agenda do plenário (poder negativo de agenda). A delegação a lideranças para gerir a reputação partidária está formulada mais diretamente em Cox & McCubbins (1993, Legislative Leviathan), ausente do .bib. A frase seguinte já marca a analogia como argumento do autor ('argumenta-se'). O problema é a paráfrase genérica, que sugere que a obra trata de recursos em sentido amplo."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:77", "tese/references.bib:451-460"]
  detalhe: "O subtítulo no bib é 'Responsible Party Government in the U.S. House of Representatives'."
severidade: MINOR
confianca: media
recomendacao: "Especificar 'controle da agenda' e considerar citar Legislative Leviathan (1993) para a delegação e a reputação."
claims: [C2.4.02]
```

```yaml
id: LIT-2-016
titulo: "Janusz et al. (2021): instrumentos, período e 'orientação ex-ante' não verificáveis e ambíguos no texto"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 212
  secao: "## Argumento"
  trecho: "esta tese segue a orientação *ex-ante* de @janusz_barreiro_cintron_2021"
afirmacao_do_autor: "Janusz et al. definem qualidade de candidatura por experiência prévia (ex-ante), tratam número de urna, TV e dinheiro como resource gatekeeping, e mostram favorecimento de incumbentes e subfinanciamento de mulheres."
problema: "A obra é citada 5 vezes e sustenta três afirmações diferentes, entre elas a escolha operacional da tese (L212). Não consigo verificar a lista de instrumentos da L65 nem a eleição analisada. Na L151, o parágrafo vem logo depois do tratamento de 2014 e dos recursos empresariais, e não diz de qual eleição ou fonte de recursos se trata. Isso importa porque a L147 afirma que o confundimento dos recursos intermediados não ocorre em 2018/2022. O .bib não tem volume nem páginas."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:65", "tese/02-literatura.qmd:147", "tese/02-literatura.qmd:151", "tese/02-literatura.qmd:212", "tese/references.bib:610-616"]
  detalhe: "Entrada bib: só journal, year e doi."
severidade: MINOR
confianca: media
recomendacao: "Na L151, indicar a eleição, o cargo e a fonte de recursos analisados por Janusz et al. Conferir a lista de instrumentos da L65 e completar o .bib."
claims: [C2.3.08, C2.6.06, C2.7.05]
```

```yaml
id: LIT-2-017
titulo: "Formalidades de citação e do .bib"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 101
  secao: "## Partidos como organizações heterogêneas"
  trecho: '"afetam substantivamente a capacidade dos partidos de funcionar como um time" (p.2)'
afirmacao_do_autor: "—"
problema: "(a) L101: localizador '(p.2)' digitado à mão, fora da sintaxe Pandoc; deveria ser [-@ribeiroetal2022, p. 2]. (b) Chaves cujo ano diverge do ano da entrada: andreetal2015 → 2017, tavits2012 → 2013 (renderizam certo, mas confundem quem edita). (c) mainwaring1999: título com hífen espúrio, 'Democratizati-on', que aparece na bibliografia renderizada. (d) jonesmainwaring2003 duplicada no .bib (L83 e L131); não é citada no Cap. 2, mas gera aviso do citeproc. (e) Metadados incompletos em entradas citadas: hottmenezes2023 e janusz_barreiro_cintron_2021 (sem volume/páginas), silvacodato2024 (sem número/páginas/doi), cheibub_junqueira_moreira_2024 (working paper sem URL/instituição). (f) speck2011 e sacchetspeck2011 como @incollection com booktitle de conferência; o tipo correto é @inproceedings/@misc. (g) avelino_barone2012: a chave omite o coautor Biderman, o que só importa para busca."
evidencia:
  tipo: artefato
  fontes: ["tese/02-literatura.qmd:101", "tese/references.bib:83-89", "tese/references.bib:131-137", "tese/references.bib:91-96", "tese/references.bib:376-427", "tese/references.bib:574-616", "tese/references.bib:639-644", "tese/references.bib:676-685", "thesis-review/runs/run-003/evidence/lit_cruzamento_citacoes.out"]
  detalhe: "Saída do script: '## chaves duplicadas no bib: jonesmainwaring2003'."
severidade: MINOR
confianca: alta
recomendacao: "Corrigir (a) e (c). Remover a duplicata (d). Completar os metadados (e) e ajustar os tipos (f)."
claims: []
```

## Claims

```yaml
claim_id: C2.1.01
capitulo: 2
secao: "## Primeira e segunda gerações de estudos sobre os efeitos do voto preferencial"
claim: "Mershon (2020) organiza a literatura em primeira e segunda gerações, sem fronteira rígida entre elas."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 41}
evidencia: {tipo: citacao, referencia: "@mershon2020"}
assessment: {status: unverifiable, confidence: baixa}
concerns: ["O vocabulário de 'gerações' pode ser síntese do autor, não de Mershon."]
agent: literature-reviewer
```

```yaml
claim_id: C2.2.01
capitulo: 2
secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
claim: "Katz (1986): candidatos podem valorizar o próprio sucesso acima do sucesso do partido; Rae supõe partidos coesos."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 13}
evidencia: {tipo: citacao, referencia: "@katz1986; @rae1971"}
assessment: {status: supported, confidence: media}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.2.02
capitulo: 2
secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
claim: "Carey & Shugart (1995) ordenam ballot, pool, vote e magnitude em três níveis; o efeito da magnitude se inverte entre lista fechada e aberta."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 17}
evidencia: {tipo: citacao, referencia: "@careyshugart1995"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.2.03
capitulo: 2
secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
claim: "O pooling brasileiro não se encaixa nos níveis de Carey & Shugart e fica entre o menor e o intermediário."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 33}
evidencia: {tipo: citacao, referencia: "@careyshugart1995; @figueiredo_limongi_2002_incentivos"}
assessment: {status: contradicted, confidence: media}
concerns: ["Pela definição da própria L21, o caso é pool=0 (LIT-2-003)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.2.04
capitulo: 2
secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
claim: "Mainwaring (1999) sugere que a competição intrapartidária poderia superar a interpartidária no Brasil."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 39}
evidencia: {tipo: citacao, referencia: "@mainwaring1999"}
assessment: {status: supported, confidence: media}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.3.01
capitulo: 2
secao: "### A segunda geração e a agência partidária"
claim: "O que une a segunda geração é o condicionamento contextual dos efeitos das regras (Ferree et al. 2014)."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 45}
evidencia: {tipo: citacao, referencia: "@ferree2014"}
assessment: {status: partially_supported, confidence: media}
concerns: ["Ferree et al. tratam de sistemas partidários, não de voto preferencial (LIT-2-006)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.3.02
capitulo: 2
secao: "### A segunda geração e a agência partidária"
claim: "Samuels (1999) mostra que partidos brasileiros podem cultivar voto partidário apesar do sistema centrado no candidato."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 49}
evidencia: {tipo: citacao, referencia: "@samuels1999"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.3.03
capitulo: 2
secao: "### A segunda geração e a agência partidária"
claim: "Listas incompletas (Braga & Amaral 2013) indicam controle partidário."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 57}
evidencia: {tipo: citacao, referencia: "@braga_amaral_2013_implicacoes"}
assessment: {status: unverifiable, confidence: baixa}
concerns: ["Inferência alternativa: escassez de candidatos (LIT-2-014)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.3.04
capitulo: 2
secao: "### A segunda geração e a agência partidária"
claim: "Desposato (2006) encontra coesão partidária igual na Câmara e no Senado."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 51}
evidencia: {tipo: citacao, referencia: "@desposato_2006_impact"}
assessment: {status: unverifiable, confidence: baixa}
concerns: ["Possível inversão do achado (LIT-2-005)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.3.05
capitulo: 2
secao: "### A segunda geração e a agência partidária"
claim: "Deputados brasileiros votam segundo a orientação das lideranças (Figueiredo & Limongi 1999)."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 51}
evidencia: {tipo: citacao, referencia: "@figueiredolimongi1999"}
assessment: {status: supported, confidence: alta}
concerns: ["Falta o contraponto de Pereira & Mueller 2003 sobre a arena eleitoral (LIT-2-010)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.3.06
capitulo: 2
secao: "### A segunda geração e a agência partidária"
claim: "Partidos reduzem a sobreposição regional entre copartidários viáveis."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 63}
evidencia: {tipo: citacao, referencia: "@avelinobidermansilva2011; @silotto2019; @cheibub_junqueira_moreira_2024"}
assessment: {status: partially_supported, confidence: media}
concerns: ["avelinobidermansilva2011 é um artigo de medidas (LIT-2-013)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.3.07
capitulo: 2
secao: "### A segunda geração e a agência partidária"
claim: "Evidências de listas flexíveis corroboram que o gatekeeping não termina na convenção."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 67}
evidencia: {tipo: citacao, referencia: "@andreetal2015; @crispetal2013"}
assessment: {status: unsupported, confidence: alta}
concerns: ["A recompensa ocorre na formação da lista seguinte (LIT-2-004)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.3.08
capitulo: 2
secao: "### A segunda geração e a agência partidária"
claim: "Partidos brasileiros manipulam número de urna, TV e dinheiro (resource gatekeeping), produzindo desigualdade entre candidaturas."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 65}
evidencia: {tipo: citacao, referencia: "@janusz_barreiro_cintron_2021"}
assessment: {status: partially_supported, confidence: baixa}
concerns: ["A lista de instrumentos não foi verificada (LIT-2-016)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.4.01
capitulo: 2
secao: "## Partidos como organizações heterogêneas"
claim: "Partidos resolvem problemas de ação coletiva de candidatos (Aldrich 2011)."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 75}
evidencia: {tipo: citacao, referencia: "@aldrich2011"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.4.02
capitulo: 2
secao: "## Partidos como organizações heterogêneas"
claim: "Em Cox & McCubbins (2005), lideranças protegem a reputação partidária pelo controle de recursos escassos."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 77}
evidencia: {tipo: citacao, referencia: "@cox_mccubbins_2005_setting"}
assessment: {status: partially_supported, confidence: media}
concerns: ["O recurso escasso é a agenda (LIT-2-015)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.4.03
capitulo: 2
secao: "## Partidos como organizações heterogêneas"
claim: "Fiva et al. (2024): atribuir vantagem a alguns candidatos reduz o esforço agregado (p. 100)."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 89}
evidencia: {tipo: citacao, referencia: "@fivaetal2024"}
assessment: {status: partially_supported, confidence: media}
concerns: ["O dilema bate com o título; o localizador p. 100 é implausível (LIT-2-007)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.4.04
capitulo: 2
secao: "## Partidos como organizações heterogêneas"
claim: "Fiva et al. teorizam que partidos mais competitivos transitam melhor pelo trade-off."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 93}
evidencia: {tipo: citacao, referencia: "@fivaetal2024"}
assessment: {status: unverifiable, confidence: baixa}
concerns: ["Sem localizador; o comentário [2.2-3] propõe derivar dela uma hipótese auxiliar."]
agent: literature-reviewer
```

```yaml
claim_id: C2.4.05
capitulo: 2
secao: "## Partidos como organizações heterogêneas"
claim: "Partidos brasileiros centralizam decisões via comissões provisórias (Guarnieri 2011)."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 97}
evidencia: {tipo: citacao, referencia: "@guarnieri2011"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.4.06
capitulo: 2
secao: "## Partidos como organizações heterogêneas"
claim: "Tavits mostra que inactive branches funcionam como ferramentas de mobilização; Tavits e Webb & Keith amparam a RBV."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 97}
evidencia: {tipo: citacao, referencia: "@tavits2012; @webbkeith2017"}
assessment: {status: unverifiable, confidence: baixa}
concerns: ["LIT-2-012"]
agent: literature-reviewer
```

```yaml
claim_id: C2.5.01
capitulo: 2
secao: "## Competição intrapartidária e gastos de campanha"
claim: "Cox & Thies (1998): no SNTV japonês, a competição intra e interpartidária eleva o gasto."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 117}
evidencia: {tipo: citacao, referencia: "@cox_thies_1998_cost"}
assessment: {status: supported, confidence: media}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.5.02
capitulo: 2
secao: "## Competição intrapartidária e gastos de campanha"
claim: "Samuels (2001): o número de adversários não afeta o gasto; a qualidade dos colegas de lista afeta."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 121}
evidencia: {tipo: citacao, referencia: "@samuels_2001_every_penny; @cox1997"}
assessment: {status: supported, confidence: media}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.6.01
capitulo: 2
secao: "## Financiamento de campanhas no Brasil"
claim: "Mancuso (2015) divide a literatura em três vertentes (efeitos no desempenho, benefícios a doadores, determinantes do financiamento)."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 133}
evidencia: {tipo: citacao, referencia: "@mancuso_2015_investimento"}
assessment: {status: supported, confidence: media}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.6.02
capitulo: 2
secao: "## Financiamento de campanhas no Brasil"
claim: "Thomsen (2023): recursos são mais concentrados que votos; propõe medida de concentração de recursos como medida de competição."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 139}
evidencia: {tipo: citacao, referencia: "@thomsen2023"}
assessment: {status: supported, confidence: media}
concerns: []
agent: literature-reviewer
```

```yaml
claim_id: C2.6.03
capitulo: 2
secao: "## Financiamento de campanhas no Brasil"
claim: "Silva & Cervi (2017): em 2014 os partidos são a principal origem das receitas; 89,6% dos repasses vieram de PJ, 7,5% do FP; a desigualdade cresceu."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 145}
evidencia: {tipo: citacao, referencia: "@silvacervi2017"}
assessment: {status: unverifiable, confidence: baixa}
concerns: ["Números não conferidos; Bolognesi et al. 2020 ausente (LIT-2-001)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.6.04
capitulo: 2
secao: "## Financiamento de campanhas no Brasil"
claim: "Regras do FEFC/FP, cotas e cláusula de desempenho descritas nas L153-165."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 159}
evidencia: {tipo: nenhuma, referencia: "sem citação"}
assessment: {status: unsupported, confidence: alta}
concerns: ["Sem fonte, embora o .bib tenha fontes (LIT-2-008). A correção substantiva dos números fica fora do escopo deste agente."]
agent: literature-reviewer
```

```yaml
claim_id: C2.6.05
capitulo: 2
secao: "## Financiamento de campanhas no Brasil"
claim: "O FEFC deu aos partidos maior centralidade na estruturação da competição (Silva & Codato 2024)."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 157}
evidencia: {tipo: citacao, referencia: "@silvacodato2024"}
assessment: {status: partially_supported, confidence: media}
concerns: ["Falta a literatura de partido-cartel (LIT-2-011)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.6.06
capitulo: 2
secao: "## Financiamento de campanhas no Brasil"
claim: "Janusz et al.: distribuição seletiva a incumbentes e ex-ocupantes de cargo; mulheres recebem menos mesmo controlando pela experiência."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 151}
evidencia: {tipo: citacao, referencia: "@janusz_barreiro_cintron_2021"}
assessment: {status: supported, confidence: media}
concerns: ["Período e fonte dos recursos não indicados (LIT-2-016)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.7.01
capitulo: 2
secao: "## Argumento"
claim: "Os critérios de Silva & Cervi (p. 85) e de Cheibub & Sin (p. 79) usam resultados da própria eleição analisada."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 212}
evidencia: {tipo: citacao, referencia: "@silvacervi2017; @cheibubsin2020"}
assessment: {status: supported, confidence: media}
concerns: ["Consistente com a caracterização de candidato_forte_cs como ex-post no CLAUDE.md; páginas dentro dos intervalos do .bib."]
agent: literature-reviewer
```

```yaml
claim_id: C2.7.02
capitulo: 2
secao: "## Argumento"
claim: "A seletividade pode refletir captura por incumbentes, barganha ou ameaça de saída."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 178}
evidencia: {tipo: nenhuma, referencia: "sem citação"}
assessment: {status: unsupported, confidence: alta}
concerns: ["LIT-2-009"]
agent: literature-reviewer
```

```yaml
claim_id: C2.7.03
capitulo: 2
secao: "## Argumento"
claim: "Credenciais prévias são sinais da capacidade de contribuir para o desempenho coletivo, o que leva à priorização."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 204}
evidencia: {tipo: nenhuma, referencia: "sem citação"}
assessment: {status: unsupported, confidence: alta}
concerns: ["Faltam as literaturas de alocação e de atributos de candidatos (LIT-2-002)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.7.04
capitulo: 2
secao: "## Argumento"
claim: "As cotas de financiamento não fixam a parcela a ser transferida."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 188}
evidencia: {tipo: nenhuma, referencia: "sem citação"}
assessment: {status: unsupported, confidence: media}
concerns: ["Tensão com a L155; tse2018financiamentofeminino e tse2022criteriosfefc existem no .bib (LIT-2-008)."]
agent: literature-reviewer
```

```yaml
claim_id: C2.7.05
capitulo: 2
secao: "## Argumento"
claim: "A tese segue a orientação ex-ante de Janusz et al."
localizacao: {arquivo: tese/02-literatura.qmd, linha: 212}
evidencia: {tipo: citacao, referencia: "@janusz_barreiro_cintron_2021"}
assessment: {status: partially_supported, confidence: media}
concerns: ["Coerente com a L151 (experiência prévia como qualidade); não verificado no texto-fonte."]
agent: literature-reviewer
```

## Verificações que passaram
- As 51 chaves citadas no capítulo existem em `tese/references.bib`. Nenhuma chave quebrada (`evidence/lit_cruzamento_citacoes.out`).
- Localizadores de página dentro do intervalo do `.bib`: careyshugart1995 p. 434 (417–439), samuels_2001_every_penny p. 100 (89–102), scarrowwebb2017 p. 1 (1–28), silvacervi2017 p. 85 (75–110), cheibubsin2020 p. 79 (70–95).
- Sintaxe `[-@key]` usada corretamente onde o autor já está nomeado (L99 Ribeiro, L127 Samuels).
- Metadados de periódico conferem com o que sei para careyshugart1995, cox_thies_1998_cost, samuels_2001_every_penny, chang2005, ames1995, samuels1999, desposato_2006_impact, hagopian_gervasoni_moraes_2009_patronage, ferree2014, figueiredo_limongi_2002_incentivos, katz1986, rae1971, tavits (ano 2013).
- Uso equilibrado de evidência contrária em dois pontos: Chang (2005) × Kselman (2011); Cox & Thies (1998) × Samuels (2001).
- A caracterização ex-post de Cheibub & Sin na L212 é coerente com a definição de `candidato_forte_cs` no CLAUDE.md.

## Limites desta revisão
- Sem acesso aos textos das obras: toda avaliação de conteúdo vem do conhecimento prévio e dos títulos/periódicos do `.bib`. Os achados LIT-2-005, LIT-2-007 (L93) e LIT-2-012 têm confiança baixa e precisam ser conferidos no original.
- As sugestões de ausências (LIT-2-002, 009, 010, 011) indicam obras em cuja existência tenho confiança alta ou média, conforme marcado em cada achado. Não verifiquei páginas nem edições.
- Números e regras legais do Financiamento (L143–165) foram avaliados só quanto à fonte, não quanto ao valor (fora do escopo).
- Citações dentro de comentários HTML (L79, L192, L198) não foram avaliadas.
