# Cobertura dos eleitos pelo Top-NECr

Data da análise: 02/09/2026  
Base: `data/processed/rrd_df_novo.parquet`  
Unidade das nominatas: partido × UF × eleição

## Pergunta

Entre os 513 deputados federais eleitos em cada eleição, quantos estavam no Top-NECr do ranking de recursos partidários de suas nominatas?

O Top-NECr foi construído em duas etapas:

1. calcula-se o NECr da nominata a partir da distribuição dos recursos partidários;
2. ordenam-se os candidatos da nominata pelo volume desses recursos e selecionam-se os primeiros `k`, sendo `k` derivado do NECr.

A regra principal utiliza:

```text
k = NECr arredondado para o inteiro mais próximo
```

O arredondamento convencional utilizado leva valores com decimal 0,5 para cima. Também foram calculadas versões com o piso e o teto do NECr.

## Resultado principal

| Eleição | Eleitos no Top-NECr | Total de eleitos | Cobertura |
|---|---:|---:|---:|
| 2018 | 445,0 | 513 | 86,74% |
| 2022 | 475,2 | 513 | 92,63% |

Em 2018, aproximadamente 445 dos 513 deputados eleitos, ou 86,7%, estavam entre os candidatos que compunham o núcleo Top-NECr de suas nominatas. Em 2022, esse número aumentou para aproximadamente 475, ou 92,6%.

## Tratamento dos empates

O resultado de 2022 não é inteiro porque existem empates no volume de recursos exatamente na fronteira do Top-NECr. Para não desempatar arbitrariamente — e especialmente para não usar votos ou eleição no desempate — foi aplicado o tratamento fracionário já existente no projeto.

Quando um bloco de candidatos empatados atravessa a fronteira do Top-NECr, o número de posições restantes é multiplicado pela proporção de eleitos dentro do bloco. Com isso, o resultado é determinístico e não depende da ordem física das observações nem de um desempate baseado no resultado eleitoral.

Os limites possíveis decorrentes desses empates são:

| Eleição | Mínimo possível | Máximo possível | Estimativa fracionária |
|---|---:|---:|---:|
| 2018 | 443 | 446 | 445,0 |
| 2022 | 471 | 479 | 475,2 |

## Sensibilidade à transformação do NECr em número de candidatos

| Regra para definir o Top-NECr | 2018 | 2022 |
|---|---:|---:|
| Piso do NECr | 82,55% | 91,64% |
| Inteiro mais próximo | 86,74% | 92,63% |
| Teto do NECr | 87,67% | 93,47% |

O resultado é robusto à regra escolhida. A cobertura permanece superior a 82% em 2018 e a 91% em 2022.

## Tamanho do conjunto Top-NECr

O tamanho do núcleo Top-NECr aumentou entre as duas eleições:

| Eleição | Posições no Top-NECr | Total de candidatos | Parcela selecionada |
|---|---:|---:|---:|
| 2018 | 2.318 | 7.630 | 30,4% |
| 2022 | 3.824 | 9.675 | 39,5% |

Esse crescimento exige cautela na comparação temporal. Parte do aumento da cobertura dos eleitos decorre de um núcleo financeiro mais amplo em 2022: quanto maior o número de candidatos classificados como Top-NECr, maior tende a ser a probabilidade de incluir os vencedores.

## Comparação com uma seleção aleatória

Para avaliar se a cobertura elevada decorre apenas do tamanho do conjunto selecionado, foi calculada a cobertura esperada caso o mesmo número `k` de candidatos fosse escolhido aleatoriamente dentro de cada nominata.

| Eleição | Cobertura Top-NECr | Cobertura aleatória esperada |
|---|---:|---:|
| 2018 | 86,74% | 43,78% |
| 2022 | 92,63% | 43,75% |

O Top-NECr apresenta aproximadamente duas vezes a cobertura esperada por uma seleção aleatória em 2018 e pouco mais de duas vezes em 2022. Portanto, embora o aumento do conjunto selecionado contribua para a cobertura, o ranking de recursos partidários possui correspondência substantiva com a identidade dos candidatos eleitos.

## Listas sem recursos partidários

Em 2018, três deputados eleitos pertenciam a listas sem recursos partidários registrados. Como não há distribuição a partir da qual calcular o NECr, esses eleitos não poderiam integrar um Top-NECr. Eles foram mantidos no denominador de 513 e tratados como não cobertos.

Em 2022, nenhum eleito estava em uma lista sem recursos partidários registrados.

Excluir os três casos de 2018 elevaria artificialmente a cobertura. A manutenção do denominador nacional completo é a decisão mais conservadora e transparente.

## Salvaguarda contra circularidade

O resultado eleitoral não participa da definição do Top-NECr. O procedimento segue esta ordem:

```text
distribuição de recursos partidários
→ cálculo do NECr
→ definição do tamanho do núcleo
→ ranking dos candidatos por recursos
→ identificação do Top-NECr
→ verificação posterior de quais candidatos foram eleitos
```

Os eleitos são utilizados somente como resultado diante do qual se avalia a cobertura. Não são empregados para reconstruir a expectativa partidária, definir o tamanho do núcleo ou ordenar os candidatos.

A medida, portanto, identifica correspondência entre priorização financeira e resultado eleitoral. Ela não demonstra isoladamente que:

- o partido previu corretamente quem seria eleito;
- as lideranças controlaram integralmente a distribuição;
- os recursos causaram a eleição dos candidatos priorizados;
- a concentração observada representa necessariamente coordenação partidária, em vez de captura de recursos por candidatos eleitoralmente fortes.

## Ressalva sobre as federações partidárias

O cálculo acompanha a unidade atualmente utilizada no projeto: partido × UF × eleição. Em 2022, os partidos integrantes de uma federação não foram agregados em uma única nominata federada.

Como as federações disputaram a eleição proporcional em listas conjuntas, recomenda-se reproduzir o cálculo em uma análise de robustez cuja unidade seja federação × UF. Se os resultados forem semelhantes, a análise partidária ganhará sustentação; se forem diferentes, será necessário tratar a federação como a unidade eleitoral relevante em 2022.

## Interpretação substantiva

Os resultados mostram forte correspondência nominal entre priorização financeira e eleição. Em ambos os ciclos do FEFC, a ampla maioria dos deputados eleitos estava entre os candidatos que integravam o núcleo Top-NECr de seu partido na UF.

O aumento de 86,7% para 92,6% não deve ser interpretado automaticamente como melhora da coordenação. O Top-NECr passou a compreender uma parcela maior das candidaturas em 2022. A interpretação adequada deve combinar:

- a cobertura dos eleitos;
- o tamanho relativo do Top-NECr;
- o desempenho diante do benchmark aleatório;
- a precisão, isto é, a proporção dos integrantes do Top-NECr que foi eleita.

A cobertura responde à pergunta sobre quantos vencedores estavam entre os priorizados. Ela não informa quantos candidatos priorizados perderam a eleição. Por isso, cobertura e precisão devem ser apresentadas conjuntamente em uma avaliação completa da correspondência entre alocação e resultado.

## Arquivos reproduzíveis

- Código: `src/2_gold/cap3_cobertura_top_necr.py`
- Resultado por nominata: `data/processed/df_cobertura_top_necr_lista.parquet`
- Resumo nacional: `data/processed/df_cobertura_top_necr_resumo.csv`
