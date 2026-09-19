# Adversarial review — run-002

```yaml
issue_id: I-3-001
steelman: "A regressão descreve uma parcela intralista, mas algumas listas perdem candidaturas após o cálculo do denominador; isso pode alterar a variância e o estimando."
assessment: valid
evidencia_contra:
  - fonte: "evidence/sta_lists_missing_mass.csv"
    detalhe: "Há listas com soma observada muito inferior a 1, incluindo NOVO-DF/2022."
severidade_sugerida: MAJOR
razao: "A alteração numérica é pequena, mas a especificação precisa escolher entre parcela original e parcela renormalizada."
o_que_o_autor_pode_responder: "Reestimar após declarar o universo efetivo da lista."
```

```yaml
issue_id: I-3-002
steelman: "A frase sobre desvantagem negra em 2022 pode sugerir robustez que depende do agrupamento."
assessment: valid
evidencia_contra:
  - fonte: "evidence/sta_cluster_sensitivity.csv"
    detalhe: "p=0,0287 por lista, mas p=0,1021 por partido."
severidade_sugerida: MODERATE
razao: "A estimativa permanece, mas a qualificação inferencial é necessária."
o_que_o_autor_pode_responder: "Informar a sensibilidade e não interpretar perda de significância como paridade."
```

## Omissões dos especialistas

Nenhuma omissão CRITICAL/MAJOR foi encontrada. Os números centrais foram auditados e as referências cruzadas existem.
