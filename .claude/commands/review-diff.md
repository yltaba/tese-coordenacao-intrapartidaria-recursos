---
description: Compara dois runs de revisão do mesmo capítulo: o que foi resolvido, o que persiste, o que surgiu. Uso: /review-diff <run-A> <run-B>
argument-hint: <run-A> <run-B>
---

Argumentos: `$ARGUMENTS` — dois ids de run (A anterior, B posterior), do mesmo capítulo.

Faça você mesmo (sem subagente), lendo `issues.yaml`, `manifest.yaml` e `synthesis/final_review.md`
dos dois runs e `thesis-review/revisions/accepted_changes.md`:

1. **Insumos.** Compare os hashes em `manifest.yaml`: quais arquivos da tese/código mudaram entre A e B.
2. **Pareamento de issues.** Um issue de A corresponde a um de B se compartilha claim ids, ou a mesma
   localização (arquivo + seção) e o mesmo diagnóstico. Classifique cada issue de A como
   `resolvido` (não aparece em B e o texto mudou), `persistente` (aparece em B), `ignorado` (não
   aparece em B mas o trecho não mudou — verifique no `.qmd`), `rebaixado`/`elevado` (severidade mudou).
   Issues só em B são `novos`.
3. **Gate.** Tabela A vs B com contagens por severidade e gate por dimensão.
4. Escreva `thesis-review/runs/<run-B>/diff_from_<run-A>.md` com as tabelas e um parágrafo de síntese
   ("Os dois problemas metodológicos da versão anterior foram resolvidos; três novos problemas de
   interpretação surgiram após a reformulação da seção X").
5. Acrescente/atualize a linha de B em `thesis-review/history.md` com a coluna de diff.
6. Responda ao usuário com o parágrafo de síntese e a tabela de gate.
