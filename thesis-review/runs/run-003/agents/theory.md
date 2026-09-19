# theory-reviewer — Capítulo 2 — run-003

## Escopo e método
- Arquivos lidos: `thesis-review/PROTOCOL.md`, `thesis-review/rubric.yaml`, `thesis-review/templates/agent_report.md`, `tese/02-literatura.qmd` (inteiro, 219 linhas), `tese/03-medindo-coordenacao-intrapartidaria.qmd` (inteiro, incluindo comentários HTML, que não foram tratados como texto do autor), `tese/04-mecanismo-causal-coordenacao.qmd` (L1-76 e L133-156, mais grep por `cheibubsin|fivaetal|núcleo|antecip|argumento`). `tese/01-introducao.qmd` não tem nenhuma ocorrência de `cheibubsin|contribui|argumento|Fiva|gatekeep` (grep), ou seja, a introdução ainda não formula a contribuição.
- Recomputações executadas: nenhuma. O escopo é teórico. As checagens foram textuais, por grep: `tipo de partido`, `bancada`, `Mp`, `puxador`, `marginal` e `lift_partido` não aparecem no corpo dos Caps. 3 e 4, só em comentários.
- Convenção dos ids de claim: seções do Cap. 2 na ordem em que aparecem: 1 = "Primeira e segunda gerações…", 2 = "O cânone…", 3 = "A segunda geração…", 4 = "Partidos como organizações heterogêneas", 5 = "Competição intrapartidária e gastos", 6 = "Financiamento de campanhas no Brasil", 7 = "Argumento".
- Não foi possível verificar: o conteúdo das obras citadas (Fiva et al. 2024; Janusz, Barreiro & Cintron 2021; Cheibub & Sin 2020). As atribuições foram avaliadas pelo que o próprio texto diz delas.

### Passo obrigatório 1: o argumento em uma frase
Como o acesso futuro ao FEFC e ao Fundo Partidário depende do desempenho na Câmara (L159-169), os partidos, que alocam antes de saber o resultado, concentram os recursos em candidaturas com credenciais eleitorais prévias, tomadas como sinal de capacidade de contribuir para o desempenho coletivo da legenda (L174, L204).

### Passo obrigatório 2: expectativas testadas e sua derivação
| # | Expectativa testada (onde) | Passagem do Cap. 2 que a implica | Derivação |
|---|---|---|---|
| E1 | O núcleo priorizado sobrerrepresenta candidaturas com credencial em relação ao acaso (Cap. 3, Top-NECr, L106-114) | L204: "presença desproporcional, em relação ao acaso, de candidatos com credenciais entre os destinatários que concentram a maior parcela de recursos" | Vem do argumento. Mas o "núcleo" e o seu tamanho não são derivados (THE-2-006), e a expectativa não separa o argumento de suas rivais (THE-2-001) |
| E2 | A credencial está associada a uma parcela intralista maior, desagregada por cargo (Cap. 3, L129-175) | L204 (agregado); L214 frente (ii): "análise desagregada por cargos" | O efeito agregado vem de L204. Para a desagregação não há expectativa: nada diz quais cargos seriam sinais mais fortes |
| E3 | Priorização temporal (Cap. 4) | L214: "(iii) a identificação de uma priorização temporal ao núcleo priorizado da lista"; L77: "e quando os recebem" | **Não derivada** (THE-2-003). E o Cap. 4 testa a credencial, não o núcleo |
| E4 | O gradiente por magnitude (lift e razão crescem com M; Cap. 3, L118, L167) | Nenhuma. L25 (Carey & Shugart) e L121 (Samuels/Cox) tratam de M, mas sem implicação para a alocação | **Ausente**: o gradiente é interpretado *post hoc* (THE-2-007) |
| E5 | Mudança 2018→2022 (Cap. 3, L165; Cap. 4, L25) | Nenhuma. L165 descreve a cláusula de desempenho, sem prever a direção | **Ausente**, e as direções sugeridas se contradizem (THE-2-002) |
| E6 | (implicada, não testada) Heterogeneidade entre partidos | L87, L93 (Scarrow & Webb; Fiva et al.: partidos mais competitivos) | É implicada pelo Cap. 2 e não é testada (THE-2-008) |

## Avaliação macro
A cadeia incentivo → incerteza → sinal → expectativa existe em L174 e L204 e implica E1 e o componente agregado de E2. Três elos falham. (a) O incentivo de L174 não implica concentração. As regras de financiamento descritas no próprio capítulo (L159, L163) premiam votos, e com *pooling* isso é compatível com dispersão. O texto não diz por que a concentração domina, e o Cap. 4 (L25) chega a afirmar o incentivo oposto para 2022. (b) A expectativa E1/E2 também é implicada pelas rivais que o próprio texto enumera (L178: captura por incumbentes, barganha, ameaça de saída) e pela rival "o dinheiro segue candidatos fortes". O capítulo não diz que observação distinguiria o mecanismo de sinalização dessas leituras. O mecanismo, como está formulado, não é falseável pelos testes planejados. (c) A frente (iii) não tem derivação, e a magnitude e a heterogeneidade partidária também não. O Cap. 3 interpreta a magnitude *post hoc*; a heterogeneidade o Cap. 2 implica (Fiva et al., Scarrow & Webb) e não testa. Na contribuição, o texto reivindica "coordenação intrapartidária" que "orienta a competição" (L176) e "vantagem competitiva" (L95), mas os testes medem só o padrão de alocação. A novidade em relação a Janusz, Barreiro & Cintron (2021), que segundo L65 e L151 já mostram *gatekeeping* por recursos depois da convenção e privilégio a incumbentes, não é dita. A diferença em relação a Cheibub & Sin muda entre os capítulos: no Cap. 2 é a classificação ex-ante (L212), no Cap. 3 é convergência ("reforçam", L100), no Cap. 4 é o momento da coordenação (L13). Pela rubrica, os pontos (a), (b), (c) e a contribuição exigem mudança de interpretação: MAJOR. Nada invalida os resultados empíricos.

## Achados

```yaml
id: THE-2-001
titulo: "A expectativa central não separa o mecanismo de sinalização das rivais que o próprio texto enumera"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 204
  secao: "## Argumento"
  trecho: "Se a distribuição partidária busca favorecer candidaturas capazes de contribuir para o desempenho coletivo da legenda, a expectativa da tese é encontrar uma presença desproporcional, em relação ao acaso, de candidatos com credenciais entre os destinatários que concentram a maior parcela de recursos."
afirmacao_do_autor: "Os partidos priorizam candidaturas com credenciais porque estas sinalizam capacidade de contribuir para o desempenho coletivo; a implicação é a sobrerrepresentação de credenciados entre os mais financiados."
problema: "O condicional de L204 só vale em uma direção. A sobrerrepresentação de credenciados também é implicada pelas rivais que o texto lista em L178 ('captura de incumbentes sobre os diretórios', 'barganha', 'ameaça de sair do partido e levar votos consigo') e pela rival 'candidatos fortes atraem dinheiro' (poder de negociação de quem tem mandato). O texto nomeia as rivais em L178 e não volta a elas: nenhuma frase diz que observação distinguiria sinalização de captura/barganha, nem que resultado falsearia o argumento. Como o mecanismo alegado (a leitura de sinais pelo partido sob incerteza) não é observado diretamente, a tese precisa de implicações diferenciais. Algumas já existem nos dados do Cap. 3 e não são teorizadas. (1) Sinal de votos sem mandato: o indicador '10% do QE sem vitória acima de vereador' tem razão 2,89/1,70 (Cap. 3, L157). A captura por incumbentes não prevê prêmio para não incumbentes; a sinalização prevê. (2) A vitória para vereador (sinal de voto local, sem peso na organização estadual) versus mandatos que dão posição no diretório. (3) Pela lógica de desempenho coletivo, o prêmio deveria depender da contribuição esperada em votos (proporção de votos nominais anterior); pela captura, da posição organizacional, independente de votos. Sem essas implicações, a conclusão do Cap. 3 (Discussão proposta, L256: 'compatíveis com... Não demonstram essa intenção') é a única leitura defensável, e o Cap. 2 deveria anunciá-la como tal."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:178", "tese/02-literatura.qmd:204", "tese/03-medindo-coordenacao-intrapartidaria.qmd:157", "tese/03-medindo-coordenacao-intrapartidaria.qmd:153"]
  detalhe: "L178 enumera três rivais. As frases seguintes (L180-L218) não mencionam nenhuma delas. L204 formula só a implicação compartilhada pelo argumento e pelas rivais. O Cap. 3 reporta coeficientes (QE sem vitória, vereador, votos nominais anteriores) que poderiam discriminar entre as leituras, mas sem expectativa derivada no Cap. 2 ficam como descrição."
severidade: MAJOR
confianca: alta
recomendacao: "No Argumento, logo após L178, escrever para cada rival uma implicação que difira da sinalização (ex.: 'se a alocação reflete captura por incumbentes, não se espera prêmio para candidaturas sem mandato com votação expressiva; se reflete sinalização de capacidade de voto, espera-se'). Ou declarar explicitamente que a tese estabelece um padrão compatível com a sinalização e não o distingue da barganha."
claims: [C2.7.03, C2.7.02]
```

```yaml
id: THE-2-002
titulo: "O incentivo de L174 não implica concentração: as regras premiam votos, e com pooling isso é compatível com dispersão"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 174
  secao: "## Argumento"
  trecho: "O vínculo entre desempenho eleitoral e recursos recebidos pelos partidos presente nas regras de financiamento gera os incentivos para que as legendas distribuam seus recursos seletivamente, visando a ampliação do quociente partidário e a sobrevivência ou ampliação de recursos"
afirmacao_do_autor: "O vínculo desempenho–recursos gera incentivo à distribuição seletiva."
problema: "A premissa de incentivo é a primeira da cadeia e não leva à expectativa. As próprias regras descritas no capítulo remuneram votos: 35% do FEFC 'proporcionalmente aos votos obtidos' (L159) e 95% do FP 'conforme os votos recebidos' (L163). Em lista aberta com pooling (L33), todo voto nominal soma para a legenda. Um partido que maximiza votos poderia dispersar recursos entre muitos candidatos coletores de votos. Um partido que maximiza cadeiras poderia priorizar candidatos marginais, perto da linha de corte, e não os credenciados. 'Seletivamente' é compatível com as três estratégias, e o texto não diz qual incentivo domina nem por quê (retorno marginal decrescente do dinheiro? cláusula de desempenho?). Consequência entre capítulos: o Cap. 4 (L25) deriva do mesmo contexto institucional o incentivo oposto para 2022 ('incentivos adicionais para que os partidos alocassem recursos de forma mais desconcentrada'), e o Cap. 3 (L165) interpreta a queda do prêmio 8,16→4,58 nessa chave. Sem um incentivo com direção definida, a expectativa para 2018→2022 (E5) fica indeterminada, e qualquer resultado pode ser acomodado."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:159", "tese/02-literatura.qmd:163", "tese/02-literatura.qmd:33", "tese/02-literatura.qmd:174", "tese/04-mecanismo-causal-coordenacao.qmd:25", "tese/03-medindo-coordenacao-intrapartidaria.qmd:165"]
  detalhe: "Cap. 4 L25: 'Estes fatores criaram incentivos adicionais para que os partidos alocassem recursos de forma mais desconcentrada, já que não contavam com uma coligação para garantir o quociente partidário'. O Cap. 2 não contém previsão sobre a direção da mudança 2018→2022."
severidade: MAJOR
confianca: alta
recomendacao: "Explicitar no Argumento por que a maximização de votos/cadeiras sob pooling leva à concentração em credenciados e não à dispersão ou ao investimento em marginais (ex.: sob incerteza, só a credencial é observável ex ante; o 'puxador' eleva o quociente e elege colegas). Derivar dessa premissa a direção esperada para 2022 (fim das coligações) e alinhar o Cap. 4 (L25) com ela."
claims: [C2.7.01, C2.6.01]
```

```yaml
id: THE-2-003
titulo: "A frente (iii), timing, não tem derivação teórica, e o objeto anunciado (núcleo) não é o que o Cap. 4 testa (credencial)"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 214
  secao: "## Argumento"
  trecho: "e (iii) a identificação de uma priorização temporal ao núcleo priorizado da lista."
afirmacao_do_autor: "A estratégia empírica inclui uma frente de priorização temporal ao núcleo, testada no Cap. 4 (L218)."
problema: "Nada no Argumento explica por que o momento do repasse seria um instrumento de priorização, nem qual padrão temporal o argumento prevê. A única menção teórica é L77 ('quais candidaturas recebem recursos e quando os recebem'), sem justificativa. A lógica de Fiva et al., que o capítulo adota (L89-91), pode até prever o contrário: se proteger candidaturas reduz o esforço (risco moral), um partido que antecipa o dinheiro aos protegidos agrava o problema, e reter ou condicionar o repasse seria a resposta ótima. O Cap. 4 (L49) atribui a Fiva et al. uma previsão sobre o FEFC ('prevê que partidos, ao controlarem a distribuição do FEFC, têm incentivos para agir seletivamente') que o Cap. 2 não sustenta: em L89-95 os autores tratam de posições de vantagem na Noruega, e a extensão ao Brasil é do autor ('argumenta-se', L95). Por fim, (iii) promete 'priorização temporal ao núcleo priorizado', mas o Cap. 4 usa o corte competitivo/não competitivo (Cap. 4, L61, L63), não o Top-NECr."
evidencia:
  tipo: ausencia
  fontes: ["tese/02-literatura.qmd:77", "tese/02-literatura.qmd:89", "tese/02-literatura.qmd:214", "tese/02-literatura.qmd:218", "tese/04-mecanismo-causal-coordenacao.qmd:49", "tese/04-mecanismo-causal-coordenacao.qmd:61"]
  detalhe: "Em L171-218 não há nenhuma frase sobre custo de oportunidade do tempo, sinalização a eleitores ou cabos eleitorais, ou restrição de caixa. A justificativa substantiva do timing só aparece no Cap. 4, L29 ('maior margem para aplicação deste dinheiro... colocar a campanha na rua mais cedo')."
severidade: MAJOR
confianca: alta
recomendacao: "Derivar (iii) no Argumento: por que o dinheiro cedo vale mais (tempo de campanha, contratação, sinal a cabos eleitorais) e como isso se concilia com o risco moral de Fiva et al. Ajustar a redação de (iii) para 'candidaturas com credenciais' ou justificar o uso da credencial no lugar do núcleo. Rever a atribuição a Fiva et al. no Cap. 4, L49."
claims: [C2.7.06, C2.7.08]
```

```yaml
id: THE-2-004
titulo: "'Coordenação intrapartidária' e 'vantagem competitiva' são reivindicadas, mas os testes medem só o padrão de alocação"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 176
  secao: "## Argumento"
  trecho: "Nesta leitura, a alocação de recursos partidários constitui um instrumento de coordenação intrapartidária, por meio do qual a organização procura orientar a competição entre seus candidatos para objetivos eleitorais coletivos."
afirmacao_do_autor: "A alocação é um instrumento de coordenação que orienta a competição intralista para fins coletivos; a distribuição 'constitui um instrumento de atribuição de vantagem competitiva' (L95)."
problema: "'Coordenação' (título da tese, L176) e 'vantagem competitiva' (L95) são afirmações sobre o efeito da alocação na competição e no resultado coletivo. As três frentes (L214) só testam a destinação do dinheiro condicionada a credenciais. Nenhuma frente testa se a alocação altera a competição (por exemplo, o número efetivo de candidaturas em votos) ou melhora o desempenho da legenda. O próprio Cap. 3 (L76) descarta a correspondência com os eleitos como evidência, por estar 'contaminada'. Pelo desenho, os testes estabelecem priorização (quem recebe, quanto, quando), não coordenação no sentido de L176. Há também deriva conceitual: em L55 'coordenação' é vertical, eleitoral; em L63, número/território de candidaturas; em L176, alocação orientada a objetivos coletivos; no Cap. 4, L13, um momento (pré ou pós-lista)."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:55", "tese/02-literatura.qmd:63", "tese/02-literatura.qmd:95", "tese/02-literatura.qmd:176", "tese/02-literatura.qmd:214", "tese/03-medindo-coordenacao-intrapartidaria.qmd:76", "tese/04-mecanismo-causal-coordenacao.qmd:13"]
  detalhe: "Cap. 3 L76: 'Estes testes, entretanto, são \"contaminados\" pelo resultado eleitoral'. Nenhuma frente de L214 tem variável de resultado competitivo ou coletivo."
severidade: MAJOR
confianca: alta
recomendacao: "Definir 'coordenação' uma vez e distinguir 'priorização' (o que é testado) de 'coordenação' (efeito sobre a competição). Ou rebaixar a reivindicação de L176/L95 para 'a alocação é compatível com uma estratégia de coordenação', ou acrescentar uma implicação observável do efeito coordenador e dizer onde é testada."
claims: [C2.7.02, C2.4.01]
```

```yaml
id: THE-2-005
titulo: "A contribuição não é delimitada frente a Janusz et al. (2021), e a diferença frente a Cheibub & Sin muda entre os capítulos"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 65
  secao: "### A segunda geração e a agência partidária"
  trecho: "No Brasil, evidências recentes mostram que o *gatekeeping* não se encerra na convenção partidária. Partidos manipulam dimensões posteriores da campanha, como número de urna, tempo de televisão e recursos financeiros."
afirmacao_do_autor: "O gatekeeping continua depois da convenção (L65, L95). Janusz et al. mostram que a distribuição partidária privilegia incumbentes e ex-ocupantes de cargos (L151). A tese adota a orientação ex-ante desses autores (L212)."
problema: "Pelo que o Cap. 2 diz de Janusz, Barreiro & Cintron (2021), eles já sustentam (a) o gatekeeping por recursos depois da convenção (L65), (b) a seletividade que privilegia 'incumbentes e candidatos que ocuparam algum cargo eletivo anteriormente' (L151) e (c) a classificação ex-ante (L212). É praticamente a expectativa E1/E2. O capítulo não diz o que a tese acrescenta: período/fonte (FEFC 2018/2022?), núcleo de tamanho endógeno (NECr), comparação intralista, timing? Frente a Cheibub & Sin, a diferença varia: Cap. 2, L212, é a classificação ex-post versus ex-ante (mensuração); Cap. 3, L100, é convergência ('os resultados reforçam o argumento de @cheibubsin2020'); Cap. 4, L13, é o momento da coordenação ('se daria sobretudo antes da formação das listas'), tese que o Cap. 2 nunca atribui aos autores (L63 e L202 falam do número de competitivos, não do momento). O leitor do Cap. 2 não encontra a diferença que o Cap. 4 declara 'novamente'."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:63", "tese/02-literatura.qmd:65", "tese/02-literatura.qmd:151", "tese/02-literatura.qmd:202", "tese/02-literatura.qmd:212", "tese/03-medindo-coordenacao-intrapartidaria.qmd:100", "tese/04-mecanismo-causal-coordenacao.qmd:13"]
  detalhe: "Cap. 4 L13: 'Aqui a tese proposta se diferencia novamente de @cheibubsin2020'. A palavra 'novamente' pressupõe uma diferenciação anterior sobre o momento, ausente em L63 e L202. O Cap. 1 não contém formulação da contribuição (grep sem ocorrências)."
severidade: MAJOR
confianca: media
recomendacao: "Ao fim do Argumento, escrever duas ou três frases de contribuição: (1) o que a tese acrescenta a Janusz et al. (período sob FEFC, núcleo endógeno, comparação intralista, timing); (2) uma única formulação da diferença frente a Cheibub & Sin (coordenação também pós-lista, via dinheiro, com credencial ex-ante), atribuindo a eles, com página, a tese do momento pré-lista usada no Cap. 4."
claims: [C2.4.02, C2.7.07]
```

```yaml
id: THE-2-006
titulo: "O 'núcleo priorizado' e o seu tamanho não são teorizados, e o elo com Cheibub & Sin aponta para outro tamanho"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 63
  secao: "### A segunda geração e a agência partidária"
  trecho: "com número de candidaturas competitivas próximo ao número de cadeiras em disputa pelo partido."
afirmacao_do_autor: "Frente (i): 'um núcleo priorizado definido a partir da própria distribuição de recursos em cada nominata' (L214). Expectativa: credenciados entre 'os destinatários que concentram a maior parcela de recursos' (L204)."
problema: "O conceito de 'núcleo' aparece pela primeira vez em L214 sem definição teórica. O Cap. 2 não diz por que a priorização teria a forma de um núcleo (corte) e não de um gradiente, nem de que tamanho seria. A literatura que o capítulo mobiliza sugere um tamanho: Cheibub & Sin (L63) ligam o número de competitivos às 'cadeiras em disputa pelo partido', isto é, à bancada esperada. Thomsen (L139) sugere concentração como medida de competição. O Cap. 3 adota o número efetivo (NECr) sem que o Cap. 2 escolha entre essas referências. Como o NECr mediano (1,88/4,81; Cap. 3, L90) e o número mediano de competitivos (1; Cap. 3, L86) divergem, a escolha do tamanho do núcleo é teoricamente consequente, não só técnica."
evidencia:
  tipo: ausencia
  fontes: ["tese/02-literatura.qmd:63", "tese/02-literatura.qmd:139", "tese/02-literatura.qmd:204", "tese/02-literatura.qmd:214", "tese/03-medindo-coordenacao-intrapartidaria.qmd:86", "tese/03-medindo-coordenacao-intrapartidaria.qmd:90"]
  detalhe: "'núcleo' não ocorre no Cap. 2 antes de L214. Não há frase que relacione o tamanho do grupo priorizado a cadeiras esperadas ou a concentração efetiva."
severidade: MODERATE
confianca: alta
recomendacao: "Uma frase no Argumento, sem antecipar a fórmula: o partido financia com peso relevante um número efetivo de candidaturas, e esse número é endógeno à estratégia de cada lista (Thomsen), em vez de fixado pela bancada esperada (Cheibub & Sin). Dizer que a comparação é com um núcleo de mesmo tamanho sorteado da mesma lista (o contrafactual de 'em relação ao acaso')."
claims: [C2.7.04]
```

```yaml
id: THE-2-007
titulo: "A magnitude do distrito é teorizada na literatura revisada, mas não gera expectativa, e o gradiente do Cap. 3 é interpretado post hoc"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 121
  secao: "## Competição intrapartidária e gastos de campanha"
  trecho: "na medida em que a magnitude do distrito aumenta, a qualidade da informação disponível para os atores envolvidos no processo piora."
afirmacao_do_autor: "Carey & Shugart: em listas abertas, M maior aumenta o incentivo personalista (L25). Samuels/Cox: M maior piora a informação (L121)."
problema: "O Cap. 3 reporta um gradiente monotônico: lift de 1,40→2,52 (2018) e razão de parcelas de 4,76→13,48, e interpreta que o núcleo 'se torna mais discriminante nos distritos de maior magnitude' (Cap. 3, L118). O Cap. 2 tem os ingredientes para uma previsão, mas não a faz. As duas leituras apontam em sentidos opostos: mais personalismo e menos informação sugerem alocação mais dispersa; mas, se a informação piora, o sinal observável (credencial) ganha valor relativo, o que prevê priorização mais forte em M grande, justamente o observado. Essa segunda derivação decorre diretamente do argumento de sinalização (L204: 'Quando os recursos são distribuídos, a votação ainda é incerta') e faria do gradiente um teste do mecanismo, não uma descrição."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:25", "tese/02-literatura.qmd:121", "tese/02-literatura.qmd:204", "tese/03-medindo-coordenacao-intrapartidaria.qmd:118", "tese/03-medindo-coordenacao-intrapartidaria.qmd:167"]
  detalhe: "Nenhuma frase do Argumento (L171-218) menciona magnitude. O Cap. 3 L167 afirma que 'os dois testes indicam uma priorização mais acentuada... nos distritos de maior magnitude' sem remeter a expectativa prévia."
severidade: MODERATE
confianca: alta
recomendacao: "No Argumento, derivar a implicação: se a credencial vale como sinal sob incerteza, e a incerteza cresce com M (Samuels/Cox), a priorização de credenciados deve ser mais forte em distritos grandes. Registrar a previsão rival (personalismo leva a dispersão) e o que a distinguiria."
claims: []
```

```yaml
id: THE-2-008
titulo: "A heterogeneidade organizacional (Scarrow & Webb; Fiva et al.) implica variação entre partidos que o argumento não formula e os capítulos não testam"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 93
  secao: "## Partidos como organizações heterogêneas"
  trecho: "teorizam que partidos eleitoralmente mais competitivos conseguem transitar melhor pelo *trade-off* apresentado."
afirmacao_do_autor: "A força partidária é 'uma capacidade variável de converter recursos organizacionais em coordenação' (L87); partidos mais competitivos lidam melhor com o dilema (L93)."
problema: "A seção inteira (L71-101) sustenta que a capacidade de coordenação varia entre partidos, e L93 traz uma previsão direcional de Fiva et al. O Argumento, porém, trata o partido como ator unitário e homogêneo ('A ação será sempre atribuída ao partido', L180) e não deriva nenhuma expectativa por tipo de partido. O incentivo de sobrevivência (L169) também varia: partidos grandes não estão sob ameaça da cláusula de desempenho. Nos Caps. 3 e 4 não há, no corpo, nenhuma análise por partido ou por tipo de partido (grep por 'tipo de partido', 'bancada', 'lift_partido': só em comentários). A seção 'Partidos como organizações heterogêneas' fica sem função no teste."
evidencia:
  tipo: ausencia
  fontes: ["tese/02-literatura.qmd:87", "tese/02-literatura.qmd:93", "tese/02-literatura.qmd:169", "tese/02-literatura.qmd:180", "tese/03-medindo-coordenacao-intrapartidaria.qmd"]
  detalhe: "Grep em tese/0[234]*.qmd por 'tipo de partido|bancada|Mp|lift_partido': nenhuma ocorrência no corpo dos Caps. 3 e 4."
severidade: MODERATE
confianca: alta
recomendacao: "Ou derivar no Argumento uma expectativa auxiliar (ex.: priorização mais forte em partidos sob ameaça da cláusula, ou mais fraca, conforme Fiva et al.) e testá-la no Cap. 3, ou encurtar a seção e explicitar que a tese estima um padrão médio e não explora a heterogeneidade."
claims: [C2.4.03]
```

```yaml
id: THE-2-009
titulo: "A analogia com o dilema do gatekeeper toma só o lado da proteção; o custo em esforço, núcleo do dilema, não gera implicação"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 95
  secao: "## Partidos como organizações heterogêneas"
  trecho: "argumenta-se que a distribuição discricionária de recursos de campanha dos fundos públicos aos candidatos a Deputado Federal constitui um instrumento de atribuição de vantagem competitiva a parte das candidaturas do partido"
afirmacao_do_autor: "O repasse é o equivalente brasileiro das posições de vantagem norueguesas; a alocação é 'análoga ao problema de coordenação indicado por @fivaetal2024' (L176)."
problema: "Em Fiva et al., tal como descritos em L89-91, o dilema tem dois lados: proteger alguns reduz o esforço agregado; não proteger ninguém gera fragmentação. O Argumento importa só o lado da proteção (priorizar credenciados). Não diz como o partido brasileiro resolve o custo em esforço, nem que observação revelaria esse custo. Há também uma diferença institucional relevante não discutida: a posição de vantagem norueguesa é fixada antes da campanha e é irreversível, enquanto o dinheiro é divisível, contínuo e pode ser condicionado ao longo da campanha. Isso muda a solução ótima do dilema e se liga diretamente à frente (iii) (ver THE-2-003). 'Gatekeeping' também muda de sentido: controle de acesso à lista (L19, L31), posição de vantagem (L89), desigualdade de recursos (L65, L95)."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:89", "tese/02-literatura.qmd:91", "tese/02-literatura.qmd:95", "tese/02-literatura.qmd:176"]
  detalhe: "L91: 'correm o risco de ter um desempenho eleitoral inferior devido ao desincentivo ao esforço dos candidatos não contemplados'. Nenhuma frase do Argumento retoma esse risco."
severidade: MODERATE
confianca: media
recomendacao: "Dizer como a divisibilidade do dinheiro altera o dilema (o partido pode proteger parcialmente e manter incentivo aos demais) e se isso implica algo observável (ex.: repasses residuais amplos a não credenciados, ou timing condicionado). Definir 'gatekeeping' no sentido usado pela tese."
claims: [C2.4.01]
```

```yaml
id: THE-2-010
titulo: "As cotas são tratadas como restrição, sem o sinal do viés que produzem sobre o teste"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 188
  secao: "## Argumento"
  trecho: "As cotas que garantem financiamento de candidaturas negras e de mulheres condicionam as escolhas partidárias, mas não fixam a parcela que deve ser transferida."
afirmacao_do_autor: "As cotas condicionam, mas deixam margem de priorização dentro dos grupos."
problema: "Na rival 'obrigação legal', o texto só afirma que há margem. Não diz a direção do viés: as cotas obrigam a destinar recursos a grupos com menos credenciais prévias (o rascunho do Cap. 3 registra 4,8% de mulheres com credencial contra 16,4% de homens em 2018), o que empurra recursos para fora do grupo credenciado e torna o teste de E1/E2 conservador. Dito isso, a obrigação legal deixa de ser rival e vira argumento de robustez. O Cap. 3 (L171) usa o piso legal para interpretar a razão 1,44 para mulheres, o que só é coerente se o Cap. 2 tiver estabelecido esse papel."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:188", "tese/03-medindo-coordenacao-intrapartidaria.qmd:171"]
  detalhe: "Nenhuma frase em L171-218 indica a direção do efeito das cotas sobre a associação credencial–recursos."
severidade: MINOR
confianca: alta
recomendacao: "Acrescentar uma frase: as cotas deslocam recursos para grupos com menos credenciais prévias, então a associação estimada é, se enviesada, para baixo."
claims: []
```

## Claims

```yaml
claim_id: C2.6.01
capitulo: 2
secao: "Financiamento de campanhas no Brasil"
claim: "As eleições para deputado federal são cruciais para a sobrevivência do partido; por isso os partidos têm incentivo a distribuir recursos de forma seletiva e estratégica."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 169}
evidencia: {tipo: citacao, referencia: "L159-165 (regras FEFC/FP/cláusula)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["As regras sustentam o incentivo ao desempenho; não sustentam que a seletividade tome a forma de concentração em credenciados (THE-2-002)."]
agent: theory-reviewer
```

```yaml
claim_id: C2.7.01
capitulo: 2
secao: "Argumento"
claim: "O vínculo desempenho–recursos gera incentivo à distribuição seletiva, visando o quociente partidário e a sobrevivência."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 174}
evidencia: {tipo: citacao, referencia: "L159, L163"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["As regras premiam votos; com pooling, isso é compatível com dispersão. O Cap. 4 L25 deriva o incentivo oposto para 2022."]
agent: theory-reviewer
```

```yaml
claim_id: C2.7.02
capitulo: 2
secao: "Argumento"
claim: "A alocação de recursos partidários constitui um instrumento de coordenação intrapartidária que orienta a competição para objetivos coletivos."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 176}
evidencia: {tipo: nenhuma, referencia: "Nenhuma frente de L214 testa efeito sobre competição ou desempenho coletivo"}
assessment: {status: unsupported, confidence: alta}
concerns: ["Os testes medem priorização, não coordenação (THE-2-004)."]
agent: theory-reviewer
```

```yaml
claim_id: C2.7.03
capitulo: 2
secao: "Argumento"
claim: "E1: se a distribuição busca favorecer quem contribui para o desempenho coletivo, espera-se presença desproporcional, em relação ao acaso, de credenciados entre os que concentram mais recursos."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 204}
evidencia: {tipo: figura, referencia: "Cap. 3 fig-cap3-03-top-necr (lift 1,89/1,86)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["A expectativa é implicada pelo argumento, mas também pelas rivais de L178; não é discriminante (THE-2-001)."]
agent: theory-reviewer
```

```yaml
claim_id: C2.7.04
capitulo: 2
secao: "Argumento"
claim: "Frente (i): identificar um núcleo priorizado a partir da distribuição de recursos e verificar sua composição."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 214}
evidencia: {tipo: figura, referencia: "Cap. 3 Top-NECr (L102-127)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["O conceito e o tamanho do núcleo não são derivados no Cap. 2 (THE-2-006)."]
agent: theory-reviewer
```

```yaml
claim_id: C2.7.05
capitulo: 2
secao: "Argumento"
claim: "Frente (ii): associação, desagregada por cargo, entre credenciais e parcela intralista de recursos."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 214}
evidencia: {tipo: figura, referencia: "Cap. 3 fig-reg-frac (L129-186)"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["O agregado é derivado de L204; para a desagregação por cargo não há expectativa (quais sinais pesam mais e por quê)."]
agent: theory-reviewer
```

```yaml
claim_id: C2.7.06
capitulo: 2
secao: "Argumento"
claim: "Frente (iii): priorização temporal ao núcleo priorizado da lista."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 214}
evidencia: {tipo: nenhuma, referencia: "Sem derivação em L171-218; o Cap. 4 testa credencial, não núcleo"}
assessment: {status: unsupported, confidence: alta}
concerns: ["Sem justificativa teórica (THE-2-003); a lógica de Fiva et al. pode prever retenção."]
agent: theory-reviewer
```

```yaml
claim_id: C2.7.07
capitulo: 2
secao: "Argumento"
claim: "Diferentemente de Silva & Cervi e de Cheibub & Sin, que usam o desempenho da própria eleição, a tese classifica as credenciais exclusivamente com resultados anteriores."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 212}
evidencia: {tipo: citacao, referencia: "Cap. 3 L49-53 (definição ex-ante)"}
assessment: {status: supported, confidence: media}
concerns: ["Não verifiquei as páginas citadas (p. 85, p. 79). É uma diferença de mensuração; a diferença teórica declarada no Cap. 4 L13 é outra (THE-2-005)."]
agent: theory-reviewer
```

```yaml
claim_id: C2.7.08
capitulo: 2
secao: "Argumento"
claim: "O Cap. 3 trata das frentes (i) e (ii), e o Cap. 4 da (iii)."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 218}
evidencia: {tipo: citacao, referencia: "Cap. 3 L3; Cap. 4 L17, L61"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["O Cap. 4 opera com o corte por credencial, não com o 'núcleo priorizado' anunciado em (iii)."]
agent: theory-reviewer
```

```yaml
claim_id: C2.4.01
capitulo: 2
secao: "Partidos como organizações heterogêneas"
claim: "A distribuição discricionária de recursos públicos constitui um instrumento de atribuição de vantagem competitiva a parte das candidaturas."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 95}
evidencia: {tipo: citacao, referencia: "@silvacodato2024 (desigualdade)"}
assessment: {status: partially_supported, confidence: media}
concerns: ["A desigualdade é sustentada pela citação; a 'vantagem competitiva' (efeito sobre a disputa) não é testada na tese."]
agent: theory-reviewer
```

```yaml
claim_id: C2.4.02
capitulo: 2
secao: "Partidos como organizações heterogêneas"
claim: "No Brasil, o gatekeeping ocorre também depois da definição das nominatas."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 95}
evidencia: {tipo: citacao, referencia: "@janusz_barreiro_cintron_2021 (L65)"}
assessment: {status: supported, confidence: media}
concerns: ["Sustentada pela literatura citada. Por isso mesmo não é contribuição original, e o texto não delimita o que a tese acrescenta (THE-2-005)."]
agent: theory-reviewer
```

```yaml
claim_id: C2.4.03
capitulo: 2
secao: "Partidos como organizações heterogêneas"
claim: "Partidos eleitoralmente mais competitivos transitam melhor pelo trade-off do gatekeeper (Fiva et al.)."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 93}
evidencia: {tipo: nenhuma, referencia: "Sem teste nos Caps. 3/4"}
assessment: {status: unverifiable, confidence: alta}
concerns: ["É implicação da literatura adotada, mas não é formulada como expectativa nem testada (THE-2-008)."]
agent: theory-reviewer
```

## Verificações que passaram
- E1 (sobrerrepresentação relativa ao acaso) decorre de L204 e tem o contrafactual explícito ("em relação ao acaso"), coerente com a referência aleatória do Cap. 3 (L69, L108-110).
- O princípio ex-ante (L212) é aplicado de forma consistente na definição de credencial do Cap. 3 (L49-53). A equivalência credencial = competitivo é declarada no Cap. 3 (nota 1), o que resolve parte da ambiguidade terminológica do Cap. 2.
- A atribuição da ação ao partido (L180) é justificada por observabilidade e por centralização decisória com base em citação (Ribeiro; Guarnieri). Como escolha de unidade de análise, é defensável; o problema está só na tensão com L178 e L87 (THE-2-001, THE-2-008).
- O Cap. 3 declara testar "a dimensão distributiva do argumento" (L3), o que corresponde às frentes (i) e (ii) de L214.

## Limites desta revisão
- Não li as obras citadas. As críticas sobre Fiva et al., Janusz et al. e Cheibub & Sin avaliam só a coerência entre o que o Cap. 2 diz delas e o uso posterior. Em especial, a confiança "media" de THE-2-005 depende de a obra de Janusz et al. cobrir ou não o período sob FEFC.
- Os comentários HTML nos `.qmd` (roteiros [A0]–[A10] e os rascunhos de discussão gerados por IA) não foram tratados como texto do autor. Alguns achados coincidem com pontos já anotados neles ([A2], [A5], [A7], [A9], [2.2-3]); os achados aqui foram derivados e ancorados no corpo do texto.
- O Cap. 4 foi lido parcialmente (introdução, primeira seção, Discussão proposta); seções intermediárias foram consultadas por grep.
- Nenhuma recomputação: o contrato exclui mensuração e estatística.
