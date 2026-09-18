# Caderno técnico — Composição do núcleo priorizado (Cap. 3, `sec-metricas`)

> **Este arquivo não entra na tese.** É material de estudo, escrito para que o autor
> entenda e consiga defender oralmente o que a seção faz. Nada aqui deve ser copiado
> para `tese/*.qmd`.
>
> Criado em 17/09/2026. Números recomputados de `data/processed/rrd_df_novo.parquet`
> na mesma data. Script que reproduz tudo: `notes/tecnico/diagnostico_metricas.py`.

---

## 0. A pergunta que a seção responde

O Cap. 3 já identificou, antes desta seção, duas coisas independentes uma da outra:

1. **Quem o partido priorizou financeiramente** — o núcleo Top-NECr, definido só pela
   distribuição de recursos dentro da lista (`sec-top-necr`).
2. **Quem tinha credencial eleitoral prévia** — o indicador binário de candidatura
   competitiva (`sec-competitivos`).

A seção `sec-metricas` não cria nenhum conceito novo. Ela só monta o **cruzamento**
entre esses dois conjuntos e define como medir se a sobreposição é maior do que o acaso
produziria. É uma seção de contabilidade, não de teoria — e é importante que você a
apresente assim, porque isso reduz o que você precisa defender.

Onde o código vive:

| O quê | Arquivo |
|---|---|
| Loop principal, por lista e agregação nacional | `src/2_gold/cap3_cobertura_top_necr.py` |
| Regra de empate (`acertos_fracionarios`) | `src/2_gold/cap3_taa_features.py:97-135` |
| Preparo da base, `dm_cat`, `Mp` | `src/2_gold/cap3_taa_features.py:148-186` |
| Definição de `candidato_competitivo` | `cap3_cobertura_top_necr.py:47-48` |

---

## 1. Os três insumos

Tudo na seção se constrói a partir de três objetos por lista $l$ (partido × UF × ano):

**$C_l$ — o tamanho da lista.** Número de candidaturas registradas. Inclui quem recebeu
zero de recursos partidários. Isso é uma escolha, não uma obviedade — ver §7.1.

**$g_{il} \in \{0,1\}$ — a credencial prévia.** Vem de `candidato_competitivo`, a versão
*ex-ante* (`cap3_cobertura_top_necr.py:47-48`). O docstring do módulo é explícito ao
proibir o uso de `candidato_forte_cs`, que é a versão *ex-post* de Cheibub & Sin. Se
alguém perguntar por que não a *ex-post*: porque ela usa o desempenho na própria eleição
que se quer explicar. $G_l = \sum_i g_{il}$.

**$k_l$ — o tamanho do núcleo.** $k_l = \lfloor NECr_l + 0{,}5 \rfloor$, e $k_l = 0$
quando a lista não recebeu nada. Não é escolhido: é uma função da concentração dos
recursos. Essa é a propriedade que dá à medida seu caráter endógeno — o partido revela o
tamanho do núcleo pelo formato da distribuição que ele mesmo produziu.

> **Detalhe que você deve saber:** o código escreve `max(1, floor(NECr + 0.5))`. Esse
> piso **nunca atua**. Como $NECr \geq 1$ sempre (verificado: mínimo observado é
> exatamente 1,0000), o arredondamento já devolve pelo menos 1. O `max(1, ·)` existe
> porque a mesma linha serve às regras de robustez *piso* e *teto*. Se perguntarem,
> a resposta é "é defensivo, não binding" — e você tem a verificação em
> `tese/reports/resultados-capitulo-3/21_verificacoes.csv` ("NECr entre 1 e o número de
> recebedores: OK").

---

## 2. Os pesos $w_{il}$: por que existe uma regra de empate

Ordena-se a lista por $R_{il}$ decrescente e entrega-se peso 1 às $k_l$ primeiras
posições. O problema aparece quando **um bloco de candidaturas com exatamente o mesmo
valor cruza a posição $k_l$**. Quem entra?

Três saídas possíveis, e por que as duas primeiras são ruins:

- *Desempatar por votos recebidos.* **Contamina a medida com informação ex-post.** Você
  estaria usando o resultado da eleição para definir quem o partido priorizou antes dela.
  Isso destruiria a interpretação de toda a seção.
- *Desempatar pela ordem das linhas no arquivo.* O resultado passaria a depender de como
  o TSE gravou o CSV. Não é reprodutível nem defensável.
- *Peso fracionário* (a escolha adotada). Se restam $m$ vagas no núcleo e o bloco empatado
  tem $n > m$ candidaturas, cada uma recebe $w = m/n$. É determinístico, independe da
  ordem física das linhas e não usa nada que aconteceu depois.

A propriedade que garante que isso não distorce nada: $\sum_i w_{il} = k_l$ exatamente.
O núcleo não muda de tamanho — só se reparte a fronteira.

**Quão frequente é o empate, na prática?**

| | Listas financiadas | Com bloco empatado cruzando $k_l$ | Com $H_l$ efetivamente fracionário |
|---|---|---|---|
| 2018 | 786 | 49 (6,2%) | **2** |
| 2022 | 648 | 108 (16,7%) | **19** |

O empate na fronteira é comum, mas quase sempre entre candidaturas que são *todas*
$g=0$ ou *todas* $g=1$ — nesses casos a fração não altera $H_l$. A regra muda o número em
2 listas em 2018 e 19 em 2022. **É uma salvaguarda, não um motor do resultado.** Essa é a
frase que resolve a pergunta na arguição.

---

## 3. $H_l$, precisão e cobertura: dois denominadores, duas perguntas

$$H_l = \sum_i w_{il}\, g_{il}$$

é quantas candidaturas com credencial prévia estão dentro do núcleo daquela lista.
Agrega-se por soma nacional, e só então se formam as razões:

$$\text{Precisão} = \frac{\sum_l H_l}{\sum_l k_l}, \qquad
  \text{Cobertura} = \frac{\sum_l H_l}{\sum_l G_l}$$

Mesmo numerador, denominadores diferentes — logo, **perguntas diferentes**:

- **Precisão**: *das vagas do núcleo, quantas foram para gente com credencial?*
  Olha do ponto de vista do partido. É baixa (33,9% em 2018, 28,6% em 2022) porque os
  núcleos são grandes e há pouca gente com credencial disponível.
- **Cobertura**: *dos candidatos com credencial, quantos o partido colocou no núcleo?*
  Olha do ponto de vista do candidato. É alta (80,9% nas duas eleições).

O par alto/baixo não é contradição — é a assinatura de um caso em que o conjunto-alvo
($G$) é muito menor que o conjunto selecionado ($k$). Em 2018: $\sum G_l = 973$ contra
$\sum k_l = 2.318$. Mesmo que o partido acertasse *todos* os competitivos, a precisão
máxima possível seria $973/2318 = 42\%$. **Precisão baixa aqui não é erro do partido, é
teto aritmético.** Você precisa ter esse cálculo na ponta da língua.

---

## 4. A referência aleatória: o que ela mantém fixo

Esta é a parte conceitualmente mais densa e a que mais rende pergunta de banca.

A referência é: *dentro de cada lista, sorteiam-se $k_l$ das $C_l$ candidaturas, sem
reposição, com igual probabilidade.* Sob esse sorteio, o número de candidaturas com
credencial que cai no núcleo é uma variável hipergeométrica, cuja média é

$$\mathbb{E}[H_l] = G_l \cdot \frac{k_l}{C_l}$$

**De onde vem essa fórmula, sem apelar à distribuição hipergeométrica:** cada candidatura
individual tem probabilidade $k_l/C_l$ de ser sorteada. $H_l$ é a soma de $G_l$ variáveis
indicadoras, uma por candidatura com credencial. Pela linearidade da esperança — que vale
mesmo com as inclusões sendo dependentes entre si —, a média da soma é a soma das médias:
$G_l \times k_l/C_l$. Você não precisa da distribuição completa porque só usa a média.

**O que a referência mantém fixo (e por que isso importa):** ela preserva $C_l$, $G_l$ e
$k_l$. Ou seja, ela **não** pergunta "o partido deveria ter concentrado recursos?". A
concentração já está dada, porque $k_l$ foi derivado dela. A pergunta que o benchmark faz
é mais estreita e mais honesta:

> *Dado que o partido concentrou seus recursos em $k_l$ candidaturas efetivas, ele
> escolheu **quais** $k_l$ de um jeito relacionado à credencial eleitoral prévia, ou de
> um jeito indistinguível de um sorteio?*

Essa delimitação é uma **força** do desenho, não uma limitação a esconder: ela isola a
composição do núcleo do seu tamanho. Diga isso antes que perguntem.

**Consequência elegante e verificável:** se um partido distribui recursos em partes
iguais entre todos, $NECr_l = C_l$, logo $k_l = C_l$, o núcleo é a lista inteira,
$H_l = G_l = \mathbb{E}[H_l]$ e o lift é exatamente 1. A medida devolve "nenhuma
priorização" justamente no caso em que não houve priorização. Isso acontece de fato: em
2018, 207 das 786 listas financiadas têm $k_l = C_l$, e nelas a razão $NECr_l/C_l$ é 0,978
em média — são listas quase perfeitamente igualitárias (ou com um único candidato: 137
das 207). Ver §7.3 para o efeito agregado.

---

## 5. O lift

$$\text{Lift} = \frac{\sum_l H_l}{\sum_l G_l k_l / C_l}$$

**Por que o lift da precisão é igual ao da cobertura.** Substituindo o numerador
observado pelo esperado e mantendo o denominador, a razão observado/esperado na escala da
precisão é $\frac{\sum H/\sum k}{\sum \mathbb{E}[H]/\sum k}$ — o $\sum k$ cancela. O
mesmo com $\sum G$ na cobertura. Ambas colapsam em $\sum H / \sum \mathbb{E}[H]$.
Verificado numericamente: 1,8909 pelas três vias em 2018. Não é coincidência, é
cancelamento algébrico — e é por isso que a tese reporta **um** lift, não dois.

**Razão de somas, não média de razões.** O lift nacional pondera implicitamente pelas
listas maiores (que têm mais $\mathbb{E}[H]$). A alternativa — calcular o lift lista a
lista e tirar a média — dá outro número:

| | Razão de somas (usada) | Média dos lifts por lista | Mediana |
|---|---|---|---|
| 2018 | 1,891 | 2,736 | 2,000 |
| 2022 | 1,855 | 2,420 | 1,889 |

A média por lista é maior porque listas minúsculas com um acerto produzem lifts enormes e
pesam igual a São Paulo. A razão de somas é a escolha defensável: ela responde "entre
todas as posições de núcleo do país, qual a taxa de acerto relativa", que é a pergunta
substantiva. **Saiba que a alternativa favoreceria o seu argumento e que você não a
escolheu** — isso é o oposto de *p-hacking* e vale dizer.

---

## 6. Dois exemplos trabalhados

Leve estes dois na cabeça. Eles cobrem quase tudo que pode ser perguntado.

### 6.1 PSL/AC 2018 — o núcleo **erra**

$C_l = 8$, $G_l = 3$, $R_l = 261$, $NECr = 4{,}712$, $k_l = 5$.

| pos | $R_{il}$ | $s_{il}$ | $w_{il}$ | $g_{il}$ |
|---|---|---|---|---|
| 1 | 59 | 0,2253 | 1 | 0 |
| 2 | 59 | 0,2253 | 1 | 0 |
| 3 | 59 | 0,2253 | 1 | 0 |
| 4 | 58 | 0,2229 | 1 | 0 |
| 5 | 26 | 0,1011 | 1 | **1** |
| 6 | 0 | 0 | 0 | 0 |
| 7 | 0 | 0 | 0 | **1** |
| 8 | 0 | 0 | 0 | **1** |

$H_l = 1$, $\mathbb{E}[H_l] = 3 \times 5/8 = 1{,}875$, lift local $= 0{,}533$.

O que esse caso ensina: (a) a medida **pune** listas onde a priorização ignora a
credencial — não é construída para confirmar a hipótese; (b) dois dos três competitivos
receberam **zero** e ficaram fora do núcleo; (c) os valores são irrisórios (R$ 261 na
lista toda) — o NECr é invariante à escala, ele lê só o *formato* da distribuição, não o
volume. Essa última é uma limitação real que vale reconhecer antes que apontem.

### 6.2 PATRIOTA/SP 2022 — o empate na fronteira, em ação

$C_l = 70$, $G_l = 5$, $R_l \approx 10{,}6$ milhões, $NECr = 31{,}81$, $k_l = 32$.

As posições 32, 33 e 34 estão empatadas em exatamente R$ 100.000. Restava **1** vaga para
**3** candidaturas, então cada uma recebeu $w = 1/3$. A soma dos pesos fecha em 32,000.

Como as três empatadas têm $g = 0$, $H_l = 5{,}000$ — inteiro. $\mathbb{E}[H_l] =
5 \times 32/70 = 2{,}286$, lift local $= 2{,}188$.

É o exemplo perfeito: mostra a mecânica do empate funcionando **e** mostra que ela
frequentemente não altera o resultado.

---

## 7. As sete decisões que a banca vai atacar

Cada uma tem a mesma estrutura: qual é a escolha, em que direção ela empurra o resultado,
e qual é a alternativa. Você não precisa que todas estejam no texto — precisa saber todas.

### 7.1 Candidaturas com $R = 0$ ficam dentro de $C_l$

Elas entram no ranking empatadas na lanterna e praticamente nunca entram no núcleo. Mas
ficam no denominador de $\mathbb{E}[H_l] = G_l k_l / C_l$: inflar $C_l$ **reduz** o
esperado e portanto **aumenta** o lift.

| | Candidatos em listas financiadas | Com $R=0$ | Competitivos entre eles |
|---|---|---|---|
| 2018 | 7.395 | 1.811 (24,5%) | 64 |
| 2022 | 9.345 | 756 (8,1%) | 37 |

Recomputando com $C_l$ e $G_l$ restritos a quem recebeu algo:

| | Lift publicado | Lift restrito a $R>0$ |
|---|---|---|
| 2018 | 1,891 | **1,697** |
| 2022 | 1,855 | **1,824** |

**Esta é a sensibilidade mais séria da seção.** O lift de 2018 cai ~10%. A defesa é
conceitual e você precisa acreditar nela: a decisão de dar zero a um candidato **é** uma
decisão de alocação. Excluí-lo do denominador equivaleria a condicionar a análise numa
escolha que é parte do objeto — o partido escolheu não financiá-lo. Note também que o
resultado qualitativo não muda: 1,70 continua muito acima de 1.

### 7.2 Listas sem nenhum recurso partidário: cobertura e lift discordam

São 73 listas em 2018 (235 candidatos, 12 competitivos, 3 eleitos) e 63 em 2022
(330 candidatos, 2 competitivos, 0 eleitos). Elas têm $k_l = 0$.

O tratamento é **assimétrico**, e é bom que seja:

- Na **cobertura**, seus $G_l$ permanecem no denominador nacional. Elas só podem
  *baixar* a cobertura (0,8086 com elas contra 0,8187 sem, em 2018). É a escolha
  conservadora.
- No **lift**, elas somem inteiramente, porque $H_l = 0$ e $\mathbb{E}[H_l] =
  G_l \cdot 0/C_l = 0$. Não entram nem no numerador nem no denominador. O lift é
  idêntico com ou sem elas.

Isso não é inconsistência: a cobertura é uma pergunta sobre *todos* os competitivos do
país, e o lift é uma pergunta sobre *seleção dentro de núcleos*, que ali não existem.

### 7.3 Listas com $k_l = C_l$ puxam o lift para baixo

Como visto em §4, listas igualitárias têm lift exatamente 1 por construção.

| | Listas $k=C$ | Lift nessas | Lift nas demais ($k<C$) | Lift publicado |
|---|---|---|---|---|
| 2018 | 207 de 786 | 1,000 | **2,227** | 1,891 |
| 2022 | 100 de 648 | 1,000 | **1,873** | 1,855 |

Em 2018 elas respondem por 14,5% de $H$ e diluem sensivelmente o agregado. **O número
publicado é conservador**: restringir às listas em que o núcleo é um subconjunto próprio
da lista eleva o lift de 1,89 para 2,23. De novo, a direção do viés favorece o argumento —
saiba disso e diga.

### 7.4 Listas sem nenhum competitivo ($G_l = 0$) saem do lift

333 das 786 listas financiadas em 2018 e 275 das 648 em 2022 não têm nenhum candidato com
credencial prévia. Nelas $H_l = \mathbb{E}[H_l] = 0$. O lift nacional é, portanto,
efetivamente calculado sobre 453 listas em 2018 e 373 em 2022 — pouco mais da metade das
financiadas. Isso **não** é um problema (uma lista sem alvo não informa sobre pontaria),
mas você deve saber o número antes que alguém o descubra.

### 7.5 A regra de empate

Coberta em §2. Resumo defensivo: determinística, *ex-ante*, preserva $\sum w = k$, e altera
$H_l$ em 2 de 786 listas (2018) e 19 de 648 (2022).

### 7.6 O arredondamento em 0,5

Convenção. O código já calcula as três regras — `piso`, `arredondado`, `teto` — e os
resultados estão em `tese/reports/resultados-capitulo-3/15_cobertura_nacional.csv`. Para
eleitos em 2018, a cobertura vai de 82,6% (piso) a 87,7% (teto). **A escolha da regra não
muda nenhuma conclusão**, e você tem a tabela pronta para mostrar.

### 7.7 Razão de somas

Coberta em §5.

---

## 8. Perguntas de arguição

Escreva a resposta de cada uma com suas palavras **antes** de redigir a seção. Se alguma
travar, o problema está na compreensão, não na redação.

1. Por que a precisão é tão baixa se a cobertura é tão alta? Qual é a precisão máxima
   aritmeticamente possível em 2018?
2. O seu benchmark aleatório testa se o partido concentrou recursos? Se não, o que ele
   testa?
3. Por que $\mathbb{E}[H_l] = G_l k_l / C_l$ sem precisar da distribuição hipergeométrica
   completa?
4. Um partido que dá o mesmo valor a todo mundo tem qual lift? Por quê? Isso é bom ou ruim
   para a medida?
5. Você reporta um lift ou dois? Por quê?
6. Se eu excluir os candidatos que receberam zero, o que acontece com o seu lift? Você
   consegue justificar mantê-los?
7. Por que não desempatar por votos na fronteira do núcleo?
8. Por que o lift ignora as listas sem recursos mas a cobertura não?
9. O seu lift é a média dos lifts das listas? O que mudaria se fosse?
10. Em que fração das listas a sua medida efetivamente discrimina alguma coisa?
11. O NECr distingue uma lista que distribuiu R$ 10 milhões de outra que distribuiu
    R$ 261 do mesmo jeito? Isso é problema?
12. A sua medida pode dar lift alto sem que haja coordenação partidária? Qual seria a
    explicação alternativa?

*(A 12 é a pergunta difícil e não é respondida por esta seção — ela é do Cap. 4. Mas
esperam que você a antecipe.)*

---

## 9. Como refazer qualquer número deste caderno

```bash
cd C:/Users/yuri_taba/Desktop/recursos-campanha-local
python -u notes/tecnico/diagnostico_metricas.py
```

O script é autocontido e reimporta as mesmas funções que a tese usa
(`acertos_fracionarios`, `_preparar`), então não há risco de o caderno divergir do
pipeline. Os agregados nacionais conferem com
`data/processed/df_cobertura_top_necr_resumo.csv` e com
`tese/reports/resultados-capitulo-3/15_cobertura_nacional.csv`.
