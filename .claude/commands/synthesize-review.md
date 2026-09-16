---
description: Reexecuta apenas a síntese do chair (pass 1 e/ou 2) sobre relatórios já existentes de um run. Uso: /synthesize-review <run-NNN> [1|2|both]
argument-hint: <run-NNN> [1|2|both]
---

Argumentos: `$ARGUMENTS` — id do run e, opcionalmente, qual pass (`1`, `2` ou `both`; padrão `both`).

- Se `1` ou `both`: lance `thesis-chair` com "Run `<run>`, pass 1." (exige `agents/*.md`).
- Se `2` ou `both`: lance `thesis-chair` com "Run `<run>`, pass 2." (exige `synthesis/adversarial.md`;
  se não existir, avise o usuário e sugira `/adversarial-review <run>` antes).

Ao final, mostre o bloco "Veredito" de `synthesis/final_review.md` (se pass 2 rodou) ou a tabela de
agrupamento de `synthesis/conflicts.md` (se só pass 1).
