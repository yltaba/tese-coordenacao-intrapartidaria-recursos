# Parecer — Capítulo 3 — run-001

Chair: thesis-chair (pass 2, arbitragem). Insumos: relatórios de measurement, statistics e results (`agents/`), síntese do pass 1 (`synthesis/conflicts.md`, `issues_draft.yaml`), parecer adversarial (`synthesis/adversarial.md`) e evidências (`evidence/`, inclusive `adv_*` e as verificações do chair `chair_01`–`chair_03`). Saídas: `issues.yaml`, `priority_queue.yaml` e `claims/claims.yaml`.

## Veredito

```
THESIS REVIEW — run-001 — Capítulo 3
CRITICAL 0 | MAJOR 3 | MODERATE 12 | MINOR 6
Measurement WARN · Statistics WARN · Results WARN · Internal validity WARN
OVERALL: ⚠ Revision required
```

Theory, literature e writing não foram avaliados neste run (não havia agentes para essas dimensões).

A conclusão central sobrevive a tudo o que foi recomputado: os partidos concentram recursos num núcleo que contém muito mais candidaturas competitivas e eleitas do que um sorteio dentro da lista. Combinando qualquer definição de competitivo, qualquer correção da ligação de CPF, os dois universos de sorteio e a exclusão das listas com núcleo = lista, o lift fica entre 1,64 e 2,20, sempre fora da faixa de permutação (0,95–1,05). O que precisa mudar é outra coisa: (1) a variável "competitivo" está corrompida na base e não é a que o texto define; (2) a frase-síntese do capítulo afirmava uma invariância que a evidência não tem.

**Versão avaliada.** O parecer arbitra a versão do capítulo registrada no manifesto (sha256 `0aec63e5…`, reconstruída byte a byte em `evidence/chair_03_capitulo_auditado_reconstruido.qmd`). Às 19:16 de 14/09, depois das leituras dos especialistas, o `.qmd` foi editado (sha `679ece09…`). Só mudaram a l. 173 (a síntese "1,9") e a primeira frase da l. 175 ("O lift é o número que interessa…"); o diff está em `evidence/chair_03_diff_auditado_vs_atual.txt`. As linhas citadas abaixo continuam válidas. Quando a edição afeta um issue, isso está indicado.

## A cadeia do capítulo (macro) — elo mais fraco

| Elo | Conteúdo | Estado após arbitragem |
|---|---|---|
| Pergunta | Os partidos priorizam candidaturas na alocação intralista dos recursos (*gatekeeping*)? (l. 5–11) | Clara. |
| Teoria → hipótese | Priorização estratégica: o núcleo financiado deve concentrar credenciais prévias e sucesso posterior. | Não avaliado (sem theory/methodology reviewer). O adversarial apontou uma lacuna de desenho: eleitos não separam seleção de efeito do dinheiro (I-3-021). |
| Desenho | Núcleo endógeno (Top-NECr; Top-X%) comparado a uma referência ex-ante (competitivos) e uma ex-post (eleitos) contra sorteio intralista. | Adequado para rejeitar "alocação ao acaso". As convenções que fixam o *nível* do lift não são declaradas: universo do sorteio (I-3-003), partido × UF sob coligações (I-3-009), listas com núcleo = lista (I-3-004), razão de somas (I-3-012). |
| Medida — núcleo | NECr, k, empates, Top-X%, H, cobertura, precisão, lift. | **Sólida.** Reproduzida lista a lista (1.570 listas) e nos agregados por três agentes. |
| **Medida — referência ex-ante** | Flag `candidato_competitivo`. | **Elo mais fraco.** Três defeitos de ligação de CPF na construção da base (I-3-001), e uma definição que diverge entre l. 64, l. 68 e o código (I-3-002). |
| Resultado | Lift 1,87–2,12; cobertura 81–93 %. | Robusto no sinal. O nível de 2018 vai de 1,69 a 2,20 conforme a convenção. Números de competitivos provisórios até regenerar a base. Sem faixas de variabilidade (I-3-006). |
| Conclusão | "Partidos priorizam, e a priorização é observável antes do voto" (l. 183). | O núcleo da conclusão sobrevive. A síntese "1,9 se repete" (I-3-004), a "estimativa conservadora" (I-3-005) e a leitura de eleitos como validação (I-3-021) excedem a evidência. |

**Por que a referência ex-ante é o elo mais fraco.** É o único elo em que o objeto medido não corresponde ao definido no texto e em que a própria base está errada. É também esse elo que sustenta a parte distintiva da conclusão ("observável antes do voto"). A referência de eleitos não o substitui (I-3-021). As recomputações indicam que a conclusão numérica sobrevive: lift entre 1,76 e 1,91 em todas as 13 variantes de flag por ano. Mas "> 80 %" e "4/5" (l. 139) só sobrevivem se o autor fixar a definição da l. 68.

## Issues arbitrados

### MAJOR

#### I-3-001 — Ligação de CPF defeituosa na construção da base (histórico eleitoral e identidade da candidatura)
**MAJOR → MAJOR · confiança alta** · findings: MEA-3-001, ADV-3-001, ADV-3-002 · l. 68

**O problema.** `gerar_rrd.py` liga resultados, candidatos e histórico por CPF com três defeitos na mesma etapa:
- **D1 — chave não única.** `drop_duplicates(["ano_eleicao","sg_uf","nr_candidato"], keep="first")` (l. 61-78, 506-524). Prefeitos, vereadores, vices e suplentes compartilham número na UF, e as vitórias de dezenas de municípios vão para o primeiro CPF do arquivo. Exemplo: 2022 MG AVANTE 7025 tem 46 "vitórias de prefeito". O defeito também atinge Governador (79 de 189 vitórias) e Senador (177 de 269).
- **D2 — CPFs sem zeros à esquerda em 2012/2014** (ADV-3-001). Em `candidatos.parquet`, 28,6 % dos CPFs de 2012 e 26,4 % dos de 2014 têm 8–10 dígitos; nos outros anos têm 11. O merge é por CPF-string (l. 182, 805-808). Para os 31,8 % (2018) e 34,2 % (2022) de candidaturas com CPF iniciado em "0", **os registros de 2012 e 2014 não são ligados**. Precisão sobre o alcance: essas candidaturas não perdem todo o histórico, só o de 2012 e 2014. Na prática, 473 candidaturas de 2018 disputaram 2014 e 518 disputaram 2012 com CPF gravado sem zeros.
- **D3 — identidade da própria candidatura** (ADV-3-002). `construir_base` (l. 88-113) aplica o mesmo keep-first à base de Dep. Federal. Há 61 (2018) e 76 (2022) números com mais de um CPF (substituições). Quando o primeiro registro é o do substituído, a candidatura herda CPF, gênero, raça e histórico de outra pessoa: 21 (2018) e 26 (2022) casos.

**Verificação do chair** (`evidence/chair_01_*`, `chair_02_*`, scripts próprios):
- D2: Marx Beltrão, Vitor Lippi, Aliel Machado e Newton Cardoso Jr. constam como "ELEITO POR QP" em 2014 com CPF de 9 ou 10 dígitos. Em 2018 têm `n_eleicoes_deputado_federal = 0` e não são competitivos.
- Dos 378 deputados federais eleitos em 2014 que concorreram em 2018, 52 têm zero vitórias federais na base e 25 são não competitivos, todos com CPF iniciado em 0.
- Numa ligação independente por (UF, cargo, número), 29 (2018) e 6 (2022) candidaturas com vitória estadual/federal em 2014 são não competitivas (adversarial: 30 / 6).
- D3, 3 de 3 casos conferidos: o primeiro registro é de pessoa INAPTA. Pauderney Avelino (2022 AM 4444, 52.014 votos) fica com o CPF e o gênero FEMININO de outra candidata. Andréia Zemuner (2022 DF 4545) fica MASCULINO. José Arnon Bezerra (2022 CE 1251) herda o CPF de outro candidato e é marcado competitivo.

**O que o adversarial disse.** *Valid.* Testou e descartou todas as explicações alternativas; reproduziu a flag da base em 7.630/7.630 e 9.675/9.675 candidaturas com o merge keep-first. Propôs MAJOR: não CRITICAL porque a conclusão sobrevive, nem MODERATE porque a variável ex-ante está corrompida. Corrigiu o pass 1: a queda da cobertura para ~75 % vem da regra de 10 % em Prefeito (I-3-002), não da ligação.

**Decisão.** MAJOR, seguindo o adversarial. Regenerar a base é mudança de medida, e a conclusão qualitativa sobrevive em todas as variantes. **ADV-3-001 e ADV-3-002 foram fundidos aqui**: são o mesmo padrão de código (ligação por CPF com chave não normalizada ou não única), atingem as mesmas variáveis e se corrigem numa única regeneração.

**⚠ Números "corrigidos" são PROVISÓRIOS.**
- Os números "com CPF correto" do pass 1, vindos de MEA (1.017 / 1.554; cobertura 75,4 / 76,5 %; lift 1,82 / 1,77; pela l. 68: 907 / 1.337, 80,7 / 81,2 %, 1,88 / 1,86), **estão superados**. O script de MEA descarta CPFs sem 11 dígitos e herda D2.
- Os de `adv_02` (tabela abaixo) corrigem D1 e D2, mas não D3. Além disso, ligam cargos municipais pelo nome do município e reconstroem o QE estadual. Servem como ordem de grandeza, não como número para o texto.

| PROVISÓRIO (adv_02, D1+D2) | Competitivos | Cobertura | Precisão | Lift |
|---|---|---|---|---|
| Base atual 2018 / 2022 | 886 / 1.287 | 80,9 / 82,7 % | 30,9 / 27,8 % | 1,87 / 1,89 |
| Definição da l. 68 | 967 / 1.351 | 80,7 / 80,7 % | 33,7 / 28,5 % | 1,90 / 1,85 |
| Regras do código | 1.075 / 1.568 | 75,6 / 76,2 % | 35,1 / 31,2 % | 1,83 / 1,76 |

**Recomendação.** Em `gerar_rrd.py`:
1. Aplicar `zfill(11)` ao CPF na leitura.
2. Ligar por (ano, UF, cargo, número), e por (ano, UF, cargo, município, número) nos cargos municipais.
3. Na base de Dep. Federal, desempatar pelo registro APTO (`ds_situacao_candidatura`).
4. Regenerar `rrd_df_novo.parquet` e tudo que depende de `candidato_competitivo`, `ds_genero` e `mulher`.
5. Acrescentar a `21_verificacoes.csv`: CPF com 11 dígitos em todos os anos; `n_eleicoes_prefeito ≤ 6`; deputado federal eleito na legislatura anterior é sempre competitivo (hoje 353/378); nome e gênero da base iguais aos do registro APTO.

**Decidir I-3-002 antes.**

#### I-3-002 — Definição de "competitivo" contraditória (l. 64 × l. 68) e diferente da implementada
**MAJOR → MAJOR · confiança alta** · finding: MEA-3-002 · l. 64, 68

**O problema.**
- A l. 64 aplica os 10 % do QE a "disputas que concorreram, exceto vereador"; a l. 68, só a disputa proporcional.
- O código (l. 686-692) aplica os 10 % a Governador, Senador e Prefeito com `qt_vaga = 1`, ou seja, 10 % dos votos válidos.
- O código também exclui Presidente, inclui Distrital e usa vitórias até 2020 para 2022.

**O que o adversarial disse.** *Partially valid*, sugeriu MODERATE:
- Na base atual, texto × código move no máximo 0,02 no lift.
- A regra de 10 % em Prefeito é quase trivial: 72–81 % dos candidatos a prefeito a atingem, contra 14–20 % em Dep. Federal (`adv_07`). Alinhar o código à l. 68 seria a correção natural e preserva os números.
- Presidente, janela e Distrital já estão em `19_notas_redacao.csv`.

**Decisão: não sigo o rebaixamento.** Nenhuma saída é só textual:
- Alinhar à l. 68 exige mudar o código da medida.
- Alinhar o texto ao código faz "> 80 %" e "4/5" caírem para 75,6 / 76,2 % assim que I-3-001 for corrigido.
- "Na base atual move pouco" só vale enquanto a base estiver corrompida.
- O próprio `adv_07` mostra que a regra implementada não mede credencial.

Presidente, Distrital e janela não pesam na severidade; o que pesa é o critério (ii).

**Recomendação.** Fixar o construto na l. 68 (recomendado): 10 % do QE só em disputa proporcional. Retirar os 10 % de Governador/Senador/Prefeito no código, reescrever a l. 64 para coincidir e declarar a janela real. Se o autor mantiver a regra do código, precisa justificá-la como credencial e aceitar a cobertura de ~76 %.

#### I-3-004 — A síntese "1,9 se repete … em quase todos os limiares" não corresponde à evidência
**MAJOR → MAJOR · confiança alta** · findings: RES-3-004, STA-3-003 · l. 173 (versão auditada)

**O problema.** "O resultado do capítulo pode ser resumido em um número: 1,9", que "se repete em 2018 e 2022 … no Top-NECr e em quase todos os limiares do Top-X%"; "acima de 87 % dos eleitos". A evidência:
- Os lifts do Top-X% vão de 1,38 a 3,60; só 2 de 24 cortes ficam em [1,8; 2,0].
- A cobertura de eleitos em 2018 é 86,7 %.
- Entre anos, a igualdade depende da convenção: sem as listas com k = C, 2,20 × 1,91; entre recebedores, 1,69 × 1,85. A direção da diferença se inverte conforme a convenção.

**O que o adversarial disse.** *Partially valid*, sugeriu MODERATE:
- "Quase todos os limiares" e "> 87 %" são falsos.
- "Se repete" é descritivamente correto, e a composição favorece o autor: 163 das 207 listas com k = C têm um único candidato e puxam 2018 para 1.
- O capítulo já traz os números certos nas l. 159 e 177.

**Decisão: não sigo o rebaixamento.**
- A frase não é um número qualquer: é o **resultado declarado do capítulo**. Ela afirma invariância em três eixos e falha em dois.
- O argumento de composição vale para uma convenção (listas k = C), mas não para a outra (nulo de recebedores), em que 2018 fica em 1,69.
- Pela rubrica, a conclusão sobrevive, mas não como está escrita: MAJOR.
- A correção é barata. O próprio autor já trocou o resultado declarado, não só um número.

**Estado na versão atual (679ece09).** A l. 173 agora diz "Em todas as operacionalizações usadas, o *lift* calculado é superior a um", o que é verdadeiro (24/24 cortes + Top-NECr). As partes falsas saíram.

**Pendente:**
- A l. 181 ("A priorização em 2022 não desapareceu. Mudou de forma") ainda lê 2018 × 2022 sem reconhecer a sensibilidade à composição.
- Faltam a declaração das listas com k = C e o lift nas fronteiras comparáveis.
- A nova frase agrava I-3-021.

O status fica `open` até o run-002 confirmar.

**Recomendação.** Manter a nova l. 173 e acrescentar a amplitude: 1,9–2,1 no Top-NECr; 1,4–3,6 no Top-X%, maior quanto mais restrito o corte. Declarar as 207 / 100 listas com k = C e reportar em nota o lift nas 579 / 548 listas com fronteira comparável. Na l. 181, dizer "da mesma ordem, sensível à composição das listas".

### MODERATE

#### I-3-003 — Universo do sorteio de referência não declarado em @sec-metricas
**MAJOR → MODERATE · confiança alta** · findings: STA-3-001, MEA-3-004 · l. 107

**O problema.** O sorteio inclui quem recebeu zero, de modo que o lift também credita ao núcleo a decisão de financiar. Entre recebedores, o lift de 2018 é 1,69 (competitivos) e 1,78 (eleitos).

**O que o adversarial disse.** *Partially valid*, MODERATE.
- O universo tem justificativa no texto: gatekeeping inclui não financiar ("entre as candidaturas que autorizaram concorrer", l. 173 auditada; "transfere, retém", l. 183).
- O nulo de recebedores condiciona numa margem do próprio tratamento.
- Decomposição exata: a margem de financiar vale um fator de 1,11 em 2018 e 1,03 em 2022.

**Decisão: sigo.** Sob o nulo usado, "quase 90 % mais" e "o dobro" estão corretos. A escolha é teoricamente coerente, e a correção é declarar e reportar a variante que o autor já calculou (`validade_expost.csv`). A consequência para a síntese está em I-3-004.

**Versão atual:** a frase da l. 173 usada como justificativa foi removida; hoje só a l. 183 sustenta a escolha, o que torna a declaração mais necessária.

**Recomendação.** Uma a duas frases na l. 107 com a justificativa; em nota, o lift entre recebedores e o fator 1,11 / 1,03.

#### I-3-005 — "Estimativa conservadora" por efeito das cotas
**MAJOR → MODERATE · confiança média → alta** · findings: RES-3-001, MEA-3-008, STA-3-004 · l. 179

**O problema.** O contrafactual não foi calculado, e a premissa está num placeholder vazio. As duas operacionalizações computáveis contrariam a direção para o lift:
- estratificação por sexo: lift entre homens 1,63 / 1,75 contra 1,87 / 1,89 no agregado;
- Top-NECr refeito em listas só de homens (`adv_04`): lift 1,62 / 1,74.

A precisão sobe entre homens (35–40 %).

**O que o adversarial disse.** *Valid*, mas MODERATE: é uma frase de qualificação, a conclusão não depende dela e retirá-la resolve. Claim `unsupported`, e não `contradicted`.

**Decisão: sigo.** A correção não mexe em método, medida nem conclusão. A confiança sobe porque duas operacionalizações independentes concordam. O claim C3.9.07 fica `unsupported`: nenhuma das duas implementa a realocação sem obrigação legal. Isso contraria a regra de "status mais conservador", e a justificativa está no ledger.

**Recomendação.** Retirar "o que faz dos indicadores apresentados uma estimativa conservadora", ou restringir a afirmação à precisão. Preencher X/Y **depois** de regenerar a base, porque D3 muda o gênero atribuído em parte dos casos. Com a base atual, X/Y = 4,5 % vs 14,9 % (2018) e 6,0 % vs 17,3 % (2022).

#### I-3-021 — Eleitos como "validação" não separam priorização de efeito do dinheiro (novo, ADV-3-003)
**— → MODERATE · confiança alta** · l. 17, 84, 173

**O problema.** O lift de eleitos mistura "o partido escolheu quem venceria" com "o dinheiro produziu a vitória". O capítulo não declara a limitação (0 ocorrências de "causal"). As notas do autor já a registram: `notes/daily/2026-09-13.md`, l. 35-36 e 69-70; `19_notas_redacao.csv`, item "Interpretação".

**Decisão.** Aceito como issue, com evidência textual conferida pelo chair. MODERATE, porque a parte distintiva da conclusão repousa na referência ex-ante. Na versão atual, a nova l. 173 ("priorizam … candidatos que posteriormente são eleitos") reforça o problema.

**Recomendação.** Trocar "validação" por "correspondência" para eleitos e declarar o limite em @sec-validacao.

#### I-3-006 — Nenhuma faixa de variabilidade
**MODERATE → MODERATE · alta** · STA-3-002, STA-3-008 · l. 147

O adversarial confirmou o rebaixamento feito no pass 1. O texto não lê 1,98 → 2,12 como movimento, e o teste decisivo tem p < 0,0005. **Recomendação:** citar a faixa dos 10.000 sorteios que o autor já tem e reportar IC95 por lista e por partido, recalculados com a base nova.

#### Demais MODERATE (não revisados pelo adversarial; severidade do pass 1 confirmada)
- **I-3-008** — "Fundos públicos" rotula uma variável de origem partidária (1,2–2,0 % não é FEFC/FP). Trocar por "recursos partidários" nas l. 5, 31, 125 e 183.
- **I-3-009** — A unidade partido × UF não é declarada, embora 85 % das listas de 2018 estivessem em coligação e 25 % das de 2022 em federação. Uma frase na seção de dados.
- **I-3-007** — Lift ≡ razão de coberturas ≡ razão de precisões, apresentados como três confirmações. Uma frase após @eq-indicadores; enxugar as l. 145–147.
- **I-3-010** — A robustez troca de construto (Top-X%) e omite piso/teto do Top-NECr. Reposicionar a l. 155 e reportar piso/teto.
- **I-3-011** — A "assinatura de camadas" deveria vir dos lifts marginais por faixa (< 1 acima de ~80 % da massa), que existem e não são reportados.
- **I-3-012** — Razão de somas pondera pelas listas grandes. Declarar e citar a mediana do lift por lista (2,0 / 1,9).
- **I-3-013** — As Figuras 3–5 não renderizam (caminho antigo após a mudança para `tese/reports/`), e `03-formulas-propostas.qmd` está ausente. Corrigir os caminhos.
- **I-3-014** — Números da Discussão ainda entre colchetes; "candidaturas" onde são posições (Σk); "4 a 7 vezes" quando é 7,45. Fechar os valores.

### MINOR (confirmados)
- **I-3-015** — Convenções de denominador não declaradas (efeito ≤ 0,03 p.p.).
- **I-3-016** — Médias de competitivos por lista referem-se às listas financiadas (1,11 / 1,98 contra 1,03 / 1,81 em todas).
- **I-3-017** — "As listas dobraram" vale só para a mediana.
- **I-3-018** — Legendas das Figuras 1–5 incompletas.
- **I-3-019** — Cabeçalho "## Discussão" duplicado (l. 169).
- **I-3-020** — "Núcleos maiores elevam a cobertura" vale só para cortes aninhados.

Ordem de trabalho sugerida: `priority_queue.yaml`. Resumo: decidir I-3-002 → regenerar a base (I-3-001) → em paralelo, textos baratos (I-3-004, I-3-013, I-3-003, I-3-021) → o que depende dos números novos (I-3-005, I-3-006, I-3-011…).

## O que está sólido (não mexer)

- **Núcleo Top-NECr.** NECr, k = ⌊NECr + 0,5⌋, empates fracionários, k = 0 sem recursos, H, cobertura, precisão e lift foram reproduzidos de forma independente para as 1.570 listas. Texto, código e CSVs coincidem.
- **Agregados de eleitos.** Σk 2.318 / 3.824; cobertura 86,74 / 92,63 %; precisão 19,20 / 12,43 %; lift 1,982 / 2,117. Eleitos não dependem da flag competitiva.
- **Referência analítica.** G k / C é a esperança correta do sorteio declarado (média de 2.000 permutações = valor analítico). A faixa dos 10.000 sorteios do autor foi reproduzida.
- **Lift > 1 é robusto.** Vale em 24/24 cortes do Top-X%, sob os dois nulos, nas 13 variantes de flag por ano, sem listas com k = C e com bootstrap por lista e por partido.
- **Universo e descritivos.** 7.630 / 9.675 candidaturas; 859 / 711 listas; 73 / 63 sem recursos; medianas e médias de C, NECr, C/NECr e NECr/C (l. 117–131); valores das Figuras 1–2.
- **Top-X%.** Definição, mínimo, aninhamento e monotonia verificados; Top-50 % cobertura 57,3 / 52,8 %; Top-95 % lift 1,53 / 1,38.
- **Identidade lift ≡ razões** confere, e os scripts do autor já a verificam (o problema está só na redação, I-3-007).
- **Flag ex-ante, não ex-post.** O capítulo usa `candidato_competitivo`, não `candidato_forte_cs`.
- **Janela de 2018** (até 2016) confere com o código.
- **Linhas não afetadas pela edição das 19:16.** Os achados sobre elas continuam valendo tal como estão.

## Conflitos não resolvidos

1. **Escolha do construto de "competitivo" (I-3-002).** É decisão do autor, não da revisão. A revisão recomenda a l. 68, mas os números finais de competitivos (cobertura 75,6 % ou 80,7 %) dependem dela.
2. **Status de C3.9.07.** Statistics sustenta `contradicted`; o chair e o adversarial, `unsupported`. Registrado no ledger; muda só se alguém implementar um contrafactual de realocação.
3. **Qual nulo é o "certo" (I-3-003).** O revisor de estatística prefere o de recebedores como principal; o adversarial, o de todas as candidaturas. O chair resolveu como "declarar e reportar ambos". A escolha do nulo principal fica com o autor.
4. **Versão do capítulo.** A arbitragem vale para `0aec63e5`. A edição `679ece09` parece resolver as partes falsas de I-3-004, mas não foi revisada por especialista.
5. **`tese/03-formulas-propostas.qmd` ausente.** O que MEA e STA atribuem à nota formal (decisões em aberto, "o capítulo reporta piso e teto", "não ler como confirmação recíproca") continua não verificável pelo chair. Nenhum issue depende só disso.

## Próximo run: o que reavaliar

- **Pré-condição:** base regenerada (I-3-001 + I-3-002). O run-002 sobre um `rrd_df_novo.parquet` antigo não é comparável. Registrar no manifesto o sha de `rrd_df_novo.parquet` e de `src/1_silver/gerar_rrd.py` (hoje fora do manifesto).
- **measurement:** conferir os testes de plausibilidade da ligação (CPF 11 dígitos; `n_eleicoes_prefeito ≤ 6`; deputados da legislatura anterior 100 % competitivos; nome e gênero iguais ao registro APTO) e a coincidência entre a flag e a definição do texto.
- **statistics:** refazer permutação, bootstrap, nulo de recebedores, listas k = C e estratificação por sexo com a flag nova; verificar se as faixas entraram no texto.
- **results:** conferir os novos 886 / 1.287, "> 80 %", 30,9 / 27,8 %, 1,87 / 1,89, X/Y da l. 179, Figuras 3–4 regeneradas e caminhos das Figuras 3–5 (I-3-013).
- **Texto:** confirmar a nova l. 173 e resolver l. 181 (I-3-004), l. 179 (I-3-005) e l. 17/84 (I-3-021).
- **Agentes a acrescentar:** theory ou methodology reviewer (I-3-021 mostrou a lacuna de desenho) e, depois das correções, writing reviewer.
- **Sistema de revisão:** atualizar `tools/new_run.py`/manifesto e `CLAUDE.md` para os caminhos `tese/reports/…`, e registrar em `revisions/accepted_changes.md` o que o autor aceitar de cada issue.
