# Reprodução do benchmark de precisão do Top-NECr

Execute os comandos abaixo a partir da raiz do repositório.

## Cálculo a partir das nominatas salvas

```powershell
python tese/scripts/benchmark_precisao_top_necr.py
```

Entradas: `25_todas_nominatas.csv` e `15_cobertura_nacional.csv`, nesta pasta.
O segundo arquivo serve como conferência independente dos totais já publicados.

Saídas nesta pasta:

- `benchmark_precisao_top_necr.csv`: contagens nacionais, cobertura e precisão observadas e aleatórias, e lift.
- `benchmark_precisao_top_necr_nominatas.csv`: C, E, k, eleitos observados e esperados no núcleo, precisões por lista e peso de cada lista na precisão nacional. Precisões por lista em escala 0–1; no resumo nacional, em percentuais.
- `benchmark_precisao_top_necr_verificacao.json`: verificações, fórmulas, versões das dependências de cálculo e hashes SHA-256 das entradas e do script.

## Atualização do atlas e da imagem inserida na tese

```powershell
python tese/scripts/visualizar_capitulo3_v2.py
python tese/scripts/exportar_top_necr_atlas.py
```

O primeiro comando também recalcula o benchmark. O segundo exporta o gráfico `cobertura` do HTML atualizado para `figs/cap3_fig_top_necr_cobertura_precisao.png`. O capítulo referencia essa imagem. Não há edição manual dos valores no gráfico.

Dependências: Python, pandas, NumPy e Plotly; a exportação PNG utiliza Kaleido e Chrome compatível. O atlas também usa os módulos locais importados por seus scripts.

## Regeneração das tabelas de origem

```powershell
python tese/scripts/resultados_capitulo3.py
python tese/scripts/visualizar_capitulo3_v2.py
python tese/scripts/exportar_top_necr_atlas.py
```

O primeiro comando recompõe os resultados a partir das bases locais em `data/processed`, incluindo `rrd_df_novo.parquet`, e executa as conferências do relatório original. As fontes constam em `26_fontes.csv`. Essa etapa exige as bases e dependências do projeto, incluindo suporte a Parquet. Os scripts de cálculo não baixam os dados do TSE; a reprodução depende dessas bases locais.

## Definição e universo

Em cada nominata, o sorteio seleciona k candidatos dentre C, sem reposição, preservando E eleitos. Usa-se k arredondado conforme o relatório original; empates no corte observado recebem crédito fracionário. O número esperado de eleitos é k × E/C, calculado analiticamente, sem simulação ou semente aleatória.

No agregado nacional, precisão aleatória = Σ(k × E/C) / Σk. Não se usa a média simples de E/C nem a taxa nacional de eleitos entre todas as candidaturas. A precisão observada usa o mesmo denominador Σk.

As listas com k = 0 têm contribuição zero para numerador e denominador da precisão nacional; sua precisão individual fica indefinida. Todos os eleitos permanecem no denominador da cobertura nacional, inclusive os de listas sem recursos. Os lifts nacionais de precisão e cobertura são idênticos: Σ eleitos observados no núcleo / Σ eleitos esperados no núcleo.
