# Adversarial — Capítulo 3 — run-001

Agente: adversarial-reviewer. Insumos: `issues_draft.yaml` (pass 1), `synthesis/conflicts.md`, `agents/{measurement,statistics,results}.md`, `evidence/`. Capítulo lido na íntegra (`tese/03-medindo-coordenacao-intrapartidaria.qmd`, 185 linhas, sha do manifesto). Código: `src/1_silver/gerar_rrd.py` (inteiro), `src/2_gold/cap3_cs_features.py`. Notas do autor: `notes/daily/2026-09-05.md`, `2026-09-11.md`, `2026-09-12.md`, `2026-09-13.md`; `tese/reports/resultados-capitulo-3/19_notas_redacao.csv`. `tese/03-formulas-propostas.qmd` está ausente (não verificável; nenhuma refutação abaixo depende dele).

## Recomputações próprias (`evidence/adv_*`)

| Script | Saída | O que testa |
|---|---|---|
| `adv_01_prefeito_keepfirst.py` | `adv_01_output.txt`, `adv_01_casos_extremos.csv` | Se as vitórias múltiplas de prefeito são artefato do merge ou têm outra explicação (granularidade, turno, CPF placeholder, encoding dos rótulos de eleito) |
| `adv_02_flag_variantes.py` | `adv_02_output.txt`, `adv_02_metricas_variantes.csv`, `adv_02_incumbentes_2014_nao_competitivos.csv` | Decomposição do efeito na flag e nas métricas: D1 (keep-first), D2 (CPF sem zeros à esquerda em 2012/2014), regra do código × regra do texto × código sem 10 % em Prefeito; lift sob os dois nulos |
| `adv_03_universo_sorteio.py` | `adv_03_output.txt` | Decomposição lift_todas = lift_recebedores × lift_receber; perfil das candidaturas com R = 0; nulos com piso de R$ 1 mil / 10 mil |
| `adv_04_cotas_contrafactual.py` | `adv_04_output.txt`, `adv_04_metricas.csv` | Top-NECr refeito em listas só de homens (segunda operacionalização de "retirar as cotas") |
| `adv_05_cpf_base_depfed.py` | `adv_05_output.txt` | CPF da própria candidatura a Dep. Federal atribuído por keep-first (`construir_base`) |
| `adv_06_keepfirst_cargos_uf.py` | `adv_06_output.txt` | Se o keep-first atinge também Governador/Senador (vice e suplentes compartilham número) |
| `adv_07_limiar_prefeito.py` | `adv_07_output.txt` | Quão exigente é "≥ 10 % do QE" quando aplicado a Prefeito (vaga = 1) |

---

## Vereditos

### I-3-001 — Flag competitiva corrompida pela ligação (ano, UF, número)

```yaml
issue_id: I-3-001
steelman: "O histórico eleitoral que define 'competitivo' — a única referência ex-ante do capítulo — é ligado ao CPF por uma chave não única; vitórias e votos de prefeito de dezenas de municípios são somados ao primeiro CPF do arquivo e os ex-prefeitos reais ficam com zero. Qualquer número de competitivos (886/1.287, > 80 %, 30,9 %, 1,87/1,89) herda uma variável que não mede o que diz medir."
assessment: valid
evidencia_contra:
  - fonte: "evidence/adv_01_output.txt (a)-(d)"
    detalhe: "Tentei as explicações alternativas e todas caem. (a) resultados.parquet tem 1 linha por candidatura × município × turno (89 duplicatas em 2.592.395), então não há inflação por zona. (b) Há linhas de 2º turno com ELEITO (268), mas isso no máximo duplica uma vitória real e não chega a 46. (c) Os únicos CPFs não numéricos em rrd 2018/2022 são 7 '-4', sem placeholder compartilhado. (d) Os rótulos 'ELEITO POR MÉDIA'/'MÉDIA' estão em Unicode correto (0xC9) e casam com TXT_ELEITOS. Não há outra explicação."
  - fonte: "evidence/adv_01_casos_extremos.csv"
    detalhe: "Nos 19 casos com n_eleicoes_prefeito ≥ 5, todas as vitórias atribuídas vêm de um único ano e de N municípios distintos, sempre com um mesmo número de dois dígitos (número de legenda). Ex.: 2022 MG AVANTE 7025 = 46 vitórias de 2016, número 40, 46 municípios, 0 com o nome do candidato; ele teve 4 candidaturas reais a prefeito e 1 vitória real. Em todas as 54 candidaturas 2018/2022 com n_eleicoes_prefeito > 0, só 5 recebem ao menos uma vitória com o próprio nome (1/19 e 4/35). É o padrão exato de keep-first sobre (ano, UF, nr), em que prefeitos e vice-prefeitos compartilham o número da legenda em todos os municípios da UF."
  - fonte: "evidence/adv_02_output.txt (linha 'cod | keepfirst_raw')"
    detalhe: "Minha reprodução do merge do pipeline iguala candidato_competitivo em 7.630/7.630 e 9.675/9.675 candidaturas (MEA obteve 7.625 e 9.671). Causa confirmada sem resíduo."
  - fonte: "evidence/adv_06_output.txt"
    detalhe: "O defeito não é só municipal. Governador/vice e senador/suplentes compartilham número, e 79 de 189 vitórias de Governador e 177 de 269 de Senador recebem CPF diferente do obtido com chave por cargo. Efeito pequeno na base: 5/6 candidaturas (2018/2022) ganham vitória estadual indevida e 3/5 perdem."
  - fonte: "evidence/adv_02_metricas_variantes.csv + evidence/adv_07_output.txt"
    detalhe: "Onde a crítica exagera: o número de impacto citado no issue ('com CPF correto, regras do código: cobertura 75,4/76,5 %, lift 1,82/1,77') não é efeito do bug de ligação. É efeito de corrigir o bug mantendo o critério de 10 % aplicado a Prefeito (vaga = 1, isto é, 10 % dos votos válidos do município). Esse critério é quase trivial: 72-81 % de todas as candidaturas a prefeito de 2012-2020 o atingem, contra 14-20 % das candidaturas a Dep. Federal que atingem 10 % do QE. Corrigindo a ligação e retirando só esse critério: 80,7 % / 81,0 %, lift 1,867 / 1,849. Pela definição da l. 68: 80,7 % / 81,1 %, lift 1,877 / 1,861. A queda para 75 % pertence a I-3-002, não a I-3-001."
  - fonte: "evidence/adv_02_metricas_variantes.csv (chave_zfill)"
    detalhe: "Com os dois defeitos corrigidos (D1 e ADV-3-001) e a definição da l. 68: competitivos 967 / 1.351, cobertura 80,74 % / 80,70 %, precisão 33,7 % / 28,5 %, lift 1,896 / 1,852. Com as regras do código: 75,6 % / 76,2 %, lift 1,830 / 1,762. Em todas as 13 variantes por ano, o lift fica entre 1,76 e 1,91 e muito acima da faixa de permutação (0,95-1,05, sta_permutacao_top_necr.csv)."
severidade_sugerida: MAJOR
razao: "O defeito é real, foi verificado sem resíduo e se estende a Governador/Senador. Há ainda um segundo defeito de ligação não reportado (ADV-3-001), então a base precisa ser regenerada, o que é mudança de medida. Não é CRITICAL: sob qualquer correção, lift ≠ 1 e 'a priorização é observável antes do voto' (l. 183) sobrevivem, e pela definição escrita no texto o '> 80 %' e o '4/5' (l. 139) sobrevivem, com folga de só 0,7 p.p. Não é MODERATE: a variável ex-ante que sustenta a parte distintiva da conclusão está corrompida, e os números de competitivos de todo o capítulo mudam. As recomputações de MEA (mea_02/mea_05) herdam ADV-3-001 (filtram CPFs de 11 dígitos, mea_02:58), então os números 'com CPF correto' do issue também precisam ser substituídos pelos de adv_02."
o_que_o_autor_pode_responder: "O erro de ligação existe e será corrigido. Mas o '> 80 %' não depende dele: com a ligação corrigida e a definição declarada na l. 68, a cobertura é 80,7 % em 2018 e 2022 e o lift é 1,90 e 1,85. O que derruba a cobertura para 75 % é aplicar a Prefeito o critério de 10 %, que 3/4 dos candidatos a prefeito atingem e que não é credencial de competitividade."
```

### I-3-002 — Definição de "competitivo" contraditória (l. 64 × l. 68) e diferente da implementada

```yaml
issue_id: I-3-002
steelman: "O construto 'credenciais eleitorais prévias' não está fixado. A l. 64 aplica os 10 % a qualquer disputa exceto vereador; a l. 68 restringe a disputas proporcionais; o código aplica a Governador, Senador e Prefeito, inclui Distrital, exclui Presidente e usa janela até 2020. O leitor não sabe o que foi medido, e a escolha muda o número central."
assessment: partially_valid
evidencia_contra:
  - fonte: "evidence/adv_02_metricas_variantes.csv (keepfirst_raw: cod × txt)"
    detalhe: "Na base atual, a divergência texto × código move pouco. Flag pelo código = 886 / 1.287; pela l. 68 com a mesma ligação = 872 / 1.247. Cobertura 80,9 → 81,3 % e 82,7 → 83,3 %; lift 1,873 → 1,891 e 1,890 → 1,908. Isoladamente, a divergência é de definição, não de resultado."
  - fonte: "evidence/adv_07_output.txt; src/1_silver/gerar_rrd.py:686-692, 779"
    detalhe: "A divergência só pesa quando combinada com a correção de I-3-001, e aí há critério substantivo para escolher. '10 % do QE' com qt_vaga = 1 em Prefeito vira 10 % dos votos válidos, patamar que 72,7 % (2016) e 71,8 % (2020) das candidaturas a prefeito atingem, 6.066 e 7.156 delas derrotadas. Em Dep. Federal, 10 % do QE é atingido por 14-20 %. O critério do código em majoritárias não mede 'credencial', e a definição da l. 68 é a defensável. Adotá-la preserva os números do capítulo (80,7 %; lift 1,85-1,90)."
  - fonte: "tese/03-medindo-coordenacao-intrapartidaria.qmd:68; src/2_gold/cap3_cs_features.py:92-100; tese/reports/resultados-capitulo-3/19_notas_redacao.csv (Histórico de vitórias; Cargos elegíveis)"
    detalhe: "A janela de 2018 já foi corrigida no texto (1998-2016 = código). Presidente não existe em resultados.parquet, então incluí-lo no texto é inócuo para a flag (0 candidaturas afetadas). Distrital afeta 7/3 candidaturas. Esses itens estão registrados pelo próprio autor em 19_notas_redacao.csv, logo são reconhecidos (critério c)."
severidade_sugerida: MODERATE
razao: "A contradição l. 64 × l. 68 e a diferença texto × código são reais (valid nessa parte). Porém: (i) na base atual o efeito é ≤ 0,02 no lift e ≤ 0,6 p.p. na cobertura; (ii) a queda para 75 % atribuída a I-3-001 vem da regra de 10 % em Prefeito, que adv_07 mostra não ser construto defensável, de modo que a correção natural (código alinhado à l. 68, l. 64 reescrita) não muda a conclusão nem os números; (iii) Presidente, janela 2018 e Distrital estão registrados pelo autor. Pela rubrica é 'correção de definição … sem mudar a conclusão'. Voltaria a MAJOR só se o autor optasse por manter a regra do código e reescrever o texto para ela: nesse caso, após I-3-001, '> 80 %' e '4/5' caem para 75-76 %."
o_que_o_autor_pode_responder: "A definição é a da l. 68; a l. 64 será alinhada a ela e o código deixará de aplicar os 10 % a disputas majoritárias, em que o limiar equivale a 10 % dos votos válidos e é atingido por três quartos dos candidatos a prefeito."
```

### I-3-003 — Universo do sorteio de referência

```yaml
issue_id: I-3-003
steelman: "O lift compara o núcleo com um sorteio entre todas as C_l, inclusive as 2.046 (2018) e 1.086 (2022) candidaturas que receberam zero e por construção não podem estar no núcleo. Parte do excesso é 'financiar × não financiar', não ordenação entre financiados. O nulo não é declarado, e sob o nulo de recebedores 'quase 90 % mais' vira 69 % em 2018."
assessment: partially_valid
evidencia_contra:
  - fonte: "tese/03-medindo-coordenacao-intrapartidaria.qmd:173, 183"
    detalhe: "O universo é declarado, embora só na Discussão e não em @sec-metricas: 'Partidos não distribuem seus recursos ao acaso entre as candidaturas que autorizaram concorrer' (l. 173). E o construto inclui a decisão de não financiar: 'é o partido que transfere, retém e responde eleitoralmente' (l. 183). O sorteio entre todas as C_l é o nulo coerente com a pergunta de gatekeeping (l. 5: controle da competição intrapartidária por meio dos recursos), em que dar zero é a forma mais forte de despriorizar. O nulo de recebedores condiciona numa margem da própria variável de tratamento."
  - fonte: "evidence/adv_03_output.txt (a)"
    detalhe: "Decomposição exata: lift_todas = lift_rec × lift_receber. A margem 'financiar × não financiar' contribui com fator 1,11 em 2018 (competitivos e eleitos) e 1,02-1,03 em 2022. Mesmo sob o nulo exigente o lift é 1,69 / 1,85 (competitivos) e 1,78 / 2,05 (eleitos), ainda fora da faixa de permutação (sta_permutacao_top_necr.csv, recebedores: P97,5 = 1,045 / 1,047). Não existe um nulo 'certo' alternativo: com piso de R$ 1 mil o lift é 1,65 / 1,85 e com R$ 10 mil é 1,56 / 1,82. A escolha é um contínuo e só o universo das candidaturas autorizadas tem justificativa teórica própria."
  - fonte: "evidence/adv_03_output.txt (b); evidence/mea_03_output.txt (d)"
    detalhe: "A objeção de que o universo completo é inflado por candidaturas 'de preenchimento' de cota não se sustenta. Entre as R = 0, as mulheres são 21,0 % (2018) e 25,4 % (2022), contra 35,6 % e 36,4 % entre recebedoras. Mulheres recebem mais que homens (82 % × 69 % recebedoras em 2018). As R = 0 são majoritariamente homens com votação baixa (68 % / 86 % abaixo de 1 % do QE), e 235 / 330 delas estão em listas sem recursos, que têm k = 0 e não afetam H nem A0."
  - fonte: "tese/reports/resultados-validacao-top-necr/validade_expost.csv"
    detalhe: "O autor já calculou o nulo alternativo (critério c), mas não o reporta no capítulo."
severidade_sugerida: MODERATE
razao: "Valid: @sec-metricas (l. 107) não declara nem justifica o universo, e o nível do lift de 2018 depende dele (fator 1,11). Exagerado: o universo atual tem justificativa substantiva, dada pelo próprio texto (l. 173, 183) e pela pergunta de gatekeeping. Sob o nulo declarado, 'quase 90 % mais' (l. 143) e 'o dobro' (l. 145, 147) estão numericamente corretos, e a conclusão sobrevive sob ambos. A correção é declarar e reportar a decomposição, sem mudança de método ou de interpretação. Pela rubrica: correção de definição que afeta a leitura, sem mudar a conclusão."
o_que_o_autor_pode_responder: "O sorteio é feito entre as candidaturas que o partido autorizou concorrer porque não financiar é parte da priorização. Restrito às que receberam algum recurso, o lift é 1,69 e 1,85 para competitivos e 1,78 e 2,05 para eleitos; a margem 'financiar ou não' responde por um fator de 1,11 em 2018 e 1,03 em 2022."
```

### I-3-004 — Síntese "1,9 … se repete … e em quase todos os limiares do Top-X%"

```yaml
issue_id: I-3-004
steelman: "A frase-título do capítulo afirma que um número se repete entre anos, alvos e cortes. O Top-X% vai de 1,38 a 3,60 (só 2 de 24 cortes em [1,8; 2,0]), a cobertura de eleitos em 2018 é 86,7 % e não 'acima de 87 %', e a igualdade 2018 × 2022 depende de listas em que o núcleo é a lista inteira (lift 2,20 × 1,91 sem elas)."
assessment: partially_valid
evidencia_contra:
  - fonte: "tese/reports/sensibilidade-top-x/resumo_nacional.csv"
    detalhe: "Confirmo as partes (3) e (4). Lifts Top-X% (comp. 2018: 2,08 / 2,05 / 2,02 / 1,93 / 1,73 / 1,53; eleitos 2018: 2,38 … 1,57; comp. 2022: 2,65 … 1,38; eleitos 2022: 3,60 … 1,46). Mesmo com a faixa generosa [1,7; 2,1], só 9 de 24 cortes entram. Cobertura de eleitos em 2018 = 86,74 %. Sobre isso não há defesa."
  - fonte: "tese/03-medindo-coordenacao-intrapartidaria.qmd:159, 177"
    detalhe: "O próprio capítulo traz os números corretos (l. 159: Top-95 % = 1,53 / 1,38; l. 177: Top-50 % lift 2,4 / 3,6 e 'o gradiente é monotônico'). O defeito é inconsistência interna da frase de síntese com o que o texto já reporta, não uma leitura errada da evidência que propague para outras conclusões."
  - fonte: "evidence/sta_bootstrap_diferencas.csv; agents/measurement.md (Verificações: listas com 1 candidato 163/33, k = C 207/100)"
    detalhe: "A parte (2), 'se repete em 2018 e 2022' no Top-NECr, se sustenta descritivamente (1,87/1,89; 1,98/2,12), e a diferença entre anos tem IC por partido contendo zero (lift competitivos +0,02 [−0,17; +0,22]; eleitos +0,14 [−0,11; +0,39]). O argumento de composição vai a favor do autor: das 207 listas com k = C em 2018, 163 têm um único candidato e não oferecem escolha de priorização. Elas puxam o lift para 1 por construção, então o 1,87 de 2018 é conservador, não inflado."
severidade_sugerida: MODERATE
razao: "As partes (3) 'quase todos os limiares' e (4) 'acima de 87 %' são falsas e precisam ser reescritas; a parte (2) é descritivamente correta e o viés de composição a favorece. A conclusão da l. 173 ('Partidos não distribuem seus recursos ao acaso … subconjunto ocupado de forma desproporcional') vale em todos os 24 cortes (lift > 1) e é afirmada corretamente em l. 159/177. É correção de número e redação que afeta a leitura, sem mudar a conclusão (MODERATE). Claim C3.9.01 = contradicted como escrita: concordo com o chair."
o_que_o_autor_pode_responder: "O lift fica em torno de 1,9-2,1 no Top-NECr, nos dois anos e para os dois grupos de referência. No Top-X% ele é maior que 1 em todos os cortes e cresce à medida que o corte se restringe (1,4 no Top-95 %; até 3,6 no Top-50 %). A cobertura é de 81-83 % dos competitivos e de 86,7-92,6 % dos eleitos."
```

### I-3-005 — "Estimativa conservadora" por efeito das cotas

```yaml
issue_id: I-3-005
steelman: "A Discussão qualifica todo o resultado como limite inferior com base num contrafactual ('se as cotas fossem retiradas do cálculo') que não foi calculado e cuja premissa está num placeholder. A única versão computável (lift estratificado por sexo) dá lift entre homens menor que o agregado."
assessment: valid
evidencia_contra:
  - fonte: "evidence/adv_04_output.txt"
    detalhe: "Tentei a operacionalização mais favorável ao autor: refazer NECr, k e núcleo em listas só de homens, simulando a escolha do partido fora das candidaturas protegidas pela reserva. A precisão sobe (competitivos 30,9 → 35,5 % em 2018; 27,8 → 34,2 % em 2022; eleitos 19,2 → 21,2 %; 12,4 → 14,8 %), o que dá suporte à frase 'puxa a precisão para baixo'. Mas o lift cai (competitivos 1,873 → 1,622; 1,890 → 1,742; eleitos 1,982 → 1,689; 2,117 → 1,918), como na estratificação de STA. As duas operacionalizações disponíveis contrariam a direção para o lift, que a l. 175 elege como 'o número que interessa'."
  - fonte: "evidence/sta_lift_por_sexo.csv"
    detalhe: "A cobertura de competitivas entre mulheres (92,6 % / 88,3 %) é maior que entre homens (79,3 % / 81,6 %). As mulheres competitivas estão mais no núcleo que os homens competitivos, o que também não sugere que as cotas diluam a priorização."
  - fonte: "notes/daily/2026-09-05.md:14"
    detalhe: "O autor já antecipa o tema como risco ('pode ser pegadinha na banca'), mas não há cálculo no repositório que sustente a direção afirmada. Nada a contrapor."
severidade_sugerida: MODERATE
razao: "Crítica válida: o claim é unsupported, e a evidência disponível inclina para o contrário no lift. Severidade exagerada: é uma frase de qualificação (l. 179) com placeholder. A conclusão central (l. 173, 183) não depende dela, e retirá-la ou reduzi-la à precisão resolve o problema sem mudar método, medida ou conclusão. Status do claim C3.9.07: mantenho unsupported, e não contradicted, porque nenhuma das duas operacionalizações implementa a realocação que o partido faria sem a obrigação legal. Registro que ambas contrariam a direção para o lift."
o_que_o_autor_pode_responder: "As mulheres são menos frequentemente competitivas (4,5 % contra 14,9 % dos homens em 2018; 6,0 % contra 17,3 % em 2022), o que reduz a precisão do núcleo. Isso não implica, porém, lift maior sem as cotas: restrito aos homens, o lift fica entre 1,62 e 1,92."
```

### I-3-006 (MODERATE; rebaixado pelo chair) — confirmação solicitada

```yaml
issue_id: I-3-006
steelman: "Nenhum indicador ou diferença tem faixa de variabilidade, e listas do mesmo partido não são independentes; o leitor não sabe o que é decisivo e o que é ruído."
assessment: partially_valid
evidencia_contra:
  - fonte: "tese/03-medindo-coordenacao-intrapartidaria.qmd:147, 175"
    detalhe: "O texto não lê 1,98 → 2,12 como movimento ('cerca do dobro, em ambos os ciclos'). A única diferença entre anos que interpreta é a queda da precisão, atribuída ao crescimento de Σk (2.318 → 3.824), que é aritmética."
  - fonte: "evidence/sta_permutacao_top_necr.csv"
    detalhe: "A inferência que sustenta a conclusão (lift ≠ 1) tem p < 0,0005 sob os dois nulos. Os dados são o universo de candidaturas, e não uma amostra."
severidade_sugerida: MODERATE
razao: "Confirmo o rebaixamento do chair (C4). A ausência de faixas é lacuna de apresentação; nenhuma conclusão escrita muda. As afirmações de igualdade que excedem a evidência estão em I-3-004."
o_que_o_autor_pode_responder: "Os indicadores descrevem o universo das candidaturas; a faixa de 10.000 sorteios dentro das listas (207-242 acertos esperados contra 445 observados em 2018) mostra que o resultado não é compatível com alocação ao acaso."
```

---

## Omissões dos especialistas

```yaml
id: ADV-3-001
titulo: "Segundo defeito de ligação: CPFs de 2012 e 2014 sem zeros à esquerda; 25 deputados federais eleitos em 2014 e candidatos em 2018 classificados como não competitivos"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 68
  secao: "#### Desempenho eleitoral prévio {#sec-competitivos}"
  trecho: "Para um candidato ser considerado competitivo em 2018, verificou-se o histórico eleitoral deste candidato desde 1998 à 2016"
afirmacao_do_autor: "O histórico de 1998-2016 (2018) e 1998-2018/2020 (2022) de cada candidato é verificado."
problema: "Em candidatos.parquet, 28,6 % dos CPFs de 2012 e 26,4 % dos de 2014 estão gravados sem zeros à esquerda (7-10 dígitos); nos demais anos têm 11 dígitos. gerar_rrd.py junta o histórico ao rrd pelo CPF como string (adicionar_historico_eleitoral, l. 182; alcancou_10pct_qe_hist, l. 805-808), então todo o histórico de 2012 (prefeitos) e de 2014 (eleição geral anterior a 2018) de candidatos com CPF iniciado em '0' (31,8 % das candidaturas de 2018 e 34,2 % das de 2022) não é ligado. Os especialistas não detectaram: MEA filtra CPFs com 11 dígitos (mea_02_competitivo_como_escrito.py:58) e herda o defeito, o que explica sua taxa de ligação de 94-97 %; com zfill(11) ela sobe para 99,5 %."
evidencia:
  tipo: recomputacao
  fontes: ["src/1_silver/gerar_rrd.py:177-187", "src/1_silver/gerar_rrd.py:797-809", "data/processed/candidatos.parquet (nr_cpf_candidato, anos 2012/2014)", "thesis-review/runs/run-001/evidence/adv_02_output.txt", "thesis-review/runs/run-001/evidence/adv_02_incumbentes_2014_nao_competitivos.csv", "thesis-review/runs/run-001/evidence/adv_02_metricas_variantes.csv"]
  detalhe: "Em 2018, das 378 candidaturas de deputados federais eleitos em 2014, 25 são 'não competitivas' na base, todas com CPF iniciado em 0 e todas no núcleo (w = 1); 17 foram reeleitas. Exemplos: Marx Beltrão (AL), Newton Cardoso Jr. (MG), Vitor Lippi (SP), Aliel Machado (PR), Nilto Tatto (SP). Com qualquer vitória em 2014 na regra: 30 (2018) e 6 (2022). Efeito isolado (ligação da base + zfill): competitivos 886 → 945, cobertura 80,9 → 81,1 %, lift 1,873 → 1,894 (2018); 1.287 → 1.302, 82,7 → 82,0 %, 1,890 → 1,879 (2022). Com D1 e D2 corrigidos: pela l. 68, 967 / 1.351, cobertura 80,7 / 80,7 %, lift 1,896 / 1,852; pelas regras do código, 1.075 / 1.568, 75,6 / 76,2 %, lift 1,830 / 1,762."
severidade: MAJOR
confianca: alta
recomendacao: "Normalizar nr_cpf_candidato com zfill(11) em candidatos.parquet (ou na leitura em gerar_rrd.py) antes de qualquer merge por CPF; regenerar junto com a correção de I-3-001; substituir os números 'com CPF correto' de MEA pelos de adv_02; acrescentar a 21_verificacoes.csv o teste 'toda candidatura de deputado federal eleito na legislatura anterior é competitiva' (hoje 353/378 = 93,4 % em 2018). Fundir com I-3-001 no pass 2 (mesma regeneração, mesma variável)."
claims: [C3.4.01, C3.6.01, C3.7.01, C3.7.02, C3.7.03]
```

```yaml
id: ADV-3-002
titulo: "CPF da própria candidatura a Dep. Federal atribuído por keep-first: 21 (2018) e 26 (2022) candidaturas com histórico, sexo e raça de outra pessoa"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 25
  secao: "### Universo empírico e recursos partidários"
  trecho: "A candidatura é a unidade utilizada para identificar o histórico eleitoral e estimar a participação nos recursos."
afirmacao_do_autor: "Cada candidatura é ligada ao seu próprio histórico eleitoral."
problema: "construir_base liga resultados de Dep. Federal a candidatos.parquet por (ano, UF, nr) com drop_duplicates(keep='first') (gerar_rrd.py:88-91, 111-113). Há 61 (2018) e 76 (2022) chaves de Dep. Federal com mais de um CPF, por substituições e registros indeferidos que reaproveitam o número. Quando o primeiro registro é o do substituído, a candidatura que recebeu votos e recursos herda CPF, histórico, ds_genero e ds_cor_raca de outra pessoa. MEA auditou só a ligação do histórico, não a da própria candidatura."
evidencia:
  tipo: recomputacao
  fontes: ["src/1_silver/gerar_rrd.py:84-113", "thesis-review/runs/run-001/evidence/adv_05_output.txt"]
  detalhe: "Nome do CPF atribuído difere (primeiro e último nome) em 21 candidaturas de 2018 e 26 de 2022, todas com votos, 20/22 com R > 0, 2/6 marcadas competitivas. Exemplos: 2022 AM UNIÃO 4444 Pauderney Avelino (ex-deputado federal, 52.014 votos, R$ 2,64 mi) recebe o CPF de 'Raquel Fernandes' e fica não competitivo; 2022 DF PSDB 4545 Andréia Zemuner recebe o CPF de 'Sérgio Fernandes Ferreira' (sexo atribuído pelo CPF errado); 2022 CE PDT 1251 José Arnon Bezerra de Menezes recebe o CPF de 'Pedro Augusto Geromel Bezerra de Menezes'. Efeito agregado pequeno (≈ 0,3 % das candidaturas), mas atinge também a variável de sexo usada no argumento das cotas (l. 179)."
severidade: MODERATE
confianca: media
recomendacao: "Na ligação da base, usar (ano, UF, cargo, nr) e priorizar o registro com situação deferida / inserido na urna (candidatos.parquet tem ds_situacao_candidatura e st_candidato_inserido_urna), ou desempatar pelo nome; regenerar junto com I-3-001/ADV-3-001. Confiança média: a comparação de nomes é heurística (primeiro e último token)."
claims: [C3.6.01, C3.9.07]
```

```yaml
id: ADV-3-003
titulo: "'Validação pós-eleitoral' pelos eleitos não separa priorização de efeito do dinheiro sobre o voto; limitação listada pelo autor nas notas e ausente do capítulo"
escala: macro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 84
  secao: "#### Cobertura, precisão e lift {#sec-metricas}"
  trecho: "Para validar a relevância eleitoral do indicador calculado, pode-se ordenar cada uma das listas de acordo com os repasses partidários para cada candidatura"
afirmacao_do_autor: "A correspondência entre núcleo e eleitos valida o núcleo priorizado (l. 17: 'validação pré e pós eleitoral'; l. 173: 'subconjunto … ocupado de forma desproporcional … por quem venceu depois dela')."
problema: "Os recursos partidários afetam a votação, então o lift de eleitos (1,98 / 2,12) mistura dois mecanismos: o partido escolher quem já venceria e o dinheiro produzir a vitória. A coincidência núcleo × eleitos é esperada até sob alocação estrategicamente cega, se o dinheiro converte em votos, e por isso não valida a priorização. Os especialistas trataram eleitos como referência válida e discutiram só números. O capítulo não declara a limitação. Ela está registrada pelo próprio autor: notes/daily/2026-09-13.md:67-68 ('não identifica efeito causal do dinheiro; não separa seleção de candidatos fortes de produção de competitividade') e :36-37 ('Não validar o núcleo pelos eleitos'); 19_notas_redacao.csv, ponto 'Interpretação' ('Cobertura dos eleitos tampouco demonstra isoladamente coordenação intencional')."
evidencia:
  tipo: textual
  fontes: ["tese/03-medindo-coordenacao-intrapartidaria.qmd:17", "tese/03-medindo-coordenacao-intrapartidaria.qmd:84", "tese/03-medindo-coordenacao-intrapartidaria.qmd:173", "tese/03-medindo-coordenacao-intrapartidaria.qmd:183", "notes/daily/2026-09-13.md:36-37, 67-68", "tese/reports/resultados-capitulo-3/19_notas_redacao.csv (Interpretação)"]
  detalhe: "grep -i 'causal|efeito do dinheiro|reverso' no capítulo = 0 ocorrências. A l. 183 limita a inferência só quanto ao processo interno de decisão, não quanto ao efeito do recurso sobre o voto. A parte distintiva da conclusão ('a priorização é observável antes do voto', l. 183) repousa na referência ex-ante (competitivos), cuja variável está comprometida por I-3-001/ADV-3-001. A referência ex-post não pode substituí-la como validação."
severidade: MODERATE
confianca: alta
recomendacao: "Reenquadrar a referência de eleitos como correspondência, não validação (l. 17, 84, 173), como o autor já planeja em notes/daily/2026-09-13.md item 6; declarar em @sec-validacao que o lift de eleitos não separa seleção de efeito do financiamento e que a evidência de priorização ex-ante vem dos competitivos."
claims: [C3.7.04, C3.7.05, C3.9.01]
```

## Resumo para o pass 2

| Issue | Sev. inicial | Assessment | Sev. sugerida | Nota |
|---|---|---|---|---|
| I-3-001 | MAJOR | valid | MAJOR | Causa confirmada sem resíduo (7.630/9.675 iguais); fundir ADV-3-001 e ADV-3-002; a queda para 75 % pertence a I-3-002 |
| I-3-002 | MAJOR | partially_valid | MODERATE | Efeito ≤ 0,02 no lift na base atual; regra de 10 % em Prefeito é quase trivial (72-81 % atingem); alinhar código à l. 68 preserva os números |
| I-3-003 | MAJOR | partially_valid | MODERATE | Universo atual tem justificativa no próprio texto (l. 173, 183); fator da margem de financiar = 1,11 / 1,03; declarar e reportar |
| I-3-004 | MAJOR | partially_valid | MODERATE | "quase todos os limiares" e "> 87 %" falsos; "se repete" descritivamente correto e conservador; o capítulo já tem os números certos em l. 159/177 |
| I-3-005 | MAJOR | valid | MODERATE | Claim unsupported; duas operacionalizações contrariam a direção no lift; frase isolada, conclusão não depende dela |
| I-3-006 | MODERATE | partially_valid | MODERATE | Rebaixamento confirmado |
| ADV-3-001 | — | nova | MAJOR | CPF sem zeros à esquerda em 2012/2014; 25 deputados de 2014 não competitivos em 2018 |
| ADV-3-002 | — | nova | MODERATE | CPF de substituído na própria candidatura (21 / 26) |
| ADV-3-003 | — | nova | MODERATE | Eleitos como "validação" não separam seleção de efeito do dinheiro |

## Limites

- A reconstrução do QE de Dep. Estadual e Senador usa votos válidos / eleitos (sem `data/raw/vagas`, ausente do repositório), como fez MEA. Afeta só a margem do critério (ii).
- A ligação municipal corrigida usa o nome do município normalizado. Linhas de resultados sem CPF após zfill: 1.101 de 231.694.
- ADV-3-002 identifica troca de pessoa por heurística de nome. Não verifiquei manualmente os 47 casos.
- Não recomputei as figuras Top-X% sob as flags corrigidas.
