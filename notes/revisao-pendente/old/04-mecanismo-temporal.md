# Revisão pendente: Cap. 4 — O *timing* da distribuição de recursos partidários

- **Data da análise:** 18/09/2026.
- **Arquivo:** [tese/04-mecanismo-causal-coordenacao.qmd](../../tese/04-mecanismo-causal-coordenacao.qmd), até "## Discussão" (exclusive, fora do escopo).
- **Motivo do foco em amarração:** este foi o primeiro capítulo empírico escrito, antes do Cap. 3, e o autor pediu para amarrá-lo melhor ao resto da tese.
- **Diferença em relação ao Cap. 3:** este capítulo **não** passou por um run de revisão por agentes (`thesis-review/runs/`). Os comentários aqui são só desta leitura direta, sem a camada de recomputação independente que o Cap. 3 teve. Onde isso importa (números do KM, tabela Cox), o comentário no `.qmd` sinaliza a ausência dessa checagem, em vez de fingir que os números foram verificados.
- **Cuidado técnico ao editar:** o Cap. 4 tem um chunk de código Python (`tbl-cox`). Um comentário inserido por engano ficou dentro do chunk, entre os imports e a definição de `rotulos`, o que teria quebrado a execução do capítulo. Foi corrigido, movendo o comentário para antes do chunk. `verificar_corpo.py` não pega esse tipo de erro sozinho (comentários não contam como "corpo"), então a checagem extra foi visual: contei aberturas/fechamentos de comentário (14/14) e de cercas de código (2, um par).

## 1. Avaliação das duas extensões empíricas propostas

O autor pediu para avaliar, na execução desta tarefa, duas ideias: (a) uma medida de *lift* semana a semana; (b) separar candidatos por dentro/fora do Top-NECr em vez de competitivo/não-competitivo. Construí um piloto computacional para as duas — script e resultado completo em `notes/tecnico/cap4_piloto_topnecr_lift.py` e `notes/tecnico/cap4-piloto-topnecr-lift-semanal.md`. Resumo:

- **(a) Lift semana a semana: recomendo incluir.** O *lift* de concentração de recursos no núcleo Top-NECr é 2,04 na primeira semana (nas duas eleições) e cai monotonicamente até 1,89 (2018) e 1,87 (2022) ao fim da campanha — muito perto do *lift* de cobertura de competitivos do Cap. 3 (1,89/1,86), o que é uma coincidência a mencionar, não uma identidade (são construtos diferentes: um mede concentração financeira, o outro sobreposição com credencial). O ganho é usar uma métrica já central na tese (lift, NECr, Top-NECr) em vez de reportar só diferenças em pontos percentuais, e mostrar a MAGNITUDE da antecipação, não só sua direção.
- **(b) Dentro/fora do Top-NECr como corte: recomendo não substituir, e não necessariamente adicionar.** O índice de Jaccard entre "dentro do Top-NECr" e "competitivo" é baixo (0,31 em 2018, 0,27 em 2022) — são grupos substancialmente diferentes. Refazendo o Kaplan-Meier com o corte Top-NECr, a separação entre grupos na semana 2 fica **menor** (35,1 p.p.) do que com o corte por competitivo (43,7 p.p.), porque o núcleo Top-NECr é maior e mais heterogêneo (inclui muitos candidatos sem credencial). O corte atual por competitivo já é mais nítido para a pergunta que a seção faz.

Os comentários no `.qmd` (rótulo `[4.0]`) trazem esse resumo no ponto de abertura do capítulo, com números.

## 2. Amarração ao resto da tese (achado principal desta leitura)

O problema central do capítulo não é de conteúdo — os resultados são consistentes e bem descritos — é que ele lê como um capítulo **isolado**, com poucas remissões explícitas ao vocabulário e aos resultados dos Caps. 2 e 3:

1. **A justificativa teórica do *timing* já existe, mas está no lugar errado.** O parágrafo de abertura ("O recebimento de receitas de campanha... é no período eleitoral que se torna visível a estratégia...") é exatamente o que falta no Argumento do Cap. 2 (apontado lá como `[A9]`, e em "Partidos como organizações heterogêneas" como `[2.2-2]`). Hoje o leitor só descobre por que o momento do repasse importa ao chegar no capítulo empírico. Ver `[4.0-1]`.
2. **A frente (iii) do Argumento nunca é citada explicitamente aqui.** O Cap. 2 anuncia três frentes empíricas e diz que "o capítulo 4 investiga iii)" (priorização temporal), mas o Cap. 4 nunca remete de volta a essa frase. Ver `[4.0-2]`.
3. **A cláusula de barreira aparece uma vez e não se conecta ao argumento da sobrevivência partidária** desenvolvido em Financiamento (Cap. 2). É o mesmo tipo de incentivo institucional — merece uma remissão cruzada. Ver `[4.1-1]`.
4. **O Cox e a regressão intralista do Cap. 3 nunca são comparados**, embora usem exatamente o mesmo tipo de covariável (contagens de vitórias por cargo) e mostrem o mesmo padrão substantivo: a vantagem de credenciais cai entre 2018 e 2022 (HR de deputado federal: 55%→36%; razão de parcela do Cap. 3: 2,00→1,55). Isso é evidência de robustez por dois desenhos independentes e deveria ser dito explicitamente — inclusive como material para a Discussão. Ver `[4.3]` e `[4.3-1]`.
5. **A variável de corte usada em todo o capítulo (`candidato_competitivo`) é a medida de credencial do Cap. 3, não a medida de priorização (Top-NECr)** que é o resultado central daquele capítulo — e o capítulo nunca justifica essa escolha. Ver `[4.1]` (roteiro da seção 1) e a avaliação do piloto na seção 1 acima.

## 3. Outros pontos pontuais

- `[4.1-2]`: a conclusão da seção 1 é afirmada antes das figuras que a sustentam.
- `[4.1-3]`: "quase 48 p.p." poderia ser o valor exato (47,8 p.p.), já que o resto do parágrafo usa valores exatos.
- `[4.2]`: falta explicar, já na seção do KM, por que ele precede o Cox (a lógica só aparece na abertura da seção seguinte).
- `[4.2-2]`: os números do KM não foram recomputados nesta revisão (diferente do Cap. 3, que teve verificação independente por agente). Recomendo checar contra `regenerar_figuras_cap4.py::fig_km_primeiro_repasse` antes de fechar a versão final.
- `[4.3-2]`: `df_cox_survival.parquet` é output do modelo, não input, e o CLAUDE.md registra que ficou desatualizado por quase três meses em 2026. Não verifiquei nesta revisão se está atualizado agora — checagem rápida antes de fechar o capítulo.

## 4. Checklist de prioridade

- [ ] Mover ou repetir a justificativa teórica do timing (`[4.0-1]`) para o Cap. 2, no ponto indicado por `[2.2-2]`.
- [ ] Remissão explícita à frente (iii) do Argumento (`[4.0-2]`).
- [ ] Decidir sobre incluir o *lift* semanal (recomendado; ver `notes/tecnico/cap4-piloto-topnecr-lift-semanal.md` para o caminho de implementação).
- [ ] Comparar explicitamente Cox (Cap. 4) e regressão intralista (Cap. 3) como evidência convergente (`[4.3-1]`), inclusive na Discussão.
- [ ] Verificar se `df_cox_survival.parquet` está atualizado em relação a `rrd_df_novo.parquet` (`[4.3-2]`).
- [ ] Recomputar os números do KM antes de fechar a versão final (`[4.2-2]`) — este capítulo não teve a checagem independente que o Cap. 3 teve.
- [ ] Remissão cruzada entre cláusula de barreira (Cap. 4) e cláusula de desempenho/sobrevivência (Cap. 2, `[4.1-1]`).
