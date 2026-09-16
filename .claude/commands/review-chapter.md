---
description: Run de revisão em um capítulo, com escolha de agentes. Uso: /review-chapter <n> [measurement,statistics,results,methodology,theory,literature,writing]
argument-hint: <capítulo> [agentes]
---

Execute um run de revisão do capítulo indicado. Argumentos: `$ARGUMENTS` — o primeiro token é o número
do capítulo (1–4); o segundo, opcional, é a lista de agentes separada por vírgula. Padrão:
`measurement,statistics,results`. O `writing-reviewer`, se incluído, roda **depois** do chair pass 1
(para não polir o que outro agente condenou).

Passos:

1. Mapeie o capítulo para o arquivo (`thesis-review/tools/new_run.py` conhece o mapa) e crie o run:
   `python thesis-review/tools/new_run.py --chapter <n> --agents <lista>,thesis-chair,adversarial`.

2. Lance em paralelo os agentes especialistas escolhidos (exceto writing), cada um com:
   "Capítulo <n>: `<arquivo>`. Run: `run-NNN`. Escreva em `thesis-review/runs/run-NNN/agents/<nome>.md`;
   scripts em `evidence/`. Siga seu contrato e o PROTOCOL.md. Não leia relatórios de outros agentes."

3. `thesis-chair`, pass 1.

4. Se `writing` foi pedido: lance `writing-reviewer` agora, com o mesmo prompt do passo 2 mais
   "Leia `issues_draft.yaml` antes e não polir passagens condenadas."

5. `adversarial-reviewer`, run `run-NNN`.

6. `thesis-chair`, pass 2.

7. Responda ao usuário com o bloco "Veredito" de `final_review.md`, os issues CRITICAL/MAJOR e os caminhos.

**Fallback.** Se o Agent tool responder "Agent type '<nome>' not found", use `subagent_type: general-purpose`
e comece o prompt com: "Você atuará como o agente **<nome>**. Seu contrato completo está em
`.claude/agents/<nome>.md` — leia-o primeiro (ignore o frontmatter) e siga-o à risca, junto com CLAUDE.md,
thesis-review/PROTOCOL.md, thesis-review/rubric.yaml e thesis-review/templates/agent_report.md."
