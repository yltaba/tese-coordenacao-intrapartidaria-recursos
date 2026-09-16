# thesis-review — revisão por agentes

Pipeline de *peer review* agentic da tese, operado pelo Claude Code. O repositório é a memória do sistema;
esta pasta guarda o estado.

```
thesis-review/
├── PROTOCOL.md            regras comuns a todos os agentes
├── rubric.yaml            severidades, esquemas de finding/claim/issue, gates
├── templates/             modelos de relatório, claim e issue
├── claims/claims.yaml     ledger consolidado de afirmações verificáveis (cumulativo)
├── runs/run-NNN/          um run = uma execução completa sobre um capítulo
│   ├── manifest.yaml      data, capítulo, agentes, hashes dos insumos
│   ├── agents/*.md        relatórios dos especialistas
│   ├── evidence/          scripts e saídas de recomputação
│   ├── synthesis/
│   │   ├── conflicts.md   agrupamento, descartes e conflitos entre agentes (chair, pass 1)
│   │   ├── adversarial.md tentativa de refutação dos issues MAJOR/CRITICAL
│   │   └── final_review.md parecer final arbitrado (chair, pass 2)
│   ├── issues.yaml        issues arbitrados
│   └── priority_queue.yaml fila de revisão: prioridade × evidência
├── revisions/accepted_changes.md   o que o autor aceitou/rejeitou de cada run
└── history.md             comparação run a run (PASS/WARN/FAIL por dimensão)
```

## Como rodar

| Comando | Faz |
|---|---|
| `/review-ch3` | Run completo do MVP no Capítulo 3: measurement + statistics + results → chair → adversarial → chair. |
| `/review-chapter <n> [agentes]` | Mesmo fluxo em outro capítulo, opcionalmente escolhendo agentes (`theory,literature,writing`…). |
| `/synthesize-review <run>` | Reexecuta só a síntese (chair) sobre relatórios já existentes. |
| `/adversarial-review <run>` | Reexecuta só a fase adversarial. |
| `/review-claim <claim_id>` | Aprofunda uma única afirmação do ledger, recomputando o que for preciso. |
| `/review-diff <runA> <runB>` | Compara dois runs: o que foi resolvido, o que surgiu, o que persiste. |

## Regras que não mudam

1. Agentes de revisão nunca editam `tese/`, `src/`, `data/`.
2. Nenhuma crítica sem passagem citada + artefato que a sustenta.
3. Ordem: especialistas → chair → adversarial → chair. O writing-reviewer roda por último e só sobre texto que os demais não condenaram.
