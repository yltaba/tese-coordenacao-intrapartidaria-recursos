# statistics-reviewer — Capítulo 3 — run-002

## Escopo e método

Leitura integral do capítulo atual (200 linhas), de `CLAUDE.md`, protocolo, rubrica, template, geradores das medidas e da regressão intralista de 18/09/2026. Inspecionados os CSVs atuais de resultados, magnitude e regressão. `03-formulas-propostas.qmd` não existe; `df_cox_survival.parquet` existe, mas Capítulo 4 está fora do escopo. Não li relatórios de outros agentes.

Recomputações em `evidence/sta_audit.py`, executadas com sucesso: métricas nacionais e médias por lista do Top-NECr/Top-X%; modelos R1, R2 e interação contínua; sensibilidade de erros-padrão por partido e UF; soma das parcelas efetivamente usadas; duas correções explícitas para a massa excluída. O script extrai funções do código vigente sem executar os geradores nem escrever fora deste run. Todos os CSVs produzidos começam por `sta_`.

A discussão deliberadamente inacabada foi excluída de achados e gates. Não há cobrança por simulação histórica de 10.000 sorteios: a versão atual usa expectativa analítica e não promete essa simulação.

## Avaliação macro

A cadeia estatística sustenta a afirmação descritiva central: credenciais anteriores estão sobrerrepresentadas nos núcleos financeiros e associadas a parcelas maiores entre correligionários. O desenho intralista responde melhor à segunda pergunta que uma comparação agrupada entre listas. Cobertura, precisão e lift não são três confirmações independentes, e o capítulo corretamente apresenta o lift como resumo. A associação se conserva nos seis limiares e na análise de magnitude.

O ponto que precisa de correção antes de consolidar a seção é a implementação da regressão após exclusões: a massa de recursos dos candidatos remanescentes não soma um em 14 listas; a função usa essa igualdade no cálculo da variância, e a média prevista descrita no texto não representa diretamente a parcela original nesses conjuntos incompletos. O erro é localizado: as correções recomputadas preservam as associações centrais e alteram pouco os números nacionais.

Há dois esclarecimentos estatísticos relevantes: a agregação nacional precisa explicitar seus pesos, e a conclusão de significância para candidaturas negras em 2022 depende do nível de cluster. As comparações de dois censos eleitorais e os benchmarks analíticos podem permanecer descritivos, sem exigir intervalos para cada número. Não há evidência de que a inexistência de intervalos nas figuras descritivas invalide a conclusão central. O benchmark identifica seleção além do sorteio uniforme intralista, não elimina explicações alternativas para essa seleção.

## Achados

```yaml
id: STA-3-001
titulo: "Exclusões deixam parcelas sem soma unitária, mas o sanduíche e a interpretação da média pressupõem listas completas"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 131
  secao: "Prêmio intralista das credenciais eleitorais prévias"
  trecho: "O modelo equivale a uma regressão de Poisson da parcela com efeitos fixos de lista. Os erros-padrão são clusterizados por lista"
afirmacao_do_autor: "A regressão modela a parcela original R_il/R_l com média softmax e variância robusta por lista."
problema: "Erro de implementação/estimando. As parcelas são calculadas antes de excluir CPF e covariáveis ausentes. Nas listas incompletas, m_l = soma_i s_il < 1. O gradiente Xc' s usado pelo algoritmo continua sendo o gradiente da função objetivo ponderada por m_l, mas a Hessiana usa p em vez de m_l p, e os escores usados no sanduíche são soma_i (s_i-p_i)x_i em vez de soma_i (s_i-m_l p_i)x_i. A equivalência dos coeficientes ao PPML perfilado sobrevive; a média perfilada correta nesse caso é m_l p_i, e a variância implementada não é seu sanduíche. Os AMEs de p também passam a ter interpretação de parcela normalizada entre remanescentes, não automaticamente da parcela original."
evidencia:
  tipo: recomputacao
  fontes:
    - thesis-review/runs/run-002/evidence/sta_audit.py
    - thesis-review/runs/run-002/evidence/sta_lists_missing_mass.csv
    - thesis-review/runs/run-002/evidence/sta_missing_mass_correction.csv
    - tese/scripts/regressao_fracionaria_cap3.py:107
    - tese/scripts/regressao_fracionaria_cap3.py:182
    - tese/scripts/regressao_fracionaria_cap3.py:192
  detalhe: "Duas listas afetadas em 2018 e 12 em 2022. MG_PSB/2018 retém soma 0,816489; DF_NOVO/2022, 0,095337; RJ_PTB/2022, 0,101047. As listas completas somavam 1 antes da exclusão. Corrigir Hessiana e escores preserva beta, como esperado, e muda EP: negra/R2/2022 0,034227 -> 0,034172. Renormalizar os remanescentes muda beta competitivo/R1/2022 de 1,522477 para 1,524289. O tamanho reduzido das alterações não valida a igualdade de soma usada no código; também mostra que não há evidência de colapso do achado central."
severidade: MAJOR
confianca: alta
recomendacao: "Escolher e declarar o estimando após exclusões. Uma correção simples é renormalizar R_il pela soma dos recursos das candidaturas efetivamente incluídas em cada lista, declarar a comparação entre remanescentes e reestimar coeficientes, EP e AMEs; alternativamente, manter a parcela original e usar a massa m_l na média perfilada, Hessiana, escores e efeitos. Validar a soma observada, não apenas a prevista. Atualizar os artefatos apenas após essa decisão. É uma correção localizada do método, não recomendação para substituir a análise."
claims: [C3.8.01]
```

```yaml
id: STA-3-002
titulo: "A significância da desvantagem de candidaturas negras em 2022 depende do cluster por lista"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 149
  secao: "Prêmio intralista das credenciais eleitorais prévias"
  trecho: "a razão sobe para 0,93, mas continua estatisticamente distinguível da paridade."
afirmacao_do_autor: "A desvantagem racial permanece estatisticamente distinguível de zero em 2022."
problema: "Limitação inferencial. A frase é correta sob os EP por lista escolhidos, mas o financiamento é decidido por organizações presentes em várias UFs e a independência entre listas não é assegurada pelos efeitos fixos. A distinção a 5% não resiste ao agrupamento por partido. Não é necessário afirmar que o cluster atual é sempre inválido; é necessário qualificar a conclusão e mostrar a sensibilidade material."
evidencia:
  tipo: recomputacao
  fontes:
    - thesis-review/runs/run-002/evidence/sta_cluster_sensitivity.csv
    - tese/reports/regressao-fracionaria/coeficientes.csv
    - notes/tecnico/cap3-plano-regressao-intralista.md
  detalhe: "R2/2022/negra: beta=-0,074872. Cluster por 623 listas: EP=0,034227, p normal=0,0287. Por 31 partidos: EP=0,044404, p normal=0,0918 e p t(30)=0,1021. Por 27 UFs: p normal=0,0437, p t(26)=0,0542. A sensibilidade usa o sanduíche vigente para isolar apenas a mudança de agrupamento; STA-3-001 quantifica separadamente o erro da massa excluída, cuja correção é muito pequena para esse coeficiente. As interações de magnitude continuam fortemente significativas nos três agrupamentos."
severidade: MODERATE
confianca: alta
recomendacao: "Depois de corrigir STA-3-001, manter a razão estimada e apresentar sensibilidade por partido com inferência que considere o número de clusters; qualificar que a distinção da paridade ocorre com EP por lista e não é robusta ao agrupamento partidário. Não interpretar a perda de significância como prova de paridade."
claims: [C3.8.08]
```

```yaml
id: STA-3-003
titulo: "A agregação nacional omite os pesos que distinguem razões de somas de médias por lista"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 61
  secao: "Composição do núcleo priorizado e credenciais eleitorais"
  trecho: "Para analisar a composição do núcleo priorizado são calculados três indicadores: precisão, cobertura e *lift*; e uma referência aleatória."
afirmacao_do_autor: "O exemplo de uma nominata introduz os indicadores usados nos resultados nacionais."
problema: "Escolha defensável sem declaração suficiente. O exemplo local não informa como as listas se agregam. A cobertura nacional pondera listas pelo número de integrantes do alvo; a precisão, por k; e o lift, pela expectativa aleatória. Nenhuma dessas medidas é a experiência da lista típica. O capítulo remete a uma definição formal não presente neste arquivo, e não explicita a razão de somas na passagem aos resultados."
evidencia:
  tipo: recomputacao
  fontes:
    - thesis-review/runs/run-002/evidence/sta_metrics.csv
    - tese/scripts/regenerar_figuras_cap3.py:89
    - tese/03-medindo-coordenacao-intrapartidaria.qmd:63
  detalhe: "Top-NECr competitivo/2018: precisão nacional=33,94%, mas média das precisões das listas com k>0=41,65%; cobertura nacional=80,86%, mas média das coberturas das listas com alvo>0=84,12%. Em 2022, precisão nacional=28,64%, média por lista=28,02%. A diferença é substantiva para a leitura de uma lista típica e não é mero arredondamento."
severidade: MODERATE
confianca: alta
recomendacao: "Inserir a regra agregada: cobertura=sum H/sum G; precisão=sum H/sum k; lift=sum H/sum(Gk/C). Dizer que resumem candidaturas/posições nacionalmente, com os respectivos pesos, e não uma lista média. Explicitar também que os lifts de cobertura e precisão coincidem por identidade. Não é necessário substituir os indicadores escolhidos."
claims: [C3.4.01, C3.7.01]
```

```yaml
id: STA-3-004
titulo: "O efeito médio em pontos percentuais precisa ser distinguido da razão entre dois correligionários"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 141
  secao: "Prêmio intralista das credenciais eleitorais prévias"
  trecho: "Em pontos percentuais, essas diferenças equivalem, em média, a 20,3 e 12,1 pontos da parcela intralista."
afirmacao_do_autor: "As razões entre parcelas de 8,16 e 4,58 equivalem a diferenças médias de 20,3 e 12,1 pontos."
problema: "Definição incompleta do contraste. Os AMEs são a média de alterações 0->1 na credencial de uma candidatura de cada vez, mantendo colegas fixos e recalculando o denominador softmax. A razão exp(beta) compara dois integrantes simultaneamente da mesma lista; não é o multiplicador da parcela da mesma pessoa antes/depois dessa alteração. O número em pontos não é uma conversão única daquela razão."
evidencia:
  tipo: codigo
  fontes:
    - tese/scripts/regressao_fracionaria_cap3.py:199
    - tese/reports/regressao-fracionaria/ames.csv
    - tese/03-medindo-coordenacao-intrapartidaria.qmd:133
  detalhe: "_ame_vec calcula p_i(x_i=1, X_-i)-p_i(x_i=0, X_-i) e depois tira a média sobre candidaturas. O denominador varia entre os dois cenários, ao contrário da comparação p_i/p_j da equação de razões. O valor reportado bate com o código; o problema é a definição textual, além do ajuste de massa descrito em STA-3-001."
severidade: MODERATE
confianca: alta
recomendacao: "Nomear os pontos percentuais como contraste médio previsto da mudança individual 0->1, mantendo os demais integrantes fixos, e mencionar que o denominador é recalculado. Evitar apresentar o AME como simples equivalência da razão entre colegas."
claims: [C3.8.05]
```

## Claims

Os IDs de seção seguem a ordem dos cabeçalhos do capítulo. Comparações do mesmo parágrafo foram agrupadas quando dependem da mesma evidência. `supported` nas descrições dos universos observados não implica generalização superpopulacional nem causalidade.

```yaml
claim_id: C3.4.01
capitulo: 3
secao: "Composição do núcleo priorizado e credenciais eleitorais"
claim: "Na lista fictícia, cobertura 50%, precisão 66,7%, expectativa 1 e lift 2."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 63}
evidencia: {tipo: equacao, referencia: "Tabela tbl-resumo-indicadores; 2/4, 2/3, 3*4/12, 2/1"}
assessment: {status: supported, confidence: alta}
concerns: ["A passagem ao agregado nacional precisa explicitar os pesos: STA-3-003."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.6.01
capitulo: 3
secao: "Amplitude das nominatas e concentração dos recursos"
claim: "O universo total cresce 27%, e o grupo competitivo, 39%."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 82}
evidencia: {tipo: equacao, referencia: "9675/7630-1=26,80%; 1354/973-1=39,16%"}
assessment: {status: supported, confidence: alta}
concerns: ["Comparação descritiva entre universos observados; não requer teste para afirmar o crescimento contado."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.6.02
capitulo: 3
secao: "Amplitude das nominatas e concentração dos recursos"
claim: "O NECr mediano cresce e é menor que o tamanho formal das listas."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 88}
evidencia: {tipo: codigo, referencia: "tese/scripts/regenerar_figuras_cap3.py:44; NECr=1/sum(s^2)<=C"}
assessment: {status: supported, confidence: alta}
concerns: ["Comparação descritiva. NECr é equivalente efetivo, não contagem literal de quem recebeu algum recurso."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.7.01
capitulo: 3
secao: "Priorização financeira pelo Top-NECr"
claim: "Cobertura competitiva acima de 80%, precisão 33,9/28,6%, lift 1,89/1,86 e quase 90% mais que o acaso."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 104}
evidencia: {tipo: csv, referencia: "thesis-review/runs/run-002/evidence/sta_metrics.csv; cutoff=topnecr, outcome=competitividade"}
assessment: {status: supported, confidence: alta}
concerns: ["Comparações descritivas contra esperança uniforme; não são três testes independentes.", "Para uma afirmação de rejeição de sorteio aleatório, usar permutação intralista preservando recursos/empates. Tal afirmação não é necessária à descrição atual."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.7.02
capitulo: 3
secao: "Priorização financeira pelo Top-NECr"
claim: "O lift cresce entre os três grupos de magnitude nas duas eleições."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 112}
evidencia: {tipo: csv, referencia: "tese/reports/lift-magnitude-partido/lift_por_magnitude.csv"}
assessment: {status: supported, confidence: alta}
concerns: ["Gradiente entre agregados de três grupos, não monotonicidade lista a lista nem efeito causal da magnitude.", "Lift depende também das oportunidades de seleção (k/C); o teste contínuo intralista oferece evidência complementar, não torna o gradiente causal."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.8.01
capitulo: 3
secao: "Prêmio intralista das credenciais eleitorais prévias"
claim: "A regressão fracionária intralista tem média softmax e equivale a Poisson com EF de lista e sanduíche por lista."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 125}
evidencia: {tipo: codigo, referencia: "tese/scripts/regressao_fracionaria_cap3.py:168; evidence/sta_missing_mass_correction.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["A formulação é correta para listas completas; STA-3-001 documenta a quebra da soma unitária após filtros e seu efeito sobre média/variância."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.8.02
capitulo: 3
secao: "Prêmio intralista das credenciais eleitorais prévias"
claim: "A razão entre parcelas esperadas de dois correligionários é exp((x_i-x_j)'beta), sem o denominador da lista."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 133}
evidencia: {tipo: equacao, referencia: "Cancelamento algébrico do denominador comum da equação na linha 128"}
assessment: {status: supported, confidence: alta}
concerns: ["É uma propriedade da especificação, não prova de que composição/tamanho jamais alterem coeficientes reestimados.", "A variação em pontos percentuais não precisa diminuir para toda candidatura se uma lista específica crescer; isso depende dos atributos dos novos integrantes."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.8.03
capitulo: 3
secao: "Prêmio intralista das credenciais eleitorais prévias"
claim: "Todas as vitórias anteriores têm razões acima de um; governador/2022 não se distingue de um, e senador/governador têm os maiores intervalos."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 137}
evidencia: {tipo: csv, referencia: "tese/reports/regressao-fracionaria/coeficientes.csv; modelo=R2"}
assessment: {status: supported, confidence: alta}
concerns: ["A exceção governador/2022 é de significância, não de sinal: razão=1,33, IC inclui 1.", "A ordenação pontual de cargos não é teste de diferenças entre coeficientes; a frase sobre vereador deve permanecer descritiva.", "Revisar variância conforme STA-3-001."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.8.04
capitulo: 3
secao: "Prêmio intralista das credenciais eleitorais prévias"
claim: "Uma vitória de DF corresponde a razão 2,00/1,55; duas a cerca de quatro em 2018; QE e votos defasados têm associação positiva."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 137}
evidencia: {tipo: csv, referencia: "tese/reports/regressao-fracionaria/coeficientes.csv; exp(2*0,693458)=4,00249"}
assessment: {status: supported, confidence: alta}
concerns: ["Predições condicionais da forma log-linear, com demais atributos iguais; não efeitos causais de adquirir um mandato.", "As razões das contagens pressupõem igual incremento no log da parcela por vitória adicional."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.8.05
capitulo: 3
secao: "Prêmio intralista das credenciais eleitorais prévias"
claim: "R1 produz razões 8,16/4,58 e AMEs 20,3/12,1 pp."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 141}
evidencia: {tipo: csv, referencia: "tese/reports/regressao-fracionaria/coeficientes.csv e ames.csv, R1"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["Números batem; falta distinguir os estimandos: STA-3-004 e tratamento da massa em STA-3-001.", "R1 controla mulher/negra, mas não votação defasada nem composição detalhada do histórico; esclarecer a troca de especificação em relação a R2."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.8.06
capitulo: 3
secao: "Prêmio intralista das credenciais eleitorais prévias"
claim: "A vantagem relativa estimada diminuiu de 2018 para 2022 e não é uma conversão mecânica de 1/C."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 143}
evidencia: {tipo: csv, referencia: "tese/reports/regressao-fracionaria/coeficientes.csv, R1 competitivo"}
assessment: {status: supported, confidence: alta}
concerns: ["É comparação de estimativas de amostras e composições diferentes; não isola efeito do fim das coligações.", "Se desejar inferência formal da diferença, estimar anos conjuntamente com credencial x ano, EF lista-ano e cluster que una unidades persistentes, como partido; dois p-valores separados não testam igualdade."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.8.07
capitulo: 3
secao: "Prêmio intralista das credenciais eleitorais prévias"
claim: "Razões crescem por magnitude; interação é positiva e significativa nos dois anos."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 145}
evidencia: {tipo: csv, referencia: "tese/reports/regressao-fracionaria/interacao_magnitude.csv; evidence/sta_cluster_sensitivity.csv"}
assessment: {status: supported, confidence: alta}
concerns: ["O p documentado é da interação contínua com ln(magnitude), enquanto a tabela usa interação categórica; especificar isso evita confundir os testes.", "A significância também resiste a clusters por partido/UF na sensibilidade; não há fundamento empírico nesta auditoria para descartar o gradiente."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.8.08
capitulo: 3
secao: "Prêmio intralista das credenciais eleitorais prévias"
claim: "Mulher tem razão acima de um; negra tem razão abaixo de um, com menor desvantagem e significância em 2022."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 147}
evidencia: {tipo: csv, referencia: "tese/reports/regressao-fracionaria/coeficientes.csv; evidence/sta_cluster_sensitivity.csv"}
assessment: {status: partially_supported, confidence: alta}
concerns: ["Sinais e valores sustentados; STA-3-002 qualifica a significância racial em 2022.", "Coincidência temporal com regras não identifica causalidade das regras; o texto usa corretamente coincide, mas assegura individualmente vai além do contraste estatístico."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.10.01
capitulo: 3
secao: "Correspondência entre priorização financeira e eleição"
claim: "Eleitos têm cobertura 86,7/92,6%, precisão 19,2/12,4% e lift aproximadamente dois."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 164}
evidencia: {tipo: csv, referencia: "thesis-review/runs/run-002/evidence/sta_metrics.csv; outcome=eleicao, cutoff=topnecr"}
assessment: {status: supported, confidence: alta}
concerns: ["Descrição ex-post, reconhecida pelo autor; não identifica capacidade preditiva fora da amostra nem causalidade dos repasses.", "Cobertura, precisão e lift dividem o mesmo numerador; não são replicações independentes."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.10.02
capitulo: 3
secao: "Correspondência entre priorização financeira e eleição"
claim: "O lift de eleitos cresce entre os grupos de magnitude nas duas eleições."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 170}
evidencia: {tipo: csv, referencia: "tese/reports/lift-magnitude-partido/lift_por_magnitude.csv; alvo=eleitos"}
assessment: {status: supported, confidence: alta}
concerns: ["Gradiente descritivo entre agregados; não implica monotonicidade entre todas as listas ou efeito causal."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.11.01
capitulo: 3
secao: "Sensibilidade ao limiar Top-X%"
claim: "A cobertura competitiva passa de 50% no Top-50% e cresce com o limiar nos dois anos."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 185}
evidencia: {tipo: csv, referencia: "thesis-review/runs/run-002/evidence/sta_metrics.csv; seis limiares"}
assessment: {status: supported, confidence: alta}
concerns: ["O crescimento de cobertura é esperado por aninhamento, como o capítulo reconhece; não é evidência adicional independente de associação."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.11.02
capitulo: 3
secao: "Sensibilidade ao limiar Top-X%"
claim: "Lift é maior nos cortes restritos, fica acima de um em todos e chega a 1,55/1,37 no Top-95%."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 187}
evidencia: {tipo: csv, referencia: "thesis-review/runs/run-002/evidence/sta_metrics.csv; competitividade"}
assessment: {status: supported, confidence: alta}
concerns: ["O benchmark controla a expectativa condicional a G,k,C, não todas as consequências da composição das listas ou do universo de recebedores.", "Permutar o vetor de recursos entre todos os candidatos da lista preserva concentração/empates e testa a mesma hipótese de independência; restringir o sorteio aos recebedores responderia a pergunta mais exigente, condicional ao acesso."]
agent: statistics-reviewer
```

```yaml
claim_id: C3.11.03
capitulo: 3
secao: "Sensibilidade ao limiar Top-X%"
claim: "Há mais competitivos dentro que fora dos núcleos e a cobertura de eleitos é maior que a de competitivos."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 189}
evidencia: {tipo: csv, referencia: "thesis-review/runs/run-002/evidence/sta_metrics.csv; cobertura competitiva mínima=50,9675%; cobertura eleitos supera competitivos em todas as 12 comparações"}
assessment: {status: supported, confidence: alta}
concerns: ["Dentro versus fora é comparação de contagens nacionais, não a prevalência de credenciais nos dois grupos.", "As comparações são descritivas; para generalizar sua diferença, bootstrap de listas preservando conjuntamente os dois alvos."]
agent: statistics-reviewer
```

## Verificações que passaram

- Reprodução dos números nacionais do Top-NECr e de todos os Top-X%; monotonicidades efetivamente verificadas, não inferidas da figura.
- Expectativa aleatória Gk/C correta para sorteio uniforme de k entre C e agregação analítica; ausência de simulação não impede calcular essa esperança.
- Lift de precisão e de cobertura idênticos; texto trata lift como resumo das comparações anteriores.
- Modelos atuais são intralista; razão de parcelas não é odds ratio. Contagens têm interpretação multiplicativa e votos defasados são escalados por 0,1.
- Coeficientes e contrastes reportados reproduzidos. Correções da massa mantêm a conclusão central. Interações de magnitude também permanecem fortes sob clusters por partido/UF.
- Credenciais anteriores e resultado eleitoral posterior ocupam análises distintas; a validação ex-post não é apresentada como identificação causal.

## Limites desta revisão

Não realizei teste de especificação funcional de retornos constantes por vitória nem modelo conjunto de anos. Não fiz bootstrap populacional ou permutação porque as descrições atuais podem ser avaliadas diretamente no universo observado, e as recomputações decisivas foram soma da massa, agregação e dependência. A sensibilidade por partido não prova ser esse o único cluster correto; demonstra a dependência da conclusão racial à hipótese de independência entre listas. O reparo de variância usado para dimensionar STA-3-001 conserva o modelo escolhido; não resolve possível seleção por dados ausentes. Não avaliei a discussão, literatura ou redação fora do que muda a interpretação estatística.
