# Harmonização do capítulo 4 — 19/09/2026

Decisão do autor: identificar recursos partidários exclusivamente pela origem
`Recursos de partido político`, independentemente da fonte. O capítulo 4 conserva
a janela entre o início da campanha e o dia da eleição, inclusive.

O carregador preserva a origem ao agregar as transações. Fluxo, lift, primeiro e
maior repasse usam o mesmo filtro. Em 2018, PATRIOTA nas receitas é normalizado
para PATRI, sigla da mesma legenda na base de candidaturas. Isso recupera 218
primeiros repasses que apareciam como censurados na base RRD. As datas são
recalculadas na cópia de trabalho; `rrd_df_novo.parquet` não foi alterado.
O Cox e ambas as figuras de Kaplan-Meier foram regenerados.

## Conferência

`verificacao.csv` compara todas as 7.630 candidaturas de 2018 e 9.675 de 2022.
Os primeiros repasses recalculados conferem com as transações. A diferença entre
os recursos na janela e o total do capítulo 3 é integralmente explicada pelas
receitas fora da janela, com tolerância de um centavo por candidatura:

| Eleição | Recursos fora da janela na base de candidaturas | Lift na última semana | Lift do capítulo 3 |
|---|---:|---:|---:|
| 2018 | R$ 6.786.809,57 | 1,8979355482 | 1,8909191282 |
| 2022 | R$ 16.734.842,17 | 1,8546357827 | 1,8552167975 |

A origem foi harmonizada; os recortes temporais permanecem distintos.
`divergencias.csv` detalha os registros com diferença de total ou primeiro
repasse corrigido. Diferenças de total explicadas pela janela são esperadas.
`cap4_survival_km_primeiro.csv` e `cap4_survival_km_maior.csv` guardam S(t) nos
pontos 1 e 2 semanas da escala das curvas. O fluxo acumulado está em
`../fluxo-semanal/fluxo_semanal.csv`, e o lift em `../lift-semanal/`.

## Reprodução

Da raiz do repositório:

```powershell
python tese/scripts/regenerar_figuras_cap4.py
python -m unittest discover -s tests -p test_cap4_origem.py -v
```

O gerador interrompe a execução se os primeiros repasses não conferirem ou se
houver diferenças de recursos não explicadas pela janela temporal. Três testes
de regressão verificam: distinção entre origem e fonte, normalização da origem
de 2014 e vínculo PATRIOTA/PATRI de 2018. Os notebooks exploratórios antigos
não são os geradores oficiais das figuras e seus resultados não foram atualizados.
