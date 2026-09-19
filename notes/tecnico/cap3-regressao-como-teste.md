# Cap. 3 — regressão fracionária e Top-NECr como testes do mesmo argumento

Material de apoio. **Não é texto da tese.** Este documento não traz parágrafos para o capítulo. Ele
discute onde está o problema, o que precisa mudar na análise para a reestruturação se sustentar e
quais decisões ficam com o autor.

Números novos: `notes/tecnico/cap3_ponte_regressao.py`, que roda da raiz em cerca de 1 minuto. O
script reproduz o *lift* do capítulo (1,891 / 1,855) e a amostra da regressão (N = 7.391 / 9.288).
Os demais números vêm de `tese/reports/regressao-fracionaria/ames.csv` e do próprio `.qmd`.

---

## 0. Decisão do autor (18/09/2026)

O autor adotou uma formulação própria, no lugar das opções A, B e C da seção 5:

- **Top-NECr é o teste da estrutura da priorização.** Pergunta: quem aparece no núcleo de
  candidaturas priorizadas? Métricas: precisão, cobertura, referência aleatória e *lift*.
- **A regressão fracionária é o teste contínuo da priorização.** Pergunta: sem impor qualquer
  corte para definir um núcleo, as credenciais estão associadas a uma parcela maior dos recursos
  intralista?

O que essa formulação ainda exige das seções abaixo:

- **Seção 3.1 (mesma credencial).** Obrigatória. A pergunta fala em "as credenciais", no mesmo
  sentido do Top-NECr.
- **Seção 3.2 (tamanho da lista).** Obrigatória. A pergunta é sobre a parcela intralista.
- **Seção 4(b) (modelo de probabilidade linear da pertença ao núcleo).** Opcional.
- **Distinção com o Top-X%.** O Top-X% varia o corte; a regressão elimina o corte.

---

## 1. O argumento que os dois testes deveriam servir

A linha 17 do capítulo enuncia o argumento:

> "O argumento deste capítulo é que os partidos priorizam financeiramente candidaturas com
> credenciais eleitorais prévias."

Dele saem pelo menos duas implicações observáveis, com focos diferentes:

| | Implicação observável | Teste | O que precisa de um corte |
|---|---|---|---|
| **I1 — composição do topo** | No grupo que concentra os recursos de cada lista, há mais candidaturas com credenciais do que haveria ao acaso. | Top-NECr (cobertura, precisão e *lift* contra a referência hipergeométrica) | Um corte `k_l` decide quem é "priorizado". |
| **I2 — gradiente** | Dentro da mesma lista, a parcela de recursos de uma candidatura cresce com suas credenciais, mesmo com as restrições legais de alocação mantidas constantes. | Regressão fracionária sobre `s_il = R_il/R_l` | Nenhum corte, porque a parcela é contínua. |

As duas implicações seguem do mesmo argumento. Se ele estiver certo, ambas devem aparecer nos dados.
Cada uma deixa um ponto fraco que a outra cobre:

- **O *lift* depende de um limiar.** O Top-X% já trata isso em parte, mas continua sendo um corte.
  A regressão usa toda a distribuição, inclusive diferenças dentro do núcleo e dentro da cauda.
- **O *lift* não tem controles.** A seção de Discussão (linha 192) levanta o problema: as cotas
  de gênero e raça moldam a distribuição, e só 4,68% das mulheres são competitivas contra 15,83% dos
  homens (2018). Esse ponto põe em dúvida o próprio *lift*, mas o capítulo não conta com a regressão
  para responder, embora ela tenha `mulher` e `negra` no modelo.
- **O *lift* trata a credencial como binária.** A regressão permite perguntar quais credenciais
  pesam e se mais vitórias rendem uma parcela maior. Isso também valida a escolha da flag binária
  (seção 3.1).
- **A regressão não tem referência "ao acaso".** O *lift* tem, e é mais fácil de ler.
  Com efeitos fixos de lista, a regressão passa a ter uma referência análoga (seção 3.2).

Um ponto de honestidade para a arguição: os dois testes usam os **mesmos dados e a mesma variação**.
Eles não formam uma replicação independente. São duas formas de medir a mesma associação, e cada uma
fecha um ponto fraco da outra. "Convergência" é a palavra defensável. "Confirmação independente"
não é.

---

## 2. Por que hoje a regressão não se lê como teste do argumento

O problema é de posição e de enquadramento no texto. As três primeiras evidências abaixo vêm do
`.qmd`:

1. **Posição.** A seção `sec-premio-credenciais` (linha 162) vem **depois** de "Robustez da
   operacionalização" e fora de "Resultados". Pela estrutura, o leitor a lê como um apêndice.
2. **Motivação por disponibilidade de dados.** A linha 164 abre a seção assim:
   > "Portanto, além de selecionar o núcleo priorizado, pode-se verificar como estas credenciais
   > eleitorais impactam a fatia intralista…"

   A justificativa é que a base permite fazer a análise, e não que o argumento exige o teste. Na
   introdução, a linha 25 repete o tom com "Por fim, uma análise desagregada…".
3. **A Discussão ignora a regressão.** As linhas 180–196 não citam `@fig-reg-frac`. A conclusão
   (linha 182) diz que "os testes realizados neste capítulo sustentam a hipótese", mas se apoia
   apenas no *lift*. E o confundidor da linha 192 fica sem resposta, embora a resposta já exista na
   seção anterior.

Esses três problemas se resolvem reorganizando o capítulo. As divergências de análise da seção 3 não
se resolvem assim.

Isso responde à pergunta da nota diária de 18/09 ("entender se tudo bem falar sobre o modelo apenas
no tópico dele em resultados"). **Não.** Se a regressão for um teste do argumento, ela precisa
aparecer em quatro lugares: introdução (como a segunda implicação), método (a variável dependente e
a definição de credencial), resultados e discussão. Se ela aparecer só na própria seção, o leitor
continuará lendo-a como anexo.

---

## 3. Divergências de análise: hoje os dois testes não medem a mesma coisa

Estas divergências são mais sérias do que a posição no texto. Não basta mudar a narrativa se as
duas análises continuarem operacionalizando a hipótese de formas diferentes. Um arguidor atento
percebe.

### 3.1 Duas definições diferentes de "credencial"

| | Top-NECr (flag `candidato_competitivo`) | Regressão (`regressao_fracionaria_cap3.py`) |
|---|---|---|
| Vitória prévia (Gov, Sen, DF, DE, Pref) | sim, **binária** | sim, **contagens por cargo** |
| Vitória para **vereador** | **excluída** (`cap3_cs_features.py:82`) | **incluída** (`n_eleicoes_vereador`) |
| ≥10% do QE em disputa proporcional anterior | **incluída** | **ausente** |
| Votação prévia | via 10% do QE, qualquer disputa anterior para DF/DE | `prop_votos_nominais_lag`: parcela da lista em t−1, só DF, mesmo partido (com linhagem), estreantes = 0 |

Consequências concretas:

- **Quem entra pelo critério de 10% do QE fica sem contraparte na regressão.** São 227 candidaturas
  (2018) e 408 (2022), ou seja, 24% e 30% dos competitivos. Nesse grupo, a chance de estar no
  Top-NECr é 0,589 / 0,688, contra 0,890 / 0,863 para quem tem vitória prévia.
- **Vereador é tratado de formas opostas.** A flag exclui essa vitória, mas a regressão estima um
  AME positivo e significativo para ela (2,33 pp em 2018 e 0,34 pp em 2022, p = 0,02). O texto da
  seção (linha 170) não menciona vereador nem `prop_votos_nominais_lag`, e a figura mostra os dois.
  Há 623 (2018) e 917 (2022) vereadores eleitos fora da flag. Em média, eles recebem uma parcela
  próxima da divisão igual (s·C_l = 1,07 / 0,92), e os não competitivos sem histórico recebem
  0,65 / 0,70. Nos dados, a exclusão parece defensável porque o prêmio é pequeno. Mas a regressão é
  justamente o lugar para **mostrar** isso, em vez de o texto se calar sobre a divergência.

**Leitura:** a regressão pode justificar a flag. Hoje ela a contradiz em silêncio.

### 3.2 Dois estimandos diferentes: dentro da lista × entre listas

O *lift* compara candidaturas **dentro da mesma lista**, contra uma seleção aleatória com os mesmos
`C_l` e `k_l`. A regressão junta todas as listas sem efeito fixo. Como a parcela média numa lista
vale mecanicamente `1/C_l`, boa parte da variação da variável dependente é **tamanho de lista**, e
não priorização. No modelo, `ln(magnitude)` cumpre o papel de controle, e a linha 168 diz isso de
forma explícita ("buscando sobretudo um controle pelo tamanho das nominatas").

Recomputação (`cap3_ponte_regressao.py`, modelos M0, M1 e M1b):

| | 2018 | 2022 |
|---|---|---|
| AME de ln(magnitude), especificação do capítulo | −10,31 pp | −5,61 pp |
| AME de ln(magnitude) com ln(C_l) também no modelo | **−0,27** | **+0,93** |
| Desvio (*deviance*): ln(mag) → ln(C_l) | 1.839 → 1.307 | 1.020 → 693 |
| AME de Senador: ln(mag) → ln(C_l) | 11,87 → **3,52** | 8,69 → 7,49 |
| AME de Dep. Federal: ln(mag) → ln(C_l) | 4,69 → 3,25 | 1,92 → 1,98 |

Com o tamanho da lista no modelo, a magnitude perde o efeito. Ela funcionava como aproximação
imperfeita do tamanho da lista, e a aproximação altera AMEs que o texto comenta (Senador em 2018).

Há ainda um problema de leitura que o leitor vai notar. A `tbl-cap3-01` mostra *lift* **crescente**
com a magnitude, e a figura da regressão mostra AME **negativo** para a magnitude. Não há
contradição: o primeiro número vem de uma comparação dentro da lista, e o segundo é o efeito
mecânico de `1/C_l`. Mas, sem essa explicação, o capítulo parece se contradizer.

A atenuação entre 2018 e 2022, explicada na linha 172 pelo crescimento do NECr, tem uma causa mais
direta: o `C_l` médio passa de 9,4 para 14,4, e o `1/C_l` médio por candidatura cai de 0,106 para
0,070. Um AME em pontos percentuais de parcela não se compara entre eleições com tamanhos de lista
tão diferentes.

### 3.3 Zeros

A parcela é zero em 24,5% das candidaturas em 2018 e em 8,1% em 2022. O logit fracionário de Papke
e Wooldridge aceita zeros, então não há erro. Mas a mudança da massa de zeros entre as eleições é
parte do fenômeno (a extensão do financiamento) e também explica o AME menor em 2022. Vale ter isso
à mão.

---

## 4. Harmonização proposta

Para a regressão se ler como o **mesmo** teste, a especificação principal deveria usar os mesmos
objetos do Top-NECr. A proposta tem três camadas.

**(a) Especificação principal: a flag do capítulo, comparação dentro da lista.**
Parcela ~ `candidato_competitivo` + `mulher` + `negra` + **efeitos fixos de lista**.
Os efeitos fixos absorvem o `1/C_l`, então a pergunta passa a ser a mesma do *lift*: dentro da
mesma nominata, quem tem credencial recebe mais?

| | 2018 | 2022 |
|---|---|---|
| M2: flag binária + ln(C_l), sem efeito fixo — AME | 10,88 pp (EP 0,45) | 6,90 pp (EP 0,27) |
| M3: flag binária + efeito fixo de lista — AME | 16,73 pp (EP 0,70) | 9,66 pp (EP 0,36) |
| Mulher / Negra (M3) | +3,32 / −2,24 | +1,97 / −0,52 |

Ressalvas do M3: são cerca de 650 a 790 *dummies* com uma média de 9 a 14 candidaturas por lista.
O viés de parâmetros incidentais do logit com efeito fixo deve ser pequeno, mas existe, e o AME
calculado pela média de μ(1−μ) é aproximado. Há duas alternativas mais simples de defender. A
primeira é usar como variável dependente `s_il·C_l` (a parcela relativa à divisão igual, em que 1
indica a divisão igual) num MQO com efeito fixo. A segunda é o M4 abaixo.

**(b) A ponte explícita: o *lift* na forma de regressão.**
M4 é um modelo de probabilidade linear com efeito fixo de lista. A variável dependente é a pertença
ao Top-NECr, com a mesma regra fracionária de empates; as variáveis explicativas são a flag, `mulher`
e `negra`.

| | 2018 | 2022 |
|---|---|---|
| Coeficiente da flag (EP) | 0,645 (0,020) | 0,543 (0,016) |
| P(Top \| comp) / P(Top \| não comp), brutas | 0,819 / 0,238 | 0,810 / 0,342 |

Esse modelo mostra que a sobrerrepresentação no núcleo **sobrevive aos controles de gênero e raça**,
e é isso que responde à linha 192. Ele conecta os dois testes sem nenhum objeto novo: a mesma
definição de núcleo, a mesma flag e a mesma comparação dentro da lista. Cuidado com a leitura: o
coeficiente é uma diferença de probabilidades, e a razão bruta (3,44 / 2,37) **não** é o *lift*.
O *lift* compara com `G·k/C`, e não com os não competitivos.

**(c) Especificação decomposta, como segundo passo.**
Esta é a especificação atual, com contagens por cargo, vereador e votação defasada, mas usando
efeito fixo de lista ou `ln(C_l)` no lugar de `ln(magnitude)`. Ela responde **quais** credenciais
pesam e se a flag binária as resume bem. Nesse papel, os AMEs de vereador e da votação defasada
viram argumentos a favor da definição adotada, ou mostram onde ela perde informação.

**Um achado adicional da ponte: *lift* por magnitude.** Com o M4 separado por grupo de magnitude:

| Magnitude | 2018: coef. (EP) | P(Top\|comp) / P(Top\|não) | 2022: coef. (EP) | P(Top\|comp) / P(Top\|não) |
|---|---|---|---|---|
| Pequeno | 0,571 (0,043) | 0,863 / 0,494 | 0,390 (0,028) | 0,824 / 0,572 |
| Médio | 0,688 (0,033) | 0,819 / 0,281 | 0,584 (0,027) | 0,806 / 0,362 |
| Grande | 0,658 (0,031) | 0,787 / 0,119 | 0,613 (0,026) | 0,804 / 0,214 |

A chance de um competitivo estar no núcleo fica **em torno de 0,8 em todas as magnitudes**. O que
varia é a chance de um **não** competitivo entrar, que cai com a magnitude porque o núcleo ocupa uma
fração menor de listas maiores. O gradiente da `tbl-cap3-01` ("o núcleo se torna mais discriminante
nos distritos de maior magnitude", linha 116) vem então sobretudo da **exclusão dos não
competitivos**, e não de uma inclusão maior dos competitivos. Na diferença com efeito fixo, o
gradiente só aparece com clareza em 2022. Isso não derruba a leitura da Discussão (linha 190), mas
muda o mecanismo que ela deveria enunciar. Vale checar antes de defender "partidos distinguem melhor
nos distritos grandes".

---

## 5. Três formas de posicionar a regressão

| Opção | Onde entra | Papel | Custo |
|---|---|---|---|
| **A. Segundo teste principal (recomendada)** | Em "Resultados", logo após o Top-NECr | Implicação I2. Especificação (a) como principal, (b) como ponte e (c) como decomposição | Exige refazer o modelo, tocar introdução, método e discussão, e resolver a seção 3.1 |
| B. Robustez | Em "Robustez", ao lado do Top-X% | "O resultado não depende de corte algum" | Barato, mas desperdiça os controles, que respondem à linha 192 e são mais do que robustez |
| C. Validação da medida | Antes dos resultados, em `sec-competitivos` | Justifica a flag: quais credenciais predizem a parcela | Boa para 3.1, mas desloca o teste da hipótese para a mensuração. Pode ser combinada com A, na camada (c) |

**Por que A.** O argumento da linha 17 é sobre alocação de recursos. O *lift* mede a composição de
um grupo definido por um corte, e a regressão mede a alocação em si. Tratar a regressão como
robustez inverte a hierarquia, porque ela está mais perto do enunciado do que o próprio *lift*. O
*lift* continua como teste principal porque tem uma referência contra o acaso fácil de interpretar e
porque o Cap. 4 depende do núcleo. A regressão entra no mesmo nível, como a segunda implicação.

### Esqueleto de estrutura (ordem das seções, não texto)

1. Introdução: argumento, depois as duas implicações observáveis I1 e I2, e por que as duas.
2. Dados.
3. Medidas: parcela intralista `s_il` (base comum a NECr e à regressão); NECr e Top-NECr;
   credenciais, com a flag e as contagens por cargo e a justificativa de vereador e do 10% do QE.
4. Resultados:
   - 4.1 Amplitude e concentração (descritivo, como está).
   - 4.2 I1: composição do núcleo (Top-NECr).
   - 4.3 I2: gradiente da parcela (regressão (a) e ponte (b)), com a resposta a gênero e raça aqui.
   - 4.4 Quais credenciais (regressão (c)).
5. Robustez: Top-X%; eleitos *ex post*; magnitude, com a leitura corrigida da seção 4.
6. Discussão: as duas implicações convergem; limites; ponte para o Cap. 4.

Hoje a discussão de gênero e raça fica na Discussão (linha 192) como ressalva ao *lift*. Na
estrutura A, ela passa a ser um **resultado**, na seção 4.3.

---

## 6. Decisões que ficam com o autor

1. **Definição de credencial na regressão principal.** Usar a flag binária, para ter o mesmo objeto
   do Top-NECr, ou manter as contagens como principal e a flag como ponte?
2. **Vereador e 10% do QE.** Manter a exclusão de vereador na flag, agora com a justificativa
   empírica da seção 3.1? Criar um regressor para o critério de 10% do QE na especificação
   decomposta?
3. **Como tratar o tamanho da lista.** Efeito fixo de lista (o estimando mais próximo do *lift*),
   `ln(C_l)` (mais simples, sem parâmetros incidentais) ou a variável dependente `s·C_l` com MQO e
   efeito fixo?
4. **Incluir o M4, o modelo de probabilidade linear da pertença ao núcleo.** É a ponte mais direta
   entre os dois testes, mas acrescenta mais um modelo ao capítulo.
5. **Magnitude.** Revisar a leitura das linhas 116 e 190 à luz da seção 4, com o gradiente vindo da
   exclusão dos não competitivos.
6. **Registro.** Se a especificação mudar, `regressao_fracionaria_cap3.py`,
   `tese/reports/regressao-fracionaria/` e `figs/cap3_regressao_fracionaria.png` precisam ser
   regenerados. A frase "atenuação … acompanha o crescimento do NECr" (linha 172) deve ser
   reavaliada com os números novos.
