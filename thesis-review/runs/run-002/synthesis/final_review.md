# Parecer — Capítulo 3 — run-002

## Veredito

THESIS REVIEW — run-002 — Capítulo 3  
CRITICAL 0 | MAJOR 1 | MODERATE 5 | MINOR 1  
Measurement WARN · Statistics WARN · Results PASS · Internal validity WARN  
OVERALL: ⚠ Revision required

A cadeia do capítulo é coerente: o argumento ex-ante leva à identificação do Top-NECr, os resultados mostram a composição do núcleo, a regressão examina a distribuição contínua e a robustez testa cortes alternativos. Os números centrais foram reproduzidos. O elo mais fraco é a regressão intralista após filtros: algumas listas não conservam soma unitária nas parcelas observadas, embora as alterações recalculadas sejam pequenas.

## Issues arbitrados

1. **I-3-001 — MAJOR.** A especificação precisa declarar se o estimando é a parcela original antes dos filtros ou a parcela renormalizada entre candidaturas mantidas. A correção da massa, da Hessiana e dos escores deve preceder a consolidação dos coeficientes, EP e AMEs.
2. **I-3-002 — MODERATE.** A desvantagem racial de 2022 permanece como estimativa, mas a distinção estatística de paridade depende do cluster por lista e não resiste ao agrupamento por partido.
3. **I-3-003 — MODERATE.** Declarar que cobertura, precisão e lift nacionais são razões de somas com pesos diferentes; definir os 20,3/12,1 pontos percentuais como AMEs 0→1 com denominador recalculado.
4. **I-3-004 — MODERATE.** “Origem partidária” não deve ser apresentada como fonte exclusivamente FP/FEFC.
5. **I-3-005 — MODERATE.** “Todos os cargos” excede o conjunto mostrado na regressão; alinhar a frase à especificação efetiva.
6. **I-3-006 — MODERATE.** A contribuição deve manter linguagem associativa e reconhecer que atração por candidatos fortes e regras institucionais continuam explicações rivais.
7. **I-3-007 — MINOR.** Completar captions das tabelas de magnitude e a chave visual dos gráficos Top-X.

## O que está sólido

As definições do Top-NECr, arredondamento, empates e benchmark estão alinhadas ao código. A classificação de credenciais é ex-ante. As contagens nacionais, Top-NECr, Top-X, AMEs, razões e interações conferem com os CSVs e figuras atuais. Não foram encontrados placeholders, referências cruzadas quebradas ou problema estrutural que impeça a leitura. A seção Discussão foi deliberadamente excluída desta rodada.

## Próximo run

Após resolver I-3-001, regenerar os artefatos da regressão e reavaliar I-3-002 e I-3-003. Em seguida, revisar a redação das seções Dados, prêmio intralista e transição para a discussão.
