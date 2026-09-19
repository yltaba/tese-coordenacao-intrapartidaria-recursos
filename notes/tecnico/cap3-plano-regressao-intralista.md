# Plano: modelo fracionário do Cap. 3 com tamanho da lista e comparação intralista

> **Implementado em 18/09/2026** em `tese/scripts/regressao_fracionaria_cap3.py` (etapas 1–4 e 6;
> a etapa 5, diagnóstico de transição, não foi feita). Equivalência com Poisson com EF conferida numa
> subamostra de 80 listas (β idêntico até 1e−6).

Material de apoio. **Não é texto da tese.** O plano parte da decisão de 18/09 registrada em
`cap3-regressao-como-teste.md`, seção 0. A regressão passa a ser o **teste contínuo da
priorização**: sem impor corte algum, as credenciais estão associadas a uma parcela maior dos
recursos da própria lista?

Um piloto já foi rodado: `notes/tecnico/cap3_piloto_logit_condicional.py`. Ele serve para mostrar
que o plano é viável e para antecipar o que muda nos resultados. **Não é a versão final.**

---

## 1. O problema e o objetivo

O modelo atual (`tese/scripts/regressao_fracionaria_cap3.py`) é um GLM Binomial/logit sobre
`s_il = R_il/R_l`. Ele junta todas as listas sem efeito fixo e usa `ln(magnitude)` como
aproximação do tamanho da lista. Três consequências:

- Parte da variação da variável dependente é mecânica: a parcela média de uma lista é `1/C_l`.
- A magnitude só funciona como aproximação imperfeita do tamanho da lista. Quando `ln(C_l)` entra
  no modelo, o efeito da magnitude vai a zero (−0,27 / +0,93 pp).
- A pergunta respondida é "candidaturas com credencial têm parcelas maiores **do que candidaturas de
  outras listas**", e não "**do que seus colegas de lista**".

**Objetivo:** estimar o efeito das credenciais comparando cada candidatura aos seus colegas da mesma
nominata. É o mesmo tipo de comparação que o Top-NECr faz, agora sem corte.

---

## 2. Especificação

### 2.1 Por que só adicionar `ln(C_l)` não basta

Pôr `ln(C_l)` no modelo atual controla o nível médio de `1/C_l`, mas o modelo continua comparando
candidaturas de listas diferentes. Outras diferenças entre listas contaminam o coeficiente das
credenciais: partido, UF, quanto dinheiro a lista recebeu, quantos competitivos ela tem. Adicionar o
tamanho da lista é um passo intermediário, útil como diagnóstico, mas ainda não é uma comparação
intralista.

### 2.2 Modelo principal: logit fracionário condicional (efeito fixo de lista)

As parcelas de uma lista somam 1. O modelo natural para parcelas dentro de um grupo é um *softmax*
por lista:

    E[s_il | X, l] = exp(x_il'β) / Σ_{j ∈ l} exp(x_jl'β)

Estimação por quase-verossimilhança: maximiza-se Σ_l Σ_i s_il · log p_il.

Propriedades que resolvem o problema:

- **O efeito fixo de lista cai da equação.** Qualquer termo constante na lista (tamanho, magnitude,
  partido, UF, R_l) se cancela no *softmax*. A comparação é intralista por construção.
- **O tamanho da lista está controlado, mas não é estimado.** O pedido de "adicionar o n de
  candidatos" fica atendido por construção: o `C_l` entra no denominador do *softmax* e é absorvido
  junto com o efeito fixo. Por isso, **nem `ln(C_l)` nem `ln(magnitude)` entram como regressores.**
  Qualquer variável constante dentro da lista não é identificada.
- **Não há problema de parâmetros incidentais.** Diferentemente de um logit com ~650–790 *dummies*,
  o efeito fixo é eliminado analiticamente e não estimado. Esse estimador é equivalente a uma
  regressão de Poisson (PPML) de `s_il` com efeitos fixos de lista.
  - Referências a conferir antes de citar (não estão no `.bib`): Guimarães, Figueiredo & Woodward
    (2003) para a equivalência entre logit condicional e Poisson com efeito fixo; Mullahy (2015)
    para regressão fracionária multivariada.
  - A aplicação continua dentro da família de @papke1996, que já está no `.bib`: quase-verossimilhança
    para resposta fracionária.
- **Erros-padrão:** clusterizados por lista, com um estimador sanduíche calculado sobre os escores
  somados por lista.

Na prática, `statsmodels` não converge com ~800 *dummies* (o SVD falhou no teste). Por isso o
piloto implementa diretamente o método de Newton sobre a verossimilhança condicional, em cerca de 20
linhas. `pyfixest` (`fepois`) não está instalado. Instalá-lo daria uma checagem independente, mas
não é necessário.

### 2.3 Escala de interpretação

- **Principal: `exp(β)`, a razão de parcelas contra um colega de lista.** Por exemplo, "com
  credencial, a parcela esperada é X vezes a de um colega da mesma lista sem credencial".
  - É uma razão, como o *lift*, o que ajuda a ler os dois testes lado a lado.
  - É comparável entre 2018 e 2022 sem o efeito mecânico da mudança no tamanho das listas.
- **Secundária: AME em pontos percentuais.** O efeito marginal sobre a própria parcela é
  `β · p_il(1 − p_il)`, com a média tomada sobre as candidaturas. Para a variável binária, usar a
  variação discreta (0 → 1, recalculando o *softmax* da lista), e não a derivada.
  - Nessa escala, a queda entre 2018 e 2022 continua misturando priorização com tamanho de lista.
    O texto precisa dizer isso.

### 2.4 Regressores

Dois modelos, com a decisão da seção 0 de `cap3-regressao-como-teste.md` já aplicada:

| Modelo | Regressores | Papel |
|---|---|---|
| **R1 (principal)** | `candidato_competitivo` (a mesma variável do Top-NECr) + `mulher` + `negra` | Testa, sem corte, a mesma credencial do teste de estrutura |
| **R2 (decomposição)** | Contagens por cargo (Gov, Sen, DF, DE, Pref, Ver) + `prop_votos_nominais_lag` + `mulher` + `negra` | Mostra quais credenciais pesam. Aqui se decide o que fazer com vereador e com o critério de 10% do QE |

No R2, há duas decisões pendentes (ver `cap3-regressao-como-teste.md`, seção 3.1):

- Acrescentar um indicador de "≥10% do QE sem vitória" (`alcancou_10pct_qe_hist & ~incumbente`).
  Sem ele, cerca de 25–30% dos competitivos entram no R2 sem contraparte.
- Manter vereador. Recomendado, porque seu coeficiente justifica ou questiona a exclusão de vereador
  da variável binária.

### 2.5 Amostra

- Listas com `R_l > 0`, como hoje. CPF "-4" e raça/cor não declarada saem, como hoje.
- **Novo:** listas com uma só candidatura (`C_l = 1`) não contribuem para a verossimilhança
  condicional, porque não há colega de lista para comparar. No piloto, a mudança é:

  | | 2018 | 2022 |
  |---|---|---|
  | Candidaturas: atual → condicional | 7.391 → 7.254 | 9.288 → 9.263 |
  | Listas: atual → condicional | 786 → **649** | 648 → 623 |

  Em 2018, **137 listas** saem. Documentar essa queda. Ela não é um erro: essas listas não têm
  priorização intralista possível, e o Top-NECr também não as distingue do acaso.
- Listas em que todas as candidaturas têm os mesmos regressores também não contribuem para β.
  Relatar quantas listas têm variação na credencial.

---

## 3. Resultados do piloto (não finais)

| | 2018 | 2022 |
|---|---|---|
| **R1: `exp(β)` da credencial (EP de β)** | **8,16** (0,083) | **4,58** (0,054) |
| R1: AME da credencial (variação discreta 0→1, versão final) | 20,3 pp | 12,1 pp |
| R1: `exp(β)` de mulher / negra | 1,56 / 0,74 | 1,36 / **0,92 (p = 0,02)** |
| R2: `exp(β)` de Dep. Federal (por vitória) | 1,95 | 1,52 |
| R2: `exp(β)` de Senador | 3,61 | 3,44 |
| R2: `exp(β)` de Governador | 3,46 (p = 0,002) | 1,33 (p = 0,11) |
| R2: `exp(β)` de Vereador | 1,40 | 1,22 |

O que muda em relação ao que o capítulo diz hoje:

1. **Negra em 2022.** Hoje o texto diz "não distinguível de zero" (AME −0,004 pp). No modelo
   intralista, o efeito fica **negativo e significativo**, embora pequeno (−0,45 pp; razão 0,92).
   A leitura das linhas 174–176, de que a regra de 2022 teria nivelado a distribuição, fica mais
   fraca. É a mudança mais importante para a redação.
2. **Senador em 2018.** O AME cai de 11,9 para cerca de 8,1 pp.
3. **Governador em 2022.** Continua não significativo.
4. **O que fica de pé:** todas as credenciais têm efeito positivo, com uma hierarquia
   Sen/Gov > DF > DE > Pref > Ver. Mulher tem efeito positivo nos dois anos.

---

## 4. Etapas de implementação

Arquivo: `tese/scripts/regressao_fracionaria_cap3.py`. O autor decide se o agente edita o arquivo
ou se ele próprio edita a partir do piloto.

1. **Montagem da base (`montar_base`).**
   - Acrescentar a coluna `C_l`.
   - Descartar as listas com `C_l = 1` e registrar as contagens do antes e do depois.
   - Criar o indicador `so_10pct_qe`, se a decisão da seção 2.4 for incluí-lo.
   - Remover `ln_qt_vaga` dos regressores.
2. **Estimador.**
   - Nova função `logit_condicional_fracionario(s, X, lista)`, com Newton e o sanduíche por cluster
     (a correção L/(L−1) já está no piloto).
   - Devolve β, EP, as parcelas previstas e o número de iterações.
3. **Efeitos.**
   - `razao = exp(β)`, com IC de `exp(β ± 1,96·EP)`.
   - AME: para regressores contínuos e contagens, a média de `β·p(1−p)` com EP pelo método delta,
     reaproveitando o Jacobiano numérico que já existe no script. Para variáveis binárias, a
     variação discreta com recálculo do *softmax*.
4. **Modelos.** R1 e R2, separados por ano, como hoje.
5. **Diagnóstico de transição (robustez, não principal).** O GLM atual com `ln(C_l)` no lugar de
   `ln(magnitude)`. Serve para mostrar no apêndice ou na robustez quanto dos resultados antigos
   vinha do tamanho da lista.
6. **Saídas.**
   - Em `tese/reports/regressao-fracionaria/`: `coeficientes.csv`, `ames.csv` e um novo
     `razoes.csv`, cada um com a coluna `modelo` ∈ {R1, R2, transicao}; mais `amostra.csv`, com as
     listas e candidaturas antes e depois dos filtros e o número de listas com variação na
     credencial.
   - A figura `figs/cap3_regressao_fracionaria.png` passa a mostrar R2 na escala de razão com o eixo
     em log e a linha de referência em 1. O bloco de controles fica sem a magnitude. Decidir se R1
     entra na mesma figura (como uma linha à parte no topo) ou em outra.

---

## 5. Verificações antes de aceitar os números

| Checagem | Critério |
|---|---|
| Parcelas previstas somam 1 em cada lista | Erro máximo < 1e−8 |
| Convergência | Passo de Newton < 1e−10; relatar as iterações |
| Equivalência com o Poisson com efeito fixo | Numa subamostra (por exemplo, 50 listas), `sm.GLM(..., Poisson)` com *dummies* devolve o mesmo β. Ou usar `pyfixest.fepois`, se for instalado |
| Invariância | Somar uma constante a todos os regressores de uma lista não altera β |
| Coerência com o Top-NECr | O R1 tem `exp(β) > 1` em todos os grupos de magnitude. Rodar R1 por grupo como contraparte contínua da `tbl-cap3-01` |
| Sensibilidade | EP clusterizado por partido (em vez de lista); o R1 sem `mulher`/`negra` (para ver quanto as cotas mudam o coeficiente da credencial) |

---

## 6. O que muda no capítulo (pontos de contato, sem texto)

A redação é do autor. Estes são os trechos que dependem dos números novos:

- **Linha 166 (método).** Mudam a unidade de comparação (intralista), o estimador e o efeito fixo,
  e a escala de leitura (razão e AME).
- **Linha 168 (controles).** Sai a justificativa da magnitude como "controle pelo tamanho das
  nominatas". O tamanho da lista agora é absorvido pelo efeito fixo.
- **Linha 170 (resultados).** Todos os números mudam. Vereador e a votação defasada precisam ser
  mencionados, porque aparecem na figura.
- **Linha 172 (atenuação de 2018 para 2022).** Reavaliar: na escala de razão, a queda (8,2 → 4,6)
  já não carrega o efeito mecânico de `1/C_l`.
- **Linhas 174–176 (mulher/negra).** O resultado de negra em 2022 muda (seção 3, item 1).
- **Legenda de `fig-reg-frac`.** Mudam a escala e o modelo.
- **Seção `sec-dados`.** Registrar a exclusão das listas com `C_l = 1` da regressão, que o
  Top-NECr não exclui.

## 7. Registro depois da implementação

- **`CLAUDE.md`:** atualizar a linha de `tese/reports/regressao-fracionaria/` (data, especificação
  intralista, novo `razoes.csv`).
- **`notes/daily/`:** registrar a mudança de especificação e o resultado novo de negra em 2022.
- **`cap3-regressao-como-teste.md`:** marcar as seções 3.2 e 4(a) como resolvidas.
