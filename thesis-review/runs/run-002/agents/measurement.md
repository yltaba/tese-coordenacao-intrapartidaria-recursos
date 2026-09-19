# measurement-reviewer — Capítulo 3 — run-002

## Escopo e método

Li o capítulo, o código atual das medidas, os relatórios auditados e as recomputações em `evidence/mea_*`. A discussão foi excluída conforme o escopo registrado em `runs/run-002/ESCOPO.md`.

## Avaliação macro

As definições do Top-NECr, do arredondamento de `k`, do tratamento de empates e do benchmark correspondem ao código vigente. A classificação ex-ante também está implementada de forma coerente com a motivação temporal. Restam duas correções de apresentação e uma decisão sobre o estimando da regressão intralista: a expressão “recursos partidários” não deve ser equiparada automaticamente a FEFC/FP; e a definição ampla de cargos na seção de credenciais precisa ser distinguida dos cargos efetivamente estimados. A recomputação encontrou listas em que filtros da regressão removem candidaturas sem renormalizar a parcela original; esse ponto é tratado em detalhe pelo relatório estatístico.

## Achados

```yaml
id: MEA-3-001
titulo: "Origem partidária não equivale necessariamente a FEFC/FP"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 31
  secao: "Dados"
  trecho: "Estes somam recursos do Fundo Partidário e Fundo Especial de Financiamento de Campanhas."
afirmacao_do_autor: "Os registros cuja origem é recurso de partido somam apenas recursos do Fundo Partidário e do FEFC."
problema: "A variável identifica a origem partidária declarada, mas não garante que todo registro seja classificado exclusivamente como FP ou FEFC. A diferença é pequena, porém a frase transforma uma convenção de fonte em uma afirmação substantiva sobre a origem legal."
evidencia:
  tipo: artefato
  fontes: ["tese/reports/resultados-capitulo-3/19_notas_redacao.csv", "src/1_silver/gerar_rrd.py"]
  detalhe: "As notas de redação registram a distinção entre origem partidária e fonte exclusiva FEFC/FP; a recomputação indica 1,21% em 2018 e 1,96% em 2022 fora da classificação estrita."
severidade: MODERATE
confianca: alta
recomendacao: "Descrever a variável como repasses com origem partidária e dizer que eles incluem recursos dos fundos, sem afirmar exclusividade; ou apresentar uma checagem de fontes."
claims: []
```

```yaml
id: MEA-3-002
titulo: "Escopo dos cargos precisa coincidir com a definição operacional"
escala: micro
localizacao:
  arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd
  linha: 137
  secao: "Prêmio intralista das credenciais eleitorais prévias"
  trecho: "Vitórias anteriores para todos os cargos estão associadas a parcelas maiores dos recursos da lista nas duas eleições"
afirmacao_do_autor: "A regressão estima associações para todos os cargos listados na definição de credencial."
problema: "Presidente aparece na definição geral, mas não é apresentado como covariável no modelo/figura; a formulação ‘todos os cargos’ pode fazer o leitor procurar um efeito que não foi estimado."
evidencia:
  tipo: textual
  fontes: ["tese/03-medindo-coordenacao-intrapartidaria.qmd:53", "tese/03-medindo-coordenacao-intrapartidaria.qmd:135", "tese/reports/regressao-fracionaria/coeficientes.csv"]
  detalhe: "A tabela de coeficientes e a figura apresentam os cargos efetivamente incluídos; Presidente não aparece como coeficiente."
severidade: MODERATE
confianca: alta
recomendacao: "Substituir ‘todos os cargos’ por ‘os cargos estimados’ ou listar explicitamente os cargos na frase e explicar por que Presidente não entra na regressão."
claims: []
```

## Claims

```yaml
claim_id: C3.3.01
capitulo: 3
secao: "Seleção do núcleo priorizado: Top-NECr"
claim: "NECr, k e empates são definidos de forma endógena aos recursos e listas sem recursos recebem k=0."
localizacao: {arquivo: tese/03-medindo-coordenacao-intrapartidaria.qmd, linha: 37}
evidencia: {tipo: codigo, referencia: "src/2_gold/cap3_cobertura_top_necr.py; evidence/mea_audit.py"}
assessment: {status: supported, confidence: alta}
agent: measurement-reviewer
```

## Verificações que passaram

- Top-NECr, arredondamento, empates fracionários e benchmark reproduzem a implementação atual.
- A classificação competitiva usa informação anterior ao pleito e os números 973/1.354 e as amostras 7.254/9.263 foram reproduzidos.
- Os casos sem recursos e casos-limite do arredondamento foram verificados em `mea_caso_*.csv`.

## Limites desta revisão

Não avaliei inferência estatística, redação geral ou literatura. A reconstrução de históricos eleitorais foi limitada aos artefatos disponíveis; não regenerei a base de produção.
