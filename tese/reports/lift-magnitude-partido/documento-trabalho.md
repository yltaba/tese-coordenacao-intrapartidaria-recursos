# Lift do Top-NECr por magnitude e por partido — documento de trabalho

**Status: análise exploratória, não oficial. Não altera `tese/03-medindo-coordenacao-intrapartidaria.qmd`.**

Fonte: `base_lista_congelada.parquet` (validada em `verificacao.json`, 46/46 checks OK), regra de k = arredondado (principal do capítulo). Tabelas completas em `lift_por_magnitude.csv`, `lift_por_partido.csv` e `persistencia_ranking_partido.json`. Nenhum número citado abaixo deve divergir dessas três fontes — se divergir, é erro de transcrição deste documento, não recalcular aqui.

## Magnitude

### O que os números mostram

O lift permanece acima de 1 em toda a distribuição, nos dois anos e nos dois alvos:

| Magnitude      | Competitivos 2018 | Competitivos 2022 | Eleitos 2018 | Eleitos 2022 |
|---------------|---------------|---------------|---------------|---------------|
| Pequeno (8–12) | 1,40              | 1,37              | 1,50         | 1,44         |
| Médio (16–31)  | 1,96              | 2,00              | 2,07         | 2,40         |
| Grande (39–70) | 2,52              | 2,37              | 2,45         | 2,63         |

O lift cresce sistematicamente com a magnitude, nos dois anos e nos dois alvos, sem nenhuma inversão. O tamanho relativo médio do núcleo (k_l/C_l) cai na mesma direção — de \~0,59-0,60 nas listas pequenas para \~0,29-0,35 nas grandes —, ou seja, o núcleo fica proporcionalmente menor exatamente onde o lift é maior.

Respostas às três perguntas do item 3: - **Lift \> 1 em todo o espectro?** Sim, nas 6 combinações ano×magnitude e nos dois alvos, sem exceção. - **Cresce/diminui sistematicamente com magnitude?** Cresce, de forma monotônica, nas 4 séries (2 anos × 2 alvos). - **O padrão se replica nas duas eleições?** Sim — mesma ordenação (pequeno \< médio \< grande) e magnitudes comparáveis em 2018 e 2022.

### Mecanismo possível

Listas maiores adicionam sobretudo candidaturas de cauda (baixo recurso, baixa probabilidade de vitória), sem que o núcleo cresça na mesma proporção — daí o k_l/C_l menor. Um núcleo relativamente menor, selecionado contra um denominador maior de candidaturas periféricas, tende a ser um sinal mais nítido da prioridade do partido, o que é compatível com (mas não prova) uma leitura de que a coordenação partidária sobre os recursos se torna mais discriminante — não mais fraca — quanto mais complexa é a nominata.

### O que não permite afirmar

O padrão é uma correlação magnitude→lift, não uma relação causal: não é possível isolar o efeito da magnitude do porte do estado, do sistema partidário local ou da composição de partidos que disputam distritos grandes vs. pequenos (confundidores plausíveis, não controlados aqui). O exercício também não distingue alocação top-down de autosseleção de candidatos fortes (a mesma ressalva já registrada para a TAA em `cap3_taa_features.py`). Nenhum teste formal (regressão, interação) foi rodado — só tabulação descritiva.

### Como isso afeta o argumento

Reforça a robustez do achado central do capítulo: a focalização de recursos não é um artefato de listas pequenas nem se dilui em nominatas grandes e mais difíceis de coordenar — ao contrário, fica mais pronunciada. É um resultado de heterogeneidade que sustenta, sem substituir, o argumento principal do Cap. 3.

## Partido

### O que os números mostram

A focalização acima do benchmark aleatório é generalizada, não concentrada em poucas legendas: de 40 partidos com listas nos dois anos, apenas o **DC** fica abaixo de 1 em qualquer alvo (eleitos: lift = 0, E = 0,23; competitivos: lift = 0,66, E = 1,88 — ambos com denominador esperado minúsculo). Sete partidos marginais (PCB, PCO, PMB, PRTB, PSTU, UP, e AGIR no alvo eleitos) têm lift indefinido (0/0): não elegeram nenhum candidato no período, o que não é uma falha do indicador. Partidos grandes e consolidados (PT, PSDB, MDB, PP, PSD, PSB, PL, DEM, UNIÃO, PR, REPUBLICANOS, PRB) formam um núcleo estável entre lift 1,5 e 2,3 nos dois alvos.

Os valores mais altos de lift (PPL 9,0; PMN 5,1; REDE 4,9; PATRI/PATRIOTA 3,3–3,7; AVANTE 3,6; PRP 3,3; PROS 3,3; PSC 3,2, alvo eleitos) quase todos carregam a marca `denominador_pequeno` (E esperado \< 5 ou \< 5 listas) em `lift_por_partido.csv` — são lift altos calculados sobre pouquíssimos eleitos esperados, não evidência forte de focalização excepcional. A exceção é o **PSOL** (lift eleitos = 4,04, E = 5,45, *não* sinalizado como denominador pequeno) — um outlier que resiste ao filtro de volume mínimo e merece investigação à parte.

Sobre persistência do ranking entre 2018 e 2022 (por família partidária, `persistencia_ranking_partido.json`, restrito a famílias com E ≥ 5 nos dois anos): - Alvo **eleitos**: 9 famílias comparáveis, Spearman ρ = 0,60 (p = 0,09) — associação positiva moderada, mas não significativa ao nível convencional com esse N. - Alvo **competitivos**: 19 famílias comparáveis, Spearman ρ = 0,007 (p = 0,98) — nenhuma correlação detectável.

Respostas às cinco perguntas do item 4: - **Focalização generalizada entre partidos?** Sim, é a norma entre os partidos com volume mínimo de informação. - **Há partidos perto de 1?** Só DC (abaixo) e AGIR (perto, 1,17, mas E \< 1) — ambos com denominador minúsculo. - **Outliers muito altos por denominador pequeno?** Na maioria, sim; PSOL é a exceção que não se explica só por isso. - **Ranking minimamente persistente 2018→2022?** Fraco/incerto para eleitos (ρ = 0,60, não significativo); nulo para competitivos (ρ ≈ 0). - **Competitivos e eleitos contam a mesma história?** Não integralmente: convergem em "focalização generalizada", mas divergem na estabilidade do ranking entre eleições.

### Mecanismo possível

A persistência fraca/nula do ranking é compatível com choques específicos de cada eleição (por exemplo, o desempenho de partidos alinhados à onda eleitoral de 2018 vs. 2022) pesando mais sobre *quem* é priorizado dentro do núcleo do que qualquer traço organizacional estável do partido. Isso não invalida a focalização em si — ela se repete nos dois anos —, mas sugere que o alvo específico da focalização (que candidatos específicos) é mais contingente à conjuntura eleitoral do que uma característica fixa da legenda.

### O que não permite afirmar

Com 9 a 19 famílias comparáveis e nenhuma correção para comparações múltiplas, isto é descritivo — não um teste formal de estabilidade. O rótulo `denominador_pequeno` sinaliza imprecisão estatística implícita, mas os valores de lift em si continuam corretamente calculados; "outlier por denominador pequeno" não deve ser lido como "erro de cálculo". Nenhuma comparação par a par entre partidos específicos (ex.: "o partido X coordena mais que o partido Y") é sustentada por este exercício sem antes checar o N por trás.

### Como isso afeta o argumento

A generalização da focalização entre partidos estabelecidos reforça a validade externa do achado do Top-NECr — não é dirigido por poucas legendas grandes. Mas a heterogeneidade (outliers de baixa informação, ranking não persistente para competitivos) deve entrar como qualificação, não como uma segunda afirmação causal sobre diferenças de coordenação entre partidos específicos.

## Classificação do estatuto de cada resultado (item 6)

| Resultado | Estatuto | Justificativa |
|------------------------|------------------------|------------------------|
| Lift \> 1 em todo o espectro de magnitude, nos dois anos e alvos | **Resultado central** | Robusto, monotônico, sem exceção, replica nas duas eleições — sustenta diretamente o argumento do capítulo. |
| Focalização (lift \> 1) generalizada entre partidos com volume mínimo de informação | **Resultado central** | Não é artefato de poucas legendas grandes; reforça a validade externa do achado nacional. |
| Lift cresce sistematicamente com magnitude | **Heterogeneidade relevante** | Padrão real e replicável, mas é uma qualificação do achado central (onde o efeito é mais/menos forte), não o achado em si. |
| Ranking de lift por partido pouco/nada persistente entre 2018–2022 (ρ = 0,60 eleitos; ρ ≈ 0 competitivos) | **Heterogeneidade relevante** | Achado substantivo sobre os limites de uma leitura "traço fixo do partido", mas com N pequeno de famílias comparáveis — não deve carregar sozinho uma alegação forte. |
| Outliers de lift muito alto concentrados em partidos com E pequeno (PPL, PMN, REDE etc.) | **Diagnóstico/robustez** | Aviso de leitura da tabela (denominador minúsculo), não um achado substantivo sobre focalização partidária. |
| PSOL como outlier de lift alto sem denominador pequeno | **Diagnóstico/robustez** | Digno de nota e investigação futura, mas um único caso não sustenta generalização — fica de fora do corpo do texto por ora. |
| Partidos marginais com lift indefinido (PCB, PCO, PMB, PRTB, PSTU, UP, DC, AGIR) | **Ruído** | Ausência quase total de eleitos/competitivos no período torna o indicador não interpretável para essas legendas. |