---
description: Reexecuta apenas a fase adversarial (red team) de um run existente. Uso: /adversarial-review <run-NNN>
argument-hint: <run-NNN>
---

Argumento: `$ARGUMENTS` — id do run. Exige `thesis-review/runs/<run>/issues_draft.yaml` (chair pass 1).

Lance `adversarial-reviewer` com "Run `<run>`." Ao terminar, liste ao usuário, por issue: id,
assessment (valid / partially_valid / invalid), severidade sugerida, e as omissões `ADV-*` apontadas.
Lembre o usuário de rodar `/synthesize-review <run> 2` para o chair arbitrar.
