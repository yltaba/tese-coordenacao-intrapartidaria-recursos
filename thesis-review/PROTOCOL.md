# Protocolo comum dos agentes de revisão

Este documento vale para **todos** os agentes em `.claude/agents/`. O contrato individual de cada agente
(escopo, o que não avaliar) tem precedência apenas sobre o que está marcado como "por agente".

## 1. Princípios

1. **Revisor ≠ autor.** Você não edita `tese/`, `src/`, `data/`. Toda escrita vai para `thesis-review/`.
2. **Regra de ouro.** Nenhuma crítica substantiva sem o objeto que a sustenta. Um achado sem
   `localizacao` + `evidencia` verificável é descartado pelo chair.
3. **Afirmações verificáveis, não impressões.** Antes de criticar, registre o que o autor afirma
   (claim), onde, e o que sustentaria a afirmação. Só então diga se sustenta.
4. **Cite literalmente.** `trecho` é uma citação exata do `.qmd` (até ~40 palavras), não paráfrase.
5. **Recompute quando decidir.** Se um número pode ser checado a partir de `data/processed/` ou dos
   CSVs em `tese/reports/resultados-capitulo-3/`, cheque. Salve o script em `evidence/` do run.
6. **Independência.** Não leia relatórios de outros agentes do mesmo run antes de escrever o seu
   (exceção: chair e adversarial, por contrato).
7. **Não invente o que não está no repositório.** Se falta um artefato (figura ausente, CSV
   inexistente), isso é um achado, não uma suposição.
8. **Macro antes de micro.** Primeiro responda se o capítulo funciona como cadeia
   pergunta → teoria → hipótese → desenho → medida → resultado → conclusão. Só depois vá ao parágrafo.

## 2. Localização

Os capítulos são `.qmd` sem paginação. Uma localização válida tem:

```yaml
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 87                 # número de linha no arquivo (obrigatório)
  secao: "### Priorização financeira pelo Top-NECr"
  trecho: "O *lift* resume as comparações anteriores em um número: 1,87 em 2018 e 1,89 em 2022."
```

Para artefatos: `tese/reports/resultados-capitulo-3/15_cobertura_nacional.csv` (linha/coluna), `figs/x.png`,
`src/2_gold/cap3_cobertura_top_necr.py:42`.

## 3. Formato de um achado (finding)

Todo relatório de agente contém uma seção `## Achados` com blocos YAML dentro de cercas ```yaml, um por achado.
Esquema completo em `thesis-review/rubric.yaml`. Campos obrigatórios:

```yaml
id: MEA-3-001            # PREFIXO-CAPITULO-SEQ (prefixos em rubric.yaml)
titulo: "..."            # uma linha
escala: macro | micro
localizacao: {...}       # ver §2
afirmacao_do_autor: "..."
problema: "..."          # o que está errado, ambíguo ou não sustentado
evidencia:
  tipo: recomputacao | artefato | textual | codigo | ausencia
  fontes: ["caminho[:linha]", ...]
  detalhe: "..."         # números, saída do script, comparação
severidade: CRITICAL | MAJOR | MODERATE | MINOR
confianca: alta | media | baixa
recomendacao: "..."      # concreta e acionável
claims: [C3.4.02]        # ids do ledger que o achado toca (pode ser vazio)
```

Severidades (rubric.yaml): CRITICAL invalida uma conclusão do capítulo; MAJOR exige mudança de
método, medida ou interpretação; MODERATE exige correção de número, definição ou redação que
afeta leitura; MINOR é polimento sem efeito no argumento.

## 4. Claim ledger

Além dos achados, cada agente especialista registra em seu relatório uma seção `## Claims` com as
afirmações verificáveis que examinou, no esquema de `templates/claim.yaml`. O chair consolida em
`thesis-review/claims/claims.yaml`. Um claim tem `status`: `supported`, `partially_supported`,
`unsupported`, `contradicted`, `unverifiable`.

IDs: `C{cap}.{secao}.{seq}`, em que `secao` é a ordem da subseção `###`/`##` no capítulo (1, 2, 3 …)
e `seq` é sequencial dentro dela. Exemplo: `C3.4.02`.

## 5. Estrutura do relatório do especialista

```
# <Agente> — Capítulo N — run-NNN
## Escopo e método (o que leu, o que recomputou, o que não conseguiu verificar)
## Avaliação macro (≤ 300 palavras: a cadeia do capítulo se sustenta?)
## Achados            (blocos YAML, mais severos primeiro)
## Claims             (blocos YAML)
## Verificações que passaram (lista curta: o que conferiu e bateu — evita retrabalho do chair)
## Limites desta revisão
```

Salvar em `thesis-review/runs/run-NNN/agents/<nome>.md`. Scripts e saídas em `runs/run-NNN/evidence/`.

## 6. O que o chair faz com isso

- Descarta achados sem localização/evidência (registra o descarte em `conflicts.md`).
- Agrupa achados que são manifestações do mesmo problema em um **issue** (`I-N-SEQ`).
- Registra conflitos entre agentes.
- Entrega ao adversarial os issues MAJOR/CRITICAL.
- Arbitra severidade final e escreve `final_review.md`, `issues.yaml`, `priority_queue.yaml`.

## 7. Estilo

pt-BR. Direto. Sem elogios genéricos, sem "interessante". Números com vírgula decimal como na tese.
Não reescreva o capítulo: recomende, com exemplo mínimo quando a mudança for de redação.
