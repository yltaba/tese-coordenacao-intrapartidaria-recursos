---
description: Run completo do MVP de revisão no Capítulo 3 (measurement + statistics + results -> chair -> adversarial -> chair)
---

Execute um run completo de revisão do **Capítulo 3** (`tese/03-medindo-coordenacao-intrapartidaria.qmd`)
usando o sistema em `thesis-review/`. Você é o orquestrador; não faça a revisão você mesmo.

Passos, nesta ordem:

1. Crie o run: `python thesis-review/tools/new_run.py --chapter 3 --agents measurement,statistics,results,thesis-chair,adversarial`.
   Guarde o id impresso (`run-NNN`).

2. Lance **em paralelo** (uma única mensagem com três chamadas ao Agent tool) os subagentes
   `measurement-reviewer`, `statistics-reviewer` e `results-reviewer`, cada um com o prompt:
   "Capítulo 3: `tese/03-medindo-coordenacao-intrapartidaria.qmd`. Run: `run-NNN`. Escreva seu relatório
   em `thesis-review/runs/run-NNN/agents/<nome>.md` e scripts em `thesis-review/runs/run-NNN/evidence/`.
   Siga seu contrato e o PROTOCOL.md à risca. Não leia relatórios de outros agentes."

3. Quando os três terminarem, lance `thesis-chair` com o prompt "Run `run-NNN`, **pass 1**."

4. Quando terminar, lance `adversarial-reviewer` com o prompt "Run `run-NNN`."

5. Quando terminar, lance `thesis-chair` com o prompt "Run `run-NNN`, **pass 2**."

6. Leia `thesis-review/runs/run-NNN/synthesis/final_review.md` e responda ao usuário com: o bloco
   "Veredito", os issues CRITICAL/MAJOR (id, título, uma linha de razão), e o caminho dos arquivos.
   Não repita o parecer inteiro.

Se um agente falhar ou não escrever o arquivo esperado, relance apenas ele uma vez; se falhar de
novo, prossiga sem ele e registre a ausência no relatório final ao usuário.

**Fallback.** Se o Agent tool responder "Agent type '<nome>' not found" (acontece quando a sessão
começou antes de `.claude/agents/` existir), use `subagent_type: general-purpose` e comece o prompt com:
"Você atuará como o agente **<nome>**. Seu contrato completo está em `.claude/agents/<nome>.md` —
leia-o primeiro (ignore o frontmatter) e siga-o à risca, junto com CLAUDE.md, thesis-review/PROTOCOL.md,
thesis-review/rubric.yaml e thesis-review/templates/agent_report.md." O restante do prompt é o mesmo.

$ARGUMENTS
