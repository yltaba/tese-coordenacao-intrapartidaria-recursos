---
description: Aprofunda uma única afirmação do claim ledger, recomputando o que for preciso. Uso: /review-claim <claim_id> [agente]
argument-hint: <claim_id> [measurement|statistics|results]
---

Argumentos: `$ARGUMENTS` — id do claim (ex.: `C3.4.07`) e, opcionalmente, o agente especialista a usar
(padrão: o `agent` registrado no claim em `thesis-review/claims/claims.yaml`; se o claim não existir
no ledger, use `results-reviewer` e peça que ele o registre).

1. Localize o claim no ledger e mostre-o.
2. Lance o agente com: "Aprofundamento do claim `<id>`: `<texto do claim>`, em `<arquivo:linha>`.
   Verifique exaustivamente — recompute a partir de `data/processed/` se possível; salve o script em
   `thesis-review/claims/evidence/<id>/`. Escreva `thesis-review/claims/evidence/<id>/report.md` com:
   o claim, o que foi verificado, resultado, status final (supported / partially_supported /
   unsupported / contradicted / unverifiable), concerns, e a recomendação ao autor. Não edite a tese."
3. Atualize o `status`, `concerns` e `evidencia` do claim em `claims.yaml` com o resultado.
4. Responda ao usuário com o status final e a razão em ≤ 5 linhas.
