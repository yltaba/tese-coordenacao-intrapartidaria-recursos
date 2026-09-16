"""Grava classificacao_resultados.csv a partir da tabela do item 6 em
documento-trabalho.md (fonte de verdade é o texto; este script só serializa
a mesma tabela para uso programático, ex.: seleção do que entra no corpo do
capítulo).

Uso:
    python gerar_classificacao.py
"""
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent

LINHAS = [
    {
        "resultado": "Lift > 1 em todo o espectro de magnitude, nos dois anos e alvos",
        "estatuto": "resultado_central",
        "justificativa": "Robusto, monotônico, sem exceção, replica nas duas eleições.",
    },
    {
        "resultado": "Focalização (lift > 1) generalizada entre partidos com volume mínimo de informação",
        "estatuto": "resultado_central",
        "justificativa": "Não é artefato de poucas legendas grandes; reforça a validade externa do achado nacional.",
    },
    {
        "resultado": "Lift cresce sistematicamente com magnitude",
        "estatuto": "heterogeneidade_relevante",
        "justificativa": "Padrão real e replicável, mas qualifica o achado central em vez de constituí-lo.",
    },
    {
        "resultado": "Ranking de lift por partido pouco/nada persistente entre 2018-2022 (rho=0,60 eleitos; rho~0 competitivos)",
        "estatuto": "heterogeneidade_relevante",
        "justificativa": "Substantivo sobre limites de uma leitura de traço fixo do partido, mas N pequeno de famílias comparáveis.",
    },
    {
        "resultado": "Outliers de lift muito alto concentrados em partidos com E esperado pequeno (PPL, PMN, REDE etc.)",
        "estatuto": "diagnostico_robustez",
        "justificativa": "Aviso de leitura da tabela, não achado substantivo sobre focalização partidária.",
    },
    {
        "resultado": "PSOL como outlier de lift alto sem denominador pequeno",
        "estatuto": "diagnostico_robustez",
        "justificativa": "Caso único digno de nota, não sustenta generalização por ora.",
    },
    {
        "resultado": "Partidos marginais com lift indefinido (PCB, PCO, PMB, PRTB, PSTU, UP, DC, AGIR)",
        "estatuto": "ruido",
        "justificativa": "Ausência quase total de eleitos/competitivos no período torna o indicador não interpretável.",
    },
]


def main() -> None:
    df = pd.DataFrame(LINHAS)
    destino = HERE / "classificacao_resultados.csv"
    df.to_csv(destino, index=False, encoding="utf-8")
    print(df.to_string(index=False))
    print(f"\nSalvo em: {destino}")


if __name__ == "__main__":
    main()
