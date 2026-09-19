# Mudanças aceitas / rejeitadas pelo autor

Registre aqui, por run e por issue, o que foi aceito, rejeitado ou adiado, e por quê.
O `/review-diff` usa este arquivo para distinguir "resolvido" de "ignorado".

| Run | Issue | Decisão | Justificativa | Data |
|---|---|---|---|---|
| run-001 | I-3-002 | Aceito e implementado (código) | Seguiu a recomendação: fixado o critério (ii) de "competitivo" na definição da l. 68 (10% do QE só em disputa proporcional Dep. Federal/Estadual). Removidos Governador/Senador/Prefeito de `adicionar_alcancou_10pct_qe_hist` em `gerar_rrd.py`. Detalhe em `thesis-review/runs/run-001/implementacao_2026-09-14.md`. | 2026-09-14 |
| run-001 | I-3-001 (D2) | Aceito e implementado (código) | zfill(11) no CPF na leitura de `candidatos.parquet` (`gerar_rrd.py::carregar_dados`), corrigindo a perda de zeros à esquerda em 28,6%/26,4% dos CPFs de 2012/2014. | 2026-09-14 |
| run-001 | I-3-001 (D1+D3) | Aceito e implementado (código) | Ligação candidatos↔resultados trocada de `drop_duplicates(["ano","uf","numero"], keep="first")` para chave por (ano, UF, cargo[, município], número), com desempate pelo registro APTO (`gerar_rrd.py::ligar_cpf`). Checagens do próprio achado (378 deputados eleitos em 2014 → 377/378 competitivos; "MG AVANTE 7025" 46→1 vitória de prefeito; 3 casos de identidade trocada corrigidos) confirmadas. | 2026-09-14 |
| run-002 | I-3-001 (STA-3-001) | Aceito e implementado (código + 2 números no texto) | Estimando mantido como parcela original R_il/R_l (denominador da lista completa); média PPML m_l·p_il na Hessiana, escores e AMEs. β/razões inalterados; EP/IC/AMEs mudam na 3ª-4ª casa; texto: AME competitivo/2022 12,1→12,0 e IC sup. Grande/2022 9,70→9,71. Renormalização entre retidas como sensibilidade (`sensibilidade_massa.csv`). Estimando declarado pelo autor no parágrafo das covariáveis de sec-premio-credenciais (resolved). Detalhe em `thesis-review/runs/run-002/implementacao_2026-09-19.md`. | 2026-09-19 |
