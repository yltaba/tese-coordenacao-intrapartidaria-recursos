# Lift do Top-NECr por partido (2018 e 2022): cálculo, limites e leitura

Material de apoio. **Não é texto da tese.** Figura: `figs/cap3_fig_lift_partido.png`.
Números: `tese/reports/lift-magnitude-partido/lift_por_partido_ano.csv`. Os dois são gerados por
`python tese/scripts/regenerar_figuras_cap3.py`, a partir de `rrd_df_novo.parquet`, com a mesma
regra do capítulo (k = NECr arredondado, empates fracionários).

## 1. Como se calcula

Para o partido p na eleição t, somam-se as listas (UF) do partido:

    Lift_p,t = Σ_l H_l / Σ_l E_l,   com E_l = G_l · k_l / C_l

- H_l: acertos no núcleo Top-NECr, com empates fracionários.
- G_l: nº de alvos na lista (competitivos ou eleitos).
- k_l: tamanho do núcleo.
- C_l: tamanho da lista.

É a mesma razão de somas do lift nacional, restrita às listas do partido.

**Decomposição exata:** o lift nacional é a média dos lifts partidários ponderada por E_p. No CSV,
Σ H / Σ E reproduz 1,891/1,855 (credenciais) e 1,982/2,117 (eleitos). A figura por partido é,
literalmente, a abertura do número que já está no capítulo.

Colunas do CSV: `H_observado`, `E_esperado`, `H_maximo` (Σ min(k, G)), `lift`, `teto_lift`
(H_maximo/E), `lift_normalizado` ((H−E)/(H_maximo−E)), `dp_nulo_lift` (DP do lift sob a nula
hipergeométrica), `bancada` (eleitos em todas as listas), `bancada_listas_financiadas`,
`denominador_pequeno` (E < 5).

## 2. O que a conta por partido pode violar

**(a) Teto mecânico: o problema principal, sobretudo para eleitos.** O núcleo não comporta mais
acertos que min(k_l, G_l). Portanto `lift_l ≤ C_l / max(k_l, G_l)`. Nas listas com eleitos,
cerca de 88% estão saturadas (todos os eleitos já estão no núcleo). No agregado por partido, o
lift de eleitos é exatamente igual ao teto em 13 de 30 partidos (2018) e em 11 de 23 (2022).
A correlação de Spearman entre lift e teto é 0,81 (2018) e 0,71 (2022). O teto, por sua vez, cai
com a bancada: ρ(bancada, teto) = −0,53 e −0,72.

Consequência: ordenar partidos pelo lift de eleitos ordena, em boa parte, pelo teto de cada um,
e esse teto pune bancadas grandes por construção. O PSOL 2018 (6,10) não "coordena três vezes
mais" que o PP (1,70): os dois estão no teto. **O que discrimina é a distância até o teto.**

**(b) Denominador pequeno.** O E de eleitos fica abaixo de 1 para vários partidos: PPL 0,11,
REDE 2018 0,25, PTB 2022 0,11, PROS 2022 0,49. Com E = 0,11, um eleito a mais ou a menos move o
lift em cerca de 9 pontos. O DP nulo relativo passa de 1 nesses casos. Só 14 partidos (2018) e
9 (2022) têm E de eleitos ≥ 5; em credenciais são 20 e 22.

**(c) Seleção pelo resultado.** Partido sem eleito tem lift de eleitos 0/0 e sai do painel.
Ficaram de fora em 2018: PCO, PMB, PCB, PRTB e PSTU. Em 2022: AGIR, PMB, PMN, PCO, PCB, DC, PRTB,
PSTU e UP. O painel de eleitos descreve só partidos que conquistaram cadeiras.

**(d) Composição por magnitude.** O lift cresce com a magnitude (tbl-cap3-01/02). A fatia do E
de um partido que vem de distritos grandes vai de 0 a cerca de 0,7. Parte da diferença entre
partidos é geografia eleitoral, não comportamento. A figura não padroniza por magnitude.

**(e) Federações em 2022.** A lista é `sg_partido_norm × UF`. Para PT/PCdoB/PV, PSDB/Cidadania e
PSOL/Rede, a lista eleitoral real é a da federação, e a conta trata cada partido como sublista.
Isso é defensável, porque o FEFC é distribuído por partido. Mas a referência aleatória de cada
sublista usa o C do partido, não o da federação, e os eleitos resultam do quociente da
federação. Convém dizer isso na nota da figura.

**(f) Siglas entre anos.** Os painéis usam a sigla da época (PSL e DEM em 2018, UNIÃO em 2022;
PR→PL; PRB→REPUBLICANOS; PPS→CIDADANIA; PATRI→PATRIOTA). Não há pareamento de partido entre
anos na figura. Se algum dia houver, `tese/reports/lift-magnitude-partido/familia_partidaria.py`
**não mapeia PHS→PODE** (incorporação de 2019).

**(g) Eleitos em listas sem recursos.** Entram na bancada, mas não no lift, porque nessas listas
k = 0 e E = 0. Só afeta o PSL 2018: 52 eleitos no total, 49 em listas financiadas. O rótulo da
figura mostra 52.

**(h) Contaminação ex post.** Vale para o alvo eleitos o que o capítulo já diz no nível
nacional: o resultado depende do voto do partido, não só da alocação.

## 3. Como ler a figura

- Dois painéis, 2018 e 2022. Partidos com ≥ 1 eleito, ordenados pela bancada; o número entre
  parênteses é a bancada.
- Círculo cheio: lift de eleitos, com área proporcional à bancada.
- Losango vazado: lift de credenciais prévias.
- Segmento cinza: vai de 1 (acaso) até o teto do lift de eleitos, com um tique no teto.
- Marcador cinza: o esperado ao acaso daquele alvo é < 5.

Leitura:

- **Círculo no fim do segmento:** o partido está saturado (todos os eleitos no núcleo).
- **Círculo bem antes do fim:** parte da bancada veio de fora do núcleo priorizado.
- **Comprimento do segmento:** é o teto. Ele é curto nos partidos grandes e longo nos pequenos,
  e é isso que "infla" o lift dos partidos pequenos.

Números-chave (CSV):

| Caso | Lift eleitos | Teto | Lift normalizado |
|---|---|---|---|
| PT 2018 (56) | 2,13 | 2,13 | 1,00 |
| PSL 2018 (52) | 1,81 | 3,37 | 0,34 |
| PP 2018 (37) | 1,70 | 1,70 | 1,00 |
| PSOL 2018 (10) | 6,10 | 6,10 | 1,00 |
| PL 2022 (99) | 2,25 | 2,71 | 0,73 |
| UNIÃO 2022 (59) | 1,59 | 1,61 | 0,98 |
| PV 2022 (6) | 1,28 | 1,92 | 0,30 |

Entre os partidos com E ≥ 5 em eleitos, só quatro ficam abaixo de 0,8 no lift normalizado:
MDB 2018 (0,79), PSDB 2018 (0,75), PSL 2018 (0,34) e PL 2022 (0,73).

Credenciais prévias: o lift é > 1 em todos os partidos com lift definido, exceto o DC
(0,89 em 2018 e 0 em 2022, ambos com E < 2). Entre os partidos com E ≥ 5, a faixa é:

- 2018: de 1,49 (PC do B) a 2,38 (PDT).
- 2022: de 1,41 (UNIÃO) a 2,86 (CIDADANIA).

## 4. Include do Quarto (para colar onde quiser)

Sugestão de lugar: Robustez, logo depois de `tbl-cap3-02-lift-magnitude-eleicao`.

```markdown
![*Lift* do Top-NECr por partido em 2018 e 2022: credenciais eleitorais prévias e eleitos, com o teto do *lift* de eleitos e a bancada eleita.](../figs/cap3_fig_lift_partido.png){#fig-cap3-lift-partido fig-align="center" width="100%"}
```

---

## 5. RASCUNHO GERADO POR IA: reescrever, não colar em `tese/*.qmd`

> Pedido explícito do autor em 18/09/2026. Serve de mapa do argumento e de conferência dos
> números. A redação final é do autor.

A @fig-cap3-lift-partido abre o *lift* nacional por partido. Como o indicador é uma razão de
somas, o valor nacional é a média dos valores partidários ponderada pelo número de acertos
esperados ao acaso de cada partido. A figura mostra, portanto, de onde vem o número apresentado
na @fig-cap3-03-top-necr, e não uma medida nova.

Para as credenciais eleitorais prévias, a priorização se repete em praticamente todas as
legendas. Entre os partidos com ao menos cinco candidaturas competitivas esperadas ao acaso, o
*lift* vai de 1,49 (PC do B) a 2,38 (PDT) em 2018 e de 1,41 (União Brasil) a 2,86 (Cidadania)
em 2022. O único partido abaixo de um é o DC, cujo denominador é pequeno demais para uma leitura
substantiva. O resultado agregado, portanto, não é produzido por poucas legendas grandes.

O *lift* dos eleitos pede outra leitura. O núcleo de uma lista não pode conter mais eleitos do
que o menor valor entre seu tamanho e o número de eleitos da lista. Por isso cada partido tem um
teto de *lift*, que é mais baixo justamente quando a bancada é grande em relação às listas.
Em 2018, PT, PP e PR alcançaram esse teto; todos os seus eleitos estavam no núcleo, e ainda assim
os valores (2,13, 1,70 e 1,62) ficam abaixo dos de partidos pequenos. É o caso do PSOL, que
também está no teto, mas com 6,10. A comparação direta dos valores entre partidos confundiria o
tamanho da bancada com a intensidade da priorização. O que distingue os partidos é a distância
entre o valor observado e o teto.

Vista assim, a figura destaca dois casos. O PSL de 2018 elegeu 52 deputados com *lift* de 1,81
diante de um teto de 3,37: boa parte da bancada veio de candidaturas que o partido não havia
colocado no núcleo financiado. Isso é compatível com uma votação que surpreendeu a própria
organização. O PL de 2022, maior bancada do período (99), aparece com 2,25 diante de um teto de
2,71, uma distância menor, mas no mesmo sentido. Nos demais partidos com denominador suficiente,
o *lift* observado cobre ao menos 75% da distância entre o acaso e o teto nas duas eleições.

Três ressalvas acompanham a figura. Primeiro, nos partidos com poucos eleitos esperados ao acaso,
um único eleito altera o *lift* em vários pontos; esses casos aparecem em cinza. Segundo, os
partidos sem eleitos não têm *lift* de eleitos definido e ficam fora da figura. Terceiro, em 2022
as listas das federações são tratadas por partido, porque os recursos do FEFC são distribuídos
pelos partidos, embora a disputa pelas cadeiras ocorra no nível da federação.
