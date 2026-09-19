# writing-reviewer — Capítulo 2 — run-003

## Escopo e método
- Arquivos lidos: `CLAUDE.md`, `thesis-review/PROTOCOL.md`, `thesis-review/rubric.yaml`, `thesis-review/templates/agent_report.md`, `thesis-review/runs/run-003/issues_draft.yaml` (lido antes da revisão, como pedido), `tese/02-literatura.qmd` (integral, L1–219), `tese/_quarto.yml` (ordem dos capítulos, CSL ABNT).
- Checagens de Quarto: rótulos `{#sec-...}` em `tese/*.qmd` (grep), referências `@sec-` de/para o Cap. 2 e presença no `references.bib` das 51 chaves citadas no capítulo (grep, 51/51 encontradas). Nenhum script foi necessário, e nada foi salvo em `evidence/`.
- Não foi possível verificar: a renderização efetiva (não rodei `quarto render`) e se o CSL ABNT exige tradução das citações em inglês na configuração atual.
- Não li relatórios de outros agentes. O `issues_draft.yaml` condena, no todo ou em parte, as L33, L51, L57 (Braga & Amaral), L59, L65–67, L77, L89–95, L97, L101 (localizador), L147, L151 e toda a seção Argumento (L174–218). Não polí essas passagens. Elas aparecem abaixo em "Passagens aguardando correção substantiva", só com o registro. As exceções são WRI-2-002 e WRI-2-004, que tratam de lugar e ordem (estrutura), não de redação, e ficam explicitamente condicionadas à reescrita.

## Avaliação macro
No escopo de redação, a sequência das seções é legível: cânone → segunda geração → partidos como organizações → gastos de campanha → financiamento → Argumento. Cada seção termina com uma frase-ponte para a seguinte (L69, L103, L129, L169). Há três problemas de estrutura.

1. O capítulo começa direto na primeira seção. O único parágrafo de propósito (L9) promete um argumento sobre a literatura ("a segunda geração [...] contesta o argumento canônico"), e o capítulo fecha com outra coisa: o argumento da tese e três frentes empíricas. Falta um roteiro que anuncie o fechamento (WRI-2-001).
2. O bloco de Fiva et al. e a primeira formulação da tese (L89–95) ficam no meio da seção sobre heterogeneidade organizacional. Com isso, o fio Scarrow & Webb → Guarnieri/Ribeiro se interrompe, e a L176 retoma o mesmo bloco (WRI-2-002).
3. No Argumento, a tese só é enunciada no sétimo de nove parágrafos (L204), depois de digressões sobre atribuição da ação, cotas e literatura já revista (WRI-2-004). O comentário [A0] do próprio autor (L172) diagnostica o mesmo.

No nível micro, os problemas são polimento. Há uma concentração de erros de concordância, crase e regência nas seções 1–5, uma frase sem sujeito (L129), uma ponte sem referente (L103) e citações em inglês sem tradução. Nada aqui bloqueia a leitura, e nenhum achado passa de MODERATE.

## Achados

```yaml
id: WRI-2-001
titulo: "O capítulo não tem abertura que anuncie seu percurso e seu fechamento (Argumento e frentes empíricas)"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 9
  secao: "## Primeira e segunda gerações de estudos sobre os efeitos do voto preferencial"
  trecho: "Neste capítulo da tese, argumenta-se que a segunda geração e os estudos recentes sobre o tema contestam o argumento canônico ao deslocar o foco da agência desta conversa."
afirmacao_do_autor: "O capítulo argumenta que a segunda geração desloca o foco para a agência partidária."
problema: "O capítulo abre direto em uma seção (L5). A L7 fala da 'primeira seção', e a L9 dá o propósito do capítulo inteiro, mas só em termos de revisão de literatura. O leitor não sabe que o capítulo passa por organização partidária, gastos, regras de financiamento e termina no argumento da tese (@sec-argumento), que os Caps. 3 e 4 citam como fonte das hipóteses. Abertura e fechamento não se correspondem."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:5-9", "tese/02-literatura.qmd:171", "tese/03-medindo-coordenacao-intrapartidaria.qmd:3", "tese/04-mecanismo-causal-coordenacao.qmd:17"]
  detalhe: "Não há texto entre o título do capítulo (L2) e o primeiro '##' (L5). Os Caps. 3 e 4 remetem à @sec-argumento como origem das frentes testadas."
severidade: MODERATE
confianca: alta
recomendacao: "Antes do primeiro '##', inserir um parágrafo de roteiro que diga que o capítulo percorre as duas gerações, a organização partidária, os gastos e o financiamento, e termina no argumento da tese. Exemplo mínimo: 'O capítulo termina com o argumento da tese e as frentes empíricas testadas nos capítulos seguintes (@sec-argumento).'"
claims: [C2.1.50]
```

```yaml
id: WRI-2-002
titulo: "O bloco de Fiva et al. e a primeira formulação da tese (L89–95) interrompem a seção sobre heterogeneidade organizacional"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 95
  secao: "## Partidos como organizações heterogêneas"
  trecho: "No caso brasileiro que é foco desta tese, argumenta-se que a distribuição discricionária de recursos de campanha dos fundos públicos aos candidatos a Deputado Federal constitui um instrumento de atribuição de vantagem competitiva"
afirmacao_do_autor: "A seção trata da capacidade organizacional variável dos partidos."
problema: "A seção segue Scarrow & Webb (L81–87) → Fiva et al. e a tese (L89–95) → de volta à organização brasileira, com Guarnieri, Tavits e Ribeiro (L97–101). O bloco L89–95 trata de alocação intralista e anuncia o argumento da tese. A L176 retoma o mesmo bloco ('Ainda aproveitando o vocabulário dos autores'). O fio organizacional se interrompe, e a ideia central é aberta duas vezes, em seções diferentes."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:81-101", "tese/02-literatura.qmd:176"]
  detalhe: "A L97 ('A capacidade organizacional dos partidos brasileiros...') retoma a L87 depois de três parágrafos sobre a Noruega e um sobre a tese."
severidade: MODERATE
confianca: media
recomendacao: "Decidir o lugar do bloco: ou L97–101 vêm antes de L89, ou L89–95 passam para o Argumento, junto da L176. A redação de L89–95 aguarda I-2-004, I-2-013 e I-2-018. Este achado trata só de posição."
relacionados: [I-2-004, I-2-013, I-2-018]
claims: []
```

```yaml
id: WRI-2-003
titulo: "A frase-ponte da L103 não tem referente ('deste tipo de competição', 'tais sistemas')"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 103
  secao: "## Partidos como organizações heterogêneas"
  trecho: "Os estudos discutidos na próxima seção se debruçam sobre os efeitos deste tipo de competição sobre os gastos de campanha realizado por candidatos. De maneira geral, os estudos verificam se tais sistemas estão vinculados a gastos maiores"
afirmacao_do_autor: "Transição para a seção de gastos."
problema: "O parágrafo anterior (L101) trata da resource-based view e das organizações partidárias. Não há 'tipo de competição' nem 'sistemas' a retomar, e o referente está a mais de 30 linhas (L73). Há também um erro de concordância: 'gastos [...] realizado'."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:101-103"]
  detalhe: "'deste tipo de competição' e 'tais sistemas' não têm antecedente em L99–101."
severidade: MODERATE
confianca: alta
recomendacao: "Nomear o referente e corrigir a concordância. Exemplo: 'A próxima seção discute os efeitos da competição intrapartidária em listas abertas sobre os gastos realizados pelas candidaturas.'"
claims: [C2.4.50]
```

```yaml
id: WRI-2-004
titulo: "Argumento: a tese só é enunciada no sétimo de nove parágrafos"
escala: macro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 204
  secao: "## Argumento {#sec-argumento}"
  trecho: "O argumento desta tese é que os partidos priorizam financeiramente candidaturas com credenciais eleitorais prévias porque estas constituem sinais da capacidade destes candidatos em contribuir para o desempenho coletivo da legenda."
afirmacao_do_autor: "A seção apresenta o argumento da tese."
problema: "Ordem atual: incentivo (L174), analogia com Fiva (L176), rivais (L178), atribuição da ação (L180), cotas (L188), Silva & Codato (L196), Cheibub & Sin e Janusz (L202, literatura já revista em L63/L65), tese (L204), ex-ante (L212), frentes (L214). As rivais e as ressalvas (L178, L188) aparecem antes do que ressalvam. O autor faz o mesmo diagnóstico no comentário [A0] (L172: 'a ideia central é aberta três vezes')."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:172-218"]
  detalhe: "A frase-tese está no 7º parágrafo de texto da seção. L196 repete L95 (desigualdade, Silva & Codato). L202 repete L63 e L65 (Cheibub & Sin; resource gatekeeping)."
severidade: MODERATE
confianca: alta
recomendacao: "Aplicar só na reescrita substantiva (I-2-001 a I-2-008), porque todo o conteúdo da seção está sob revisão. Enunciar a tese logo depois do incentivo (L174), levar as rivais e as ressalvas (L178, L180, L188) para depois das implicações observáveis e retirar as reapresentações de literatura (L196, L202)."
relacionados: [I-2-001, I-2-002, I-2-004, I-2-008]
claims: [C2.7.50]
```

```yaml
id: WRI-2-005
titulo: "L129: frase sem sujeito e adjetivo em função adverbial"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 129
  secao: "## Competição intrapartidária e gastos de campanha"
  trecho: "Por este motivo, na próxima seção discute a literatura sobre financiamento político no Brasil."
afirmacao_do_autor: "Transição para Financiamento."
problema: "'discute' não tem sujeito. Na mesma linha, 'Diferente da literatura que evidencia...' usa adjetivo onde cabe advérbio ('Diferentemente')."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:129"]
  detalhe: "Trecho literal acima; início da linha: 'Diferente da literatura que evidencia os efeitos da competição intrapartidária sobre os gastos de campanha'."
severidade: MINOR
confianca: alta
recomendacao: "'Por este motivo, a próxima seção discute a literatura sobre financiamento político no Brasil.' e 'Diferentemente da literatura...'."
claims: [C2.5.50]
```

```yaml
id: WRI-2-006
titulo: "Erros de concordância (L7, L45, L47, L91, L101, L109)"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 47
  secao: "### A segunda geração e a agência partidária"
  trecho: "Nuances à cadeia causal entre regras eleitorais, incentivos e comportamento foram levantados por @marsh1985"
afirmacao_do_autor: "—"
problema: "Concordância nominal e verbal em seis pontos."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:7", "tese/02-literatura.qmd:45", "tese/02-literatura.qmd:47", "tese/02-literatura.qmd:91", "tese/02-literatura.qmd:101", "tese/02-literatura.qmd:109"]
  detalhe: "L7 'gera consequências nas arenas eleitorais e legislativas, que acaba por afetar' (consequências → acabam). L45 'o contexto social, econômico e político moldam' (→ molda). L47 'Nuances [...] foram levantados' (→ levantadas); 'a ativação do voto preferencial e suas consequências personalistas depende' (→ dependem). L91 'Do outro lado, ao não privilegiar ninguém, corre o risco' (o sujeito implícito são os partidos → correm). L101 'O mesmo é observado em @ribeiroetal2022, que contesta' (a frase seguinte diz 'os autores' → contestam). L109 'candidaturas podem se destacar [...] por ser adepto de um sub-grupo' (→ adeptas; 'subgrupo', sem hífen)."
severidade: MINOR
confianca: alta
recomendacao: "Corrigir as formas indicadas em 'detalhe'. As L7 e L45 estão em passagens tocadas por I-2-017, mas só na atribuição das citações. A correção gramatical independe disso."
claims: []
```

```yaml
id: WRI-2-007
titulo: "Crase ausente (L17, L57, L75)"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 17
  secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
  trecho: "estimar o valor relativo da reputação pessoal frente a reputação partidária"
afirmacao_do_autor: "—"
problema: "Falta crase antes de substantivo feminino determinado."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:17", "tese/02-literatura.qmd:57", "tese/02-literatura.qmd:75"]
  detalhe: "L17 'frente a reputação partidária' → 'frente à'. L57 'Ainda com relação a arena eleitoral' → 'à arena'; 'os recursos que serviam a patronagem estatal' → 'à patronagem'. L75 'abrir mão de autonomia frente a organização partidária' → 'frente à'."
severidade: MINOR
confianca: alta
recomendacao: "Acrescentar a crase nos quatro pontos."
claims: []
```

```yaml
id: WRI-2-008
titulo: "Regência e uso de 'onde' (L15, L23, L31, L49, L57, L99, L117)"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 99
  secao: "## Partidos como organizações heterogêneas"
  trecho: "verificando o grau que as bases e instâncias inferiores do partido participam do processo decisório interno"
afirmacao_do_autor: "—"
problema: "Regência verbal e nominal inadequada, e 'onde' com antecedente não locativo."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:15", "tese/02-literatura.qmd:23", "tese/02-literatura.qmd:31", "tese/02-literatura.qmd:49", "tese/02-literatura.qmd:57", "tese/02-literatura.qmd:99", "tese/02-literatura.qmd:117"]
  detalhe: "L15 'da organização que pertence' → 'à qual pertence'. L23 'há o caso intermediário onde ocorre' → 'em que ocorre'. L31 'Ao aplicar para o caso brasileiro' → 'ao caso'. L49 'agir em desacordo aos incentivos' → 'em desacordo com'. L57 'o controle partidário ao acesso' → 'sobre o acesso'. L99 'o grau que as bases [...] participam' → 'o grau em que'. L117 'Encontram evidências que o aumento' → 'evidências de que'."
severidade: MINOR
confianca: alta
recomendacao: "Aplicar as formas indicadas."
claims: []
```

```yaml
id: WRI-2-009
titulo: "L13: oração que admite duas leituras e primeira pessoa do plural isolada"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 13
  secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
  trecho: "Como os candidatos de um mesmo partido não são iguais, quais candidaturas correligionárias são eleitas ou não têm efeitos de curto e longo prazos sobre o poder, atuação e a própria sobrevivência dos partidos políticos."
afirmacao_do_autor: "—"
problema: "(a) A oração interrogativa indireta usada como sujeito se lê como 'são eleitas ou não têm efeitos', o que inverte o sentido. (b) Na mesma linha, 'no caso de assumirmos partidos políticos' é o único uso da 1ª pessoa do plural no capítulo. No resto, o capítulo usa o impessoal ('argumenta-se', L9, L77, L95, L169; 'considera-se', L33)."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:13", "tese/02-literatura.qmd:9", "tese/02-literatura.qmd:33"]
  detalhe: "Não há outra ocorrência de 1ª pessoa do plural no capítulo."
severidade: MINOR
confianca: alta
recomendacao: "(a) 'Saber quais candidaturas são eleitas tem efeitos...'. (b) 'no caso de se assumirem partidos...' ou 'se os partidos forem tomados como...'."
claims: []
```

```yaml
id: WRI-2-010
titulo: "Redundância: 'candidaturas que o partido permitiu' repetida em L19, L31 (duas vezes) e L95"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 31
  secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
  trecho: "A competição intrapartidária ocorre entre candidaturas que o partido *permitiu* disputar. Há, em listas abertas, um controle da legenda na entrada de candidaturas, mas não sobre a ordenação final de sua lista."
afirmacao_do_autor: "O Brasil está no nível intermediário quanto ao controle de acesso."
problema: "As duas frases repetem a anterior ('devem aprovar suas candidaturas em convenção [...] mas não controlam a ordenação final'), que já repetia a L19 ('entre candidatos que o partido *permitiu* acessar'). A ideia volta pela quarta vez na L95."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:19", "tese/02-literatura.qmd:31", "tese/02-literatura.qmd:95"]
  detalhe: "Quatro ocorrências da mesma ideia, três delas com o mesmo *permitiu* em itálico."
severidade: MINOR
confianca: alta
recomendacao: "Na L31, manter uma das duas frases citadas e seguir direto para 'Este fator é o que abre espaço...'."
claims: []
```

```yaml
id: WRI-2-011
titulo: "Transição abrupta L141→L143 e oração relativa sem vírgula na L143"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 143
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "Até o STF julgar como procedente a ADI 4650 que proibiu doações de pessoas jurídicas, as empresas podiam destinar às campanhas recursos correspondentes a até 2% de seu faturamento bruto no ano anterior à eleição."
afirmacao_do_autor: "Contexto pré-2015."
problema: "A L141, paragrafo de uma frase, fecha o bloco sobre Thomsen. A L143 passa para a história institucional sem ligação. A oração 'que proibiu' atribui a proibição à ação (ADI), não ao julgamento, e falta vírgula na relativa explicativa. 'julgar como procedente' tem regência inadequada."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:139-143"]
  detalhe: "O tema muda de 'papel do dinheiro na capacidade competitiva' (L141) para 'ADI 4650' (L143) sem frase de passagem."
severidade: MINOR
confianca: alta
recomendacao: "Abrir a L143 com uma ponte e ajustar a oração. Exemplo: 'Até o STF julgar procedente a ADI 4650, em 2015, e proibir doações de pessoas jurídicas, ...'. A falta de fonte (I-2-011) fica com o literature."
relacionados: [I-2-011]
claims: []
```

```yaml
id: WRI-2-012
titulo: "L145: 'Alguns estudos estudaram' (plural com uma só obra citada) e verbos repetidos"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 145
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "Alguns estudos estudaram estes recursos empresariais que são intermediados pelas legendas. @silvacervi2017 mostram que em 2014"
afirmacao_do_autor: "—"
problema: "Há uma redundância lexical ('estudos estudaram'). O texto anuncia 'alguns estudos' e cita apenas @silvacervi2017. A série 'mostram / mostram / evidenciam / apontam' (L145–147) já está marcada pelo autor no comentário da L149."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:145-149"]
  detalhe: "Uma única citação no parágrafo. Comentário do autor na L149: 'mostram, mostram, apontam, mostram...'."
severidade: MINOR
confianca: alta
recomendacao: "'@silvacervi2017 examinam os recursos empresariais intermediados pelas legendas e mostram que...'. A L147 está condenada (I-2-012) e não foi polida."
claims: []
```

```yaml
id: WRI-2-013
titulo: "L153: aposto 'Já vigente' sem núcleo"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 153
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "Já vigente nas eleições municipais de 2016, é a partir das eleições de 2018 que candidaturas a deputado federal não podem receber recursos de pessoas jurídicas."
afirmacao_do_autor: "—"
problema: "'Já vigente' modifica um substantivo que não aparece (a proibição). A frase também sugere que a proibição começa em 2018 para deputados, quando ela vale desde 2015/2016 e 2018 é apenas a primeira eleição geral sob a regra."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:153"]
  detalhe: "A frase não tem sujeito expresso a que o particípio 'vigente' se ligue."
severidade: MINOR
confianca: alta
recomendacao: "'A proibição, já vigente nas eleições municipais de 2016, alcança as candidaturas a deputado federal pela primeira vez em 2018.'"
claims: []
```

```yaml
id: WRI-2-014
titulo: "L155: parênteses aninhados com referência normativa em lugar de citação"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 155
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "Decisões posteriores (STF ADI 5617 e consulta ao TSE (2018) para mulheres; consulta ao TSE (2020) e ADPF 738 para candidaturas negras; EC 117/2022) limitaram tal autonomia"
afirmacao_do_autor: "—"
problema: "Os parênteses dentro de parênteses interrompem o período. A lista de atos normativos fica no meio da frase, e os anos entre parênteses imitam uma citação autor-data sem serem uma."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:155"]
  detalhe: "Dois níveis de parênteses e quatro atos normativos no sujeito da frase."
severidade: MINOR
confianca: alta
recomendacao: "Levar a lista para uma nota de rodapé ou desdobrá-la em duas frases (mulheres; pessoas negras), com as fontes que I-2-011 pede."
relacionados: [I-2-011]
claims: []
```

```yaml
id: WRI-2-015
titulo: "Citações diretas em inglês sem tradução nem nota (L85, L127)"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 127
  secao: "## Competição intrapartidária e gastos de campanha"
  trecho: "\"incentives for Brazilian candidates to worry first and foremost about beating out their list-mates for a seat; obtaining more votes than other parties' candidates becomes a secondary concern\""
afirmacao_do_autor: "—"
problema: "O capítulo, em pt-BR, com CSL ABNT, traz duas citações diretas em inglês, a da L127 e o bloco de Scarrow & Webb (L85), sem tradução no texto nem nota com o original. Pela NBR 10520, a citação traduzida leva 'tradução nossa'. A opção de manter o original, se for essa, precisa ser uniforme e declarada."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:85", "tese/02-literatura.qmd:127", "tese/_quarto.yml:18"]
  detalhe: "`csl: associacao-brasileira-de-normas-tecnicas.csl`. Nenhuma das duas citações tem nota."
severidade: MINOR
confianca: media
recomendacao: "Definir uma política única para a tese: traduzir no corpo com '[tradução nossa]' e o original em nota, ou manter o original com a tradução em nota. Aplicar às L85 e L127."
claims: []
```

```yaml
id: WRI-2-016
titulo: "A seção Financiamento não tem rótulo, e o Cap. 3 remete a ela em texto plano"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 131
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "## Financiamento de campanhas no Brasil"
afirmacao_do_autor: "—"
problema: "No capítulo, só o Argumento tem rótulo (`{#sec-argumento}`, L171). A nota N5 do Cap. 3 (L270) registra que a menção à cláusula de desempenho remete ao 'capítulo anterior' em texto plano por falta de rótulo. O capítulo em si também não tem rótulo, mas os Caps. 3 e 4 têm (`#sec-cap3`, `#sec-cap4`)."
evidencia:
  tipo: ausencia
  fontes: ["tese/02-literatura.qmd:1-3", "tese/02-literatura.qmd:131", "tese/03-medindo-coordenacao-intrapartidaria.qmd:270"]
  detalhe: "Grep de '{#sec-' no Cap. 2: só `sec-argumento`. Cap. 3 L1 `{#sec-cap3}`; Cap. 4 L1 `{#sec-cap4}`."
severidade: MINOR
confianca: alta
recomendacao: "Adicionar `{#sec-financiamento}` à L131 e, por simetria, um rótulo de capítulo (por exemplo, `# Controle partidário sob listas abertas {#sec-cap2}` no lugar do title YAML). Depois, trocar o texto plano do Cap. 3 por referência cruzada."
claims: []
```

```yaml
id: WRI-2-017
titulo: "Expressões vagas ou coloquiais em frases de enquadramento (L9, L69, L113, L169)"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 9
  secao: "## Primeira e segunda gerações de estudos sobre os efeitos do voto preferencial"
  trecho: "contestam o argumento canônico ao deslocar o foco da agência desta conversa"
afirmacao_do_autor: "—"
problema: "'o foco da agência desta conversa' é ambíguo (desloca o foco para a agência? a agência de quem?), e 'conversa' é coloquial. Casos semelhantes: L69 'o que se espera de um partido organizacionalmente'; L113 'Agora, caso tais posições...' (marcador oral); L169 'Sob este contexto' (a forma usual é 'nesse contexto')."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:9", "tese/02-literatura.qmd:69", "tese/02-literatura.qmd:113", "tese/02-literatura.qmd:169"]
  detalhe: "Trechos literais: L69 'vale delinear o argumento sobre o que se espera de um partido organizacionalmente'; L113 'Agora, caso tais posições não permitam distinguir'; L169 'Sob este contexto, argumenta-se'."
severidade: MINOR
confianca: alta
recomendacao: "L9: '...ao deslocar o foco dos incentivos individuais para a agência partidária'. L113: 'Se, porém, tais posições...'. L169: 'Nesse contexto'."
claims: []
```

```yaml
id: WRI-2-018
titulo: "L7: período longo com gerúndio e coordenação ambígua ('benefícios particularistas para eleitores e corrupção')"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 7
  secao: "## Primeira e segunda gerações de estudos sobre os efeitos do voto preferencial"
  trecho: "consequentemente tornando a atuação de políticos focada em distribuição de benefícios particularistas para eleitores e corrupção"
afirmacao_do_autor: "Síntese do cânone."
problema: "O gerúndio encadeia uma terceira consequência ao período. 'e corrupção' pode ser lido como segundo destinatário ('para eleitores e [para a] corrupção'). Na mesma linha, 'efeitos do voto preferencial sobre a organização' vem logo depois de 'estudos sobre', e 'sobre' se repete."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:7"]
  detalhe: "'posicionar as duas gerações de estudos sobre os efeitos do voto preferencial sobre a organização e atuação dos partidos'."
severidade: MINOR
confianca: alta
recomendacao: "Partir o período: '...enfraquecem os partidos como organizações e como time legislativo. A atuação dos políticos passaria a se orientar para benefícios particularistas e para a corrupção.'"
claims: []
```

```yaml
id: WRI-2-019
titulo: "Anglicismo 'insular' (L89)"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 89
  secao: "## Partidos como organizações heterogêneas"
  trecho: "dando ao partido a possibilidade de insular candidaturas específicas da competição intrapartidária"
afirmacao_do_autor: "—"
problema: "'insular' como verbo transitivo ('isolar de') é decalque de 'to insulate'. Na mesma linha, 'posições de vantagens' não concorda com a forma 'posições de vantagem', usada no resto do texto."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:89"]
  detalhe: "'Atribuir posições de vantagens a candidaturas específicas' × 'posições de vantagem' (L89, L95)."
severidade: MINOR
confianca: alta
recomendacao: "'blindar' ou 'proteger candidaturas específicas da competição intrapartidária'; 'posições de vantagem'. O localizador 'p. 100' da mesma linha fica com I-2-018."
relacionados: [I-2-018]
claims: []
```

```yaml
id: WRI-2-020
titulo: "L109: oração subordinada isolada como período"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 109
  secao: "## Competição intrapartidária e gastos de campanha"
  trecho: "Já que candidatos seriam diferenciáveis aos olhos dos eleitores justamente por seu posicionamento em determinados assuntos."
afirmacao_do_autor: "—"
problema: "O período começa com conjunção causal e não tem oração principal."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:109"]
  detalhe: "Fragmento separado por ponto da frase anterior."
severidade: MINOR
confianca: alta
recomendacao: "Unir à frase anterior com vírgula: '...causados pela competição intralista, já que candidatos seriam...'."
claims: []
```

```yaml
id: WRI-2-021
titulo: "L161 e L121: ordem e construção que dificultam a leitura"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 161
  secao: "## Financiamento de campanhas no Brasil"
  trecho: "Estas regras concentram no desempenho partidário nas eleições para a Câmara a distribuição de 83% dos valores do FEFC."
afirmacao_do_autor: "—"
problema: "L161: o objeto direto ('a distribuição de 83%') vem depois de um adjunto longo. Na mesma linha, 'eleitos em 2014 mas em meio de mandato' tem locução imprópria. L121: 'possuem pouca informação sobre suas próprias chances de vitória, e de seus concorrentes internos e externos': a vírgula e a elipse deixam o segundo termo solto."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:161", "tese/02-literatura.qmd:121"]
  detalhe: "Trechos literais citados."
severidade: MINOR
confianca: alta
recomendacao: "L161: 'Por essas regras, 83% do FEFC são distribuídos conforme o desempenho partidário na Câmara.'; '...eleitos em 2014, ainda em meio ao mandato'. L121: '...sobre as próprias chances de vitória e sobre as dos concorrentes internos e externos'."
claims: []
```

```yaml
id: WRI-2-022
titulo: "Hífen em 'pós-Constituição' e cargo com maiúscula inconsistente"
escala: micro
localizacao:
  arquivo: tese/02-literatura.qmd
  linha: 39
  secao: "### O cânone sobre os incentivos para cultivar o voto pessoal"
  trecho: "Este componente justificaria a instabilidade política dos primeiros anos pós Constituição de 1988"
afirmacao_do_autor: "—"
problema: "'pós' prefixal pede hífen ('pós-Constituição'). O cargo aparece como 'Deputado Federal'/'Prefeito' (L55, L95) e como 'deputado federal' (L145, L153, L163, L165, L169). As L37 e L39 também começam com o mesmo 'Esta combinação'."
evidencia:
  tipo: textual
  fontes: ["tese/02-literatura.qmd:37", "tese/02-literatura.qmd:39", "tese/02-literatura.qmd:55", "tese/02-literatura.qmd:95", "tese/02-literatura.qmd:145"]
  detalhe: "L55 'para Deputado Federal e para Prefeito'; L145 'candidaturas a deputado federal'."
severidade: MINOR
confianca: alta
recomendacao: "'pós-Constituição de 1988'; padronizar em minúscula ('deputado federal', 'prefeito'); variar a abertura da L39 ('Esse arranjo embasou...')."
claims: []
```

## Claims

Os ids usam seq ≥ 50 para não colidir com os ids canônicos do chair (conflicts.md §2). Registram só afirmações de estrutura e remissão do próprio texto.

```yaml
claim_id: C2.1.50
capitulo: 2
secao: "## Primeira e segunda gerações de estudos sobre os efeitos do voto preferencial"
claim: "Neste capítulo, argumenta-se que a segunda geração contesta o argumento canônico ao deslocar o foco para a agência partidária (propósito declarado do capítulo)."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 9}
evidencia: {tipo: nenhuma, referencia: "Estrutura do capítulo, L5-218"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["As seções 1-3 cumprem o propósito. As seções Financiamento e Argumento vão além dele, e a abertura não as anuncia (WRI-2-001)."]
agent: writing-reviewer
```

```yaml
claim_id: C2.4.50
capitulo: 2
secao: "## Partidos como organizações heterogêneas"
claim: "Os estudos discutidos na próxima seção tratam dos efeitos da competição intrapartidária sobre os gastos de campanha."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 103}
evidencia: {tipo: nenhuma, referencia: "tese/02-literatura.qmd:105-127"}
assessment: {status: supported, confidence: alta}
concerns: ["O conteúdo anunciado bate com a seção seguinte, mas a frase não tem referente (WRI-2-003)."]
agent: writing-reviewer
```

```yaml
claim_id: C2.5.50
capitulo: 2
secao: "## Competição intrapartidária e gastos de campanha"
claim: "A próxima seção discute a literatura sobre financiamento político no Brasil."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 129}
evidencia: {tipo: nenhuma, referencia: "tese/02-literatura.qmd:131-169"}
assessment: {status: supported, confidence: alta}
concerns: ["Frase sem sujeito (WRI-2-005)."]
agent: writing-reviewer
```

```yaml
claim_id: C2.7.50
capitulo: 2
secao: "## Argumento {#sec-argumento}"
claim: "Estas frentes estão distribuídas nos próximos dois capítulos: o @sec-cap3 trata de (i) e (ii), e o @sec-cap4 de (iii)."
localizacao: {arquivo: "tese/02-literatura.qmd", linha: 218}
evidencia: {tipo: nenhuma, referencia: "tese/03-medindo-coordenacao-intrapartidaria.qmd:1; tese/04-mecanismo-causal-coordenacao.qmd:1,17"}
assessment: {status: supported, confidence: alta}
concerns: ["Os rótulos existem e o Cap. 4 L17 remete de volta à @sec-argumento. A correspondência de conteúdo da frente (iii) é tratada em I-2-003, fora do meu escopo."]
agent: writing-reviewer
```

## Passagens aguardando correção substantiva (não polidas)
- L33 (classificação do pooling): aguarda I-2-014. O comentário [2.1-4] do autor já pede a frase declarativa.
- L45, e L7 na atribuição: aguardam I-2-017. As correções de concordância de WRI-2-006 independem disso.
- L51 (Desposato): aguarda I-2-016.
- L57, última frase (Braga & Amaral), e L59 (Kselman, possível deslocamento): aguardam I-2-021.
- L65–67 (gatekeeping pós-convenção): aguardam I-2-013 e I-2-015. Há também redundância com L202 (resource gatekeeping reapresentado).
- L77 (Cox & McCubbins, "recursos escassos"): aguarda I-2-021.
- L89–95: aguardam I-2-004, I-2-013 e I-2-018. A L93 tem construção truncada ("gerando os incentivos que faltam aos partidos menos competitivos estimularem"), a corrigir na reescrita. A posição do bloco está em WRI-2-002.
- L97 (Tavits): aguarda I-2-021. A sintaxe está truncada ("em análise comparada das organizações partidárias surgidas em nações pós-soviéticas do funcionamento das *inactive branches*").
- L101 (localizador "(p.2)"): já coberto por I-2-022.
- L147 ("não ocorre"): aguarda I-2-012. Há vírgula entre sujeito e verbo ("os dados de 2018 e 2022, refletem").
- L151 (Janusz et al., período ambíguo pela posição logo depois do bloco pré-2015): aguarda I-2-005.
- L174–218 (Argumento, inteiro): aguarda I-2-001 a I-2-010 e I-2-020. Na reescrita, conferir: L212 "adapta os critérios de @cheibubsin2020 (definido em @sec-competitivos)", em que 'definido' não concorda com 'critérios'; "*ex-ante*" com hífen e itálico, forma ainda não decidida segundo a nota N1 do Cap. 3; L196 repete L95 (Silva & Codato); L202 repete L63 e L65. A ordem da seção está em WRI-2-004.

## Verificações que passaram
- As 51 chaves `@...` citadas no capítulo existem em `tese/references.bib` (grep com alternação: 51 ocorrências).
- As referências cruzadas `@sec-competitivos`, `@sec-cap3` e `@sec-cap4` resolvem (Cap. 3 L1 e L45; Cap. 4 L1). `@sec-argumento` é usada pelos Caps. 3 (L3) e 4 (L17).
- Formato de citação: `[-@key, p. N]` (L127), `Ribeiro [-@...]` (L99), `@key [p. N]` (L212) e `[@a; @b]` estão corretos em Pandoc.
- Itálico em estrangeirismos consistente: *pooling*, *pork*, *coattail*, *gatekeeping*, *resource gatekeeping*, *trade-off*, *resource-based view*, *inactive branches*.
- Notação: o capítulo só usa $t$, $t+4$ e $t+8$ (L165), de forma consistente. Não há figuras, tabelas nem equações numeradas.
- As pontes entre seções existem (L69, L103, L129, L169) e anunciam corretamente a seção seguinte. O problema da L103 é só de referente.

## Limites desta revisão
- Não renderizei o livro. Por isso não confirmei como `@sec-cap3` aparece em pt-BR ("Capítulo 3") nem se os comentários HTML deixam algum resíduo no PDF/DOCX.
- A exigência de tradução (WRI-2-015) depende da norma que o programa adota. Confiança média.
- Não avaliei mérito, atribuição de obras nem números (fora do escopo). As passagens condenadas no `issues_draft.yaml` não foram polidas.
