# Rascunho: `sec-premio-credenciais` com a regressão intralista

**Texto redigido por IA a pedido explícito do autor (18/09/2026). Não está no `.qmd`.** Serve de base para o autor reescrever com a própria voz (contrato de autoria: memória `no-ai-text-in-thesis-body`).

Terceira versão (18/09): a razão de parcelas $\exp(\beta)$ passa a ser a medida principal no texto e na figura. As fontes de cada número estão nas notas ao final.

---

### Prêmio das credenciais eleitorais prévias {#sec-premio-credenciais}

O Top-NECr depende de um corte que separa o núcleo priorizado do restante da nominata. Esta seção examina a mesma relação sem esse corte, usando toda a distribuição dos recursos partidários dentro de cada lista. A pergunta passa a ser se candidaturas com credenciais eleitorais prévias recebem uma parcela maior dos recursos do que seus correligionários, e não apenas se estão entre os mais financiados. Como a base registra, para cada candidatura, o número de vitórias anteriores por cargo desde 1998 (@sec-dados), é possível também verificar quais credenciais pesam mais nessa alocação.

A variável dependente é a parcela intralista de recursos partidários, $s_{il}=R_{il}/R_l$, a mesma razão empregada no cálculo do NECr. O modelo pertence à família de modelos fracionários de @papke1996, com uma diferença: a parcela esperada de cada candidatura é definida em relação às demais candidaturas da mesma lista,

$$
E[s_{il}\mid X_l]=\frac{\exp(x_{il}'\beta)}{\sum_{j=1}^{C_l}\exp(x_{jl}'\beta)} .
$$

Tudo o que é comum aos integrantes de uma lista se cancela entre o numerador e o denominador dessa expressão: o tamanho da nominata, a magnitude do distrito, o partido, a UF e o volume total de recursos. Os coeficientes resultam, assim, apenas da comparação entre correligionários que disputam a mesma eleição no mesmo distrito, como no Top-NECr. O modelo equivale a uma regressão de Poisson da parcela com efeitos fixos de lista. Os erros-padrão são clusterizados por lista, e as estimações são feitas separadamente para 2018 e 2022, dadas as mudanças institucionais entre os pleitos.

Os resultados são apresentados como razões de parcelas. Para duas candidaturas da mesma lista, a razão entre suas parcelas esperadas é $\exp\big((x_{il}-x_{jl})'\beta\big)$. Assim, $\exp(\beta)$ indica quantas vezes a parcela esperada de uma candidatura supera a de um correligionário que difere dela apenas em uma unidade do atributo considerado. Essa razão não depende do tamanho da lista nem da composição das demais candidaturas, o que permite comparar eleições e magnitudes. Os efeitos em pontos percentuais da parcela, por sua vez, diminuem mecanicamente à medida que as nominatas crescem, porque a parcela média de cada candidatura fica menor. Nas contagens de vitórias, a razão se refere a cada vitória adicional e se acumula de forma multiplicativa.

As covariáveis de interesse reproduzem, de forma desagregada, os critérios usados para identificar as credenciais na @sec-competitivos. O primeiro critério, a vitória anterior, entra como contagem de vitórias por cargo. O segundo, a votação de ao menos 10% do quociente eleitoral em disputa proporcional anterior, entra como indicador restrito às candidaturas sem vitória acima de vereador, pois é somente para elas que esse critério altera a classificação. A contagem de vitórias para vereador, que não integra a definição de credencial, também é incluída, assim como a proporção de votos nominais obtida pela candidatura em sua lista na eleição anterior para deputado federal. Como controles, entram indicadores de candidatura de mulher e de pessoa negra, grupos aos quais a legislação vincula critérios de repasse. A magnitude do distrito não entra como covariável, porque é constante dentro da lista. Pela mesma razão, as nominatas com uma única candidatura ficam fora da estimação, já que não oferecem comparação entre correligionários. São analisadas 7.254 candidaturas em 649 listas em 2018 e 9.263 candidaturas em 623 listas em 2022.

As razões estimadas estão na @fig-reg-frac. Vitórias anteriores para todos os cargos estão associadas a parcelas maiores dos recursos da lista nas duas eleições, com exceção de governador em 2022. Cada vitória anterior para deputado federal dobra a parcela esperada em 2018 (razão de 2,00) e a multiplica por 1,55 em 2022. Uma candidatura com dois mandatos anteriores de deputado federal recebe, portanto, cerca de quatro vezes a parcela de um correligionário sem esse histórico em 2018. Para deputado estadual, as razões são de 1,71 e 1,48, e para prefeito, de 1,57 e 1,42. As estimativas para senador (3,76 e 3,45) e para governador em 2018 (3,59) são as mais altas, mas esses cargos aparecem em poucas candidaturas, e seus intervalos de confiança são os mais amplos. A vitória para vereador tem a menor associação entre os cargos, com razões de 1,30 e 1,18, o que é coerente com sua exclusão da definição de credencial.

O critério de votação também tem associação própria. Entre candidaturas sem vitória acima de vereador, ter alcançado 10% do quociente eleitoral em uma disputa anterior multiplica a parcela esperada por 2,89 em 2018 e por 1,70 em 2022. A votação obtida na própria lista na eleição anterior segue na mesma direção: cada dez pontos percentuais a mais na proporção de votos nominais correspondem a uma parcela 15% maior em 2018 e 11% maior em 2022.

Quando os dois critérios são reunidos no indicador binário usado no Top-NECr, a candidatura com credencial prévia tem uma parcela esperada 8,16 vezes maior que a de um correligionário sem credencial em 2018 e 4,58 vezes maior em 2022. Em pontos percentuais, essas diferenças equivalem, em média, a 20,3 e 12,1 pontos da parcela intralista.

A queda entre as duas eleições não é um efeito mecânico do crescimento das nominatas após o fim das coligações, já que a razão não depende do tamanho das listas. O resultado é compatível com o aumento do NECr discutido na @sec-discussao-cap3: os recursos passaram a ser distribuídos entre mais candidaturas, e a vantagem de quem tem credenciais diminuiu, embora continue expressiva.

A @tbl-cap3-03-premio-magnitude apresenta essa razão por grupo de magnitude, estimada pela interação entre o indicador de credencial e a magnitude do distrito. Em 2018, a candidatura com credencial recebe 4,76 vezes a parcela de um correligionário sem credencial nos distritos pequenos, 10,61 vezes nos médios e 13,48 vezes nos grandes. Em 2022, as razões são de 2,95, 5,57 e 7,99. A interação é positiva e estatisticamente significativa nas duas eleições. O padrão acompanha o *lift* por magnitude da @tbl-cap3-01-lift-magnitude, e os dois testes indicam uma priorização mais acentuada de candidaturas com credenciais nos distritos de maior magnitude.

Ser mulher está associado a uma parcela maior dos recursos intralista nas duas eleições, com razões de 1,44 em 2018 e de 1,32 em 2022, mesmo com as credenciais eleitorais sob controle. O resultado é coerente com o piso legal de repasse às candidaturas femininas, que assegura recursos a essas candidatas independentemente de seu histórico eleitoral.

As candidaturas negras recebem parcelas menores que as de seus correligionários nas duas eleições. Em 2018, sua parcela esperada corresponde a 74% da de um correligionário comparável. Em 2022, primeira eleição em que a legislação vinculou os repasses à proporção de candidaturas negras na nominata, a razão sobe para 0,93, mas continua estatisticamente distinguível da paridade. A regra coincide, portanto, com uma redução expressiva da desvantagem, mas não com seu desaparecimento. As causas dessa desigualdade envolvem fatores estruturais da sociedade brasileira que extrapolam o objeto desta tese.

![Prêmio das credenciais eleitorais prévias na alocação intralista de recursos partidários em 2018 e 2022: razões de parcelas $\exp(\beta)$ das vitórias anteriores por cargo (por vitória adicional), da votação anterior e dos controles (mulher, negra), em escala logarítmica, com referência em 1. Logit fracionário condicional à lista [@papke1996]; intervalos de 95% com erros-padrão clusterizados por lista.](../figs/cap3_regressao_fracionaria.png){#fig-reg-frac fig-align="center" width="100%"}

---

## Notas para o autor (fora do texto)

1. **Fontes dos números** (todos em `tese/reports/regressao-fracionaria/`):
   - Razões por cargo, votação t−1 (+10 p.p.), QE, mulher e negra: `coeficientes.csv`, modelo R2, colunas `razao_rep`, `razao_rep_ic_inf` e `razao_rep_ic_sup`.
   - Indicador binário: `coeficientes.csv`, modelo R1 (8,16 / 4,58). Os pontos percentuais vêm de `ames.csv`, modelo R1 (20,3 / 12,1).
   - Magnitude: `interacao_magnitude.csv`. O teste da interação contínua credencial × ln(magnitude) dá b = 0,61 (EP 0,09) em 2018 e b = 0,58 (EP 0,06) em 2022.
   - Amostra: `amostra.csv`. São 786 e 648 listas antes do filtro de listas com mais de uma candidatura, e 649 e 623 depois.
   - Negra em 2022: razão 0,93, IC de 0,87 a 0,99, p = 0,03. Governador em 2022: razão 1,33, IC de 0,95 a 1,88, p = 0,10.
2. **Nome da medida.** "Razão de parcelas" não é *odds ratio*: não há chance envolvida. Se aparecer "chance" no texto, a leitura fica errada.
3. **Pontos que o rascunho afirma e que você precisa sustentar oralmente:**
   - **Equivalência com o Poisson com efeitos fixos.** Foi conferida numericamente, mas não na bibliografia; as referências candidatas estão em `cap3-plano-regressao-intralista.md`, seção 2.2.
   - **"Coerente com sua exclusão da definição de credencial" (vereador).** O efeito continua positivo e significativo, então a exclusão é uma escolha de corte, não uma ausência de efeito.
   - **Queda de 8,16 para 4,58 "compatível com o aumento do NECr".** É uma interpretação, não um teste.
4. **"Quatro vezes" com dois mandatos** vem de 2,00², ou seja, supõe que o efeito se multiplica a cada vitória, como o modelo impõe. Não é uma estimativa separada para quem tem dois mandatos.
5. **Rótulo da variável do QE.** Diz "sem vitória acima de vereador", e não "nunca eleitos", porque metade desses casos (106 de 215 em 2018; 194 de 407 em 2022) já venceu para vereador.
6. **Fora do rascunho.** A Discussão (linhas 180–196) ainda não cita a regressão. A `tbl-cap3-03-premio-magnitude` está sem legenda e precisa dizer que os valores são razões de parcelas.
