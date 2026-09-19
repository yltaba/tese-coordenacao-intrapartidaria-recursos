# Coerência entre os capítulos 2, 3 e 4

- **Data da análise:** 18/09/2026.
- **Escopo:** só os pontos de junção entre `tese/02-literatura.qmd`, `tese/03-medindo-coordenacao-intrapartidaria.qmd` e `tese/04-mecanismo-causal-coordenacao.qmd` — terminologia, cadeia de frentes empíricas, redundâncias entre capítulos e referências cruzadas. Não repete os achados internos de cada capítulo, já registrados em:
  - [02-literatura-secoes-iniciais.md](02-literatura-secoes-iniciais.md) (seções 2.1–2.3)
  - [02-literatura-financiamento-e-argumento.md](02-literatura-financiamento-e-argumento.md) (Financiamento e Argumento)
  - [03-medindo-coordenacao.md](03-medindo-coordenacao.md) (Cap. 3, cruzado com `thesis-review/runs/run-002/`)
  - [04-mecanismo-temporal.md](04-mecanismo-temporal.md) (Cap. 4, com piloto de extensões empíricas)
- **Método:** leitura dos três capítulos já revisados (comentários HTML inseridos), mais buscas de texto (`grep`) para contar usos de termos e referências cruzadas entre arquivos. Nenhum `.qmd` foi alterado por esta nota.
- **Nenhum comentário HTML foi inserido nos capítulos para os pontos desta nota** — são todos de coerência entre arquivos, não de um parágrafo específico, então ficam só aqui. Onde um ponto já tinha comentário no capítulo (ex.: `[A10]`, `[3.7-3]`), esta nota remete a ele em vez de duplicar.

---

## 1. A cadeia de três frentes, do Argumento aos capítulos empíricos

O fim do Argumento (Cap. 2) promete três frentes: **(i)** composição do núcleo priorizado, **(ii)** prêmio intralista por credencial, **(iii)** priorização temporal — "o capítulo 3 trata dos pontos i) e ii), enquanto o capítulo 4 investiga iii)".

| Frente | Onde é anunciada | Onde é testada | A conexão é explícita? |
|---|---|---|---|
| (i) núcleo priorizado | Argumento, `@cheibubsin2020` | Cap. 3, Top-NECr | Sim — `@sec-argumento` é citado no Cap. 3 (l. 5) |
| (ii) prêmio intralista | Argumento | Cap. 3, `sec-premio-credenciais` | Sim |
| (iii) priorização temporal | Argumento | Cap. 4 inteiro | **Não** — o Cap. 4 cita `@sec-argumento` uma vez (l. 17, para diferenciar-se de Cheibub & Sin), mas nunca diz "esta é a frente (iii)". Ver `[4.0-2]` no Cap. 4. |

A frente (iii) também é a única das três sem justificativa teórica própria no Cap. 2 — o comentário `[A9]` no Argumento já aponta isso, e o comentário `[2.2-2]` em "Partidos como organizações heterogêneas" identifica o parágrafo (dinheiro **e** *timing* juntos, `cox_mccubbins_2005_setting`) que poderia sediar essa justificativa. **Esta é a lacuna estrutural mais importante encontrada nas três revisões**: a tese testa (iii) muito bem no Cap. 4, mas nunca constrói, no Cap. 2, por que (iii) deveria ser verdade.

## 2. Terminologia

Checagem por contagem de ocorrências (`grep`, 18/09/2026):

| Termo | Cap. 2 | Cap. 3 | Cap. 4 | Situação |
|---|---|---|---|---|
| "ex ante" / "ex-ante" | 3 sem hífen, 2 com hífen | 1 com hífen | 3 com hífen | **Inconsistente já dentro do Cap. 2.** O comentário `[A8]` no Argumento já pede para uniformizar com "ex ante" (sem hífen, como no latim), mas isso deveria valer para os três capítulos: Cap. 3 e Cap. 4 usam hífen. Decidir uma forma e aplicar nos três. |
| "lista" / "nominata" | 55 / 13 | 61 / 23 | 4 / 3 | "Lista" domina nos três, "nominata" é usado como variação estilística. Não é um problema — o CLAUDE.md já registra os dois como sinônimos —, mas o Cap. 4 usa "nominata" só 3 vezes em um capítulo curto, o que pode soar como inserção pontual em vez de escolha de registro. Não é prioritário. |
| "credencial" / "competitivo" | 14 / 20 | 38 / 40 | 6 / 38 | **Cap. 4 quase não usa "credencial" (6 ocorrências) e usa "competitivo" 38 vezes** — o oposto do Cap. 3, que usa os dois de forma equilibrada porque a nota de rodapé de `sec-competitivos` os declara intercambiáveis. Como o Cap. 4 não repete essa nota de rodapé nem remete a ela, um leitor que começasse pelo Cap. 4 não saberia que "candidato competitivo" é a mesma variável `candidato_competitivo` definida no Cap. 3. Sugestão: uma frase no início do Cap. 4 remetendo a `@sec-competitivos`. |
| "Top-NECr" no Cap. 4 | — | central | **0 ocorrências** | O Cap. 4 nunca menciona Top-NECr, apesar de ser o resultado central do Cap. 3 e de o piloto de extensão (ver `04-mecanismo-temporal.md`) mostrar que ele produz um sinal diferente (e, para o *lift* semanal, complementar) do que "competitivo". Ver a seção 3 abaixo. |

## 3. A escolha de variável de corte entre capítulos

O Cap. 3 tem **dois** resultados centrais, com significados diferentes:
- **Top-NECr**: núcleo de concentração financeira (definido pela distribuição de recursos, tamanho ≈ NECr).
- **`candidato_competitivo`**: credencial eleitoral prévia (definida pelo histórico eleitoral, independente do financiamento).

O Cap. 3 mostra que os dois se relacionam (mais de 80% dos competitivos estão no Top-NECr), mas não são a mesma coisa — o piloto do Cap. 4 (`notes/tecnico/cap4-piloto-topnecr-lift-semanal.md`) quantifica isso: índice de Jaccard de apenas 0,31/0,27 entre as duas variáveis.

O Cap. 4 usa **exclusivamente** `candidato_competitivo` como variável de corte em todas as figuras e no Cox, e nunca menciona Top-NECr. Isso não é necessariamente um erro — a pergunta do Cap. 4 ("quem tem credencial recebe antes?") é diferente da pergunta do Top-NECr ("quem o partido decidiu concentrar recebe antes?") —, mas a tese nunca torna essa escolha explícita. Um leitor que acabou de ler o Cap. 3, onde Top-NECr é o resultado mais enfatizado, pode estranhar que o Cap. 4 mude de variável sem aviso.

**Recomendação:** uma frase no início da seção "A campanha eleitoral semana a semana" (Cap. 4) dizendo por que o corte por credencial, e não por Top-NECr, é o adequado para a pergunta temporal — e, se o autor decidir incluir o *lift* semanal do piloto (recomendado em `04-mecanismo-temporal.md`), essa figura preencheria exatamente a lacuna de nunca usar Top-NECr no Cap. 4.

## 4. Redundâncias de conteúdo entre capítulos

Mapeadas nas notas de cada capítulo, reunidas aqui para visão de conjunto:

| Conteúdo | Aparece em | Nota de origem |
|---|---|---|
| @silvacervi2017, 89,6% empresarial, achados sobre incumbentes | Cap. 2: "No Brasil, evidências recentes..." (2.1) → Financiamento → Argumento (3 vezes) | `02-literatura-secoes-iniciais.md` `[2.1-7]`; `02-literatura-financiamento-e-argumento.md` seção 4 |
| @janusz_barreiro_cintron_2021, *resource gatekeeping*, mulheres | Idem | Idem |
| Argumento central da tese (partido conecta ambições individuais a interesse coletivo) | Cap. 2: fim de 2.1 (`[2.1-8]`), fim de 2.2 (`[2.2-5]`), Argumento (l. 189) | `02-literatura-secoes-iniciais.md` seção 3 |
| Vitórias por cargo como preditor de recebimento | Cap. 3 (regressão intralista, parcela) e Cap. 4 (Cox, tempo) — mesmo tipo de covariável, resultados nunca comparados | `04-mecanismo-temporal.md` seção 2, item 4; comentário `[4.3-1]` |
| Cláusula de barreira / cláusula de desempenho | Cap. 2 (Financiamento, sobrevivência) e Cap. 4 (contraste 2018/2022) — mesma lógica institucional, nunca conectada | `04-mecanismo-temporal.md` comentário `[4.1-1]` |

Nenhuma dessas redundâncias é um erro por si — repetir uma fonte entre capítulos é normal. O padrão comum é que a *mesma evidência* aparece em lugares diferentes sem nunca ser *comparada consigo mesma*, perdendo a chance de mostrar convergência (caso de vitórias por cargo) ou é *repetida quase literalmente* sem nenhuma versão servir de remissão para a outra (caso de Silva & Cervi / Janusz et al.).

## 5. Referências cruzadas do Quarto

Checagem de todas as `@sec-*` usadas nos três capítulos (`grep`, 18/09/2026):

- `@sec-argumento`: citado por Cap. 2 (2×, dentro do próprio Argumento), Cap. 3 (abertura) e Cap. 4 (l. 17). **Uso correto e consistente.**
- `@sec-dados`, `@sec-competitivos`, `@sec-metricas`, `@sec-discussao-cap3`, `@sec-apendice-formal`: só citados dentro do próprio Cap. 3. Nenhum é citado pelo Cap. 4, apesar de o Cap. 4 depender diretamente da definição de `@sec-competitivos` (usa a mesma variável) — ver seção 2 desta nota.
- `@sec-premio-credenciais`: **nunca citado por nenhum outro capítulo**, apesar de ser o resultado mais próximo, em espírito, do Cox do Cap. 4 (mesmas covariáveis de vitórias por cargo). Ver seção 4, item "vitórias por cargo".
- "capítulo 3" / "capítulo 4" em texto plano (Argumento, Cap. 2, comentário `[A10]`): já apontado como inconsistente com o padrão de referência cruzada do Quarto (`@sec-...`) usado em todo o resto do livro.

**Recomendação:** ao decidir incluir a remissão de `[4.0-2]` (frente iii) e a frase sugerida na seção 3 desta nota, usar `@sec-competitivos` e `@sec-premio-credenciais` como referências cruzadas, não texto plano.

## 6. Dois pontos que atravessam os três capítulos e merecem decisão do autor antes de fechar a versão final

1. **O compromisso de autoria no Argumento.** O comentário no próprio `.qmd` do Cap. 2 (`<!-- Revisão pendente: texto melhorado por IA a partir de rascunho humano -->`) marca a seção inteira como escrita com auxílio de IA — o único ponto, nos três capítulos, em conflito direto com o contrato pessoal de não inserir texto gerado por IA no corpo da tese. Como o Argumento é o texto que mais aparece redundantemente nos outros capítulos (seção 4 acima), reescrevê-lo do próprio punho teria efeito de cascata: resolveria também parte da redundância, porque as versões em Financiamento e no próprio Cap. 3/4 poderiam passar a remeter à formulação final, em vez de cada uma reformular o argumento à sua maneira.
2. **A correção metodológica MAJOR do Cap. 3 (`I-3-001`, massa não unitária na regressão fracionária) afeta indiretamente o Cap. 4.** O comentário `[4.3-1]` recomenda comparar os HRs do Cox com as razões de parcela do Cap. 3 como evidência convergente. Se `I-3-001` for corrigido e os coeficientes da regressão intralista mudarem (mesmo que pouco, como os testes do run-002 sugerem), essa comparação deveria ser refeita depois da correção, não antes.

## 7. Checklist de prioridade (transversal)

- [ ] Escrever, no Cap. 2, a justificativa teórica de por que o *timing* do repasse importa (hoje só existe no Cap. 4) — ver seção 1.
- [ ] Adicionar remissão explícita no Cap. 4 à frente (iii) do Argumento — ver seção 1, comentário `[4.0-2]`.
- [ ] Uniformizar "ex ante"/"ex-ante" nos três capítulos — ver seção 2.
- [ ] Uma frase no Cap. 4 remetendo a `@sec-competitivos` para declarar a equivalência credencial = competitivo, e justificando o uso de competitivo (não Top-NECr) como corte temporal — ver seções 2 e 3.
- [ ] Comparar explicitamente os HRs do Cox (Cap. 4) com as razões de parcela da regressão intralista (Cap. 3) como evidência convergente, citando `@sec-premio-credenciais` — ver seção 4 e 6.2.
- [ ] Decidir sobre reescrever o Argumento do próprio punho (contrato de autoria) — ver seção 6.1.
- [ ] Resolver a correção metodológica `I-3-001` do Cap. 3 antes de fazer a comparação Cox/regressão intralista do item acima — ver seção 6.2.
