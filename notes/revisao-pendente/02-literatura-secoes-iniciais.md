# Revisão pendente: seções iniciais do Cap. 2 (2.1–2.3)

- **Data da análise:** 18/09/2026.
- **Arquivo:** [tese/02-literatura.qmd](../../tese/02-literatura.qmd), do início até "## Financiamento de campanhas no Brasil" (exclusive).
- **Seções cobertas:** "Primeira e segunda gerações de estudos..." (com as subseções "O cânone..." e "A segunda geração..."), "Partidos como organizações heterogêneas", "Competição intrapartidária e gastos de campanha".
- **Fora do escopo:** "Financiamento de campanhas no Brasil" e "Argumento", já revisadas em [02-literatura-financiamento-e-argumento.md](02-literatura-financiamento-e-argumento.md).
- **Como ler esta nota:** os comentários HTML estão no próprio `.qmd`, com o rótulo `[2.1-n]`, `[2.2-n]` ou `[2.3-n]`. Esta nota resume o que está lá, sem repetir o texto completo dos comentários. As referências são pelo início do parágrafo, porque as linhas mudam com edições.
- **O que esta nota não faz:** não traz prosa pronta. Correções pontuais ficam no nível da palavra ou frase curta.
- **Checagens feitas:** magnitude de distrito no Brasil (8 a 70 cadeiras, confirmado em `rrd_df_novo.parquet`, coluna `qt_vaga`); proporção de recursos partidários na receita total por ano; todas as chaves de citação das três seções existem em `references.bib` (nenhuma faltando).

---

## 1. Diagnóstico geral

Diferente de Financiamento/Argumento, estas três seções são puramente de revisão de literatura, sem números a auditar. O trabalho aqui é sobretudo de **coerência interna do capítulo**: encontrar onde a tese já formulou, em estado bruto, ideias que reaparecem (com força desigual) no Argumento — e apontar onde a formulação mais forte deveria ganhar precedência, com as demais remetendo a ela.

Três padrões recorrentes:

1. **A tese se anuncia várias vezes antes de chegar ao Argumento.** A costura entre "recursos financeiros como instrumento de coordenação" (L2.1-8, fim de 2.1) e "distribuição discricionária de recursos... instrumento de atribuição de vantagem competitiva" (L2.2-5, fim de 2.2) já contêm, juntas, quase todo o argumento da tese — de forma mais direta do que o próprio Argumento no Cap. 2. Ver `[2.1-8]` e `[2.2-5]`.
2. **Lacunas afirmadas, não demonstradas.** Repete o padrão identificado na revisão de estilo anterior: "resta observar diretamente..." (2.1) e "Ainda não está claro, porém, como medir a coordenação..." (2.3) são boas frases de transição, mas generalizam a partir de evidência mais estreita do que sugerem. Ver `[2.1-8]` e `[2.3-3]`.
3. **Elos que a tese usa no Cap. 3/4 mas não amarra no Cap. 2.** Dois exemplos concretos, verificados no código: (a) @cheibubsin2020 é a fonte mais citada do Cap. 3 (justifica o afunilamento de competitivos e o tamanho do núcleo Top-NECr), mas aparece em 2.1 em pé de igualdade com três outros estudos de sobreposição territorial (`[2.1-6]`); (b) a magnitude do distrito, central no argumento de Samuels em 2.3, é a mesma dimensão absorvida pelos efeitos fixos de lista da regressão intralista do Cap. 3, e essa ligação nunca é feita (`[2.3-2]`).

## 2. Resumo dos comentários por seção

### 2.1 — Primeira e segunda gerações de estudos

| Rótulo | Parágrafo (início) | Ponto |
|---|---|---|
| `[2.1-1]` | "Essa mudança de perspectiva não implica negar..." | Repete a distinção já feita duas vezes antes; candidato a corte. |
| `[2.1-2]` | "@mershon2020 organiza uma série de estudos..." | Anuncia três arenas, mas a arena "seleção de candidatos" nunca é desenvolvida explicitamente. |
| `[2.1-3]` | "Ao aplicar para o caso brasileiro..." | O elo mais importante da seção (controle de entrada, não de ordenação) fica implícito até muito depois. |
| `[2.1-4]` | "A aplicação relativa ao *pooling*..." | Classificação do sistema brasileiro fica indecisa ("entre X e Y") num ponto central para o argumento de votos vs. cadeiras. |
| `[2.1-5]` | "Esta combinação embasou os diagnósticos iniciais..." | Citação de Mainwaring antecipa quase literalmente a de Samuels em 2.3 (l. 123 na versão anterior). |
| `[2.1-6]` | "A literatura sobre coordenação intralista avança..." | Cheibub & Sin — a fonte mais usada no Cap. 3 — está em lista com outros três estudos; sugiro destacar. |
| `[2.1-7]` | "No Brasil, evidências recentes mostram..." | Primeira aparição de Janusz et al. e *resource gatekeeping*; volta quase idêntica em Financiamento e no Argumento. |
| `[2.1-8]` | "A contribuição desta tese se posiciona..." | Formulação mais direta da lacuna da tese, mas com abertura abstrata (mesmo ponto da revisão de estilo anterior). |

### 2.2 — Partidos como organizações heterogêneas

| Rótulo | Parágrafo (início) | Ponto |
|---|---|---|
| `[2.2-1]` | "É nesse ponto que o argumento de @aldrich2011..." | Primeira formulação do argumento central da tese; quase repetida no Argumento (l. 189). |
| `[2.2-2]` | "Essa delegação não exige que o partido controle..." | Primeira menção a dinheiro **e** *timing* juntos — candidata a sediar a justificativa teórica da frente (iii), que falta no Argumento `[A9]`. |
| `[2.2-3]` | "A capacidade de realizar essa coordenação..." | O "dilema do gatekeeper" de Fiva et al. termina sem posição sobre o caso brasileiro; conexão com "tipo de partido" do Cap. 3 não é feita. |
| `[2.2-4]` | "O número de posições de vantagem atribuídas..." | Período sem oração principal ("Enquanto blindar... pode fazer com que..."). |
| `[2.2-5]` | "No caso norueguês tratado pelos autores..." | O argumento da tese já está aqui em estado quase completo; considerar remissão do Argumento para este parágrafo. |

### 2.3 — Competição intrapartidária e gastos de campanha

| Rótulo | Parágrafo (início) | Ponto |
|---|---|---|
| `[2.3-1]` | "@cox_thies_1998_cost argumentam que candidaturas..." | Falta marcar a diferença institucional (SNTV sem pooling x lista aberta com pooling) antes da comparação com o Brasil. |
| `[2.3-2]` | "Enquanto @cox_thies_1998_cost testam a hipótese..." | Magnitude do distrito (Samuels) é a mesma dimensão absorvida por efeitos fixos de lista no Cap. 3; ligação nunca é feita. |
| `[2.3-3]` | "A literatura mostrou que a presença..." | Lacuna de mensuração afirmada com base estreita; a lacuna mais precisa é a falta de medida da ação partidária, não do comportamento do candidato. |
| `[2.3-4]` | "Diferente da literatura que evidencia..." | Afirmação "grande parte do dinheiro... é de origem pública" checada: 43,6% em 2018 e 87,8% em 2022 (recursos de partido / receita total). Sustenta 2022, é maioria mais estreita em 2018 — sugiro separar os dois anos. |

## 3. Checklist de prioridade

- [ ] Decidir a formulação-âncora do argumento central (candidatas: `[2.2-1]`/`[2.2-5]` no Cap. 2 vs. o parágrafo central do Argumento) e fazer as demais remeterem a ela.
- [ ] Fechar a classificação do sistema brasileiro quanto a *pooling* (`[2.1-4]`) — decide a tensão votos vs. cadeiras do Argumento `[A2]`.
- [ ] Escrever a justificativa teórica de *timing* em `[2.2-2]`, resolvendo a lacuna apontada em `[A9]` do Argumento.
- [ ] Destacar Cheibub & Sin (`[2.1-6]`) e considerar remissão em vez de repetição de Janusz et al. (`[2.1-7]`, Financiamento, Argumento).
- [ ] Consertar o período sem oração principal em `[2.2-4]`.
- [ ] Separar 2018 e 2022 na afirmação sobre predominância de recursos públicos (`[2.3-4]`).
