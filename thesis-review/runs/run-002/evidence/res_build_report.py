from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
qmd='tese/03-medindo-coordenacao-intrapartidaria.qmd'
lines=(ROOT/qmd).read_text(encoding='utf-8').splitlines()
source='tese/reports/resultados-capitulo-3/'
reg='tese/reports/regressao-fracionaria/'
checks=[]
def check(line,number,artifact,value,ok='Sim',excerpt=None):
    checks.append((line,excerpt or lines[line-1][:110],number,artifact,value,ok))
check(9,'2014; 89,6%', 'referência silvacervi2017','Número citado da literatura, não derivado da base','Não auditado: literatura')
check(11,'2018; 2022; 30%', 'referências tse2018financiamentofeminino; tse2022criteriosfefc','Datas e regra legal, não resultado empírico','Não auditado: literatura/legislação')
check(27,'7.630 (2018); 9.675 (2022)',source+'01_universos.csv','7.630; 9.675')
check(29,'1998','src/1_silver/gerar_rrd.py','Limite histórico declarado; não reconstruído','Fora da recomputação de resultados')
check(33,'859; 711; 73; 63; três; nenhum',source+'01_universos.csv','859; 711; 73; 63; 3; 0')
check(40,'1; 2 (expoente)', 'eq-necr; regenerar_figuras_cap3.py:62','1 / soma dos quadrados das parcelas; definição')
check(44,'0', 'regenerar_figuras_cap3.py:61','NECr calculado apenas se total > 0')
check(49,'0,5; 0','regenerar_figuras_cap3.py:63-69','floor(NECr+0,5); k=0 se recursos=0')
check(53,'10%', 'src/2_gold/cap3_cs_features.py; candidato_competitivo','Limiar definicional; empregada flag atual','Definição, ver measurement')
check(57,'10%', 'src/2_gold/cap3_cs_features.py; candidato_competitivo','Repetição do limiar; restrição ex-ante declarada','Definição, ver measurement')
check(63,'12; 4; 3; 2','exemplo hipotético','12 candidatos, 4 credenciais, k=3, H=2')
check(67,'2; 3; 66,7%', 'aritmética','100×2/3=66,6667%')
check(68,'2; 4; 50%', 'aritmética','100×2/4=50%')
check(69,'3; 12; 4; 12; 1', 'aritmética','3×4/12=1')
check(70,'2; 1; 2','aritmética','2/1=2')
check(74,'2; dobro','aritmética','2 vezes o esperado')
check(82,'7.630; 973; 12,75%; 9.675; 1.354; 13,99%',source+'01_universos.csv','7.630; 973; 12,752294%; 9.675; 1.354; 13,994832%')
check(82,'27%; 39%', 'aritmética dos universos','26,802097%; 39,157246%')
check(84,'quatro; nove; um; 1,22; 2,09','evidence/res_resumo_recomputado.json','C mediana=4/9; F mediana=1/1; F média=1,222646/2,086420')
check(88,'1,88; 4,81',source+'05_concentracao_ano.csv','1,878129; 4,814424')
check(94,'1,95; 1,86; 51,36%; 53,65%','evidence/res_resumo_recomputado.json','1,946906; 1,864093; 51,363652%; 53,645394%')
check(98,'metade','evidence/res_resumo_recomputado.json','Medianas NECr/C=51,36%/53,65%; aproximação de número efetivo','Sim como número efetivo, não proporção com R>0')
check(104,'mais de 80%; 4/5; 42,8%; 43,6%','evidence/res_metricas_recomputadas.csv','Cobertura=80,858171/80,892312%; acaso=42,761306/43,602619%')
check(106,'33,9%; 28,6%; 17,9%; 15,4%','evidence/res_metricas_recomputadas.csv','33,940897; 28,642309; 17,949418; 15,438794%')
check(108,'1,89; 1,86; quase 90%','evidence/res_metricas_recomputadas.csv','1,890919; 1,855217; excedentes=89,0919/85,5217%')
for line,number,value in [(116,'8–12; 1,40; 1,37','1,398174; 1,366705'),(117,'16–31; 1,96; 2,00','1,958733; 1,998911'),(118,'39–70; 2,52; 2,37','2,516292; 2,372097')]:
    check(line,number,'tese/reports/lift-magnitude-partido/lift_por_magnitude.csv',value+'; intervalos são rótulos dos grupos')
check(123,'1998','src/1_silver/gerar_rrd.py','Repetição do início do histórico','Não reconstruído')
check(128,'1 (índice inferior)','equação softmax','Constante de indexação, não resultado')
check(133,'uma unidade',reg+'coeficientes.csv','incremento +1 nas contagens/binárias, +10 p.p. em votação')
check(135,'10%; uma; 7.254; 649; 9.263; 623',reg+'amostra.csv','limiar=10%; filtro C>1; n=7.254/9.263; listas=649/623')
check(137,'2,00; 1,55; dois; quatro',reg+'coeficientes.csv','DF=2,000623/1,551393; razão de +2 vitórias em 2018=4,002491')
check(137,'1,71; 1,48; 1,57; 1,42',reg+'coeficientes.csv','DE=1,712108/1,477378; prefeito=1,574807/1,422692')
check(137,'3,76; 3,45; 3,59',reg+'coeficientes.csv','senador=3,759311/3,450653; governador 2018=3,586949')
check(137,'1,30; 1,18',reg+'coeficientes.csv','vereador=1,298639/1,181482')
check(139,'10%; 2,89; 1,70',reg+'coeficientes.csv','qe_sem_vitoria=2,886261/1,701290')
check(139,'dez pontos percentuais; 15%; 11%',reg+'coeficientes.csv','incremento=0,1; exp(0,1β)−1=15,199805/10,792497%')
check(141,'dois; 8,16; 4,58; 20,3; 12,1',reg+'coeficientes.csv; ames.csv','R1=8,157191/4,583564; AME=20,276840/12,081646 p.p.; dois critérios da flag')
check(145,'4,76; 10,61; 13,48; 2,95; 5,57; 7,99',reg+'interacao_magnitude.csv','4,759999; 10,614010; 13,478327; 2,947403; 5,569094; 7,989421')
check(147,'1,44; 1,32',reg+'coeficientes.csv','R2 mulher=1,442963/1,323580')
check(149,'74%; 0,93',reg+'coeficientes.csv','R2 negra=0,735958/0,927862; IC2022=[0,867658;0,992244]; p=0,028707')
check(151,'2018; 2022; 1; 95%','figs/cap3_regressao_fracionaria.png; '+reg+'coeficientes.csv','Anos, linha em 1 e IC95% correspondem ao arquivo')
for line,number,value in [(155,'8–12; 4,76; 3,81–5,95; 2,95; 2,58–3,37','4,759999 [3,805083;5,954558]; 2,947403 [2,577981;3,369762]'),(156,'16–31; 10,61; 8,09–13,92; 5,57; 4,72–6,57','10,614010 [8,090332;13,924917]; 5,569094 [4,719819;6,571186]'),(157,'39–70; 13,48; 10,69–16,99; 7,99; 6,58–9,70','13,478327 [10,693270;16,988749]; 7,989421 [6,581656;9,698295]')]:
    check(line,number,reg+'interacao_magnitude.csv',value)
check(164,'86,7%; 92,6%; dobro','evidence/res_metricas_recomputadas.csv','86,744639/92,630079%; lift=1,981544/2,117435 (aproximação explicitada L166)')
check(166,'19,2%; 12,4%; 513; duas; 1,98; 2,12; dobro','evidence/res_metricas_recomputadas.csv; '+source+'01_universos.csv','19,197584/12,426577%; 513/ano; lifts=1,981544/2,117435')
for line,number,value in [(174,'8–12; 1,50; 1,44','1,498595; 1,443861'),(175,'16–31; 2,07; 2,40','2,066886; 2,397709'),(176,'39–70; 2,45; 2,63','2,447180; 2,631874')]:
    check(line,number,'tese/reports/lift-magnitude-partido/lift_por_magnitude.csv',value)
check(183,'50; 60; 70; 80; 90; 95%', 'tese/scripts/regenerar_figuras_cap3.py:36','TAUS=[50,60,70,80,90,95]')
check(185,'2018; 2022; Top-50%; mais de 50%','evidence/res_metricas_recomputadas.csv','Cobertura Top50=56,692605/50,967504%')
check(187,'um; Top-95%; 1,55; 1,37','evidence/res_metricas_recomputadas.csv','Todos lifts>1; Top95=1,545648/1,369754')
check(193,'um','evidence/res_metricas_recomputadas.csv','Todos lifts dos eleitos>1; mínimos=1,566021/1,464544')

header='''# results-reviewer — Capítulo 3 — run-002

## Escopo e método

Leitura integral do capítulo atual (200 linhas), dos contratos e do template. Auditoria texto → PNG/CSV → código; recomputação da base de listas diretamente de `data/processed/rrd_df_novo.parquet` usando exclusivamente as funções de cálculo do gerador atual. Nenhuma figura ou tabela de produção foi regenerada. A seção de discussão está explicitamente fora do escopo por instrução do autor; sua situação não gera achado nem pesa no gate.

Arquivos principais: `tese/scripts/regenerar_figuras_cap3.py`, `tese/scripts/regressao_fracionaria_cap3.py`, `tese/reports/resultados-capitulo-3/{01_universos,02_competitivos_ano,05_concentracao_ano,15_cobertura_nacional,19_notas_redacao}.csv`, `tese/reports/lift-magnitude-partido/lift_por_magnitude.csv`, todos os quatro CSVs de `tese/reports/regressao-fracionaria/`, `tese/_quarto.yml` e `tese/apendice-a-formalizacao.qmd`. Não foram lidos relatórios de outros agentes.

Script reproduzível: `evidence/res_recompute.py`; saídas: `res_metricas_recomputadas.csv`, `res_resumo_recomputado.json`, `res_referencias.json`, `res_inventario_tokens_numericos.csv`. O último preserva integralmente todos os trechos com algarismos, incluindo anos bibliográficos, identificadores e largura de imagens. A tabela abaixo foi construída antes do julgamento e cobre os números substantivos; repetições de anos/identificadores de figura não são novas estimativas. Constantes matemáticas e números do exemplo fictício são distinguidos de resultados empíricos. Percentuais legais e números atribuídos a terceiros são declarados não auditados, sem alegar confirmação.

### Tabela de números

| Linha | Trecho | Número(s) | Artefato-fonte | Valor no artefato/recomputação | Bate? |
|---|---|---|---|---|---|
'''
rows=['| '+' | '.join(str(x).replace('|','\\|') for x in row)+' |' for row in checks]
figures='''

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
claims: [C3.13.01, C3.13.02]
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
claims: [C3.8.07, C3.9.07, C3.12.04]
```

## Claims

'''
claims=[]
def claim(id,sec,text,line,artifact,status='supported',concerns=None,kind='csv'):
    claims.append(dict(claim_id=id,capitulo=3,secao=sec,claim=text,localizacao=dict(arquivo=qmd,linha=line),evidencia=dict(tipo=kind,referencia=artifact),assessment=dict(status=status,confidence='alta'),concerns=concerns or [],agent='results-reviewer'))
claim('C3.1.01','Dados','2018: 7.630 candidaturas, 859 listas, 73 sem recursos e 3 eleitos nessas listas.',27,source+'01_universos.csv')
claim('C3.1.02','Dados','2022: 9.675 candidaturas, 711 listas, 63 sem recursos e nenhum eleito nessas listas.',33,source+'01_universos.csv')
claim('C3.4.01','Composição do núcleo','O exemplo com C=12, G=4, k=3, H=2 tem precisão 66,7%, cobertura 50%, esperado 1 e lift 2.',63,'tese/03-medindo-coordenacao-intrapartidaria.qmd:65-70',kind='equacao')
claim('C3.7.01','Amplitude','Há 973 competitivos (12,75%) em 2018 e 1.354 (13,99%) em 2022.',82,source+'01_universos.csv')
claim('C3.7.02','Amplitude','As candidaturas crescem 27% e as competitivas 39%.',82,'evidence/res_resumo_recomputado.json')
claim('C3.7.03','Amplitude','Nas listas financiadas, mediana C=4/9; mediana F=1/1; média F=1,22/2,09.',84,'evidence/res_resumo_recomputado.json')
claim('C3.7.04','Amplitude','NECr mediano financiado=1,88 em 2018 e 4,81 em 2022.',88,'evidence/res_resumo_recomputado.json')
claim('C3.7.05','Amplitude','C/NECr mediano=1,95/1,86; NECr/C mediano=51,36%/53,65%.',94,'evidence/res_resumo_recomputado.json')
claim('C3.7.06','Amplitude','A figura amplitude apresenta médias e medianas no universo financiado.',86,'figs/cap3_fig_amplitude_barras.png',kind='figura')
claim('C3.7.07','Amplitude','A figura concentração apresenta NECr/C e coincide com os percentuais do texto.',96,'figs/cap3_fig_concentracao_barras.png',kind='figura')
for seq,(year,cov,ref,prec,pr,lift) in enumerate([(2018,'80,86','42,76','33,94','17,95','1,8909'),(2022,'80,89','43,60','28,64','15,44','1,8552')]):
    claim(f'C3.8.0{1+seq*2}','Top-NECr',f'{year}: cobertura competitivos={cov}% contra {ref}% ao acaso; precisão={prec}% contra {pr}%.',104,'evidence/res_metricas_recomputadas.csv')
    claim(f'C3.8.0{2+seq*2}','Top-NECr',f'{year}: lift competitivos={lift}, arredondado como no texto.',108,'evidence/res_metricas_recomputadas.csv')
claim('C3.8.05','Top-NECr','Os dois anos têm cobertura maior que 80%.',104,'evidence/res_metricas_recomputadas.csv')
claim('C3.8.06','Top-NECr','A figura apresenta os três indicadores e as respectivas referências nas duas eleições.',110,'figs/cap3_fig_top_necr.png',kind='figura')
claim('C3.8.07','Top-NECr','Lift cresce nos três grupos de magnitude em ambos os anos; todos os seis valores conferem.',112,'tese/reports/lift-magnitude-partido/lift_por_magnitude.csv')
claim('C3.9.01','Prêmio intralista','Amostras=7.254/649 e 9.263/623 candidaturas/listas.',135,reg+'amostra.csv')
claim('C3.9.02','Prêmio intralista','As razões de vitória de deputado federal, estadual, prefeito, senador e vereador e governador 2018 conferem.',137,reg+'coeficientes.csv')
claim('C3.9.03','Prêmio intralista','QE sem vitória tem razões 2,89/1,70; +10 p.p. de voto anterior têm razões 1,1520/1,1079.',139,reg+'coeficientes.csv')
claim('C3.9.04','Prêmio intralista','R1 tem razão 8,16/4,58 e AME de 20,3/12,1 p.p.',141,reg+'coeficientes.csv; '+reg+'ames.csv')
claim('C3.9.05','Prêmio intralista','Mulher tem razão R2=1,44/1,32.',147,reg+'coeficientes.csv')
claim('C3.9.06','Prêmio intralista','Negra tem razão R2=0,74/0,93, ambas com IC95% abaixo de 1.',149,reg+'coeficientes.csv')
claim('C3.9.07','Prêmio intralista','Razões por magnitude e seis IC95% conferem; interação contínua positiva com p<0,001 nos dois anos.',145,reg+'interacao_magnitude.csv')
claim('C3.9.08','Prêmio intralista','Forest plot representa R2 atualizado, incluindo critério QE, voto escalado, controles e IC95%.',151,'figs/cap3_regressao_fracionaria.png',kind='figura')
claim('C3.12.01','Correspondência com eleição','2018: cobertura=86,7446%, precisão=19,1976%, lift=1,9815; alvo de 513 eleitos.',164,'evidence/res_metricas_recomputadas.csv')
claim('C3.12.02','Correspondência com eleição','2022: cobertura=92,6301%, precisão=12,4266%, lift=2,1174; alvo de 513 eleitos.',166,'evidence/res_metricas_recomputadas.csv')
claim('C3.12.03','Correspondência com eleição','A figura Top-NECr dos eleitos coincide com as métricas nacionais e suas referências.',168,'figs/cap3_fig_top_necr_eleicao.png',kind='figura')
claim('C3.12.04','Correspondência com eleição','Lifts dos eleitos crescem nos grupos de magnitude nos dois anos; seis valores conferem.',170,'tese/reports/lift-magnitude-partido/lift_por_magnitude.csv')
claim('C3.13.01','Top-X','Figura de credenciais representa corretamente os seis limiares e três métricas em cada ano.',191,'figs/cap3_fig_topx_competitividade.png',concerns=['RES-3-001: duas convenções visuais sem chave.'],kind='figura')
claim('C3.13.02','Top-X','Figura dos eleitos representa corretamente os seis limiares e três métricas em cada ano.',195,'figs/cap3_fig_topx_eleicao.png',concerns=['RES-3-001: mesmas convenções sem chave.'],kind='figura')
claim('C3.13.03','Top-X','Cobertura de competitivos supera 50% no Top50 em ambos os anos (56,69%; 50,97%).',185,'evidence/res_metricas_recomputadas.csv')
claim('C3.13.04','Top-X','Lift dos competitivos diminui ao elevar o limiar, mas permanece >1; Top95=1,55/1,37.',187,'evidence/res_metricas_recomputadas.csv')
claim('C3.13.05','Top-X','Há mais competitivos dentro do que fora do núcleo agregado em cada limiar/ano, pois a cobertura supera 50%.',189,'evidence/res_metricas_recomputadas.csv',concerns=['Leitura nacional agregada; não é afirmação sobre cada lista individual.'])
claim('C3.13.06','Top-X','Em todos os limiares/anos, a cobertura dos eleitos supera a dos competitivos, e o lift dos eleitos é >1.',193,'evidence/res_metricas_recomputadas.csv')

ending='''
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
'''
# JSON é subconjunto válido de YAML, mantendo valores e acentuação sem escape ambíguo.
claim_blocks='\n\n'.join('```yaml\n'+json.dumps(c,ensure_ascii=False,indent=2)+'\n```' for c in claims)
import re
report=header+'\n'.join(rows)+figures+claim_blocks+'\n'+ending
section_ids={'7':'6','8':'7','9':'8','12':'10','13':'11'}
report=re.sub(r'C3\.(7|8|9|12|13)\.',lambda m:'C3.'+section_ids[m.group(1)]+'.',report)
(OUT.parent/'agents/results.md').write_text(report,encoding='utf-8')
print(f'Relatório salvo: {len(checks)} linhas de auditoria numérica, {len(claims)} claims, 2 achados MINOR.')
