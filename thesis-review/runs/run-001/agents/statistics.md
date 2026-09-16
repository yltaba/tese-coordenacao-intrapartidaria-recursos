# statistics-reviewer — Capítulo 3 — run-001

## Escopo e método
- Arquivos lidos: `tese/03-medindo-coordenacao-intrapartidaria.qmd` (sha256 conferido com `manifest.yaml`: `0aec63e5…`), `tese/03-formulas-propostas.qmd` (lido antes de ser movido), `src/2_gold/cap3_cobertura_top_necr.py`, `cap3_cs_features.py`, `cap3_taa_features.py`, `tese/scripts/validacao_mensuracao_top_necr.py`, `tese/sensibilidade-top-x/analisar.py`; artefatos `15_cobertura_nacional.csv`, `16_cobertura_distribuicao.csv`, `17_precisao_distribuicao.csv`, `05_concentracao_ano.csv`, `benchmark_precisao_top_necr.csv/.json`, `README-benchmark-top-necr.md`, `sensibilidade-top-x/resumo_nacional.csv`, `faixas_incrementais.csv`, `tamanhos.csv`, `interpretacao.json`, `resultados-validacao-top-necr/sorteios_referencia.csv`, `validade_expost.csv`, `validade_exante.csv`, `validade_interna.csv`, `robustez_cortes.csv`, `exante_por_corte.csv`; `data/processed/df_cobertura_top_necr_lista.parquet`, `rrd_df_novo.parquet`, `df_cox_survival.parquet` (só localizado; Cap. 4 fora do escopo deste run).
- **Aviso de caminho.** Durante o run, as pastas `tese/resultados-capitulo-3/`, `tese/sensibilidade-top-x/`, `tese/resultados-validacao-top-necr/` e `tese/alternativas-top-necr/` foram movidas para `tese/reports/…`. Os caminhos citados abaixo usam a localização atual (`tese/reports/…`); o `manifest.yaml` ainda aponta para os caminhos antigos.
- Recomputações executadas (scripts em `evidence/`):
  - `sta_recompute.py` → `sta_recompute_log.txt`, `sta_razoes_de_somas.csv`, `sta_permutacao_top_necr.csv`, `sta_bootstrap_ic.csv`, `sta_bootstrap_diferencas.csv`, `sta_media_razoes_vs_razao_somas.csv`, `sta_contribuicao_listas_grandes.csv`, `sta_nucleo_por_sexo.csv`, `sta_gradiente_marginal.csv`, `sta_resultados.json`. Fonte: `tese/reports/sensibilidade-top-x/candidaturas.parquet` (pesos $w_{il}$ do Top-NECr e do Top-X%, `competitivo_previo`, `eleito`) + `rrd_df_novo.parquet` (sexo). Reproduz exatamente os agregados do capítulo ($\sum H$ = 716,75; $A_0$ = 382,54; lift 1,874 etc.) e acrescenta: (i) nulo por permutação dentro da lista preservando o vetor de recursos e os pesos fracionários, 2.000 réplicas, dois universos (todos os candidatos / só recebedores); (ii) bootstrap por lista (859/711 clusters) e por partido (35/32 clusters), 2.000 réplicas, para cobertura, precisão, lift e para as diferenças que o texto afirma (2022−2018; eleitos−competitivos; Top-50%−Top-NECr); (iii) média das razões por lista vs razão das somas e peso das listas com $k_l=C_l$; (iv) contribuição das 10% maiores listas; (v) lift acumulado vs lift marginal por faixa do Top-X%.
  - `sta_sexo_lift.py` → `sta_lift_por_sexo.csv`: cobertura, precisão e lift do Top-NECr restritos a homens e a mulheres dentro de cada lista.
- Não foi possível verificar: o comportamento sob um contrafactual "sem cotas" (não computável a partir dos dados; ver STA-3-004). A nota formal `03-formulas-propostas.qmd` não está mais em `tese/` após a reorganização; as citações a ela usam a versão lida no início do run.

## Avaliação macro
A cadeia medida → resultado → conclusão funciona no que depende de descrição: os três indicadores são razões de somas bem definidas, o denominador do lift é a expectativa hipergeométrica correta para o nulo "sorteio uniforme de $k_l$ entre $C_l$", e a recomputação reproduz todos os agregados. Sob esse nulo, o lift observado está muito fora da faixa de permutação (95% dos sorteios dão lift entre 0,95 e 1,05 para competitivos e 0,92–1,08 para eleitos; observado 1,87–2,12; p < 0,0005). A afirmação central — o núcleo captura cerca do dobro do acaso — sobrevive.

O que não se sustenta como está escrito é a camada de comparações e de interpretação construída sobre esse fato. Primeiro, o nulo não é declarado quanto ao universo do sorteio: sortear entre todos os candidatos, inclusive os que não receberam nada, credita ao núcleo a diferença entre receber e não receber; entre recebedores, o lift de 2018 cai de 1,87 para 1,69 (competitivos) e de 1,98 para 1,78 (eleitos). Segundo, nenhuma comparação (2018 vs 2022, competitivos vs eleitos, Top-NECr vs Top-X%) tem medida de variabilidade, e o bootstrap por lista mostra que a diferença de lift entre eleições é indistinguível de zero enquanto o texto lê "1,98 → 2,12" e "se repete". Terceiro, a comparabilidade entre eleições é comprometida por composição: em 2018, 207 listas têm núcleo igual à lista inteira (lift = 1 por construção) e respondem por 27% do denominador; em 2022, 100 listas e 2%. Excluindo-as, 2018 dá 2,20 e 2022 1,91 — a "estabilidade" do 1,9 depende do universo. Quarto, a leitura das cotas como "estimativa conservadora" é contradita para o lift: restrito a homens, o lift é menor que o agregado. O capítulo precisa (a) declarar o nulo e reportar o mais exigente, (b) anexar faixas de permutação e intervalos de bootstrap por lista, tratando-os como estabilidade sob reamostragem e não como inferência amostral, e (c) reescrever as comparações entre eleições como descritivas.

## Achados

```yaml
id: STA-3-001
titulo: "Universo da referência aleatória não declarado; sob sorteio só entre recebedores o lift de 2018 cai de 1,87 para 1,69 (competitivos) e de 1,98 para 1,78 (eleitos)"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 107
  secao: "#### Cobertura, precisão e lift {#sec-metricas}"
  trecho: "se um subconjunto de tamanho $k_l$ fosse extraído ao acaso, sem reposição, entre as $C_l$ candidaturas da lista $l$, o número esperado de candidaturas no grupo de referência nele contidas seria $G_l\\,k_l/C_l$"
afirmacao_do_autor: "O lift compara o núcleo com um sorteio uniforme entre todas as C_l candidaturas da lista; o núcleo tem 'quase 90% mais' competitivos (l. 143) e 'o dobro' dos eleitos (l. 147) do que esse sorteio."
problema: "O núcleo Top-NECr é, por construção, composto só de recebedores (k_l ≤ nº de recebedores; verificação 'NECr entre 1 e o número de recebedores' em 21_verificacoes.csv). Sortear entre todas as C_l candidaturas inclui quem recebeu zero — 24% dos candidatos das listas financiadas em 2018 (média 2,30 de 9,41 por lista, 05_concentracao_ano.csv) e 8% em 2022. Parte do lift mede portanto a diferença entre receber e não receber, não a ordenação dentro dos recebedores. A nota formal (03-formulas-propostas.qmd, 'Decisões que permanecem em aberto', item 2) reconhece a alternativa e diz que 'o capítulo deve declarar qual adota e por quê'; o capítulo não declara. O próprio autor já calculou o universo alternativo para eleitos (validade_expost.csv, linhas 'Apenas recebedores positivos') e não o reporta."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-001/evidence/sta_razoes_de_somas.csv"
    - "thesis-review/runs/run-001/evidence/sta_permutacao_top_necr.csv"
    - "tese/reports/resultados-validacao-top-necr/validade_expost.csv"
    - "tese/reports/resultados-capitulo-3/05_concentracao_ano.csv"
  detalhe: "Lift com nulo 'todos' vs 'só recebedores' (recomputado, coincide com validade_expost.csv para eleitos): competitivos 2018 1,874 → 1,686; 2022 1,890 → 1,851; eleitos 2018 1,982 → 1,782; 2022 2,117 → 2,048. Faixa de permutação (2.000 réplicas, universo recebedores) para o lift sob o nulo: 2018 competitivos [0,95; 1,05]; observado 1,69 continua fora (p < 0,0005). 'Quase 90% mais' em 2018 vira 'cerca de 69% mais'."
severidade: MAJOR
confianca: alta
recomendacao: "Declarar no texto o universo do sorteio e o que ele testa. Reportar os dois nulos lado a lado (todos / recebedores), tratando o segundo como o benchmark exigente para a pergunta 'o partido ordena entre quem financia?'. Reescrever 'quase 90% mais' como intervalo entre os dois nulos (69–87% em 2018; 85–89% em 2022) ou adotar o mais exigente como principal. A conclusão (lift > 1, fora da faixa de permutação) sobrevive nos dois casos."
claims: [C3.5.04, C3.5.07]
```

```yaml
id: STA-3-002
titulo: "Nenhuma comparação tem medida de variabilidade; a diferença de lift entre 2018 e 2022 é indistinguível de zero no bootstrap por lista, e a simulação de 10.000 sorteios existente não é usada"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 147
  secao: "### Priorização financeira pelo Top-NECr"
  trecho: "o núcleo reúne 1,98 vez o número de eleitos esperado em 2018 e 2,12 vez em 2022. Isto é, cerca do dobro, em ambos os ciclos"
afirmacao_do_autor: "Lifts, coberturas e precisões são apresentados como pontos; as comparações entre eleições ('1,98 … 2,12'; 'se repete em 2018 e 2022', l. 173; 'a queda da precisão … de 19,2% para 12,4%', l. 175), entre referências (competitivos vs eleitos) e entre cortes (Top-NECr vs Top-X%) são lidas como diferenças ou como igualdades sem qualquer faixa."
problema: "O capítulo não reporta nenhuma faixa de permutação nem intervalo de reamostragem, embora (a) `sorteios_referencia.csv` contenha 10.000 sorteios por ano e universo e (b) as quantidades sejam razões de somas sobre 859/711 listas, cuja estabilidade sob reamostragem de listas é calculável. Sem isso, o leitor não distingue o que é decisivo (lift ≠ 1) do que é apenas descritivo (2022 ≠ 2018). Como a base é o universo de candidaturas, intervalos devem ser apresentados como estabilidade sob reamostragem de listas (como os próprios scripts do autor fazem em `financiamento_alternativo_top_necr.py`), não como erro amostral."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-001/evidence/sta_bootstrap_ic.csv"
    - "thesis-review/runs/run-001/evidence/sta_bootstrap_diferencas.csv"
    - "thesis-review/runs/run-001/evidence/sta_permutacao_top_necr.csv"
    - "tese/reports/resultados-validacao-top-necr/sorteios_referencia.csv"
    - "tese/reports/resultados-validacao-top-necr/validade_expost.csv"
  detalhe: "Permutação dentro da lista (2.000 réplicas): sob o nulo o lift fica em [0,95; 1,05] (competitivos) e [0,92; 1,08] (eleitos) em 95% dos sorteios; máximo simulado 421 acertos vs 716,75 observados (2018, competitivos) — p < 0,0005 em todos os casos. Bootstrap por lista, IC95 do lift Top-NECr: competitivos 2018 [1,76; 1,99], 2022 [1,80; 1,99]; eleitos 2018 [1,84; 2,13], 2022 [1,99; 2,27]. Diferenças 2022−2018: lift competitivos +0,02 [−0,13; +0,16]; lift eleitos +0,14 [−0,07; +0,34]; cobertura eleitos +5,9 pp [+0,8; +11,2]; precisão eleitos −6,8 pp [−9,8; −3,9]. Eleitos−competitivos no mesmo ano: 2018 +0,11 [0,00; +0,22]; 2022 +0,23 [+0,13; +0,34]. Top-50%−Top-NECr: 2018 +0,20 [+0,13; +0,28] (competitivos), 2022 +1,48 [+1,26; +1,73] (eleitos). O arquivo `sorteios_referencia.csv` (P2,5–P97,5 = 207–242 acertos em 2018, observado 445) nunca é citado no capítulo."
severidade: MAJOR
confianca: alta
recomendacao: "(1) Na seção de métricas, acrescentar uma frase com a faixa de permutação do nulo ('em 95% de 10.000 sorteios o lift ficaria entre 0,92 e 1,08; o observado é 1,98') — o autor já tem os sorteios. (2) Na figura ou em nota, IC95 por bootstrap de listas (2.000 réplicas) para cada lift, declarado como estabilidade sob reamostragem de listas. (3) Reescrever as comparações entre eleições como descritivas: 'os lifts de 2018 e 2022 são da mesma ordem' em vez de ler 1,98 → 2,12 como movimento; a queda da precisão dos eleitos (−6,8 pp, IC excluindo zero por lista) pode ser mantida como diferença, mas ver STA-3-008 para o cluster por partido."
claims: [C3.5.04, C3.5.07, C3.7.01, C3.7.02]
```

```yaml
id: STA-3-003
titulo: "Listas com núcleo igual à lista inteira (lift = 1 por construção) são 26% das financiadas em 2018 e 15% em 2022; sem elas o lift de 2018 é 2,20 e o de 2022 1,91 — a 'repetição' do 1,9 entre eleições depende do universo"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 173
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "e ela se repete em 2018 e 2022, para candidaturas competitivas e para eleitas, no Top-NECr e em quase todos os limiares do Top-X%"
afirmacao_do_autor: "O lift de 1,9 é estável entre as duas eleições; em 2022 'a priorização não desapareceu. Mudou de forma' (l. 181)."
problema: "Quando k_l = C_l (NECr arredonda para o tamanho da lista, típico de listas de 1–3 candidatos da era das coligações), H_l = G_l = A0_l e a lista contribui exatamente com lift 1, puxando o agregado para 1 sem informar nada sobre ordenação. Essas listas são 207 de 786 financiadas em 2018 (validade_interna.csv, 'Núcleo = lista inteira') e 100 de 648 em 2022, mas seu peso no denominador é muito desigual: 27% de A0 em 2018 contra 2% em 2022 (competitivos). Logo o agregado de 2018 está mais diluído que o de 2022 e os dois lifts não são comparáveis como estão. A composição das listas também mudou (fim das coligações), o que o texto usa em l. 181 sem reconhecer que isso afeta o próprio lift."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-001/evidence/sta_media_razoes_vs_razao_somas.csv"
    - "tese/reports/resultados-validacao-top-necr/validade_interna.csv"
  detalhe: "Competitivos: 2018 lift agregado 1,874; só listas com 0 < k_l < C_l: 2,204. 2022: 1,890 → 1,909. Eleitos: 2018 1,982 → 2,331; 2022 2,117 → 2,122. Share de A0 das listas degeneradas: 27,5% (2018) vs 2,1% (2022) para competitivos; 26,3% vs 0,5% para eleitos. Combinando com STA-3-001: sob nulo 'recebedores' o lift sobe de 2018 para 2022 (1,69 → 1,85); sem listas degeneradas ele cai (2,20 → 1,91). A direção da mudança entre eleições não é identificável."
severidade: MAJOR
confianca: alta
recomendacao: "Reportar, ao lado do agregado, o lift restrito às listas com fronteira comparável (0 < k_l < C_l; o autor já tem o conceito 'Fronteiras comparáveis' = 579/548 em validade_interna.csv) e declarar quantas listas contribuem com lift 1 por construção. Reescrever l. 173 e l. 181: em vez de 'se repete', dizer que o lift é da mesma ordem nas duas eleições sob o universo completo e que a comparação entre elas é sensível à composição das listas (coligações em 2018)."
claims: [C3.7.01, C3.7.07]
```

```yaml
id: STA-3-004
titulo: "A leitura das cotas como 'estimativa conservadora' é contradita para o lift: restrito a homens, o lift é menor que o agregado (1,63 vs 1,87 em 2018; 1,75 vs 1,89 em 2022)"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 179
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "Se as cotas fossem retiradas do cálculo, a concentração escolhida pelo partido apareceria maior do que a medida aqui — o que faz dos indicadores apresentados uma estimativa conservadora da priorização."
afirmacao_do_autor: "As cotas de gênero e raça forçam o partido a financiar candidaturas raramente competitivas; isso 'puxa a precisão para baixo' e torna os indicadores conservadores. (O parágrafo ainda contém o placeholder '[inserir: X% das mulheres…]'.)"
problema: "A afirmação é um contrafactual não computado e, na única versão computável — recalcular C_l, k_l, G_l e H_l dentro de cada lista só entre homens — o sinal é o oposto para o lift, que o próprio texto chama de 'o número que interessa' (l. 175). A precisão entre homens é de fato maior (39,7% vs 30,9% em 2018), mas o lift entre homens é menor, porque o nulo estratificado deixa de creditar ao núcleo a diferença de competitividade entre sexos. Além disso, as mulheres ocupam 33–36% das posições do núcleo, aproximadamente sua participação entre as candidaturas (32–35%): as cotas não inflam o núcleo com mulheres além da proporção."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-001/evidence/sta_lift_por_sexo.csv"
    - "thesis-review/runs/run-001/evidence/sta_nucleo_por_sexo.csv"
    - "tese/reports/resultados-validacao-top-necr/validade_exante.csv"
  detalhe: "Top-NECr, competitivos: todos 2018 precisão 30,9% / lift 1,874; homens 39,7% / 1,633; mulheres 13,1% / 1,628. 2022: todos 27,8% / 1,890; homens 36,3% / 1,755; mulheres 13,0% / 1,806. Eleitos: 2018 lift todos 1,982, homens 1,689; 2022 2,117 vs 1,911. Competitivos entre mulheres 4,5% (2018) e 6,0% (2022) vs 14,9% e 17,3% entre homens. validade_exante.csv já mostra lift ≈ 1,0 para 'Mulheres' como perfil (1,03 e 1,00), i.e., o núcleo não sobre- nem sub-representa mulheres."
severidade: MAJOR
confianca: media
recomendacao: "Ou retirar a frase sobre 'estimativa conservadora', ou substituí-la pelo cálculo estratificado com a direção correta para cada indicador: 'a precisão entre homens é maior (39,7% e 36,3%); o lift, não (1,63 e 1,75), porque parte do lift agregado reflete a maior competitividade prévia dos homens'. Preencher o placeholder com os percentuais acima (4,5% vs 14,9%; 6,0% vs 17,3%). Confiança média porque 'retirar as cotas do cálculo' admite outras leituras não computáveis; em nenhuma delas a frase está sustentada."
claims: [C3.7.06]
```

```yaml
id: STA-3-005
titulo: "Razão de cobertura, razão de precisão e lift são o mesmo número; o texto os apresenta como três confirmações"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 147
  secao: "### Priorização financeira pelo Top-NECr"
  trecho: "Estas taxas de precisão seguem duas vezes maiores quando comparadas ao seu *benchmark* aleatório. O *lift* confirma que essa diferença não vem do tamanho dos grupos selecionados pelo Top-NECr"
afirmacao_do_autor: "Cobertura é 'o dobro' da esperada (l. 145); precisão é 'duas vezes maior' que o benchmark; e o lift 'confirma' que a diferença não vem do tamanho."
problema: "Por @eq-indicadores, Cobertura/Cobertura_acaso = Precisão/Precisão_acaso = ΣH/A0 = Lift, identicamente. Não há confirmação independente: as três frases relatam a mesma razão. A nota formal (seção 'Referência aleatória') já adverte que 'a coincidência numérica entre os dois lifts no texto não seja lida como confirmação recíproca'. O 'não vem do tamanho' também é impreciso: o lift desconta o tamanho por lista, mas continua sendo uma soma ponderada por G_l k_l/C_l (ver STA-3-006)."
evidencia:
  tipo: artefato
  fontes:
    - "tese/reports/resultados-capitulo-3/benchmark_precisao_top_necr_verificacao.json"
    - "tese/reports/sensibilidade-top-x/analisar.py:127"
  detalhe: "benchmark_…_verificacao.json lista a verificação 'Lift de precisão = lift de cobertura = observados / esperados'; analisar.py:127 checa 'Lift idêntico por cobertura e precisão'. 86,74/43,78 = 19,20/9,69 = 1,98; 92,63/43,75 = 12,43/5,87 = 2,12."
severidade: MODERATE
confianca: alta
recomendacao: "Dizer uma vez, na seção de métricas, que os dois quocientes coincidem por construção e usar o lift como única razão. Em l. 145–147, retirar 'Estas taxas de precisão seguem duas vezes maiores' e 'O lift confirma', deixando: 'a razão observado/esperado — a mesma para cobertura e precisão — é 1,98 e 2,12'."
claims: [C3.5.05, C3.5.06, C3.5.07]
```

```yaml
id: STA-3-006
titulo: "Razões de somas ponderam implicitamente pelas listas grandes; a lista típica tem lift 2,0 (mediana) e 2,7 (média), não 1,9, e o texto não declara a escolha"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 95
  secao: "#### Cobertura, precisão e lift {#sec-metricas}"
  trecho: "Os três indicadores são calculados nacionalmente, somando as listas"
afirmacao_do_autor: "As métricas são nacionais; o resultado 'pode ser resumido em um número: 1,9' (l. 173)."
problema: "Razão de somas ≠ média das razões. A escolha é defensável (evita denominadores indefinidos, é a leitura 'quantos competitivos no total estão no núcleo'), mas implica peso proporcional a G_l k_l/C_l: as 10% maiores listas por G_l (SP, MG, RJ, BA) carregam 41–64% do denominador A0. O texto não diz que o 1,9 é um agregado ponderado nem que a distribuição entre listas é muito heterogênea (P25–P75 da precisão por lista 0–50% em 2018, 17_precisao_distribuicao.csv). A nota formal declara 'razões nacionais, calculadas sobre as somas, e não médias das razões por lista'; o capítulo, não."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-001/evidence/sta_media_razoes_vs_razao_somas.csv"
    - "thesis-review/runs/run-001/evidence/sta_contribuicao_listas_grandes.csv"
    - "tese/reports/resultados-capitulo-3/16_cobertura_distribuicao.csv"
    - "tese/reports/resultados-capitulo-3/17_precisao_distribuicao.csv"
  detalhe: "Competitivos 2018: razão de somas — cobertura 80,9%, precisão 30,9%, lift 1,87; médias por lista — cobertura 82,9% (listas com G_l>0), precisão 38,6% (listas com k_l>0), lift 2,70 (mediana 2,00; listas com A0_l>0). 2022: 82,7/27,8/1,89 vs 83,2/27,7/2,42 (mediana 1,88). Eleitos 2018: cobertura nacional 86,7% vs média por lista 90,9% (16_cobertura_distribuicao.csv); lift médio por lista 3,09. Top-10% listas por G_l: share de A0 41% (comp. 2018) a 64% (eleitos 2022)."
severidade: MODERATE
confianca: alta
recomendacao: "Acrescentar uma frase em @sec-metricas: 'São razões de somas nacionais, e não médias por lista; listas com mais candidaturas do grupo-alvo pesam mais.' Reportar em nota a mediana do lift por lista (2,0 / 1,9) como leitura complementar da 'lista típica', e citar os CSVs 16/17 para a dispersão."
claims: [C3.7.01]
```

```yaml
id: STA-3-007
titulo: "O gradiente Top-X% acumulado é monotônico por construção dado o decréscimo da densidade marginal; a evidência de 'camadas' está nos lifts marginais por faixa, que o autor calculou (faixas_incrementais.csv) e não reporta — e o '1,9 em quase todos os limiares' não descreve os valores (1,38–3,60)"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 177
  secao: "## Discussão {#sec-discussao-cap3}"
  trecho: "O gradiente é monotônico nas duas eleições e nas duas referências. Esta é a assinatura esperada de uma distribuição em camadas"
afirmacao_do_autor: "Precisão e lift crescem ao restringir o corte (l. 159, 177); isso assina uma distribuição em camadas e não uma alocação uniforme com ruído; o 1,9 'se repete … em quase todos os limiares do Top-X%' (l. 173)."
problema: "(a) Os cortes Top-τ são aninhados; precisão(τ) e lift(τ) acumulados são médias ponderadas das densidades marginais das faixas. Se a densidade marginal decresce no ranking, a monotonia dos acumulados é aritmética — não é evidência adicional além de 'o topo é mais denso que a cauda'. A afirmação correta contra o nulo uniforme é que a curva não é plana (o que a permutação já estabelece). (b) A distinção entre 'camadas' e 'uniforme com ruído' é decidida pelos lifts marginais, que existem em faixas_incrementais.csv e mostram algo que o texto não diz: as faixas 80–90% e 90–95% têm lift < 1 (0,71 e 0,36 em 2018, competitivos), e para eleitos em 2018 já a faixa 70–80% está abaixo de 1 (0,76) — ou seja, o núcleo Top-NECr (≈ Top-80% da massa em 2018) inclui uma faixa com densidade de eleitos abaixo da média da lista. (c) Os lifts do Top-X% vão de 1,38 (Top-95%, 2022) a 3,60 (Top-50%, eleitos 2022); '1,9 se repete em quase todos os limiares' não é uma descrição desses valores."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-001/evidence/sta_gradiente_marginal.csv"
    - "tese/reports/sensibilidade-top-x/faixas_incrementais.csv"
    - "tese/reports/sensibilidade-top-x/resumo_nacional.csv"
    - "tese/reports/sensibilidade-top-x/interpretacao.json"
  detalhe: "Lift marginal por faixa (competitivos 2018): 0–50% 2,08; 50–60% 1,86; 60–70% 1,79; 70–80% 1,26; 80–90% 0,71; 90–95% 0,36; fora do Top-95% 0,30. Eleitos 2018: 2,38; 2,10; 1,42; 0,76; 0,51; 0,20; 0,24. Eleitos 2022: 3,60; 1,70; 1,13; 0,61; 0,21; 0,09; 0,12. Lifts acumulados (resumo_nacional.csv): mínimo 1,375, máximo 3,599; Top-NECr 1,87/1,89/1,98/2,12."
severidade: MODERATE
confianca: alta
recomendacao: "Em l. 159 e 177, substituir a leitura 'quanto mais restrito, maior a presença desproporcional' pela sua versão marginal: reportar (tabela curta ou figura) o lift de cada faixa incremental e dizer onde ele cruza 1 (entre 70% e 90% da massa). Isso sustenta 'camadas' de forma direta e revela a amplitude do Top-NECr. Em l. 173, trocar 'se repete em quase todos os limiares' por 'permanece acima de 1 em todos os limiares, variando de 1,4 a 3,6'."
claims: [C3.6.03, C3.7.01, C3.7.04, C3.7.05]
```

```yaml
id: STA-3-008
titulo: "Dependência entre listas do mesmo partido não é reconhecida; com cluster por partido (35/32) os intervalos dobram e a diferença de cobertura entre eleições deixa de excluir zero"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 25
  secao: "### Universo empírico e recursos partidários"
  trecho: "Para examinar a distribuição intrapartidária, essas observações são agregadas por partido, unidade da federação e eleição."
afirmacao_do_autor: "A lista partido × UF × eleição é a unidade em que o núcleo é definido; a inferência (l. 183: 'É evidência de que o partido, como organização, prioriza') é sobre partidos."
problema: "Candidaturas estão aninhadas em listas, e listas em partidos que podem aplicar a mesma regra de alocação em todas as UFs. O nulo hipergeométrico trata as listas como independentes, o que é adequado para o teste 'lift ≠ 1' (a evidência é esmagadora em qualquer nível), mas qualquer afirmação comparativa que venha a receber intervalo depende do nível de cluster. O capítulo não discute isso. É limitação a reconhecer, não erro."
evidencia:
  tipo: recomputacao
  fontes:
    - "thesis-review/runs/run-001/evidence/sta_bootstrap_ic.csv"
    - "thesis-review/runs/run-001/evidence/sta_bootstrap_diferencas.csv"
  detalhe: "IC95 da precisão dos eleitos 2022: por lista [10,7%; 14,3%], por partido [7,3%; 17,9%]. Cobertura eleitos 2022−2018: por lista +5,9 pp [+0,8; +11,2]; por partido [−3,5; +18,3]. Precisão eleitos 2022−2018: por lista [−9,8; −3,9]; por partido [−15,4; +1,8]. Lift: IC por partido só ~20–40% mais largo (2018 competitivos [1,75; 2,00])."
severidade: MODERATE
confianca: alta
recomendacao: "Acrescentar ao parágrafo de unidades uma frase: as listas de um mesmo partido não são independentes; os intervalos reportados (se adotados conforme STA-3-002) devem ser apresentados nos dois níveis (lista e partido), e as comparações entre eleições consideradas descritivas quando o intervalo por partido inclui zero."
claims: [C3.7.02]
```

```yaml
id: STA-3-009
titulo: "'Núcleos maiores elevam por construção a taxa de cobertura' vale apenas para cortes aninhados"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 107
  secao: "#### Cobertura, precisão e lift {#sec-metricas}"
  trecho: "Núcleos maiores elevam por construção a taxa de cobertura, pois adicionam mais candidaturas."
afirmacao_do_autor: "Cobertura cresce mecanicamente com o tamanho do núcleo."
problema: "A monotonia é garantida quando o núcleo maior contém o menor (Top-τ para τ crescente; piso ⊂ arredondado ⊂ teto), que é o caso de todos os cortes usados. Para núcleos de tamanho maior mas não aninhados, não vale. Precisão de enunciado, sem efeito no argumento."
evidencia:
  tipo: artefato
  fontes:
    - "tese/reports/sensibilidade-top-x/analisar.py:96"
    - "tese/reports/sensibilidade-top-x/trajetorias.csv"
  detalhe: "analisar.py verifica 'Aninhamento e posições' (w ≥ w_anterior) para cada limiar e 'Cobertura não decrescente' em trajetorias.csv."
severidade: MINOR
confianca: alta
recomendacao: "Escrever 'Núcleos maiores que contêm os menores elevam por construção a cobertura'."
claims: []
```

## Claims

Numeração de seção usada aqui (ordem das subseções `###` do capítulo, com a Discussão `##` como 7): 1 Universo empírico; 2 Seleção do núcleo; 3 Validação (competitivos, métricas); 4 Amplitude e concentração; 5 Priorização pelo Top-NECr; 6 Robustez Top-X%; 7 Discussão.

```yaml
claim_id: C3.4.01
capitulo: 3
secao: "### Amplitude das nominatas e concentração dos recursos"
claim: "Houve um aumento desproporcional dentro do grupo de candidaturas competitivas: o total de candidatos aumentou 27%, o de competitivas 45%."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 115}
evidencia: {tipo: csv, referencia: "tese/reports/resultados-capitulo-3/01_universos.csv"}
assessment: {status: supported, confidence: alta}
concerns:
  - "Descritivo. 9.675/7.630 = 1,268; 1.287/886 = 1,453. Os universos diferem (coligações em 2018, listas puras em 2022); não é comparação inferencial."
agent: statistics-reviewer
```

```yaml
claim_id: C3.5.01
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Mais de 80% das candidaturas competitivas compõem o núcleo Top-NECr em 2018 e 2022; a referência aleatória é 43,2% e 43,7%."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 139}
evidencia: {tipo: csv, referencia: "tese/reports/sensibilidade-top-x/resumo_nacional.csv (top_necr, competitividade); evidence/sta_bootstrap_ic.csv"}
assessment: {status: supported, confidence: alta}
concerns:
  - "80,9% e 82,7%; IC95 bootstrap por lista [77,9; 83,9] e [80,5; 84,7]. Referência aleatória recomputada 43,18% e 43,75%."
agent: statistics-reviewer
```

```yaml
claim_id: C3.5.02
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Precisão de 30,9% e 27,8% contra 16,5% e 14,7% esperados ao acaso."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 141}
evidencia: {tipo: csv, referencia: "evidence/sta_razoes_de_somas.csv"}
assessment: {status: supported, confidence: alta}
concerns:
  - "Recomputado 30,95% / 27,84%; acaso 16,52% / 14,73%. Sob nulo 'só recebedores', acaso = 18,4% / 15,0%."
agent: statistics-reviewer
```

```yaml
claim_id: C3.5.04
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "O lift é 1,87 em 2018 e 1,89 em 2022: quase 90% mais candidaturas competitivas do que o esperado pelo tamanho das listas e do núcleo."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 143}
evidencia: {tipo: csv, referencia: "evidence/sta_razoes_de_somas.csv; evidence/sta_permutacao_top_necr.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns:
  - "Números corretos sob o nulo 'todos os candidatos' (1,874; 1,890) e muito fora da faixa de permutação (p < 0,0005)."
  - "Sob nulo 'só recebedores' (STA-3-001): 1,686 e 1,851 — 'quase 90% mais' vira 69% em 2018."
  - "Sem listas com k = C (STA-3-003): 2,20 e 1,91."
agent: statistics-reviewer
```

```yaml
claim_id: C3.5.05
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "86,7% dos eleitos de 2018 e 92,6% de 2022 estão no núcleo Top-NECr; proporções que representam o dobro das esperadas aleatoriamente."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 145}
evidencia: {tipo: csv, referencia: "tese/reports/resultados-capitulo-3/15_cobertura_nacional.csv (arredondado)"}
assessment: {status: supported, confidence: alta}
concerns:
  - "86,74/43,78 = 1,98; 92,63/43,75 = 2,12. IC95 por lista da cobertura: [81,8; 91,1] e [89,7; 95,3]. 'O dobro' é a mesma razão que o lift (STA-3-005)."
agent: statistics-reviewer
```

```yaml
claim_id: C3.5.06
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "Precisão de 19,2% e 12,4% dos eleitos, duas vezes maior que o benchmark aleatório; a queda reflete sobretudo o tamanho menor do alvo."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 147}
evidencia: {tipo: csv, referencia: "tese/reports/resultados-capitulo-3/benchmark_precisao_top_necr.csv"}
assessment: {status: supported, confidence: alta}
concerns:
  - "19,20/9,69 = 1,98; 12,43/5,87 = 2,12 — identidade com o lift, não confirmação (STA-3-005)."
  - "A queda 2018→2022 (−6,8 pp) exclui zero por lista, não por partido (STA-3-008)."
agent: statistics-reviewer
```

```yaml
claim_id: C3.5.07
capitulo: 3
secao: "### Priorização financeira pelo Top-NECr"
claim: "O núcleo reúne 1,98 vez o número de eleitos esperado em 2018 e 2,12 vez em 2022 — cerca do dobro em ambos os ciclos."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 147}
evidencia: {tipo: csv, referencia: "evidence/sta_bootstrap_diferencas.csv; tese/reports/resultados-validacao-top-necr/validade_expost.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns:
  - "Pontos corretos; 'cerca do dobro' sustentado (IC95 por lista [1,84; 2,13] e [1,99; 2,27])."
  - "A diferença 2022−2018 (+0,14) tem IC95 [−0,07; +0,34]: não é um movimento identificável."
  - "Sob nulo 'só recebedores': 1,78 e 2,05 (o autor já calculou em validade_expost.csv)."
agent: statistics-reviewer
```

```yaml
claim_id: C3.6.01
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "Padrão consistente entre as métricas de 2018 e 2022; no Top-50% há mais de 50% de cobertura dos competitivos; a cobertura cresce com o limiar."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 157}
evidencia: {tipo: csv, referencia: "tese/reports/sensibilidade-top-x/resumo_nacional.csv; trajetorias.csv"}
assessment: {status: supported, confidence: alta}
concerns:
  - "57,3% e 52,8% no Top-50%; cobertura não decrescente em τ por aninhamento. 'Consistente' é descritivo."
agent: statistics-reviewer
```

```yaml
claim_id: C3.6.03
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "Quanto mais se restringe o núcleo ao topo, maior a presença desproporcional de competitivas; o lift permanece acima de um em todos os limiares — 1,53 em 2018 e 1,38 em 2022 no Top-95%."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 159}
evidencia: {tipo: csv, referencia: "tese/reports/sensibilidade-top-x/resumo_nacional.csv; evidence/sta_gradiente_marginal.csv"}
assessment: {status: supported, confidence: alta}
concerns:
  - "Números corretos (1,534; 1,375). A monotonia acumulada é aritmética dada a densidade marginal decrescente; os lifts marginais das faixas acima de 70–80% são < 1 (STA-3-007)."
  - "IC95 por lista do lift Top-50% (competitivos): [1,94; 2,23] e [2,51; 2,81]; diferença Top-50% − Top-NECr exclui zero nos dois anos."
agent: statistics-reviewer
```

```yaml
claim_id: C3.6.04
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "Sistematicamente há mais candidaturas competitivas dentro do núcleo priorizado do que fora."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 161}
evidencia: {tipo: csv, referencia: "tese/reports/sensibilidade-top-x/resumo_nacional.csv (precisao vs proporcao_perfil_fora)"}
assessment: {status: supported, confidence: alta}
concerns:
  - "Em todos os 12 limiares × anos: precisão 19–39% vs proporção fora 2,6–7,7%."
agent: statistics-reviewer
```

```yaml
claim_id: C3.6.05
capitulo: 3
secao: "#### Sensibilidade ao limiar Top-X%"
claim: "Para eleitos, os resultados estão todos acima do esperado ao acaso e os lifts sempre acima de um."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 165}
evidencia: {tipo: csv, referencia: "tese/reports/sensibilidade-top-x/interpretacao.json (todos_24_lifts_acima_1: true)"}
assessment: {status: supported, confidence: alta}
concerns: []
agent: statistics-reviewer
```

```yaml
claim_id: C3.7.01
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "O resultado se resume em 1,9: a razão se repete em 2018 e 2022, para competitivas e eleitas, no Top-NECr e em quase todos os limiares do Top-X%."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 173}
evidencia: {tipo: csv, referencia: "evidence/sta_media_razoes_vs_razao_somas.csv; tese/reports/sensibilidade-top-x/resumo_nacional.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns:
  - "Top-NECr: 1,87 / 1,89 / 1,98 / 2,12 — 'da mesma ordem' sim; a igualdade entre anos depende do universo (STA-3-003: 2,20 vs 1,91 sem listas degeneradas; 1,69 vs 1,85 sob nulo de recebedores)."
  - "Top-X%: lifts entre 1,38 e 3,60; '1,9 em quase todos os limiares' não descreve os valores (STA-3-007)."
  - "1,9 é um agregado ponderado; mediana por lista 2,0 (STA-3-006)."
agent: statistics-reviewer
```

```yaml
claim_id: C3.7.02
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "A queda da precisão entre os pleitos, de 19,2% para 12,4%, é consequência direta de um núcleo que cresceu enquanto o alvo ficou em 513; mesmo descontado o tamanho, o núcleo acerta o dobro."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 175}
evidencia: {tipo: csv, referencia: "evidence/sta_bootstrap_diferencas.csv"}
assessment: {status: supported, confidence: media}
concerns:
  - "Aritmética correta: H 445 → 475 com k 2.318 → 3.824. Diferença −6,8 pp, IC95 por lista [−9,8; −3,9]; por partido [−15,4; +1,8] (STA-3-008)."
  - "'Acerta o dobro' descontado o tamanho: sustentado sob o nulo declarado; 1,78–2,05 sob nulo de recebedores."
agent: statistics-reviewer
```

```yaml
claim_id: C3.7.04
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "No Top-50%, a precisão sobe, o lift sobe e a cobertura cai; o gradiente é monotônico nas duas eleições e nas duas referências."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 177}
evidencia: {tipo: csv, referencia: "tese/reports/sensibilidade-top-x/trajetorias.csv; interpretacao.json"}
assessment: {status: supported, confidence: alta}
concerns:
  - "Monotonia dos acumulados verificada (precisao_lift_nao_crescentes: true). Os números entre colchetes (26%/20%, 2,4/3,6, 66%/70%) correspondem à referência 'eleitos' e o texto não o diz."
  - "Monotonia acumulada é implicada pela densidade marginal decrescente; evidência de 'camadas' é o lift marginal (STA-3-007)."
agent: statistics-reviewer
```

```yaml
claim_id: C3.7.05
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "Esta é a assinatura esperada de uma distribuição em camadas — poucas no topo, uma faixa intermediária financiada de modo efetivo, uma cauda — e não de uma alocação uniforme com ruído."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 177}
evidencia: {tipo: csv, referencia: "tese/reports/sensibilidade-top-x/faixas_incrementais.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns:
  - "Contra 'uniforme com ruído': sustentado (permutação; curva não plana)."
  - "A 'faixa intermediária' (70–95% da massa) tem lift marginal < 1 para eleitos em 2018 (0,76; 0,51; 0,20) e para competitivos acima de 80% (0,71; 0,36): ela é financiada, mas não é desproporcionalmente competitiva/eleita. O texto não reporta isso."
agent: statistics-reviewer
```

```yaml
claim_id: C3.7.06
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "As cotas puxam a precisão para baixo; se fossem retiradas do cálculo, a concentração escolhida apareceria maior — os indicadores são uma estimativa conservadora da priorização."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 179}
evidencia: {tipo: csv, referencia: "evidence/sta_lift_por_sexo.csv"}
assessment: {status: contradicted, confidence: media}
concerns:
  - "Precisão entre homens é maior (39,7% / 36,3%): essa parte é sustentada."
  - "Lift entre homens é menor que o agregado (1,63 / 1,75 competitivos; 1,69 / 1,91 eleitos): para 'o número que interessa', a direção é oposta (STA-3-004)."
  - "Placeholder '[inserir: X% …]' não preenchido; valores: 4,5% vs 14,9% (2018), 6,0% vs 17,3% (2022)."
agent: statistics-reviewer
```

```yaml
claim_id: C3.7.07
capitulo: 3
secao: "## Discussão {#sec-discussao-cap3}"
claim: "A proporção de candidaturas efetivas ficou estável, em torno de metade da nominata, enquanto as listas dobraram; a priorização em 2022 não desapareceu, mudou de forma."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 181}
evidencia: {tipo: csv, referencia: "tese/reports/resultados-capitulo-3/05_concentracao_ano.csv"}
assessment: {status: partially_supported, confidence: media}
concerns:
  - "Descritivo: mediana NECr/C 51,4% → 53,7%; mediana C 4 → 9; média C 9,4 → 14,4 (não 'dobrou' na média)."
  - "'Não desapareceu': lift 2022 fora da faixa de permutação — sustentado. 'Mudou de forma' não é testado neste capítulo e a comparação entre eleições é sensível à composição (STA-3-003)."
agent: statistics-reviewer
```

## Verificações que passaram
- Todos os agregados nacionais do Top-NECr (ΣH, ΣG, Σk, A0, cobertura, precisão, lift) recomputados a partir de `candidaturas.parquet` coincidem com `15_cobertura_nacional.csv`, `benchmark_precisao_top_necr.csv`, `resumo_nacional.csv` e a tabela da nota formal, para competitivos (universo 7.626/9.672) e eleitos (7.630/9.675).
- Identidade lift-cobertura ≡ lift-precisão verificada (e já checada pelos scripts do autor).
- Média da permutação coincide com a expectativa analítica $G_l k_l/C_l$ (382,55 vs 382,54; 224,52 vs 224,57), i.e., o denominador do lift é o valor esperado correto do nulo declarado, com pesos fracionários.
- Faixa P2,5–P97,5 dos 10.000 sorteios de `sorteios_referencia.csv` (207–242 em 2018; 206–243 em 2022) reproduzida pela permutação (207–242; 206–243).
- Lifts do Top-X% todos > 1 (mínimo 1,375); precisão e lift acumulados não crescentes em τ; cobertura não decrescente (aninhamento).
- Números citados: 43,2/43,7%; 16,5/14,7%; 1,87/1,89; 86,7/92,6%; 19,2/12,4%; 1,98/2,12; 57,3/52,8% (Top-50%); 1,53/1,38 (Top-95%); 2.318/3.824 posições; 27% e 45% de crescimento.
- Listas com núcleo = lista inteira: 207 (2018) e 100 (2022), igual a `validade_interna.csv`.

## Limites desta revisão
- Cap. 4 (Kaplan-Meier, Cox, fractional logit) não foi avaliado neste run; `df_cox_survival.parquet` apenas localizado.
- Os intervalos de bootstrap são estabilidade sob reamostragem de listas/partidos de um universo observado, não erro amostral; foram usados só para dizer se as diferenças que o texto afirma são maiores que a variabilidade entre listas.
- O nulo "só recebedores" foi implementado como permutação de $g$ entre recebedores mantendo os pesos $w$; coincide com `validade_expost.csv` para eleitos e é a versão mais direta da alternativa listada pela nota formal. Outras alternativas (permutação condicionada a atributos, p.ex. sexo) só foram exploradas via estratificação em `sta_sexo_lift.py`.
- A reorganização de `tese/` durante o run (pastas movidas para `tese/reports/`) foi detectada e contornada; os hashes do `manifest.yaml` não foram reconferidos para os artefatos movidos, só para o capítulo. O chair deve conferir se os caminhos de figuras do `.qmd` (`relatorio-consolidado-capitulo-3/figuras/…`) ainda resolvem.
- Não avaliei se a definição de competitivo no texto corresponde ao código (measurement-reviewer) nem se os números batem com as figuras (results-reviewer).
