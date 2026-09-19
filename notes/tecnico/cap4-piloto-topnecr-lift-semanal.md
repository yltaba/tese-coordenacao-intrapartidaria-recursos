# Piloto: lift semana a semana e split por Top-NECr no Cap. 4

> **ATUALIZAÇÃO 19/09/2026 — parte (a) SUPERADA.** A medida do piloto (parcela de recursos do Top-NECr ÷ k/C) é ≥ 1 por construção e o benchmark era fixo (totais finais) enquanto o numerador seguia o fluxo até a semana w; a queda 2,04 → 1,89 e a "coincidência" com o lift do Cap. 3 não são informativas. A versão efetivada recalcula o lift do Cap. 3 (competitivos ex-ante no Top-NECr) a cada semana sobre os recursos acumulados: `src/2_gold/cap4_lift_semanal.py`, `tese/reports/lift-semanal/`, `figs/cap4_lift_semanal.png` (resultado: ~1,9 quase constante; ver comentário [4.1-5] no Cap. 4). A parte (b) segue válida.

**18/09/2026.** Avaliação de duas extensões empíricas propostas pelo autor para o Cap. 4: (a) uma medida de *lift* semana a semana; (b) separar candidatos por dentro/fora do Top-NECr em vez de competitivo/não-competitivo (ex-ante). Script: `cap4_piloto_topnecr_lift.py`, nesta pasta. **Não altera nenhum artefato oficial** (`figs/`, `data/processed/df_cox_survival.parquet`); roda à parte, a partir da raiz do repo.

## (b) Dentro/fora do Top-NECr como variável de grupo

**O que o piloto faz:** calcula, por candidatura, o peso de pertencimento ao Top-NECr da sua lista (1 se está estritamente dentro do corte $k_l$, peso fracionário no bloco de empate na fronteira, 0 fora — mesma regra de `acertos_fracionarios` em `src/2_gold/cap3_cobertura_top_necr.py`, mas devolvida por candidato em vez de agregada). Um candidato entra no grupo "Dentro do Top-NECr" se o peso for ≥ 0,5.

**Achado 1 — sobreposição com "competitivo" é baixa.** O índice de Jaccard entre "dentro do Top-NECr" e "candidato_competitivo" é **0,31 em 2018** e **0,27 em 2022**. As duas variáveis capturam coisas diferentes: Top-NECr é sobre *concentração financeira* dentro da lista; competitivo é sobre *credencial eleitoral prévia*. A maioria dos candidatos dentro do Top-NECr NÃO tem credencial prévia (1.554/2.342 em 2018; 2.782/3.889 em 2022), o que é esperado — o núcleo financeiro é maior que o grupo de credenciados (é exatamente o "afunilamento" oposto que o Cap. 3 documenta: Top-NECr cobre >80% dos competitivos, mas o Top-NECr em si é maior que o conjunto de competitivos).

**Achado 2 — o padrão de antecipação se mantém, mas não fica mais nítido.** Refazendo as curvas de Kaplan-Meier (primeiro repasse) com o corte Top-NECr em vez de competitivo:

| | S(1 semana) | S(2 semanas) |
|---|---|---|
| 2018, Dentro do Top-NECr | 73,7% | 40,3% |
| 2018, Fora do Top-NECr | 89,1% | 75,4% |
| 2018, Competitivo (já no texto) | 71,8% | 26,5% |
| 2018, Não-competitivo (já no texto) | 86,2% | 70,2% |

A separação por Top-NECr é parecida na semana 1, mas **menor** na semana 2 (35,1 p.p. de diferença entre grupos, contra 43,7 p.p. usando competitivo). Isso é esperado: o grupo Top-NECr é maior e mais heterogêneo (inclui muita gente sem credencial, ver Achado 1), então a diferença de velocidade fica diluída.

**Recomendação:** não SUBSTITUIR o corte por competitivo pelo corte por Top-NECr nas figuras de KM/fluxo — o corte por competitivo já é mais nítido para essa pergunta específica (antecipação por credencial). O valor de Top-NECr está em outra pergunta, mais próxima da definição do Cap. 3: não "quem tem credencial recebe antes", mas "quem o partido decidiu concentrar recebe antes". As duas perguntas são complementares e o Cap. 4 só faz a primeira hoje. Se o autor quiser manter as duas, a rota mais barata é uma nota ou anexo com a versão Top-NECr das figuras já existentes, sem duplicar toda a seção.

## (a) Lift semana a semana

**O que o piloto faz:** para cada semana $w$, calcula a proporção acumulada dos recursos partidários (FEFC+FP) que foi para candidaturas do Top-NECr até $w$, e divide pela proporção que o Top-NECr teria "por direito" se o dinheiro fosse distribuído proporcionalmente ao tamanho do núcleo em cada lista ($k_l/C_l$, ponderado pelo total de recursos de cada lista — o mesmo tipo de benchmark hipergeométrico usado no Cap. 3 para cobertura/precisão, aqui aplicado ao fluxo cumulativo em vez do total final).

**Resultado (2018 e 2022, `top_necr_peso >= 0,5` como corte de conferência; o cálculo em si usa o peso fracionário):**

| Semana | Lift 2018 | Lift 2022 |
|---|---|---|
| 1 | 2,04 | 2,04 |
| 2 | 2,02 | 1,94 |
| 3 | 1,96 | 1,91 |
| 4 | 1,93 | 1,89 |
| 5 | 1,91 | 1,88 |
| 6 | 1,91 | 1,87 |
| Fim de campanha | 1,89 | 1,87 |

**O padrão é exatamente o que a seção "A campanha eleitoral semana a semana" já mostra qualitativamente, mas quantificado com a métrica do Cap. 3:** o *lift* é maior nas primeiras semanas (2,04 nas duas eleições) e cai monotonicamente até o valor de fim de campanha (1,89/1,87 — muito próximo do *lift* de cobertura de competitivos do Cap. 3, 1,89/1,86, o que é uma coincidência interessante a mencionar, mas não uma identidade — são construtos diferentes). Ou seja: o núcleo priorizado não só acaba a campanha com mais recursos do que seu tamanho justificaria — ele já começa a campanha nessa posição, e a vantagem relativa (embora ainda alta) se dilui um pouco ao longo dos dias.

**Recomendação: incluir.** Esta é a extensão com maior retorno para o esforço: usa infraestrutura já existente (`calc_cumulative`, `carregar_receitas`), amarra o Cap. 4 diretamente ao vocabulário do Cap. 3 (NECr, Top-NECr, benchmark aleatório — hoje o Cap. 4 usa só "competitivo", uma medida do Cap. 3 mas não a medida central do capítulo), e mostra algo que as figuras de fluxo cumulativo atuais não mostram: a *magnitude relativa* da antecipação, não só sua existência qualitativa.

## Limitações do piloto (a resolver antes de qualquer figura oficial)

1. **Peso fracionário tratado como binário só no KM/fluxo** (achado b); o *lift* semanal (achado a) já usa o peso contínuo corretamente.
2. **Referência aleatória do lift semanal é constante ao longo das semanas** (usa $k_l/C_l$ do fim de campanha, não um $k_l/C_l$ que mude semana a semana — mas como $k_l$ e $C_l$ são propriedades da lista, não do tempo, isso é o correto: a única coisa que muda por semana é quanto dinheiro já foi transferido, e é isso que o numerador captura).
3. **Universo de listas do piloto é todo `rrd_df_novo.parquet`**, sem os mesmos filtros de qualidade que `regenerar_figuras_cap4.py` aplica (ex.: `dropna` em covariáveis do Cox). Para uma figura oficial, replicar exatamente os filtros de `cap3_survival_features.preparar_survival`.
4. Script não testado com o corte por magnitude nem por partido — só nacional, por eleição.
5. Não recomputado com correção do CPF/candidato mais recente além do que já está em `rrd_df_novo.parquet` (não há motivo para achar que está desatualizado, mas não foi verificado o hash/data do arquivo contra a última regeneração).

## Como transformar isso em figura oficial, se o autor decidir seguir

Estender `tese/scripts/regenerar_figuras_cap4.py` com uma função `fig_lift_semanal()` que reaproveita `top_necr_por_candidato()` (mover de `cap4_piloto_topnecr_lift.py` para `cap3_survival_features.py` ou um novo módulo `cap4_lift_features.py`, para não duplicar a regra de corte do Top-NECr que já existe em `cap3_cobertura_top_necr.py` — considerar refatorar aquele módulo para expor a função por candidato, em vez de reimplementá-la). A figura mais direta é uma linha de lift por semana, por eleição (2 painéis, como as figuras de KM existentes).
