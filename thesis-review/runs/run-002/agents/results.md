# results-reviewer — Capítulo 3 — run-002

## Escopo e método

Leitura integral do capítulo atual (200 linhas), dos contratos e do template. Auditoria texto → PNG/CSV → código; recomputação da base de listas diretamente de `data/processed/rrd_df_novo.parquet` usando exclusivamente as funções de cálculo do gerador atual. Nenhuma figura ou tabela de produção foi regenerada. A seção de discussão está explicitamente fora do escopo por instrução do autor; sua situação não gera achado nem pesa no gate.

Arquivos principais: `tese/scripts/regenerar_figuras_cap3.py`, `tese/scripts/regressao_fracionaria_cap3.py`, `tese/reports/resultados-capitulo-3/{01_universos,02_competitivos_ano,05_concentracao_ano,15_cobertura_nacional,19_notas_redacao}.csv`, `tese/reports/lift-magnitude-partido/lift_por_magnitude.csv`, todos os quatro CSVs de `tese/reports/regressao-fracionaria/`, `tese/_quarto.yml` e `tese/apendice-a-formalizacao.qmd`. Não foram lidos relatórios de outros agentes.

Script reproduzível: `evidence/res_recompute.py`; saídas: `res_metricas_recomputadas.csv`, `res_resumo_recomputado.json`, `res_referencias.json`, `res_inventario_tokens_numericos.csv`. O último preserva integralmente todos os trechos com algarismos, incluindo anos bibliográficos, identificadores e largura de imagens. A tabela abaixo foi construída antes do julgamento e cobre os números substantivos; repetições de anos/identificadores de figura não são novas estimativas. Constantes matemáticas e números do exemplo fictício são distinguidos de resultados empíricos. Percentuais legais e números atribuídos a terceiros são declarados não auditados, sem alegar confirmação.

### Tabela de números

| Linha | Trecho | Número(s) | Artefato-fonte | Valor no artefato/recomputação | Bate? |
|---|---|---|---|---|---|
| 9 | O financiamento partidário já ocupava posição central antes das reformas que vedaram as doações empresariais e | 2014; 89,6% | referência silvacervi2017 | Número citado da literatura, não derivado da base | Não auditado: literatura |
| 11 | Nas eleições gerais imediatamente seguintes, em 2018, os partidos passaram a distribuir os recursos do FEFC. A | 2018; 2022; 30% | referências tse2018financiamentofeminino; tse2022criteriosfefc | Datas e regra legal, não resultado empírico | Não auditado: literatura/legislação |
| 27 | A análise utiliza registros de candidaturas, resultados eleitorais e prestação de contas provenientes do Porta | 7.630 (2018); 9.675 (2022) | tese/reports/resultados-capitulo-3/01_universos.csv | 7.630; 9.675 | Sim |
| 29 | O histórico eleitoral de cada candidatura destas eleições foi verificado pelo CPF, retroagindo até as eleições | 1998 | src/1_silver/gerar_rrd.py | Limite histórico declarado; não reconstruído | Fora da recomputação de resultados |
| 33 | A base de dados composta soma 859 listas em 2018 e 711 em 2022. Destas, 73 não receberam recursos partidários  | 859; 711; 73; 63; três; nenhum | tese/reports/resultados-capitulo-3/01_universos.csv | 859; 711; 73; 63; 3; 0 | Sim |
| 40 | NECr_l=\frac{1}{\sum_{i=1}^{C_l}s_{il}^{2}}, | 1; 2 (expoente) | eq-necr; regenerar_figuras_cap3.py:62 | 1 / soma dos quadrados das parcelas; definição | Sim |
| 44 | R_l=\sum_{i=1}^{C_l}R_{il}>0 . | 0 | regenerar_figuras_cap3.py:61 | NECr calculado apenas se total > 0 | Sim |
| 49 | O NECr de cada lista é convertido em inteiro por $k_l=\lfloor NECr_l+0{,}5\rfloor$, um arredondamento convenci | 0,5; 0 | regenerar_figuras_cap3.py:63-69 | floor(NECr+0,5); k=0 se recursos=0 | Sim |
| 53 | Para analisar a composição do *núcleo de priorizados* propõe-se um indicador binário que classifica uma *candi | 10% | src/2_gold/cap3_cs_features.py; candidato_competitivo | Limiar definicional; empregada flag atual | Definição, ver measurement |
| 57 | Estas regras de identificação de credenciais eleitorais prévias adaptam a proposta de @cheibubsin2020. Os auto | 10% | src/2_gold/cap3_cs_features.py; candidato_competitivo | Repetição do limiar; restrição ex-ante declarada | Definição, ver measurement |
| 63 | A @tbl-resumo-indicadores detalha o cálculo dos indicadores em um cenário fictício e a pergunta substantiva qu | 12; 4; 3; 2 | exemplo hipotético | 12 candidatos, 4 credenciais, k=3, H=2 | Sim |
| 67 | \| Precisão \| Dos candidatos priorizados, quantos possuem credenciais? \| $2 \div 3 \approx 66{,}7\%$ \| | 2; 3; 66,7% | aritmética | 100×2/3=66,6667% | Sim |
| 68 | \| Cobertura \| Dos candidatos com credenciais, quantos foram priorizados? \| $2 \div 4 = 50\%$ \| | 2; 4; 50% | aritmética | 100×2/4=50% | Sim |
| 69 | \| Referência aleatória \| Quantos candidatos com credenciais esperaríamos encontrar ao selecionar 3 dos 12 cand | 3; 12; 4; 12; 1 | aritmética | 3×4/12=1 | Sim |
| 70 | \| *Lift* \| Quantos acertos observamos em relação ao esperado ao acaso? \| $2 \div 1 = 2$ \| | 2; 1; 2 | aritmética | 2/1=2 | Sim |
| 74 | O *lift* igual a 2 neste cenário indica que esta nominata possui um núcleo priorizado com uma frequência de ca | 2; dobro | aritmética | 2 vezes o esperado | Sim |
| 82 | Dos 7.630 candidatos a Deputado Federal em 2018, 973 (12,75%) foram classificados como "competitivos" pelos cr | 7.630; 973; 12,75%; 9.675; 1.354; 13,99% | tese/reports/resultados-capitulo-3/01_universos.csv | 7.630; 973; 12,752294%; 9.675; 1.354; 13,994832% | Sim |
| 82 | Dos 7.630 candidatos a Deputado Federal em 2018, 973 (12,75%) foram classificados como "competitivos" pelos cr | 27%; 39% | aritmética dos universos | 26,802097%; 39,157246% | Sim |
| 84 | A @fig-amplitude apresenta a amplitude formal e efetiva das nominatas financiadas. Calculando-se a partir da b | quatro; nove; um; 1,22; 2,09 | evidence/res_resumo_recomputado.json | C mediana=4/9; F mediana=1/1; F média=1,222646/2,086420 | Sim |
| 88 | O Número Efetivo de Candidaturas em recursos, o NECr, também cresce: em 2018, na mediana, partidos concentrara | 1,88; 4,81 | tese/reports/resultados-capitulo-3/05_concentracao_ano.csv | 1,878129; 4,814424 | Sim |
| 94 | A @fig-concentracao compara o número formal de candidatos ao NECr nas nominatas financiadas. A lista mediana p | 1,95; 1,86; 51,36%; 53,65% | evidence/res_resumo_recomputado.json | 1,946906; 1,864093; 51,363652%; 53,645394% | Sim |
| 98 | Em conjunto, os resultados reforçam o argumento de @cheibubsin2020 sobre o afunilamento das candidaturas quand | metade | evidence/res_resumo_recomputado.json | Medianas NECr/C=51,36%/53,65%; aproximação de número efetivo | Sim como número efetivo, não proporção com R>0 |
| 104 | Entre as candidaturas competitivas, mais de 80% compõem o núcleo identificado pelo Top-NECr nas eleições de 20 | mais de 80%; 4/5; 42,8%; 43,6% | evidence/res_metricas_recomputadas.csv | Cobertura=80,858171/80,892312%; acaso=42,761306/43,602619% | Sim |
| 106 | A precisão nos mostra que 33,9 e 28,6% dos candidatos selecionados no núcleo Top-NECr estão entre os classific | 33,9%; 28,6%; 17,9%; 15,4% | evidence/res_metricas_recomputadas.csv | 33,940897; 28,642309; 17,949418; 15,438794% | Sim |
| 108 | O *lift* resume as comparações anteriores em um número: 1,89 em 2018 e 1,86 em 2022. Isto representa que o núc | 1,89; 1,86; quase 90% | evidence/res_metricas_recomputadas.csv | 1,890919; 1,855217; excedentes=89,0919/85,5217% | Sim |
| 116 | \| Pequeno (8–12) \| 1,40              \| 1,37              \| | 8–12; 1,40; 1,37 | tese/reports/lift-magnitude-partido/lift_por_magnitude.csv | 1,398174; 1,366705; intervalos são rótulos dos grupos | Sim |
| 117 | \| Médio (16–31)  \| 1,96              \| 2,00              \| | 16–31; 1,96; 2,00 | tese/reports/lift-magnitude-partido/lift_por_magnitude.csv | 1,958733; 1,998911; intervalos são rótulos dos grupos | Sim |
| 118 | \| Grande (39–70) \| 2,52              \| 2,37              \| | 39–70; 2,52; 2,37 | tese/reports/lift-magnitude-partido/lift_por_magnitude.csv | 2,516292; 2,372097; intervalos são rótulos dos grupos | Sim |
| 123 | O Top-NECr depende de um corte que separa o núcleo priorizado do restante da nominata. Esta seção examina a me | 1998 | src/1_silver/gerar_rrd.py | Repetição do início do histórico | Não reconstruído |
| 128 | E[s_{il}\mid X_l]=\frac{\exp(x_{il}'\beta)}{\sum_{j=1}^{C_l}\exp(x_{jl}'\beta)} . | 1 (índice inferior) | equação softmax | Constante de indexação, não resultado | Sim |
| 133 | Os resultados são apresentados como razões de parcelas. Para duas candidaturas da mesma lista, a razão entre s | uma unidade | tese/reports/regressao-fracionaria/coeficientes.csv | incremento +1 nas contagens/binárias, +10 p.p. em votação | Sim |
| 135 | As covariáveis de interesse reproduzem, de forma desagregada, os critérios usados para identificar as credenci | 10%; uma; 7.254; 649; 9.263; 623 | tese/reports/regressao-fracionaria/amostra.csv | limiar=10%; filtro C>1; n=7.254/9.263; listas=649/623 | Sim |
| 137 | As razões estimadas estão na @fig-reg-frac. Vitórias anteriores para todos os cargos estão associadas a parcel | 2,00; 1,55; dois; quatro | tese/reports/regressao-fracionaria/coeficientes.csv | DF=2,000623/1,551393; razão de +2 vitórias em 2018=4,002491 | Sim |
| 137 | As razões estimadas estão na @fig-reg-frac. Vitórias anteriores para todos os cargos estão associadas a parcel | 1,71; 1,48; 1,57; 1,42 | tese/reports/regressao-fracionaria/coeficientes.csv | DE=1,712108/1,477378; prefeito=1,574807/1,422692 | Sim |
| 137 | As razões estimadas estão na @fig-reg-frac. Vitórias anteriores para todos os cargos estão associadas a parcel | 3,76; 3,45; 3,59 | tese/reports/regressao-fracionaria/coeficientes.csv | senador=3,759311/3,450653; governador 2018=3,586949 | Sim |
| 137 | As razões estimadas estão na @fig-reg-frac. Vitórias anteriores para todos os cargos estão associadas a parcel | 1,30; 1,18 | tese/reports/regressao-fracionaria/coeficientes.csv | vereador=1,298639/1,181482 | Sim |
| 139 | O critério de votação também tem associação própria. Entre candidaturas sem vitória acima de vereador, ter alc | 10%; 2,89; 1,70 | tese/reports/regressao-fracionaria/coeficientes.csv | qe_sem_vitoria=2,886261/1,701290 | Sim |
| 139 | O critério de votação também tem associação própria. Entre candidaturas sem vitória acima de vereador, ter alc | dez pontos percentuais; 15%; 11% | tese/reports/regressao-fracionaria/coeficientes.csv | incremento=0,1; exp(0,1β)−1=15,199805/10,792497% | Sim |
| 141 | Quando os dois critérios são reunidos no indicador binário usado no Top-NECr, a candidatura com credencial pré | dois; 8,16; 4,58; 20,3; 12,1 | tese/reports/regressao-fracionaria/coeficientes.csv; ames.csv | R1=8,157191/4,583564; AME=20,276840/12,081646 p.p.; dois critérios da flag | Sim |
| 145 | A @tbl-cap3-03-premio-magnitude apresenta essa razão por grupo de magnitude, estimada pela interação entre o i | 4,76; 10,61; 13,48; 2,95; 5,57; 7,99 | tese/reports/regressao-fracionaria/interacao_magnitude.csv | 4,759999; 10,614010; 13,478327; 2,947403; 5,569094; 7,989421 | Sim |
| 147 | Ser mulher está associado a uma parcela maior dos recursos intralista nas duas eleições, com razões de 1,44 em | 1,44; 1,32 | tese/reports/regressao-fracionaria/coeficientes.csv | R2 mulher=1,442963/1,323580 | Sim |
| 149 | As candidaturas negras recebem parcelas menores que as de seus correligionários nas duas eleições. Em 2018, su | 74%; 0,93 | tese/reports/regressao-fracionaria/coeficientes.csv | R2 negra=0,735958/0,927862; IC2022=[0,867658;0,992244]; p=0,028707 | Sim |
| 151 | ![Prêmio das credenciais eleitorais prévias na alocação intralista de recursos partidários em 2018 e 2022: raz | 2018; 2022; 1; 95% | figs/cap3_regressao_fracionaria.png; tese/reports/regressao-fracionaria/coeficientes.csv | Anos, linha em 1 e IC95% correspondem ao arquivo | Sim |
| 155 | \| Pequeno (8–12) \| 4,76       \| 3,81 – 5,95   \| 2,95       \| 2,58 – 3,37 \| | 8–12; 4,76; 3,81–5,95; 2,95; 2,58–3,37 | tese/reports/regressao-fracionaria/interacao_magnitude.csv | 4,759999 [3,805083;5,954558]; 2,947403 [2,577981;3,369762] | Sim |
| 156 | \| Médio (16–31)  \| 10,61      \| 8,09 – 13,92  \| 5,57       \| 4,72 – 6,57 \| | 16–31; 10,61; 8,09–13,92; 5,57; 4,72–6,57 | tese/reports/regressao-fracionaria/interacao_magnitude.csv | 10,614010 [8,090332;13,924917]; 5,569094 [4,719819;6,571186] | Sim |
| 157 | \| Grande (39–70) \| 13,48      \| 10,69 – 16,99 \| 7,99       \| 6,58 – 9,70 \| | 39–70; 13,48; 10,69–16,99; 7,99; 6,58–9,70 | tese/reports/regressao-fracionaria/interacao_magnitude.csv | 13,478327 [10,693270;16,988749]; 7,989421 [6,581656;9,698295] | Sim |
| 164 | A @fig-cap3-03-top-necr-eleicao repete o exercício de correspondência do Top-NECr, mas desta vez a referência  | 86,7%; 92,6%; dobro | evidence/res_metricas_recomputadas.csv | 86,744639/92,630079%; lift=1,981544/2,117435 (aproximação explicitada L166) | Sim |
| 166 | Já a precisão é de 19,2 e 12,4% em 2018 e 2022. Esta menor proporção reflete sobretudo o tamanho menor do alvo | 19,2%; 12,4%; 513; duas; 1,98; 2,12; dobro | evidence/res_metricas_recomputadas.csv; tese/reports/resultados-capitulo-3/01_universos.csv | 19,197584/12,426577%; 513/ano; lifts=1,981544/2,117435 | Sim |
| 174 | \| Pequeno (8–12) \| 1,50         \| 1,44         \| | 8–12; 1,50; 1,44 | tese/reports/lift-magnitude-partido/lift_por_magnitude.csv | 1,498595; 1,443861 | Sim |
| 175 | \| Médio (16–31)  \| 2,07         \| 2,40         \| | 16–31; 2,07; 2,40 | tese/reports/lift-magnitude-partido/lift_por_magnitude.csv | 2,066886; 2,397709 | Sim |
| 176 | \| Grande (39–70) \| 2,45         \| 2,63         \| | 39–70; 2,45; 2,63 | tese/reports/lift-magnitude-partido/lift_por_magnitude.csv | 2,447180; 2,631874 | Sim |
| 183 | Para avaliar a sensibilidade dos achados deste capítulo sobre a arbitrariedade do recorte do núcleo de candida | 50; 60; 70; 80; 90; 95% | tese/scripts/regenerar_figuras_cap3.py:36 | TAUS=[50,60,70,80,90,95] | Sim |
| 185 | A @fig-cap3-04-topx-competitividade mostra um padrão consistente entre as métricas de 2018 e 2022. Ao consider | 2018; 2022; Top-50%; mais de 50% | evidence/res_metricas_recomputadas.csv | Cobertura Top50=56,692605/50,967504% | Sim |
| 187 | Quanto mais se restringe o núcleo ao topo da distribuição de recursos de campanha partidários, maior é a prese | um; Top-95%; 1,55; 1,37 | evidence/res_metricas_recomputadas.csv | Todos lifts>1; Top95=1,545648/1,369754 | Sim |
| 193 | Já a @fig-cap3-05-topx-eleicao apresenta os testes realizados com o resultado eleitoral posterior como referên | um | evidence/res_metricas_recomputadas.csv | Todos lifts dos eleitos>1; mínimos=1,566021/1,464544 | Sim |

### Inspeção visual de cada PNG

Todos os sete PNGs foram abertos e inspecionados, não apenas localizados. Não há `manifesto-figuras.csv` entre os arquivos enumerados do repositório; a conferência de legendas foi feita diretamente contra a figura e seu código, sem converter a ausência desse instrumento auxiliar em defeito do capítulo.

| Figura e linha | O que mostra | Resultado |
|---|---|---|
| `figs/cap3_fig_amplitude_barras.png` — 86 | Dois painéis, média e mediana de C, F e NECr em 2018/2022, universo financiado. Médias F=1,22/2,09; medianas NECr=1,88/4,81. | Valores/legenda conferem. |
| `figs/cap3_fig_concentracao_barras.png` — 96 | Média e mediana de NECr/C; medianas 51,36%/53,65%. | Valores/legenda conferem. |
| `figs/cap3_fig_top_necr.png` — 110 | Cobertura, precisão e lift de credenciais; duas eleições; observado e referência aleatória. | Valores/legenda conferem. |
| `figs/cap3_regressao_fracionaria.png` — 151 | Forest plot R2 de razões intralista, IC95%, eixo log e linha 1; governador 2022=1,33 com IC incluindo 1. Inclui termo QE sem vitória e voto em +10 p.p. | Atualizada e coerente com CSV 18/09. Os rótulos de alguns pares estão próximos, mas legíveis na imagem fonte. |
| `figs/cap3_fig_top_necr_eleicao.png` — 168 | Três painéis para eleitos; cobertura 86,7%/92,6%, precisão 19,2%/12,4%, lift 1,98/2,12. | Valores/legenda conferem. |
| `figs/cap3_fig_topx_competitividade.png` — 191 | Seis painéis, dois anos × três métricas, seis limiares, observado/acaso; cobertura crescente e lift decrescente. | Dados conferem; referência horizontal e marcador ampliado sem chave, RES-3-001. |
| `figs/cap3_fig_topx_eleicao.png` — 195 | Mesma estrutura para eleitos, cobertura maior do que a de competitivos, lift>1. | Dados conferem; mesma omissão de chave. |

## Avaliação macro

A cadeia empírica se sustenta no escopo de resultados: amplitude/concentração descrevem a distribuição; o Top-NECr identifica sobrerrepresentação de credenciais; o modelo intralista testa a associação sem o corte; Top-X e sucesso eleitoral posterior complementam a leitura. A recomputação confirma os números nacionais e a monotonicidade alegada para os grupos de magnitude e os limiares observados. O prêmio intralista de 18/09 está sincronizado entre texto, figura e CSVs, inclusive o componente de votação prévia e os controles.

Não encontrei erro numérico central nem artefato ausente. As ressalvas abaixo são de identificação dos objetos exibidos: os gráficos de sensibilidade têm convenções visuais sem legenda e as três tabelas por magnitude carecem de título explicativo. São ajustes locais, sem exigir refazer a análise. As diferenças de médias de competitivos entre `02_competitivos_ano.csv` e o texto são legítimas: o CSV cobre todas as listas; a figura e o parágrafo usam listas financiadas. Não se deve substituir 1,22/2,09 por 1,13/1,90.

## Achados

```yaml
id: RES-3-001
titulo: "Figuras Top-X não identificam a linha Top-NECr e o destaque do limiar 80%"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 191
  secao: "Sensibilidade ao limiar Top-X%"
  trecho: "Sensibilidade da cobertura, precisão e *lift* de candidatos com credenciais eleitorais prévias ao limiar Top-X%, por eleição."
afirmacao_do_autor: "As figuras permitem acompanhar a sensibilidade das três métricas ao limiar Top-X%."
problema: "Há duas convenções não identificadas na legenda/caption: linha horizontal tracejada e marcador ampliado em 80%. O leitor pode confundir a linha com outra referência aleatória ou atribuir ao limiar destacado uma escolha substantiva que o texto não explica."
evidencia:
  tipo: codigo
  fontes:
    - tese/scripts/regenerar_figuras_cap3.py:224
    - tese/scripts/regenerar_figuras_cap3.py:227
    - figs/cap3_fig_topx_competitividade.png
    - figs/cap3_fig_topx_eleicao.png
    - tese/03-medindo-coordenacao-intrapartidaria.qmd:195
  detalhe: "idx80 destaca 80%; ax.axhline(ref,...) desenha a métrica do Top-NECr, mas a chave possui apenas Observado e Referência aleatória. Confirmado visualmente em ambos os PNGs."
severidade: MINOR
confianca: alta
recomendacao: "Identificar a linha tracejada como Top-NECr na chave/caption; explicar o destaque 80% ou retirar a ampliação do marcador se não houver função analítica."
claims: [C3.11.01, C3.11.02]
```

```yaml
id: RES-3-002
titulo: "As três tabelas por magnitude possuem rótulo de referência, mas não título descritivo"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 119
  secao: "Priorização financeira pelo Top-NECr"
  trecho: ": {#tbl-cap3-01-lift-magnitude}"
afirmacao_do_autor: "A tabela apresenta o lift agregado por magnitude; a tabela posterior apresenta razões de parcelas."
problema: "As captions das linhas 119, 158 e 177 contêm somente o identificador. Fora do parágrafo de chamada, a primeira e a terceira tabelas não explicitam no cabeçalho que a estatística é lift; a segunda não identifica que a razão é de parcelas esperadas do modelo intralista."
evidencia:
  tipo: textual
  fontes:
    - tese/03-medindo-coordenacao-intrapartidaria.qmd:114
    - tese/03-medindo-coordenacao-intrapartidaria.qmd:119
    - tese/03-medindo-coordenacao-intrapartidaria.qmd:153
    - tese/03-medindo-coordenacao-intrapartidaria.qmd:158
    - tese/03-medindo-coordenacao-intrapartidaria.qmd:172
    - tese/03-medindo-coordenacao-intrapartidaria.qmd:177
  detalhe: "São três captions vazias. Os números conferem nos CSVs; o problema é a identificação autônoma da estatística, não seus valores."
severidade: MINOR
confianca: alta
recomendacao: "Adicionar títulos que nomeiem a estatística e o alvo: lift de credenciais, razão intralista de parcelas por credencial, lift dos eleitos; manter os identificadores atuais."
claims: [C3.7.07, C3.8.07, C3.10.04]
```

## Claims

```yaml
{
  "claim_id": "C3.1.01",
  "capitulo": 3,
  "secao": "Dados",
  "claim": "2018: 7.630 candidaturas, 859 listas, 73 sem recursos e 3 eleitos nessas listas.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 27
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/resultados-capitulo-3/01_universos.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.1.02",
  "capitulo": 3,
  "secao": "Dados",
  "claim": "2022: 9.675 candidaturas, 711 listas, 63 sem recursos e nenhum eleito nessas listas.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 33
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/resultados-capitulo-3/01_universos.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.4.01",
  "capitulo": 3,
  "secao": "Composição do núcleo",
  "claim": "O exemplo com C=12, G=4, k=3, H=2 tem precisão 66,7%, cobertura 50%, esperado 1 e lift 2.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 63
  },
  "evidencia": {
    "tipo": "equacao",
    "referencia": "tese/03-medindo-coordenacao-intrapartidaria.qmd:65-70"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.6.01",
  "capitulo": 3,
  "secao": "Amplitude",
  "claim": "Há 973 competitivos (12,75%) em 2018 e 1.354 (13,99%) em 2022.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 82
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/resultados-capitulo-3/01_universos.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.6.02",
  "capitulo": 3,
  "secao": "Amplitude",
  "claim": "As candidaturas crescem 27% e as competitivas 39%.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 82
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_resumo_recomputado.json"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.6.03",
  "capitulo": 3,
  "secao": "Amplitude",
  "claim": "Nas listas financiadas, mediana C=4/9; mediana F=1/1; média F=1,22/2,09.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 84
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_resumo_recomputado.json"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.6.04",
  "capitulo": 3,
  "secao": "Amplitude",
  "claim": "NECr mediano financiado=1,88 em 2018 e 4,81 em 2022.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 88
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_resumo_recomputado.json"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.6.05",
  "capitulo": 3,
  "secao": "Amplitude",
  "claim": "C/NECr mediano=1,95/1,86; NECr/C mediano=51,36%/53,65%.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 94
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_resumo_recomputado.json"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.6.06",
  "capitulo": 3,
  "secao": "Amplitude",
  "claim": "A figura amplitude apresenta médias e medianas no universo financiado.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 86
  },
  "evidencia": {
    "tipo": "figura",
    "referencia": "figs/cap3_fig_amplitude_barras.png"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.6.07",
  "capitulo": 3,
  "secao": "Amplitude",
  "claim": "A figura concentração apresenta NECr/C e coincide com os percentuais do texto.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 96
  },
  "evidencia": {
    "tipo": "figura",
    "referencia": "figs/cap3_fig_concentracao_barras.png"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.7.01",
  "capitulo": 3,
  "secao": "Top-NECr",
  "claim": "2018: cobertura competitivos=80,86% contra 42,76% ao acaso; precisão=33,94% contra 17,95%.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 104
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.7.02",
  "capitulo": 3,
  "secao": "Top-NECr",
  "claim": "2018: lift competitivos=1,8909, arredondado como no texto.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 108
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.7.03",
  "capitulo": 3,
  "secao": "Top-NECr",
  "claim": "2022: cobertura competitivos=80,89% contra 43,60% ao acaso; precisão=28,64% contra 15,44%.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 104
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.7.04",
  "capitulo": 3,
  "secao": "Top-NECr",
  "claim": "2022: lift competitivos=1,8552, arredondado como no texto.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 108
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.7.05",
  "capitulo": 3,
  "secao": "Top-NECr",
  "claim": "Os dois anos têm cobertura maior que 80%.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 104
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.7.06",
  "capitulo": 3,
  "secao": "Top-NECr",
  "claim": "A figura apresenta os três indicadores e as respectivas referências nas duas eleições.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 110
  },
  "evidencia": {
    "tipo": "figura",
    "referencia": "figs/cap3_fig_top_necr.png"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.7.07",
  "capitulo": 3,
  "secao": "Top-NECr",
  "claim": "Lift cresce nos três grupos de magnitude em ambos os anos; todos os seis valores conferem.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 112
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/lift-magnitude-partido/lift_por_magnitude.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.8.01",
  "capitulo": 3,
  "secao": "Prêmio intralista",
  "claim": "Amostras=7.254/649 e 9.263/623 candidaturas/listas.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 135
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/regressao-fracionaria/amostra.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.8.02",
  "capitulo": 3,
  "secao": "Prêmio intralista",
  "claim": "As razões de vitória de deputado federal, estadual, prefeito, senador e vereador e governador 2018 conferem.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 137
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/regressao-fracionaria/coeficientes.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.8.03",
  "capitulo": 3,
  "secao": "Prêmio intralista",
  "claim": "QE sem vitória tem razões 2,89/1,70; +10 p.p. de voto anterior têm razões 1,1520/1,1079.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 139
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/regressao-fracionaria/coeficientes.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.8.04",
  "capitulo": 3,
  "secao": "Prêmio intralista",
  "claim": "R1 tem razão 8,16/4,58 e AME de 20,3/12,1 p.p.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 141
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/regressao-fracionaria/coeficientes.csv; tese/reports/regressao-fracionaria/ames.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.8.05",
  "capitulo": 3,
  "secao": "Prêmio intralista",
  "claim": "Mulher tem razão R2=1,44/1,32.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 147
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/regressao-fracionaria/coeficientes.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.8.06",
  "capitulo": 3,
  "secao": "Prêmio intralista",
  "claim": "Negra tem razão R2=0,74/0,93, ambas com IC95% abaixo de 1.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 149
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/regressao-fracionaria/coeficientes.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.8.07",
  "capitulo": 3,
  "secao": "Prêmio intralista",
  "claim": "Razões por magnitude e seis IC95% conferem; interação contínua positiva com p<0,001 nos dois anos.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 145
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/regressao-fracionaria/interacao_magnitude.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.8.08",
  "capitulo": 3,
  "secao": "Prêmio intralista",
  "claim": "Forest plot representa R2 atualizado, incluindo critério QE, voto escalado, controles e IC95%.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 151
  },
  "evidencia": {
    "tipo": "figura",
    "referencia": "figs/cap3_regressao_fracionaria.png"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.10.01",
  "capitulo": 3,
  "secao": "Correspondência com eleição",
  "claim": "2018: cobertura=86,7446%, precisão=19,1976%, lift=1,9815; alvo de 513 eleitos.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 164
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.10.02",
  "capitulo": 3,
  "secao": "Correspondência com eleição",
  "claim": "2022: cobertura=92,6301%, precisão=12,4266%, lift=2,1174; alvo de 513 eleitos.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 166
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.10.03",
  "capitulo": 3,
  "secao": "Correspondência com eleição",
  "claim": "A figura Top-NECr dos eleitos coincide com as métricas nacionais e suas referências.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 168
  },
  "evidencia": {
    "tipo": "figura",
    "referencia": "figs/cap3_fig_top_necr_eleicao.png"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.10.04",
  "capitulo": 3,
  "secao": "Correspondência com eleição",
  "claim": "Lifts dos eleitos crescem nos grupos de magnitude nos dois anos; seis valores conferem.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 170
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "tese/reports/lift-magnitude-partido/lift_por_magnitude.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.11.01",
  "capitulo": 3,
  "secao": "Top-X",
  "claim": "Figura de credenciais representa corretamente os seis limiares e três métricas em cada ano.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 191
  },
  "evidencia": {
    "tipo": "figura",
    "referencia": "figs/cap3_fig_topx_competitividade.png"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [
    "RES-3-001: duas convenções visuais sem chave."
  ],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.11.02",
  "capitulo": 3,
  "secao": "Top-X",
  "claim": "Figura dos eleitos representa corretamente os seis limiares e três métricas em cada ano.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 195
  },
  "evidencia": {
    "tipo": "figura",
    "referencia": "figs/cap3_fig_topx_eleicao.png"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [
    "RES-3-001: mesmas convenções sem chave."
  ],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.11.03",
  "capitulo": 3,
  "secao": "Top-X",
  "claim": "Cobertura de competitivos supera 50% no Top50 em ambos os anos (56,69%; 50,97%).",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 185
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.11.04",
  "capitulo": 3,
  "secao": "Top-X",
  "claim": "Lift dos competitivos diminui ao elevar o limiar, mas permanece >1; Top95=1,55/1,37.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 187
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.11.05",
  "capitulo": 3,
  "secao": "Top-X",
  "claim": "Há mais competitivos dentro do que fora do núcleo agregado em cada limiar/ano, pois a cobertura supera 50%.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 189
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [
    "Leitura nacional agregada; não é afirmação sobre cada lista individual."
  ],
  "agent": "results-reviewer"
}
```

```yaml
{
  "claim_id": "C3.11.06",
  "capitulo": 3,
  "secao": "Top-X",
  "claim": "Em todos os limiares/anos, a cobertura dos eleitos supera a dos competitivos, e o lift dos eleitos é >1.",
  "localizacao": {
    "arquivo": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "linha": 193
  },
  "evidencia": {
    "tipo": "csv",
    "referencia": "evidence/res_metricas_recomputadas.csv"
  },
  "assessment": {
    "status": "supported",
    "confidence": "alta"
  },
  "concerns": [],
  "agent": "results-reviewer"
}
```

## Verificações que passaram

- Universos e competitivos reproduzidos diretamente da base atual; o descompasso histórico das flags não reaparece nos números desta versão.
- Todas as porcentagens, razões, contagens, ICs e médias de resultados auditadas concordam com CSVs e/ou recomputação, nos arredondamentos do texto.
- Prêmio intralista atualizado em 18/09: amostras, R2, R1, AMEs e interação coincidem com os artefatos atuais; a figura contém QE sem vitória e voto em incremento de 10 p.p.
- Sete figuras existentes, abertas e coerentes com suas chamadas. Quatro tabelas: exemplo hipotético e três tabelas por magnitude; nenhuma divergência de valor.
- Todas as referências `@fig-`, `@tbl-`, `@sec-`, `@eq-` possuem definição no livro. `sec-apendice-formal` existe no apêndice incluído no `_quarto.yml`.
- Não se identificou placeholder numérico: `X%` em Top-X% designa deliberadamente a família de limiares, e não uma pendência.

## Limites desta revisão

- O valor 89,6% atribuído a Silva/Cervi e as datas/regras legais não foram confrontados com fontes externas; pertencem ao exame de literatura. Não os classifico como resultados confirmados.
- O histórico desde 1998 e a validade do critério de credencial não foram reconstruídos neste escopo. A recomputação toma a base atual como entrada; os modelos foram conferidos contra os CSVs e código, sem nova estimação.
- A fala sobre ausência de associação de governador em 2022 foi lida como ausência de associação estatisticamente discernível: a estimativa é positiva (1,33), mas o IC contém 1 e p=0,10. Se desejado, explicitar “estatisticamente distinguível de 1” elimina ambiguidade, sem alterar o resultado.
- A soma de origem partidária não é validada aqui como soma exclusiva FP/FEFC; `19_notas_redacao.csv` e o código alertam para a distinção, a cargo de measurement/methodology.
- A frase “todos os cargos” (L137) foi confrontada com os seis cargos efetivamente exibidos no modelo. A presença de Presidente apenas na definição geral deve ser resolvida no exame de mensuração; nenhum efeito presidencial foi inventado para completar a figura.
- Sem renderização do livro: não avaliada a paginação, a quebra de captions ou o tamanho final dos gráficos na página. Inspeção realizada nas imagens fonte.
- Não há gate adverso de resultados: 0 CRITICAL, 0 MAJOR, 0 MODERATE e 2 MINOR. A discussão não foi avaliada.
